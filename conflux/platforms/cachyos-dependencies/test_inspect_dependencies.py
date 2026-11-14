"""Deterministic offline tests for the non-mutating CachyOS dependency checker."""
import unittest

import inspect_dependencies as tool

CACHY = {"ID": "cachyos", "PRETTY_NAME": "CachyOS", "ID_LIKE": "arch"}
OTHER = {"ID": "fedora", "PRETTY_NAME": "Fedora Linux"}

class PreflightTests(unittest.TestCase):
    def test_static_portal_plan_only_missing_required(self):
        report = tool.inspect("static-portal", distro=CACHY,
            installed={"python", "git", "podman"},
            binaries={"podman", "git", "pacman", "systemctl"},
            python_version=(3, 13))
        self.assertEqual(report["missing_required_packages"], ["podman-compose"])
        self.assertEqual(report["suggested_install_command_NOT_EXECUTED"],
                         "sudo pacman -Syu --needed podman-compose")
        self.assertFalse(any("tailscale" in x for x in report["missing_required_packages"]))

    def test_available_deps_have_no_install_command(self):
        report = tool.inspect("static-portal", distro=CACHY,
            installed={"podman", "podman-compose", "git"},
            binaries={"podman", "podman-compose", "git", "pacman", "systemctl"})
        self.assertEqual(report["missing_required_packages"], [])
        self.assertIsNone(report["suggested_install_command_NOT_EXECUTED"])

    def test_other_distros_never_get_pacman_command(self):
        report = tool.inspect("media-foundation", distro=OTHER, installed=set(),
            binaries={"pacman"})
        self.assertIsNone(report["suggested_install_command_NOT_EXECUTED"])

    def test_compose_alternative_requires_review(self):
        report = tool.inspect("static-portal", distro=CACHY, installed={"podman"},
            binaries={"podman", "docker-compose", "pacman", "systemctl"})
        row = next(r for r in report["checks"] if r["package"] == "podman-compose")
        self.assertEqual(row["status"], "review")
        self.assertIsNone(report["suggested_install_command_NOT_EXECUTED"])

    def test_absent_inventory_does_not_guess_packages(self):
        report = tool.inspect("media-foundation", distro=CACHY, installed=None,
            pacman_error="simulated query error", binaries={"pacman"})
        self.assertEqual(report["missing_required_packages"], [])
        self.assertIsNone(report["suggested_install_command_NOT_EXECUTED"])
        self.assertTrue(all(r["status"] == "unknown" for r in report["checks"]))

    def test_pacman_installed_but_no_binary_is_review(self):
        self.assertEqual(
            tool.requirement_status("podman", "podman", {"podman"}, set(), (3,13))[0],
            "review")

    def test_version_requirement(self):
        self.assertEqual(tool.requirement_status("python","python3",{"python"},
            {"python3"}, (3,9))[0], "review")

if __name__ == "__main__":
    unittest.main()
