"""Theme Studio validation and isolated Git publication regression tests."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from theme_studio import DEFAULT, StudioError, ThemeStudio, validate_palette, contrast


def run_git(cwd, *args):
    result = subprocess.run(["git", "-C", str(cwd), *args],
                            text=True, capture_output=True, timeout=15)
    if result.returncode:
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout.strip()


class ThemeValidationTest(unittest.TestCase):
    def test_baseline_and_readable_contrast(self):
        colors = validate_palette(DEFAULT)
        self.assertEqual(set(colors), set(DEFAULT))
        self.assertGreaterEqual(contrast(colors["ink"], colors["surface"]), 4.5)

    def test_textures_preserve_schema_and_refuse_unknown_values(self):
        with tempfile.TemporaryDirectory() as folder:
            studio = ThemeStudio(folder)
            result = studio.propose({
                "name": "Starfield", "agent": "specula", "provider": "manual",
                "palette": DEFAULT, "texture": "constellation",
            })
            self.assertEqual(result["texture"], "constellation")
            with self.assertRaises(StudioError):
                studio.propose({
                    "name": "Bad", "agent": "specula", "provider": "manual",
                    "palette": DEFAULT, "texture": "url(https://invalid)"
                })

    def test_invalid_values_fail_closed(self):
        for change in ({"ink": "red"}, {"ink": "url(javascript:alert(1))"},
                       {"ink": "#111522"}, {"muted": "#111522"},
                       {"extra": "#ffffff"}):
            with self.subTest(change=change):
                with self.assertRaises(StudioError):
                    validate_palette({**DEFAULT, **change})

    def test_manual_proposal_is_read_only_and_needs_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            manager = ThemeStudio(folder)
            result = manager.propose({
                "name": "Quiet grove", "agent": "limen", "provider": "manual",
                "instruction": "", "palette": DEFAULT})
            self.assertEqual(result["slug"], "quiet-grove")
            self.assertFalse(list(Path(folder).iterdir()))
            with self.assertRaises(StudioError):
                manager.publish({"ticket": result["ticket"]})
            self.assertFalse(list(Path(folder).iterdir()))

    def test_missing_or_malicious_theme_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            manager = ThemeStudio(folder)
            for slug in ("../escape", "no_theme", "UPPER", "", "a"*50):
                with self.subTest(slug=slug), self.assertRaises(StudioError):
                    manager.inspect_theme(slug)
            target = Path(folder) / "conflux" / "portal-app" / "studio-themes"
            target.mkdir(parents=True)
            (target / "safe.json").write_text(json.dumps({
                "schema": 1, "name": "safe", "agent": "ratio", "palette": DEFAULT
            }), encoding="utf-8")
            self.assertTrue(manager.inspect_theme("safe")["loaded"])


@unittest.skipUnless(__import__("shutil").which("git"), "Git unavailable")
class ThemeGitWorkflowTest(unittest.TestCase):
    def test_review_branch_push_then_preview_without_touching_main(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "repo"
            remote = Path(folder) / "bare.git"
            root.mkdir()
            run_git(folder, "init", "--bare", str(remote))
            run_git(folder, "init", "-b", "main", str(root))
            run_git(root, "config", "user.name", "Review Tester")
            run_git(root, "config", "user.email", "review@example.invalid")
            (root / "README.md").write_text("unchanged\n", encoding="utf-8")
            run_git(root, "add", "README.md")
            run_git(root, "commit", "-m", "baseline")
            run_git(root, "remote", "add", "origin", str(remote))
            run_git(root, "push", "-u", "origin", "main")
            original = run_git(root, "rev-parse", "HEAD")
            (root / "private-untracked.txt").write_text("keep me", encoding="utf-8")

            manager = ThemeStudio(root)
            proposal = manager.propose({
                "name": "Personal Sky", "agent": "specula", "provider": "manual",
                "instruction": "", "palette": DEFAULT,
            })
            with mock.patch.object(manager, "repository", return_value="wayfarer/fork"):
                published = manager.publish({
                    "ticket": proposal["ticket"],
                    "confirmation": "PUBLISH REVIEWED THEME",
                })
                self.assertEqual(run_git(root, "rev-parse", "HEAD"), original)
                self.assertEqual(run_git(root, "branch", "--show-current"), "main")
                self.assertEqual((root / "private-untracked.txt").read_text(), "keep me")
                self.assertTrue(published["branch"].startswith("conflux/studio-"))
                self.assertEqual(run_git(root, "ls-remote", "--heads", "origin",
                                             published["branch"]).split()[0][:12],
                                 published["commit"])
                self.assertFalse((root / published["path"]).exists())
                with self.assertRaises(StudioError):
                    manager.preview({"branch": published["branch"]})
                self.assertTrue(manager.preview({
                    "branch": published["branch"], "confirmation": "PREVIEW REVIEW BRANCH",
                })["relaunch"])
                self.assertTrue(manager.inspect_theme("personal-sky")["loaded"])
                self.assertTrue(manager.return_to_main({
                    "confirmation": "RETURN TO MAIN",
                })["relaunch"])
                self.assertEqual(run_git(root, "rev-parse", "HEAD"), original)
                self.assertEqual((root / "private-untracked.txt").read_text(), "keep me")


if __name__ == "__main__":
    unittest.main()
