"""Soundtrack discovery and safe ZIP install tests, using fake tiny audio files only."""
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError

import music_library


class SoundtrackLibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "soundtrack"
        self.a = b"ID3 Conflux first recording"
        self.b = b"ID3 Conflux alternate recording"
        self.assets = {"Conflux-A.mp3": self.a, "Conflux-B.mp3": self.b}
        self.catalog = {"tracks":[{
            "id":"sacrament-of-oath", "title":"Sacrament of Oath",
            "variants":[{"id":"take-1", "duration_seconds":10,
                         "release_asset_filename":"Conflux-A.mp3"},
                        {"id":"take-2", "duration_seconds":11,
                         "release_asset_filename":"Conflux-B.mp3"}]
        }]}
        self.hashes = {name: hashlib.sha256(content).hexdigest()
                       for name, content in self.assets.items()}
        patches = [mock.patch.object(music_library, "metadata",
                                     return_value=self.catalog),
                   mock.patch.object(music_library, "checksums",
                                     return_value=self.hashes),
                   mock.patch.object(music_library, "music_directory",
                                     return_value=self.directory)]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)
        music_library._cached_assets = None

    def make_zip(self, content=None):
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, payload in (content or self.assets).items():
                archive.writestr(name, payload)
            archive.writestr("RELEASE_NOTES.md", "Test release")
        return output.getvalue()

    def test_verified_import_stays_in_user_data(self):
        installed = music_library.install_release_zip(self.make_zip())
        self.assertEqual(installed["installed"], 2)
        self.assertEqual((self.directory / "Conflux-A.mp3").read_bytes(), self.a)
        self.assertEqual((self.directory / "Conflux-B.mp3").read_bytes(), self.b)
        self.assertEqual(music_library.local_asset("Conflux-A.mp3"),
                         self.directory / "Conflux-A.mp3")
        self.assertIsNone(music_library.local_asset("../sensitive.txt"))

    def test_tampered_file_is_rejected_before_writing(self):
        bad = dict(self.assets)
        bad["Conflux-B.mp3"] = b"modified bytes"
        with self.assertRaisesRegex(music_library.MusicError, "Checksum mismatch"):
            music_library.install_release_zip(self.make_zip(bad))
        self.assertFalse((self.directory / "Conflux-A.mp3").exists())

    def test_incomplete_zip_rejected(self):
        with self.assertRaisesRegex(music_library.MusicError, "incomplete"):
            music_library.install_release_zip(
                self.make_zip({"Conflux-A.mp3": self.a}))

    def test_duplicate_audio_entry_rejected(self):
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            archive.writestr("Conflux-A.mp3", self.a)
            archive.writestr("Conflux-A.mp3", self.a)
            archive.writestr("Conflux-B.mp3", self.b)
        with self.assertRaisesRegex(music_library.MusicError, "Repeated"):
            music_library.install_release_zip(output.getvalue())

    def test_symlink_destination_rejected(self):
        self.directory.mkdir(parents=True)
        target = self.directory.parent / "other-file"
        target.write_bytes(b"original")
        (self.directory / "Conflux-A.mp3").symlink_to(target)
        with self.assertRaisesRegex(music_library.MusicError, "symlink"):
            music_library.install_release_zip(self.make_zip())
        self.assertEqual(target.read_bytes(), b"original")

    def test_auto_catalog_prefers_local_and_uses_release_only_if_published(self):
        self.directory.mkdir(parents=True)
        (self.directory / "Conflux-A.mp3").write_bytes(self.a)
        with mock.patch.object(music_library, "public_release_assets",
            return_value=({"Conflux-B.mp3": music_library.RELEASE_PREFIX +
                           "Conflux-B.mp3"}, None)):
            data = music_library.library()
        items = data["tracks"][0]["variants"]
        self.assertEqual(items[0]["source"], "local")
        self.assertEqual(items[0]["url"], "/music/audio/Conflux-A.mp3")
        self.assertEqual(items[1]["source"], "published")
        self.assertEqual(data["available"], 2)
        self.assertTrue(data["music_off_by_default"])

    def test_missing_release_does_not_expose_invented_mp3_urls(self):
        with mock.patch.object(music_library, "public_release_assets",
                               return_value=({}, "release-not-yet-reachable")):
            data = music_library.library()
        self.assertEqual(data["available"], 0)
        self.assertTrue(all(i["url"] is None
                            for t in data["tracks"] for i in t["variants"]))

    def test_release_asset_urls_are_validated(self):
        fake_response = {
            "tag_name":music_library.RELEASE_TAG, "draft":False,
            "assets":[{"name":"Conflux-A.mp3","size":200,
                       "browser_download_url":music_library.RELEASE_PREFIX+"Conflux-A.mp3"},
                      {"name":"Conflux-B.mp3","size":300,
                       "browser_download_url":"https://untrusted.invalid/music.mp3"}]
        }
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *_): return None
            def read(self, *args): return json.dumps(fake_response).encode("utf-8")
        with mock.patch("music_library.urllib.request.urlopen",return_value=Reply()):
            music_library._cached_assets = None
            result, error = music_library.public_release_assets()
        self.assertEqual(set(result), {"Conflux-A.mp3"})
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
