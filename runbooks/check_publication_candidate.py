#!/usr/bin/env python3
"""Fail closed when a private note is promoted into a public Git history."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path, PurePosixPath


WIKILINK = re.compile(r"!?\[\[[^\]\n]+\]\]")
BLOCK_REFERENCE = re.compile(r"(?<![A-Za-z0-9_])(?:#)?\^[A-Za-z0-9][A-Za-z0-9-]{2,}")
PRIVATE_PATHS = (
    re.compile(r"(?i)(?:^|[\s('])/(?:Users|home)/[^\s)'\"]+"),
    re.compile(r"(?i)\b[A-Z]:[\\/]Users[\\/][^\s)'\"]+"),
    re.compile(r"(?i)\bfile://[^\s)'\"]+"),
    re.compile(r"(?i)(?:^|[/\\])notes-private(?:[/\\]|$)"),
    re.compile(r"(?i)obsidian://[^\s)'\"]+"),
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"
    ),
)
MARKDOWN_LINK = re.compile(r"(!?)\[[^\]\n]*\]\(([^)\s]+)(?:\s+['\"][^)]*['\"])?\)")
HTML_ASSET = re.compile(r"(?i)\b(src|href)\s*=\s*['\"]([^'\"]+)['\"]")
ASSET_SUFFIXES = {
    ".avif",
    ".bmp",
    ".doc",
    ".docx",
    ".gif",
    ".heic",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".svg",
    ".wav",
    ".webm",
    ".webp",
    ".xls",
    ".xlsx",
    ".zip",
}
SAFE_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")


class PublicationRejected(RuntimeError):
    """A publication boundary rejected one or more non-public signals."""

    def __init__(self, reasons: Iterable[str]):
        unique = tuple(sorted(set(reasons)))
        self.reasons = unique
        super().__init__("publication rejected: " + ", ".join(unique))


def run_git(root: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=not binary,
        encoding=None if binary else "utf-8",
    )
    if result.returncode != 0:
        raise PublicationRejected(("git_inspection_failed",))
    return result.stdout


def is_local_asset(target: str, *, is_image: bool) -> bool:
    normalized = target.strip("<>")
    lowered = normalized.lower()
    if lowered.startswith(("https://", "http://", "data:", "#")):
        return False
    path_without_query = lowered.split("?", 1)[0].split("#", 1)[0]
    return is_image or PurePosixPath(path_without_query).suffix in ASSET_SUFFIXES


def detect_text_violations(text: str, *, canary: str) -> set[str]:
    """Return category names only; never return matching private text."""
    reasons: set[str] = set()
    if WIKILINK.search(text):
        reasons.add("private_wikilink")
    if BLOCK_REFERENCE.search(text):
        reasons.add("block_reference")
    if any(pattern.search(text) for pattern in PRIVATE_PATHS):
        reasons.add("private_path")
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        reasons.add("secret")
    if canary and canary in text:
        reasons.add("canary")

    for match in MARKDOWN_LINK.finditer(text):
        if is_local_asset(match.group(2), is_image=bool(match.group(1))):
            reasons.add("local_asset")
    for match in HTML_ASSET.finditer(text):
        if is_local_asset(match.group(2), is_image=match.group(1).lower() == "src"):
            reasons.add("local_asset")
    return reasons


def decode_publication_text(data: bytes) -> str | None:
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def normalize_relative_path(raw: str | Path) -> PurePosixPath:
    path = PurePosixPath(str(raw))
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise PublicationRejected(("unsafe_input_path",))
    return path


def validate_ref(raw: str) -> str:
    if (
        not SAFE_REF.fullmatch(raw)
        or ".." in raw
        or "//" in raw
        or raw.endswith(("/", ".", ".lock"))
    ):
        raise PublicationRejected(("unsafe_git_ref",))
    return raw


def repository_root(raw: Path) -> Path:
    root = raw.expanduser().resolve()
    output = str(run_git(root, "rev-parse", "--show-toplevel")).strip()
    if Path(output).resolve() != root:
        raise PublicationRejected(("blog_root_not_repository_root",))
    return root


def new_history_objects(root: Path, base_commit: str) -> list[tuple[str, str]]:
    output = str(run_git(root, "rev-list", "--objects", f"{base_commit}..HEAD"))
    objects: list[tuple[str, str]] = []
    for line in output.splitlines():
        object_id, separator, path = line.partition(" ")
        objects.append((object_id, path if separator else ""))
    return objects


def inspect_new_history(root: Path, base_commit: str, *, canary: str) -> set[str]:
    reasons: set[str] = set()
    commits = str(run_git(root, "rev-list", "--reverse", f"{base_commit}..HEAD"))
    for commit in commits.splitlines():
        message = str(run_git(root, "show", "-s", "--format=%B", commit))
        reasons.update(detect_text_violations(message, canary=canary))

    for object_id, path in new_history_objects(root, base_commit):
        object_type = str(run_git(root, "cat-file", "-t", object_id)).strip()
        if object_type != "blob":
            continue
        reasons.update(detect_text_violations(path, canary=canary))
        data = run_git(root, "cat-file", "blob", object_id, binary=True)
        assert isinstance(data, bytes)
        text = decode_publication_text(data)
        if text is None:
            reasons.add("binary_asset")
            continue
        reasons.update(detect_text_violations(text, canary=canary))
    return reasons


def inspect_artifact_root(
    root: Path, raw_artifact_root: str, *, canary: str
) -> set[str]:
    relative = normalize_relative_path(raw_artifact_root)
    artifact_root = root.joinpath(*relative.parts)
    if (
        not artifact_root.is_dir()
        or artifact_root.is_symlink()
        or not is_within(artifact_root.resolve(), root)
    ):
        raise PublicationRejected(("artifact_root_missing",))

    reasons: set[str] = set()
    for path in artifact_root.rglob("*"):
        if path.is_symlink():
            reasons.add("artifact_symlink")
            continue
        if not path.is_file():
            continue
        relative_name = path.relative_to(root).as_posix()
        reasons.update(detect_text_violations(relative_name, canary=canary))
        data = path.read_bytes()
        if canary and canary.encode("utf-8") in data:
            reasons.add("canary")
        text = data.decode("utf-8", errors="ignore")
        reasons.update(detect_text_violations(text, canary=canary))
    return reasons


def validate_publication(
    *,
    blog_root: Path,
    candidate: str | Path,
    base_ref: str,
    artifact_roots: Iterable[str] = (),
    canary: str,
) -> None:
    if not canary:
        raise PublicationRejected(("canary_not_configured",))

    root = repository_root(blog_root)
    candidate_relative = normalize_relative_path(candidate)
    candidate_path = root.joinpath(*candidate_relative.parts)
    if (
        not candidate_path.is_file()
        or candidate_path.is_symlink()
        or not is_within(candidate_path.resolve(), root)
    ):
        raise PublicationRejected(("candidate_missing_or_unsafe",))

    safe_ref = validate_ref(base_ref)
    base_commit = str(run_git(root, "rev-parse", "--verify", f"{safe_ref}^{{commit}}"))
    base_commit = base_commit.strip()
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_commit, "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if ancestor.returncode != 0:
        raise PublicationRejected(("base_not_ancestor",))

    reasons = detect_text_violations(
        candidate_path.read_text(encoding="utf-8"), canary=canary
    )
    reasons.update(inspect_new_history(root, base_commit, canary=canary))
    for artifact_root in artifact_roots:
        reasons.update(inspect_artifact_root(root, artifact_root, canary=canary))
    if reasons:
        raise PublicationRejected(reasons)


def is_within(path: Path, parent: Path) -> bool:
    return path.is_relative_to(parent)


def verify_private_boundary(public_root: Path, private_root: Path) -> None:
    public = public_root.expanduser().resolve()
    private_input = private_root.expanduser().absolute()
    private = private_root.expanduser().resolve()
    reasons: set[str] = set()
    if is_within(private_input, public) or is_within(private, public):
        reasons.add("private_root_inside_public")

    try:
        tracked = str(run_git(public, "ls-files", "-z")).split("\x00")
    except PublicationRejected:
        reasons.add("public_root_not_git_repository")
        tracked = []
    for relative in tracked:
        if not relative:
            continue
        tracked_path = public / relative
        if tracked_path.is_symlink() and is_within(tracked_path.resolve(), private):
            reasons.add("private_symlink_tracked")
    if reasons:
        raise PublicationRejected(reasons)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser(
        "check", help="inspect candidate, new history, and artifacts"
    )
    check.add_argument("--blog-root", required=True, type=Path)
    check.add_argument("--candidate", required=True)
    check.add_argument("--base-ref", required=True)
    check.add_argument("--artifact-root", action="append", default=[])
    check.add_argument("--canary-env", default="PUBLICATION_CANARY")

    boundary = commands.add_parser(
        "verify-private-boundary",
        help="require the private clone to live outside public root",
    )
    boundary.add_argument("--public-root", required=True, type=Path)
    boundary.add_argument("--private-root", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "verify-private-boundary":
            verify_private_boundary(args.public_root, args.private_root)
            print("PASS: private clone is outside the public workspace")
            return 0

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args.canary_env):
            raise PublicationRejected(("unsafe_canary_environment_name",))
        canary = os.environ.get(args.canary_env, "")
        validate_publication(
            blog_root=args.blog_root,
            candidate=args.candidate,
            base_ref=args.base_ref,
            artifact_roots=args.artifact_root,
            canary=canary,
        )
        print("PASS: publication candidate and complete pushed history are safe")
        return 0
    except (OSError, UnicodeError, PublicationRejected) as error:
        if isinstance(error, PublicationRejected):
            reasons = ", ".join(error.reasons)
        else:
            reasons = "local_inspection_failed"
        print(f"FAIL: publication rejected ({reasons})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
