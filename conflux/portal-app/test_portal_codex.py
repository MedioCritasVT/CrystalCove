"""Codex app-server protocol tests: no network, no OpenAI account, no Git clone."""
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

from portal_codex import CodexBridge, CodexError


FAKE_CODEX = """#!/usr/bin/env python3
import json,sys
def out(obj):
    sys.stdout.write(json.dumps(obj)+"\\n")
    sys.stdout.flush()
for line in sys.stdin:
    req=json.loads(line)
    method=req.get("method")
    rid=req.get("id")
    if method=="initialize":
        out({"id":rid,"result":{"userAgent":"test-codex/1.0"}})
    elif method=="initialized":
        pass
    elif method=="account/read":
        out({"id":rid,"result":{"account":{"type":"chatgpt","planType":"plus"},
                                  "requiresOpenaiAuth":True}})
    elif method=="account/login/start":
        out({"id":rid,"result":{"type":"chatgpt","loginId":"fake-login",
                                  "authUrl":"https://chatgpt.com/auth/fake-test"}})
    elif method=="thread/start":
        out({"id":rid,"result":{"thread":{"id":"thr_test_1234"}}})
        out({"method":"thread/started","params":{"thread":{"id":"thr_test_1234"}}})
    elif method=="thread/resume":
        out({"id":rid,"result":{"thread":{"id":req["params"]["threadId"]}}})
    elif method=="turn/start":
        out({"id":rid,"result":{"turn":{"id":"turn_test_123","status":"inProgress"}}})
        out({"method":"turn/started","params":{"turn":{"id":"turn_test_123"}}})
        out({"method":"item/agentMessage/delta","params":{"itemId":"m1","delta":"Here are the checks."}})
        out({"method":"item/completed","params":{"item":{"id":"m1","type":"agentMessage","text":"Here are the checks."}}})
        out({"method":"turn/completed","params":{"turn":{"id":"turn_test_123","status":"completed"}}})
    elif rid is not None:
        out({"id":rid,"result":{}})
"""


class CodexProtocolTest(unittest.TestCase):
    def test_missing_cli_is_clear_without_install_or_spawn(self):
        with tempfile.TemporaryDirectory() as tmp:
            bridge=CodexBridge(tmp, executable="/not/a/real/codex")
            with mock.patch.object(bridge,"binary",return_value=None):
                self.assertFalse(bridge.snapshot()["installed"])
                with self.assertRaisesRegex(CodexError,"isn't installed"):
                    bridge.start()
            self.assertFalse(bridge.snapshot()["running"])
            self.assertFalse((Path(tmp)/".git").exists())

    def test_real_stdio_handshake_and_stream_with_fake_codex(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake=Path(tmp)/"codex-mock"
            fake.write_text(FAKE_CODEX,encoding="utf-8")
            fake.chmod(0o700)
            bridge=CodexBridge(tmp,executable=str(fake))
            try:
                state=bridge.start()
                self.assertTrue(state["running"])
                self.assertTrue(state["authenticated"])
                self.assertFalse(state["editing"])
                self.assertEqual(state["account_type"],"chatgpt")
                self.assertTrue(bridge.login()["auth_url"].startswith("https://chatgpt.com/"))
                reply=bridge.send("Please inspect this project.")
                self.assertTrue(reply["accepted"])
                self.assertEqual(reply["thread"],"thr_test_1234")
                for _ in range(40):
                    results=bridge.poll()
                    if any(e["kind"]=="turn_finished" for e in results["events"]):
                        break
                    time.sleep(.025)
                kinds=[e["kind"] for e in bridge.poll()["events"]]
                self.assertIn("delta",kinds)
                self.assertIn("answer",kinds)
                self.assertIn("turn_finished",kinds)
                self.assertFalse(bridge.snapshot()["busy"])
                self.assertEqual(bridge.snapshot()["thread"],"thr_test_1234")
                self.assertFalse((Path(tmp)/".git").exists())
                self.assertTrue(bridge.stop()["stopped"])
            finally:
                if bridge.running():bridge.stop()

    def test_explicit_edit_permission_and_approval_denial(self):
        with tempfile.TemporaryDirectory() as tmp:
            bridge=CodexBridge(tmp)
            bridge.thread_id="thr_test_1234"
            bridge.busy=True
            bridge._handle({"id":777,"method":"item/fileChange/requestApproval",
                            "params":{"threadId":"thr_test_1234",
                                      "turnId":"turn_test","command":"edit file"}})
            with self.assertRaisesRegex(CodexError,"Enable workspace editing"):
                bridge.decide("777","accept")
            self.assertIn("777",bridge.approvals)
            sent=[]
            with mock.patch.object(bridge,"_send",side_effect=lambda msg:sent.append(msg)):
                self.assertTrue(bridge.decide("777","decline")["answered"])
            self.assertEqual(sent[0]["result"]["decision"],"decline")
            bridge.busy=False
            self.assertTrue(bridge.edits(True)["editing"])
            bridge.busy=True
            with self.assertRaises(CodexError):
                bridge.edits(False)
            self.assertEqual(len(bridge.approvals),0)

    def test_read_only_by_default_and_user_owned_write_toggle(self):
        with tempfile.TemporaryDirectory() as tmp:
            bridge=CodexBridge(tmp)
            bridge.thread_id="thr_test_1234"
            with mock.patch.object(bridge,"running",return_value=True), \
                 mock.patch.object(bridge,"_request",return_value={"turn":{"id":"turn_abc"}}) as call:
                bridge.send("Read only?")
                readonly=call.call_args.args[1]["sandboxPolicy"]
                self.assertEqual(readonly["type"],"readOnly")
                self.assertEqual(readonly["access"]["readableRoots"],[str(Path(tmp).resolve())])
                bridge.busy=False
                bridge.edits(True)
                bridge.send("Apply approved changes.")
                policy=call.call_args.args[1]["sandboxPolicy"]
                self.assertEqual(policy["type"],"workspaceWrite")
                self.assertFalse(policy["networkAccess"])
                self.assertEqual(policy["readOnlyAccess"]["readableRoots"],[str(Path(tmp).resolve())])
                self.assertEqual(policy["writableRoots"],[str(Path(tmp).resolve())])


if __name__=="__main__":
    unittest.main()
