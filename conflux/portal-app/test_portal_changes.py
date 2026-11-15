"""Privacy, review, and Git safety tests for Portal assistant editing."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from portal_changes import ChatEdits, EditError, json_reply, CSS_DANGEROUS
from portal_prs import PullDesk, PullError


def git(cwd,*args):
    p=subprocess.run(["git","-C",str(cwd),*args],text=True,
                     capture_output=True,timeout=20)
    if p.returncode:
        raise AssertionError(p.stderr)
    return p.stdout.strip()


class FakeConnections:
    def github_token(self):
        return "fake-token"


class ChangeValidationTest(unittest.TestCase):
    def test_exact_json_and_css_risk_rejections(self):
        self.assertEqual(json_reply('{"find":"hello","replace":"goodbye"}'),
                         ("hello","goodbye"))
        for payload in ("abc", '{"find":"","replace":"hi"}',
                        '{"find":"x","replace":"y","command":"rm"}'):
            with self.subTest(payload=payload),self.assertRaises(EditError):
                json_reply(payload)
        for text in ('body{background:url(https://tracker.test)}',
                     '@import "remote.css";', 'behavior: url(foo)'):
            self.assertTrue(CSS_DANGEROUS.search(text))

    def test_explicit_file_sharing_required_without_ai_call(self):
        with tempfile.TemporaryDirectory() as folder:
            editor=ChatEdits(folder,FakeConnections())
            with mock.patch("portal_changes.model_suggestion") as generated:
                with self.assertRaises(EditError):
                    editor.propose({"file":"conflux/portal-app/portal_chat.css",
                                    "provider":"ollama","agent":"limen",
                                    "instruction":"Change padding please",
                                    "approve_share":False})
                generated.assert_not_called()


@unittest.skipUnless(__import__("shutil").which("git"),"Git unavailable")
class GitReviewTest(unittest.TestCase):
    def test_chat_change_cannot_touch_main_before_review(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            working=base/"repo"
            remote=base/"bare.git"
            working.mkdir()
            git(folder,"init","--bare",str(remote))
            git(folder,"init","-b","main",str(working))
            git(working,"config","user.name","Test Reviewer")
            git(working,"config","user.email","review@example.invalid")
            css=working/"conflux"/"portal-app"/"portal_chat.css"
            css.parent.mkdir(parents=True)
            css.write_text("button { padding:12px; }\n",encoding="utf-8")
            git(working,"add",".")
            git(working,"commit","-m","baseline")
            git(working,"remote","add","origin",str(remote))
            git(working,"push","-u","origin","main")
            baseline=git(working,"rev-parse","HEAD")
            editor=ChatEdits(working,FakeConnections())
            request={"file":"conflux/portal-app/portal_chat.css",
                     "provider":"ollama","agent":"limen",
                     "instruction":"Please reduce the button padding.",
                     "approve_share":True}
            replacement=json.dumps({"find":"padding:12px","replace":"padding:8px"})
            with mock.patch.object(editor.repo,"repository",return_value="tester/fork"), \
                 mock.patch("portal_changes.model_suggestion",return_value=replacement):
                proposal=editor.propose(request)
                self.assertTrue(proposal["diff"])
                self.assertEqual(git(working,"rev-parse","HEAD"),baseline)
                self.assertIn("padding:12px",css.read_text())
                with self.assertRaises(EditError):
                    editor.publish({"ticket":proposal["ticket"],
                                    "confirmation":"MERGE NOW"})
                result=editor.publish({
                    "ticket":proposal["ticket"],
                    "confirmation":"PUSH REVIEW TO tester/fork",
                })
                self.assertTrue(result["published"])
                self.assertFalse(result["pr_created"])
                self.assertEqual(git(working,"rev-parse","HEAD"),baseline)
                self.assertIn("padding:12px",css.read_text())
                remote_sha=git(working,"ls-remote","--heads","origin",result["branch"])
                self.assertTrue(remote_sha.startswith(result["commit"]))
                with self.assertRaises(EditError):
                    editor.publish({"ticket":proposal["ticket"],
                                    "confirmation":"PUSH REVIEW TO tester/fork"})


class PullReviewTest(unittest.TestCase):
    def test_open_pr_inspection_and_confirmed_merge(self):
        head="a"*40
        pr={"number":12,"title":"Small styling fix","draft":False,
            "state":"open","base":{"ref":"main"},
            "head":{"ref":"fix","sha":head},"user":{"login":"editor"},
            "html_url":"https://github.com/tester/fork/pull/12",
            "mergeable":True,"changed_files":1,"body":"CSS adjustment"}
        files=[{"filename":"style.css","status":"modified",
                "additions":1,"deletions":1,
                "patch":"@@ -1 +1 @@\n-red\n+blue"}]
        calls=[]
        def request(method,path,token=None,payload=None):
            calls.append((method,path,token,payload))
            if path.endswith("/pulls/12/files?per_page=100"):
                return files
            if path.endswith("/pulls/12/merge"):
                return {"merged":True,"sha":"b"*40}
            if path.endswith("/pulls/12"):
                return pr
            raise AssertionError(path)
        desk=PullDesk(lambda:"tester/fork",FakeConnections(),request=request)
        details=desk.detail(12)
        self.assertTrue(details["merge_available"])
        self.assertIn("+blue",details["files"][0]["patch"])
        with self.assertRaises(PullError):
            desk.merge({"number":12,"sha":head,"ticket":details["ticket"],
                        "confirmation":"please merge"})
        result=desk.merge({"number":12,"sha":head,"ticket":details["ticket"],
                           "confirmation":"MERGE #12 INTO tester/fork"})
        self.assertTrue(result["merged"])
        self.assertEqual(len([x for x in calls if x[0]=="PUT"]),1)

    def test_hidden_diff_blocks_inline_merge_button(self):
        head="a"*40
        pr={"number":4,"title":"Opaque file","draft":False,"state":"open",
            "base":{"ref":"main"},"head":{"ref":"opaque","sha":head},
            "user":{"login":"editor"},"mergeable":True,"changed_files":1}
        def request(method,path,token=None,payload=None):
            return [{"filename":"binary.png","additions":0,"deletions":0}] if path.endswith("/files?per_page=100") else pr
        desk=PullDesk(lambda:"tester/fork",FakeConnections(),request=request)
        details=desk.detail(4)
        self.assertFalse(details["merge_available"])
        self.assertTrue(details["partial_file_list"])


if __name__=="__main__":
    unittest.main()
