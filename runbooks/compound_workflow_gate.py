#!/usr/bin/env python3
"""Validate ticket-backed Compound Engineering workflow evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

WORKFLOW_SCHEMA = "compound-work/v1"
REVIEW_TYPES = ("code", "doc")
REQUIRED_SECTIONS = ("주요 변경 지점", "검증", "외부 동기화")
KB_REQUIRED_SECTIONS = (
    "현재 기능 상태",
    "주요 동작과 경계",
    "검증 결과",
    "운영 및 사용 시 주의사항",
)
PLACEHOLDER_MARKERS = ("[작성 필요]", "TODO", "TBD", "ZZA-000", "example.com", "...")


class GateError(RuntimeError):
    """A workflow gate requirement was not met."""


@dataclass(frozen=True)
class Evidence:
    path: PurePosixPath
    fields: Mapping[str, str]
    body: str


@dataclass(frozen=True)
class PendingCloseout:
    section: str
    repo: str
    pr: int
    evidence: str


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(command: list[str], *, cwd: Path) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise GateError(f"{' '.join(command)}: {detail}")
    return result.stdout


def git(root: Path, *args: str) -> str:
    return run(["git", *args], cwd=root)


def gh(root: Path, *args: str) -> str:
    return run(["gh", *args], cwd=root)


def refresh_origin_main(root: Path) -> None:
    git(
        root,
        "fetch",
        "--quiet",
        "origin",
        "+refs/heads/main:refs/remotes/origin/main",
    )


def normalize_relative_path(raw: str, *, prefix: str | None = None) -> PurePosixPath:
    value = raw.strip()
    if not value:
        raise GateError("required path is empty")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise GateError(f"path must be workspace-relative without '..': {value}")
    if prefix and (not path.parts or path.parts[0:2] != tuple(prefix.split("/"))):
        raise GateError(f"path must be under {prefix}/: {value}")
    return path


def parse_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_evidence_text(path: PurePosixPath, text: str) -> Evidence:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise GateError(f"evidence must start with YAML frontmatter: {path}")

    closing = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        ),
        None,
    )
    if closing is None:
        raise GateError(f"evidence frontmatter is not closed: {path}")

    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([a-z][a-z0-9_]*):\s*(.*)", line)
        if not match:
            raise GateError(f"unsupported frontmatter at {path}:{line_number}: {line}")
        key, raw_value = match.groups()
        if key in fields:
            raise GateError(f"duplicate frontmatter field '{key}' in {path}")
        fields[key] = parse_scalar(raw_value)

    body = "\n".join(lines[closing + 1 :])
    return Evidence(path=path, fields=fields, body=body)


def read_evidence(root: Path, raw_path: str, *, ref: str | None = None) -> Evidence:
    path = normalize_relative_path(raw_path, prefix="docs/works")
    if ref:
        text = git(root, "show", f"{ref}:{path.as_posix()}")
    else:
        file_path = root.joinpath(*path.parts)
        if not file_path.is_file():
            raise GateError(f"evidence file does not exist: {path}")
        text = file_path.read_text(encoding="utf-8")
    return parse_evidence_text(path, text)


def require_field(fields: Mapping[str, str], name: str) -> str:
    value = fields.get(name, "").strip()
    if not value:
        raise GateError(f"required field is empty: {name}")
    if any(marker.lower() in value.lower() for marker in PLACEHOLDER_MARKERS):
        raise GateError(f"required field still contains a placeholder: {name}")
    return value


def require_https_url(
    fields: Mapping[str, str],
    name: str,
    *,
    allowed_hosts: tuple[str, ...] = (),
) -> str:
    value = require_field(fields, name)
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not hostname:
        raise GateError(f"{name} must be an HTTPS URL")
    if allowed_hosts and not any(
        hostname == allowed or hostname.endswith(f".{allowed}")
        for allowed in allowed_hosts
    ):
        expected = ", ".join(allowed_hosts)
        raise GateError(f"{name} must use an approved host: {expected}")
    return value


def ref_contains_file(root: Path, ref: str | None, path: PurePosixPath) -> bool:
    if ref:
        result = subprocess.run(
            ["git", "cat-file", "-t", f"{ref}:{path.as_posix()}"],
            cwd=root,
            check=False,
            text=True,
            capture_output=True,
        )
        return result.returncode == 0 and result.stdout.strip() == "blob"
    return root.joinpath(*path.parts).is_file()


def read_artifact_text(root: Path, ref: str | None, path: PurePosixPath) -> str:
    if ref:
        return git(root, "show", f"{ref}:{path.as_posix()}")
    return root.joinpath(*path.parts).read_text(encoding="utf-8")


def require_artifact(
    root: Path,
    fields: Mapping[str, str],
    path_field: str,
    *,
    prefix: str,
    ref: str | None,
    allowed_suffixes: tuple[str, ...],
) -> PurePosixPath:
    path = normalize_relative_path(require_field(fields, path_field), prefix=prefix)
    if path.suffix.lower() not in allowed_suffixes:
        expected = ", ".join(allowed_suffixes)
        raise GateError(f"{path_field} must use one of these suffixes: {expected}")
    if not ref_contains_file(root, ref, path):
        location = ref or "working tree"
        raise GateError(f"{path_field} must be a file in {location}: {path}")
    return path


def require_section(body: str, heading: str) -> None:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##\s|\Z)",
        body,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise GateError(f"work evidence is missing section: ## {heading}")
    content = match.group("body").strip()
    compact = re.sub(r"\s+", "", content)
    if len(compact) < 12 or any(
        marker.lower() in content.lower() for marker in PLACEHOLDER_MARKERS
    ):
        raise GateError(
            f"work evidence section is empty or placeholder-only: ## {heading}"
        )


def validate_optional_phase(
    root: Path,
    fields: Mapping[str, str],
    *,
    phase: str,
    path_prefix: str,
    ref: str | None,
) -> None:
    status = require_field(fields, f"{phase}_status").lower()
    if status == "complete":
        require_artifact(
            root,
            fields,
            f"{phase}_path",
            prefix=path_prefix,
            ref=ref,
            allowed_suffixes=(".md", ".html"),
        )
        require_https_url(
            fields,
            f"{phase}_notion_url",
            allowed_hosts=("notion.so", "notion.site"),
        )
        return
    if status == "waived":
        reason = require_field(fields, f"{phase}_waiver_reason")
        if len(reason.strip()) < 12:
            raise GateError(
                f"{phase}_waiver_reason must explain why the phase was skipped"
            )
        return
    raise GateError(f"{phase}_status must be complete or waived")


def validate_work_evidence(
    root: Path,
    evidence: Evidence,
    *,
    expected_ticket_status: str | None,
    ref: str | None,
) -> None:
    fields = evidence.fields
    if fields.get("workflow_schema") != WORKFLOW_SCHEMA:
        raise GateError(f"workflow_schema must be {WORKFLOW_SCHEMA}")

    ticket_id = require_field(fields, "ticket_id")
    if not re.fullmatch(r"[A-Z][A-Z0-9]+-\d+", ticket_id):
        raise GateError("ticket_id must look like ZZA-123")
    require_https_url(fields, "ticket_url", allowed_hosts=("linear.app",))

    ticket_status = require_field(fields, "ticket_status")
    if (
        expected_ticket_status
        and ticket_status.casefold() != expected_ticket_status.casefold()
    ):
        raise GateError(f"ticket_status must be {expected_ticket_status} for this gate")
    if not expected_ticket_status and ticket_status.casefold() not in {
        "in progress".casefold(),
        "in review".casefold(),
        "done".casefold(),
    }:
        raise GateError("ticket_status must be In Progress, In Review, or Done")

    validate_optional_phase(
        root, fields, phase="ideation", path_prefix="docs/ideation", ref=ref
    )
    validate_optional_phase(
        root, fields, phase="plan", path_prefix="docs/plans", ref=ref
    )

    work_status = require_field(fields, "work_status").lower()
    if expected_ticket_status is None:
        if work_status not in {"in_progress", "complete"}:
            raise GateError("work_status must be in_progress or complete")
    elif work_status != "complete":
        raise GateError("work_status must be complete before PR merge or closeout")
    require_https_url(
        fields,
        "work_notion_url",
        allowed_hosts=("notion.so", "notion.site"),
    )
    for heading in REQUIRED_SECTIONS:
        require_section(evidence.body, heading)


def expected_pr_url(repo: str, pr: int) -> str:
    parse_repo(repo)
    if pr <= 0:
        raise GateError("pr must be a positive integer")
    return f"https://github.com/{repo}/pull/{pr}"


def parse_repo(repo: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise GateError("repo must look like OWNER/REPO")


def pr_metadata(root: Path, repo: str, pr: int) -> dict[str, object]:
    parse_repo(repo)
    output = gh(
        root,
        "pr",
        "view",
        str(pr),
        "--repo",
        repo,
        "--json",
        "number,url,state,isDraft,headRefOid,mergeCommit,mergedAt,mergeable,mergeStateStatus",
    )
    try:
        metadata = json.loads(output)
    except json.JSONDecodeError as error:
        raise GateError("GitHub returned invalid PR metadata JSON") from error
    if not isinstance(metadata, dict):
        raise GateError("GitHub returned an unexpected PR metadata shape")
    return metadata


def trusted_review_comments(
    root: Path, repo: str, pr: int
) -> tuple[str, list[dict[str, object]]]:
    actor_login = gh(root, "api", "user", "--jq", ".login").strip()
    if not re.fullmatch(r"[A-Za-z0-9-]+", actor_login):
        raise GateError("GitHub did not return a valid authenticated reviewer login")

    comments_output = gh(
        root,
        "api",
        "--paginate",
        "--slurp",
        f"repos/{repo}/issues/{pr}/comments?per_page=100",
    )
    try:
        pages = json.loads(comments_output)
    except json.JSONDecodeError as error:
        raise GateError("GitHub returned invalid PR comments JSON") from error
    if not isinstance(pages, list) or not all(isinstance(page, list) for page in pages):
        raise GateError("GitHub returned an unexpected paginated PR comments shape")

    comments: list[dict[str, object]] = []
    for page in pages:
        if not all(isinstance(comment, dict) for comment in page):
            raise GateError("GitHub returned an unexpected PR comment entry")
        comments.extend(page)
    return actor_login, comments


def validate_pre_merge(root: Path, evidence_path: str, repo: str, pr: int) -> str:
    refresh_origin_main(root)
    evidence = read_evidence(root, evidence_path, ref="origin/main")
    validate_work_evidence(
        root,
        evidence,
        expected_ticket_status="In Review",
        ref="origin/main",
    )

    fields = evidence.fields
    expected_url = expected_pr_url(repo, pr)
    if require_https_url(fields, "pr_url") != expected_url:
        raise GateError(f"pr_url must be {expected_url}")
    if require_field(fields, "closeout_status").lower() != "pending":
        raise GateError("closeout_status must be pending before merge")

    metadata = pr_metadata(root, repo, pr)
    if metadata.get("state") != "OPEN":
        raise GateError("PR must be OPEN before merge")
    if metadata.get("isDraft"):
        raise GateError("draft PR cannot pass the workflow gate")
    if metadata.get("url") != expected_url:
        raise GateError("GitHub PR URL does not match workflow evidence")
    if (
        metadata.get("mergeable") != "MERGEABLE"
        or metadata.get("mergeStateStatus") != "CLEAN"
    ):
        raise GateError("PR must be MERGEABLE/CLEAN before merge")

    head_sha = str(metadata.get("headRefOid") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", head_sha):
        raise GateError("GitHub did not return a full PR head SHA")

    actor_login, comments = trusted_review_comments(root, repo, pr)
    ticket_id = fields["ticket_id"]
    matched_comment_ids: dict[str, int] = {}
    marker_pattern = re.compile(r"<!-- ce-review:v1 .*? -->")
    trusted_associations = {"OWNER", "MEMBER", "COLLABORATOR"}
    for review_type in REVIEW_TYPES:
        verdict_pattern = re.compile(
            rf"<!-- ce-review:v1 type={review_type} ticket={re.escape(ticket_id)} "
            rf"head_sha={head_sha} verdict=(pass|fail) -->"
        )
        candidates: list[tuple[int, str, str]] = []
        for comment in comments:
            user = comment.get("user")
            login = str(user.get("login") or "") if isinstance(user, dict) else ""
            association = str(comment.get("author_association") or "").upper()
            body = str(comment.get("body") or "")
            marker_match = verdict_pattern.search(body)
            comment_id = comment.get("id")
            if (
                login == actor_login
                and association in trusted_associations
                and marker_match
                and isinstance(comment_id, int)
            ):
                candidates.append((comment_id, marker_match.group(1), body))
        if not candidates:
            raise GateError(
                f"latest head is missing a trusted {review_type} review verdict for {ticket_id}"
            )

        comment_id, verdict, body = max(candidates, key=lambda item: item[0])
        if verdict != "pass":
            raise GateError(f"latest trusted {review_type} review verdict is fail")
        review_text = marker_pattern.sub("", body)
        if len(re.sub(r"\s+", "", review_text)) < 40:
            raise GateError(
                f"{review_type} review comment must include a substantive review summary"
            )
        matched_comment_ids[review_type] = comment_id

    if matched_comment_ids["code"] == matched_comment_ids["doc"]:
        raise GateError("code and doc reviews must be posted as separate PR comments")
    return head_sha


def parse_kb_paths(fields: Mapping[str, str]) -> list[str]:
    raw = require_field(fields, "kb_paths")
    paths = [item.strip() for item in raw.split(",") if item.strip()]
    if not paths:
        raise GateError("kb_paths must contain at least one docs/kb path")
    return paths


def require_iso_timestamp(fields: Mapping[str, str], name: str) -> str:
    value = require_field(fields, name)
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise GateError(f"{name} must be an ISO-8601 timestamp") from error
    return value


def expected_closeout_ticket_status(fields: Mapping[str, str]) -> str:
    completion = require_field(fields, "ticket_completion").lower()
    if completion == "complete":
        return "Done"
    if completion == "pending":
        remaining = [
            item.strip() for item in require_field(fields, "remaining_prs").split(",")
        ]
        if not remaining:
            raise GateError(
                "remaining_prs must list dependent PRs while ticket completion is pending"
            )
        for url in remaining:
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.hostname != "github.com":
                raise GateError("remaining_prs must contain GitHub HTTPS URLs")
        return "In Review"
    raise GateError("ticket_completion must be pending or complete")


def validate_kb_document(
    root: Path,
    ref: str,
    path: PurePosixPath,
    evidence: Evidence,
    expected_url: str,
) -> None:
    kb = parse_evidence_text(path, read_artifact_text(root, ref, path))
    fields = kb.fields
    require_field(fields, "title")
    expected_fields = {
        "ticket": evidence.fields["ticket_id"],
        "merged_pr": expected_url,
        "merge_commit": evidence.fields["merge_commit"],
        "work_evidence": evidence.path.as_posix(),
        "notion_feature_status": evidence.fields["notion_feature_status_url"],
        "notion_ticket": evidence.fields["notion_ticket_url"],
    }
    for name, expected in expected_fields.items():
        if require_field(fields, name) != expected:
            raise GateError(f"KB field {name} does not match work evidence")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", require_field(fields, "last_verified")):
        raise GateError("KB last_verified must use YYYY-MM-DD")
    for heading in KB_REQUIRED_SECTIONS:
        require_section(kb.body, heading)


def validate_closeout(
    root: Path,
    evidence_path: str,
    repo: str,
    pr: int,
    *,
    ref: str,
) -> None:
    evidence = read_evidence(root, evidence_path, ref=ref)
    fields = evidence.fields
    expected_ticket_status = expected_closeout_ticket_status(fields)
    validate_work_evidence(
        root,
        evidence,
        expected_ticket_status=expected_ticket_status,
        ref=ref,
    )

    if require_field(fields, "closeout_status").lower() != "complete":
        raise GateError("closeout_status must be complete")
    expected_url = expected_pr_url(repo, pr)
    if require_https_url(fields, "pr_url") != expected_url:
        raise GateError(f"pr_url must be {expected_url}")
    if require_https_url(fields, "merged_pr_url") != expected_url:
        raise GateError(f"merged_pr_url must be {expected_url}")
    require_https_url(
        fields,
        "notion_feature_status_url",
        allowed_hosts=("notion.so", "notion.site"),
    )
    require_https_url(
        fields,
        "notion_ticket_url",
        allowed_hosts=("notion.so", "notion.site"),
    )
    require_iso_timestamp(fields, "closed_at")

    kb_paths: list[PurePosixPath] = []
    for raw_path in parse_kb_paths(fields):
        path = normalize_relative_path(raw_path, prefix="docs/kb")
        if path.suffix.lower() != ".md":
            raise GateError(f"KB path must be a Markdown file: {path}")
        if path.name in {"README.md", "_template.md"}:
            raise GateError(f"kb_paths cannot use a template or README: {path}")
        if not ref_contains_file(root, ref, path):
            raise GateError(f"KB path must be a file in {ref}: {path}")
        validate_kb_document(root, ref, path, evidence, expected_url)
        kb_paths.append(path)
    if not kb_paths:
        raise GateError("at least one durable KB document is required")

    metadata = pr_metadata(root, repo, pr)
    if metadata.get("state") != "MERGED" or not metadata.get("mergedAt"):
        raise GateError("PR must be MERGED before closeout")
    merge_commit = metadata.get("mergeCommit") or {}
    merge_oid = (
        str(merge_commit.get("oid") or "") if isinstance(merge_commit, dict) else ""
    )
    if require_field(fields, "merge_commit") != merge_oid:
        raise GateError("merge_commit does not match GitHub remote truth")


def closeout_section(repo: str, pr: int) -> str:
    parse_repo(repo)
    if pr <= 0:
        raise GateError("pr must be a positive integer")
    digest = hashlib.sha256(f"{repo}#{pr}".encode()).hexdigest()[:16]
    return f"compound.closeout-{digest}"


def record_closeout(root: Path, evidence_path: str, repo: str, pr: int) -> None:
    path = normalize_relative_path(evidence_path, prefix="docs/works")
    section = closeout_section(repo, pr)
    git(root, "config", "--local", f"{section}.repo", repo)
    git(root, "config", "--local", f"{section}.pr", str(pr))
    git(root, "config", "--local", f"{section}.evidence", path.as_posix())
    print(f"RECORDED: post-merge closeout required for {repo}#{pr} ({path})")


def pending_records(root: Path) -> Iterable[PendingCloseout]:
    result = subprocess.run(
        [
            "git",
            "config",
            "--local",
            "--get-regexp",
            r"^compound\.closeout-[0-9a-f]+\.(repo|pr|evidence)$",
        ],
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode == 1:
        return ()
    if result.returncode != 0:
        detail = result.stderr.strip() or "cannot read local closeout state"
        raise GateError(detail)

    grouped: dict[str, dict[str, str]] = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition(" ")
        if not separator:
            raise GateError("invalid local closeout config entry")
        section, field = key.rsplit(".", maxsplit=1)
        grouped.setdefault(section, {})[field] = value

    records: list[PendingCloseout] = []
    for section, values in sorted(grouped.items()):
        try:
            record = PendingCloseout(
                section=section,
                repo=values["repo"],
                pr=int(values["pr"]),
                evidence=values["evidence"],
            )
        except (KeyError, ValueError) as error:
            raise GateError(f"incomplete local closeout state: {section}") from error
        if closeout_section(record.repo, record.pr) != section:
            raise GateError(
                f"closeout identity does not match its config section: {section}"
            )
        normalize_relative_path(record.evidence, prefix="docs/works")
        records.append(record)
    return records


def validate_pending_closeouts(root: Path, ref: str) -> None:
    records = list(pending_records(root))
    for record in records:
        validate_closeout(root, record.evidence, record.repo, record.pr, ref=ref)
        print(f"PASS: closeout is committed in {ref} for {record.repo}#{record.pr}")
    if not records:
        print("PASS: no pending Compound Engineering closeouts")


def cancel_closeout(root: Path, repo: str, pr: int) -> None:
    section = closeout_section(repo, pr)
    record = next(
        (item for item in pending_records(root) if item.section == section), None
    )
    if record is None:
        raise GateError(f"no pending closeout record for {repo}#{pr}")
    metadata = pr_metadata(root, repo, pr)
    if metadata.get("state") == "MERGED" or metadata.get("mergedAt"):
        raise GateError("cannot cancel closeout debt for a merged PR")
    git(root, "config", "--local", "--remove-section", section)
    print(f"CANCELLED: unmerged closeout attempt for {repo}#{pr}")


def acknowledge_closeout(root: Path, repo: str, pr: int) -> None:
    refresh_origin_main(root)
    section = closeout_section(repo, pr)
    record = next(
        (item for item in pending_records(root) if item.section == section), None
    )
    if record is None:
        raise GateError(f"no pending closeout record for {repo}#{pr}")
    validate_closeout(root, record.evidence, record.repo, record.pr, ref="origin/main")
    git(root, "config", "--local", "--remove-section", section)
    print(f"CLEARED: closeout is present on origin/main for {repo}#{pr}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate-work", help="validate local work evidence"
    )
    validate.add_argument("--evidence", required=True)

    pre_merge = subparsers.add_parser(
        "pre-merge", help="validate evidence and PR review comments"
    )
    pre_merge.add_argument("--evidence", required=True)
    pre_merge.add_argument("--repo", required=True)
    pre_merge.add_argument("--pr", required=True, type=int)

    closeout = subparsers.add_parser(
        "closeout", help="validate a committed post-merge closeout"
    )
    closeout.add_argument("--evidence", required=True)
    closeout.add_argument("--repo", required=True)
    closeout.add_argument("--pr", required=True, type=int)

    record = subparsers.add_parser(
        "record-closeout", help="record post-merge closeout debt"
    )
    record.add_argument("--evidence", required=True)
    record.add_argument("--repo", required=True)
    record.add_argument("--pr", required=True, type=int)

    pending = subparsers.add_parser(
        "pending-closeouts", help="validate all local closeout debt"
    )
    pending.add_argument("--ref", default="HEAD")

    cancel = subparsers.add_parser(
        "cancel-closeout", help="clear debt for an unmerged PR"
    )
    cancel.add_argument("--repo", required=True)
    cancel.add_argument("--pr", required=True, type=int)

    acknowledge = subparsers.add_parser(
        "ack-closeout", help="clear closeout debt after push"
    )
    acknowledge.add_argument("--repo", required=True)
    acknowledge.add_argument("--pr", required=True, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = workspace_root()
    try:
        if args.command == "validate-work":
            evidence = read_evidence(root, args.evidence)
            validate_work_evidence(
                root, evidence, expected_ticket_status=None, ref=None
            )
            print(f"PASS: work evidence is structurally complete ({evidence.path})")
        elif args.command == "pre-merge":
            verified_head = validate_pre_merge(root, args.evidence, args.repo, args.pr)
            print(
                f"PASS: workflow evidence and latest-head reviews are complete for {args.repo}#{args.pr}"
            )
            print(f"VERIFIED_HEAD_SHA={verified_head}")
        elif args.command == "closeout":
            validate_closeout(root, args.evidence, args.repo, args.pr, ref="HEAD")
            print(f"PASS: closeout is committed locally for {args.repo}#{args.pr}")
        elif args.command == "record-closeout":
            record_closeout(root, args.evidence, args.repo, args.pr)
        elif args.command == "pending-closeouts":
            validate_pending_closeouts(root, args.ref)
        elif args.command == "cancel-closeout":
            cancel_closeout(root, args.repo, args.pr)
        elif args.command == "ack-closeout":
            acknowledge_closeout(root, args.repo, args.pr)
        else:
            raise GateError(f"unsupported command: {args.command}")
    except GateError as error:
        print(f"⛔ compound-workflow-gate: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
