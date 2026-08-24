#!/usr/bin/env python3
"""Focused tests for the private-to-public publication boundary."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "runbooks" / "check_publication_candidate.py"
SPEC = importlib.util.spec_from_file_location("check_publication_candidate", SCRIPT)
assert SPEC and SPEC.loader
PUBLICATION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PUBLICATION
SPEC.loader.exec_module(PUBLICATION)


class PublicationCandidateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name) / "blog"
        self.root.mkdir()
        self.git("init", "-q", "-b", "v4")
        self.git("config", "user.name", "Publication Test")
        self.git("config", "user.email", "publication@example.test")
        self.write(".gitignore", "dist/\n")
        self.write("README.md", "# Public blog\n")
        self.git("add", ".gitignore", "README.md")
        self.git("commit", "-q", "-m", "initial public state")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.candidate = Path("src/data/blog/public-note.md")
        self.canary = "PRIVATE-CANARY-7cbd2144e19d"

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )

    def write(self, relative: str | Path, content: str | bytes) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")

    def commit_candidate(self, content: str, message: str = "publish note") -> None:
        self.write(self.candidate, content)
        self.git("add", self.candidate.as_posix())
        self.git("commit", "-q", "-m", message)

    def validate(self, *, artifact_roots: tuple[str, ...] = ()) -> None:
        PUBLICATION.validate_publication(
            blog_root=self.root,
            candidate=self.candidate,
            base_ref=self.base,
            artifact_roots=artifact_roots,
            canary=self.canary,
        )

    def test_accepts_standard_markdown_and_public_artifact(self) -> None:
        self.commit_candidate(
            "# 공개 노트\n\n[설계 문서](../architecture.md)와 "
            '<a href="/posts/public">공개 글</a>입니다.\n'
        )
        self.write("dist/index.html", "<h1>공개 노트</h1>")

        self.validate(artifact_roots=("dist",))

    def test_detects_private_markdown_secret_path_asset_and_canary(self) -> None:
        synthetic_token = "".join(("gh", "p_", "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"))
        cases = {
            "wikilink": ("[[Private Note]]", "private_wikilink"),
            "embed": ("![[secret.png]]", "private_wikilink"),
            "block": ("문단 내용 ^private-block", "block_reference"),
            "private_path": ("/Users/alice/notes-private/source.md", "private_path"),
            "secret": (
                f"token = {synthetic_token}",
                "secret",
            ),
            "local_asset": ("![diagram](./private-diagram.png)", "local_asset"),
            "canary": (self.canary, "canary"),
        }

        for label, (text, expected) in cases.items():
            with self.subTest(label=label):
                self.assertIn(
                    expected,
                    PUBLICATION.detect_text_violations(text, canary=self.canary),
                )

    def test_rejects_secret_removed_from_final_diff_but_present_in_history(
        self,
    ) -> None:
        secret = "".join(("gh", "p_", "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"))
        self.commit_candidate(f"token = {secret}\n", "accidentally add secret")
        self.commit_candidate(
            "# 공개 노트\n\n민감값을 제거했습니다.\n", "remove secret"
        )

        with self.assertRaises(PUBLICATION.PublicationRejected) as caught:
            self.validate()

        self.assertIn("secret", caught.exception.reasons)
        self.assertNotIn(secret, str(caught.exception))

    def test_rejects_binary_blob_removed_before_head(self) -> None:
        asset = Path("src/assets/private.bin")
        self.write(asset, b"\x00\x01private-binary")
        self.git("add", asset.as_posix())
        self.git("commit", "-q", "-m", "add binary")
        self.git("rm", "-q", asset.as_posix())
        self.git("commit", "-q", "-m", "remove binary")
        self.commit_candidate("# 공개 노트\n", "add safe note")

        with self.assertRaises(PUBLICATION.PublicationRejected) as caught:
            self.validate()

        self.assertIn("binary_asset", caught.exception.reasons)

    def test_rejects_canary_in_generated_artifact(self) -> None:
        self.commit_candidate("# 공개 노트\n")
        self.write("dist/pagefind/index.js", f"window.data='{self.canary}'")

        with self.assertRaises(PUBLICATION.PublicationRejected) as caught:
            self.validate(artifact_roots=("dist",))

        self.assertIn("canary", caught.exception.reasons)

    def test_private_clone_must_be_outside_public_workspace(self) -> None:
        inside = self.root / "projects" / "notes-private"
        inside.mkdir(parents=True)
        outside = Path(self.tempdir.name) / "notes-private"
        outside.mkdir()

        PUBLICATION.verify_private_boundary(self.root, outside)
        with self.assertRaises(PUBLICATION.PublicationRejected) as caught:
            PUBLICATION.verify_private_boundary(self.root, inside)

        self.assertEqual(caught.exception.reasons, ("private_root_inside_public",))

    def test_rejects_tracked_symlink_into_private_vault(self) -> None:
        private = Path(self.tempdir.name) / "notes-private"
        private.mkdir()
        link = self.root / "private-notes"
        link.symlink_to(private, target_is_directory=True)
        self.git("add", "private-notes")
        self.git("commit", "-q", "-m", "track unsafe private link")

        with self.assertRaises(PUBLICATION.PublicationRejected) as caught:
            PUBLICATION.verify_private_boundary(self.root, private)

        self.assertEqual(caught.exception.reasons, ("private_symlink_tracked",))

    def test_rejects_candidate_and_artifact_roots_that_escape_through_symlinks(
        self,
    ) -> None:
        outside = Path(self.tempdir.name) / "outside"
        outside_candidate = outside / "data" / "blog" / "public-note.md"
        outside_candidate.parent.mkdir(parents=True)
        outside_candidate.write_text("# 외부 파일\n", encoding="utf-8")
        (self.root / "src").symlink_to(outside, target_is_directory=True)

        with self.assertRaises(PUBLICATION.PublicationRejected) as caught:
            self.validate()
        self.assertEqual(caught.exception.reasons, ("candidate_missing_or_unsafe",))

        (self.root / "src").unlink()
        self.commit_candidate("# 공개 노트\n")
        (self.root / "dist").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(PUBLICATION.PublicationRejected) as caught:
            self.validate(artifact_roots=("dist",))
        self.assertEqual(caught.exception.reasons, ("artifact_root_missing",))

    def test_cli_failure_does_not_echo_private_content_or_path(self) -> None:
        private_path = "/Users/alice/notes-private/secret.md"
        secret = "".join(("gh", "p_", "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"))
        self.commit_candidate(
            f"{private_path}\n{secret}\n{self.canary}\n",
            "unsafe candidate",
        )
        env = os.environ.copy()
        env["PUBLICATION_CANARY"] = self.canary

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "check",
                "--blog-root",
                str(self.root),
                "--candidate",
                self.candidate.as_posix(),
                "--base-ref",
                self.base,
            ],
            check=False,
            text=True,
            encoding="utf-8",
            capture_output=True,
            env=env,
        )

        combined = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1)
        self.assertIn("publication rejected", combined)
        self.assertNotIn(private_path, combined)
        self.assertNotIn(secret, combined)
        self.assertNotIn(self.canary, combined)


if __name__ == "__main__":
    unittest.main()
