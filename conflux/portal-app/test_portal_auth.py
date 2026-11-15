"""Local OAuth safety checks with zero external sign-in or account use."""
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlsplit

import portal_auth


class AuthLocalTest(unittest.TestCase):
    def test_github_state_and_token_storage_are_not_public(self):
        with tempfile.TemporaryDirectory() as folder:
            state_dir=Path(folder)/"conflux-private"
            client=portal_auth.PortalConnections(state_dir)
            env={"CONFLUX_GITHUB_CLIENT_ID":"fake-id",
                 "CONFLUX_GITHUB_CLIENT_SECRET":"fake-secret"}
            callback="http://127.0.0.1:8765/auth/github/callback"
            with mock.patch.dict(os.environ,env):
                attempt=client.start("github",callback)
                url=urlsplit(attempt["url"])
                self.assertEqual(url.scheme,"https")
                self.assertEqual(url.hostname,"github.com")
                state=parse_qs(url.query)["state"][0]
                with self.assertRaises(portal_auth.AuthError):
                    client.finish("github",{"code":["fake-code"],"state":["wrong"]})
                client.start("github",callback)
                state=client.pending["github"]["state"]
                with mock.patch.object(portal_auth,"_form",
                      return_value={"access_token":"private-user-token","expires_in":3600}), \
                     mock.patch.object(portal_auth,"_response",
                      return_value={"login":"test-wayfarer"}):
                    result=client.finish("github",{
                        "code":["fake-code"],"state":[state]})
                self.assertTrue(result["connected"])
                status=client.status()
                self.assertTrue(status["github"]["connected"])
                self.assertNotIn("private-user-token",json.dumps(status))
                auth_file=state_dir/"github.json"
                self.assertEqual(stat.S_IMODE(auth_file.stat().st_mode),0o600)
                self.assertEqual(stat.S_IMODE(state_dir.stat().st_mode),0o700)
                self.assertEqual(client.github_token(),"private-user-token")
                client.sign_out("github")
                self.assertFalse(client.status()["github"]["connected"])

    def test_auth_rejects_nonloopback_callback(self):
        with tempfile.TemporaryDirectory() as folder:
            client=portal_auth.PortalConnections(folder)
            with self.assertRaises(portal_auth.AuthError):
                client.start("chatgpt","https://fake-callback.example/auth/chatgpt/callback")
            with self.assertRaises(portal_auth.AuthError):
                client.start("github","http://0.0.0.0:8765/auth/github/callback")
            self.assertFalse(client.status()["chatgpt"]["connected"])

    def test_missing_provider_registration_has_no_fake_redirect(self):
        with tempfile.TemporaryDirectory() as folder:
            client=portal_auth.PortalConnections(folder)
            with mock.patch.dict(os.environ,{
                "CONFLUX_GITHUB_CLIENT_ID":"",
                "CONFLUX_GITHUB_CLIENT_SECRET":""
            }):
                with self.assertRaises(portal_auth.AuthError):
                    client.start("github","http://127.0.0.1:8765/auth/github/callback")


if __name__=="__main__":
    unittest.main()
