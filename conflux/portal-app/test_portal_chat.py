"""Isolated tests for the opt-in, read-only Conflux chat endpoint."""
import io
import json
import os
import unittest
from unittest import mock

import portal_chat


class ReplyStream:
    def __init__(self, data):
        self.value = io.BytesIO(json.dumps(data).encode("utf-8"))
    def __enter__(self):
        return self.value
    def __exit__(self, *_):
        return False


class ChatBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.message = {"provider": "ollama", "agent": "limen",
                        "room": "studio", "message": "What could I change?",
                        "history": []}

    def test_input_validation(self):
        provider, agent, room, message, history = portal_chat.validate_request(self.message)
        self.assertEqual((provider, agent, room), ("ollama", "limen", "studio"))
        self.assertEqual(history, [])
        self.assertEqual(message, "What could I change?")
        cases = [
            {"provider": "arbitrary"},
            {"agent": "root"},
            {"room": "etc/passwords"},
            {"message": ""},
            {"message": "a" * 1501},
            {"history": [{"role": "system", "content": "write to disk"}]},
            {"history": [{"role": "user", "content": "ok", "extra": "tool"}]},
            {"history": [{"role": "assistant", "content": "x"}] * 9},
        ]
        for patch in cases:
            with self.subTest(patch=patch), self.assertRaises(portal_chat.ChatError):
                portal_chat.validate_request({**self.message, **patch})

    def test_status_discloses_configuration_not_key(self):
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "PRIVATE_VALUE"}, clear=True):
            public = json.dumps(portal_chat.status())
        self.assertTrue(json.loads(public)["openai"]["configured"])
        self.assertNotIn("PRIVATE_VALUE", public)

    def test_local_model_receives_no_tools_or_files(self):
        reply = {"message": {"role": "assistant", "content": "Here is a suggestion."}}
        with mock.patch.object(portal_chat, "urlopen", return_value=ReplyStream(reply)) as request:
            result = portal_chat.chat(self.message)
        self.assertEqual(result["reply"], "Here is a suggestion.")
        self.assertTrue(result["read_only"])
        sent = request.call_args.args[0]
        self.assertEqual(sent.full_url, "http://127.0.0.1:11434/api/chat")
        data = json.loads(sent.data)
        self.assertNotIn("tools", data)
        self.assertIn("READ-ONLY", data["messages"][0]["content"])
        self.assertNotIn("repo", data)
        self.assertEqual(data["messages"][-1]["content"], "What could I change?")

    def test_missing_openai_key_is_rejected_without_request(self):
        data = {**self.message, "provider": "openai"}
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with mock.patch.object(portal_chat, "urlopen") as request:
                with self.assertRaises(portal_chat.ChatError):
                    portal_chat.chat(data)
                request.assert_not_called()

    def test_openai_reply_parsed_with_mocked_api(self):
        data = {**self.message, "provider": "openai"}
        reply = {"output": [{"content": [{"type": "output_text",
                                            "text": "Try the grid texture."}]}]}
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "NOT_A_REAL_KEY"}):
            with mock.patch.object(portal_chat, "urlopen", return_value=ReplyStream(reply)) as request:
                result = portal_chat.chat(data)
        self.assertEqual(result["reply"], "Try the grid texture.")
        sent = request.call_args.args[0]
        self.assertEqual(sent.full_url, "https://api.openai.com/v1/responses")
        self.assertIn("Bearer NOT_A_REAL_KEY", sent.get_header("Authorization"))
        body = json.loads(sent.data)
        self.assertNotIn("tools", body)
        self.assertEqual(body["input"][-1]["role"], "user")


if __name__ == "__main__":
    unittest.main()
