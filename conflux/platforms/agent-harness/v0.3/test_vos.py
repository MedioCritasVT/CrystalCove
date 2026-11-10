"""Local checks: PYTHONPATH=<pika installation> python3 -m unittest -v test_vos.py"""
import json
import os
import tempfile
import threading
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import coordinator as c
import transport as t


def call(name, **arguments):
    return {'function': {'name': name, 'arguments': arguments}}


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.previous = c.DB
        c.DB = self.tmp.name + '/board.db'
        c.initialize()

    def tearDown(self):
        c.DB = self.previous
        self.tmp.cleanup()

    def test_post_and_read_are_shared_and_persistent(self):
        a = c.execute_tool('post_note', {'text': 'COVE-TEST-001'}, 1, 60)
        c.initialize()
        b = c.execute_tool('read_notes', {}, 4, 60)
        self.assertEqual(b['notes'][0]['text'], 'COVE-TEST-001')
        self.assertEqual(b['notes'][0]['node'], 1)
        self.assertEqual(b['notes'][0]['id'], a['note_id'])

    def test_real_tool_loop_records_receipt(self):
        responses = [
            {'role': 'assistant', 'content': '', 'tool_calls': [call('post_note', text='hello')]},
            {'role': 'assistant', 'content': 'Saved.'}]
        with patch.object(c, 'rpc', side_effect=responses) as rpc:
            result = c.chat(1, [{'role': 'user', 'content': 'Post hello'}])
        self.assertTrue(result['trace'][0]['ok'])
        self.assertEqual(result['trace'][0]['result']['note_id'], 1)
        self.assertEqual(rpc.call_args.args[1][-1]['role'], 'tool')
        with c.database() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM events').fetchone()[0], 1)

    def test_peer_tools_disabled_and_history_not_forwarded(self):
        with patch.object(c, 'rpc', return_value={'content': 'Peer answer'}) as rpc:
            result = c.execute_tool('ask_node', {'node': 2, 'question': 'What is 2+2?'}, 1, 60)
        self.assertEqual(result['from_node'], 2)
        self.assertIsNone(rpc.call_args.kwargs['tools'])
        self.assertEqual(len(rpc.call_args.args[1]), 2)
        self.assertEqual(rpc.call_args.args[1][-1]['content'], 'What is 2+2?')

    def test_self_delegation_and_unknown_tools_rejected(self):
        with self.assertRaises(ValueError): c.execute_tool('ask_node', {'node': 1, 'question': 'x'}, 1, 60)
        with self.assertRaises(ValueError): c.execute_tool('shell', {'command': 'anything'}, 1, 60)

    def test_tool_budget(self):
        outputs = [{'content': '', 'tool_calls': [call('read_notes')]} for _ in range(5)]
        with patch.object(c, 'rpc', side_effect=outputs) as rpc:
            result = c.chat(1, [{'role': 'user', 'content': 'read'}])
        self.assertEqual(len(result['trace']), 4)
        self.assertIsNone(rpc.call_args.kwargs['tools'])
        self.assertIn('limit reached', result['answer'])

    def test_oversized_batch_no_actions(self):
        with patch.object(c, 'rpc', return_value={'content': '', 'tool_calls': [call('post_note', text='x')] * 5}):
            result = c.chat(1, [{'role': 'user', 'content': 'hello'}])
        self.assertEqual(result['trace'], [])
        self.assertEqual(c.execute_tool('read_notes', {}, 1, 60)['notes'], [])

    def test_failure_after_note_preserves_receipt(self):
        outputs = [{'content': '', 'tool_calls': [call('post_note', text='saved')]}, RuntimeError('model unavailable')]
        with patch.object(c, 'rpc', side_effect=outputs):
            result = c.chat(1, [{'role': 'user', 'content': 'post'}])
        self.assertIn('error', result)
        self.assertTrue(result['trace'][0]['ok'])

    def test_error_is_not_success(self):
        outputs = [{'content': '', 'tool_calls': [call('ask_node', node=1, question='self')]}, {'content': 'Cannot do that.'}]
        with patch.object(c, 'rpc', side_effect=outputs):
            result = c.chat(1, [{'role': 'user', 'content': 'ask yourself'}])
        self.assertFalse(result['trace'][0]['ok'])

    def test_no_tools_for_background_task(self):
        with patch.object(c, 'rpc', return_value={'content': 'Title'}) as rpc:
            result = c.chat(1, [{'role': 'user', 'content': 'title'}], use_tools=False)
        self.assertIsNone(rpc.call_args.kwargs['tools'])
        self.assertEqual(result['trace'], [])

    def test_images_rejected(self):
        with self.assertRaises(ValueError):
            c.validate_messages([{'role': 'user', 'content': [{'type': 'image_url'}]}], True)

    def test_http_auth_board_and_chat(self):
        server = c.ThreadingHTTPServer(('127.0.0.1', 0), c.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        try:
            with patch.dict(os.environ, {'VOS_RABBIT_PASSWORD': 'test-password'}):
                with self.assertRaises(HTTPError) as denied: urlopen(base + '/health')
                self.assertEqual(denied.exception.code, 401)
                headers = {'Authorization': 'Bearer test-password', 'Content-Type': 'application/json'}
                with urlopen(Request(base + '/notes', headers=headers)) as response:
                    self.assertEqual(json.load(response), {'notes': []})
                with patch.object(c, 'rpc', return_value={'content': 'hello'}):
                    payload = json.dumps({'node': 2, 'messages': [{'role': 'user', 'content': 'hello'}]}).encode()
                    with urlopen(Request(base + '/chat', headers=headers, data=payload)) as response:
                        self.assertEqual(json.load(response)['answer'], 'hello')
        finally:
            server.shutdown(); server.server_close(); thread.join()

    def test_protocol_keeps_tool_calls(self):
        assistant = {'role': 'assistant', 'content': '', 'tool_calls': [call('read_notes')]}
        response = MagicMock(); response.__enter__.return_value.read.return_value = json.dumps({'message': assistant}).encode()
        with patch.object(t, 'urlopen', return_value=response) as opened:
            actual = t.infer(3, [{'role': 'user', 'content': 'read board'}], c.TOOLS)
        self.assertEqual(actual, assistant)
        self.assertEqual(json.loads(opened.call_args.args[0].data)['tools'], c.TOOLS)
        self.assertIn('ollama_node_3', opened.call_args.args[0].full_url)


if __name__ == '__main__':
    unittest.main()
