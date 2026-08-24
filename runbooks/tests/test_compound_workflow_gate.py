from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "compound_workflow_gate.py"
SPEC = importlib.util.spec_from_file_location("compound_workflow_gate", MODULE_PATH)
assert SPEC and SPEC.loader
GATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GATE
SPEC.loader.exec_module(GATE)


class CompoundWorkflowGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        for directory in ("docs/ideation", "docs/plans", "docs/works"):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        (self.root / "docs/ideation/idea.md").write_text("idea\n", encoding="utf-8")
        (self.root / "docs/plans/plan.md").write_text("plan\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def evidence_text(self, **overrides: str) -> str:
        fields = {
            "workflow_schema": "compound-work/v1",
            "ticket_id": "ZZA-123",
            "ticket_url": "https://linear.app/example/issue/ZZA-123/example",
            "ticket_status": "In Progress",
            "ticket_completion": "pending",
            "remaining_prs": "https://github.com/owner/repo/pull/43",
            "ideation_status": "complete",
            "ideation_path": "docs/ideation/idea.md",
            "ideation_notion_url": "https://www.notion.so/idea",
            "ideation_waiver_reason": "",
            "plan_status": "complete",
            "plan_path": "docs/plans/plan.md",
            "plan_notion_url": "https://www.notion.so/plan",
            "plan_waiver_reason": "",
            "work_status": "complete",
            "work_notion_url": "https://www.notion.so/work",
            "pr_url": "",
            "closeout_status": "pending",
            "merged_pr_url": "",
            "merge_commit": "",
            "kb_paths": "",
            "notion_feature_status_url": "",
            "notion_ticket_url": "",
            "closed_at": "",
        }
        fields.update(overrides)
        frontmatter = "\n".join(f"{key}: {value}" for key, value in fields.items())
        return f"""---
{frontmatter}
---

# ZZA-123 작업 기록

## 주요 변경 지점

- API 계약과 실행 경계의 변경 지점을 파일 단위로 정리했다.

## 검증

- 관련 단위 테스트와 문서 검사를 실행해 결과를 기록했다.

## 외부 동기화

- Linear 상태와 Notion 구현 문서를 같은 작업 사실로 동기화했다.
"""

    def v2_evidence_text(self, **overrides: str) -> str:
        fields = {
            "workflow_schema": "compound-work/v2",
            "ticket_id": "GH-7",
            "ticket_url": "https://github.com/owner/control/issues/7",
            "ticket_completion": "pending",
            "remaining_prs": "",
            "ideation_status": "complete",
            "ideation_path": "docs/ideation/idea.md",
            "ideation_waiver_reason": "",
            "plan_status": "complete",
            "plan_path": "docs/plans/plan.md",
            "plan_waiver_reason": "",
            "work_status": "in_progress",
            "pr_url": "",
            "closeout_status": "pending",
            "merged_pr_url": "",
            "merge_commit": "",
            "kb_paths": "",
            "closeout_completed_at": "",
        }
        fields.update(overrides)
        frontmatter = "\n".join(f"{key}: {value}" for key, value in fields.items())
        return f"""---
{frontmatter}
---

# GH-7 작업 기록

## 작업 목표

- GitHub Issue와 저장소 문서만으로 작업 흐름을 추적한다.

## 주요 변경 지점

- v2 evidence와 remote Issue 경계를 파일 단위로 구현했다.

## 검증

- v1 회귀와 v2 lifecycle 단위 테스트를 실행했다.

## GitHub 추적

- Issue, PR, work evidence와 KB 사이의 링크를 기록했다.

## Merge closeout

- merge 전에는 pending이며 merge 뒤 KB와 SHA를 기록한다.
"""

    def issue_pr_index_body(self, *urls: str) -> str:
        entries = "\n".join(f"- {url}" for url in urls)
        return f"{GATE.PR_INDEX_START}\n{entries}\n{GATE.PR_INDEX_END}\n"

    def write_evidence(self, text: str) -> str:
        relative = "docs/works/2026-07-14-ZZA-123-example-work.md"
        (self.root / relative).write_text(text, encoding="utf-8")
        return relative

    def validate(self, text: str) -> None:
        relative = self.write_evidence(text)
        evidence = GATE.read_evidence(self.root, relative)
        GATE.validate_work_evidence(
            self.root,
            evidence,
            expected_ticket_status=None,
            ref=None,
        )

    def test_workspace_root_resolves_invoking_nested_repository(self) -> None:
        GATE.run(["git", "init"], cwd=self.root)
        nested = self.root / "nested" / "directory"
        nested.mkdir(parents=True)
        self.assertEqual(GATE.workspace_root(nested), self.root.resolve())

    def test_git_reads_utf8_evidence_under_non_utf8_host_locale(self) -> None:
        GATE.run(["git", "init"], cwd=self.root)
        evidence_path = self.write_evidence(
            self.evidence_text().replace("작업 기록", "호스트 자동 기동 작업 기록")
        )
        GATE.run(["git", "add", evidence_path], cwd=self.root)
        GATE.run(
            [
                "git",
                "-c",
                "user.name=Workflow Test",
                "-c",
                "user.email=workflow@example.test",
                "commit",
                "-m",
                "UTF-8 evidence",
            ],
            cwd=self.root,
        )
        evidence = GATE.read_evidence(self.root, evidence_path, ref="HEAD")
        self.assertIn("호스트 자동 기동 작업 기록", evidence.body)

    def test_shared_command_runner_fails_closed_on_timeout(self) -> None:
        with mock.patch.object(
            GATE.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["gh", "issue", "view"], 120),
        ):
            with self.assertRaisesRegex(GATE.GateError, "gh command timed out"):
                GATE.run(["gh", "issue", "view"], cwd=self.root)

    def test_accepts_complete_work_evidence(self) -> None:
        self.validate(self.evidence_text())

    def test_accepts_github_native_v2_without_notion_or_linear(self) -> None:
        self.validate(self.v2_evidence_text())

    def test_v2_rejects_no_ticket_and_mismatched_issue_number(self) -> None:
        with self.assertRaisesRegex(GATE.GateError, "ticket_id must look like GH-7"):
            self.validate(self.v2_evidence_text(ticket_id="NO-TICKET"))
        with self.assertRaisesRegex(GATE.GateError, "ticket_id must look like GH-7"):
            self.validate(self.v2_evidence_text(ticket_id="GH-0"))
        with self.assertRaisesRegex(GATE.GateError, "ticket_id must match ticket_url"):
            self.validate(self.v2_evidence_text(ticket_id="GH-8"))

    def test_v2_rejects_noncanonical_issue_urls(self) -> None:
        for ticket_url in (
            "http://github.com/owner/control/issues/7",
            "https://invalid.test/owner/control/issues/7",
            "https://github.com/owner/control/pull/7",
            "https://github.com/owner/control/issues/7?view=1",
        ):
            with (
                self.subTest(ticket_url=ticket_url),
                self.assertRaisesRegex(GATE.GateError, "ticket_url must look like"),
            ):
                self.validate(self.v2_evidence_text(ticket_url=ticket_url))

    def test_issue_metadata_rejects_invalid_json(self) -> None:
        issue = GATE.GitHubIssue(
            repo="owner/control",
            number=7,
            url="https://github.com/owner/control/issues/7",
        )
        with mock.patch.object(GATE, "gh", return_value="not-json"):
            with self.assertRaisesRegex(GATE.GateError, "invalid Issue metadata JSON"):
                GATE.issue_metadata(self.root, issue)

    def test_v2_rejects_legacy_tracker_fields(self) -> None:
        with self.assertRaisesRegex(GATE.GateError, "not allowed in compound-work/v2"):
            self.validate(
                self.v2_evidence_text(
                    work_notion_url="https://www.notion.so/legacy",
                )
            )

    def test_accepts_in_progress_work_evidence_before_pr(self) -> None:
        self.validate(self.evidence_text(work_status="in_progress"))

    def test_accepts_explicit_no_ticket_waiver(self) -> None:
        self.validate(
            self.evidence_text(
                ticket_id="NO-TICKET",
                ticket_url="",
                ticket_status="waived",
                ticket_completion="waived",
                remaining_prs="",
            )
        )

    def test_no_ticket_waiver_requires_empty_ticket_url(self) -> None:
        with self.assertRaisesRegex(GATE.GateError, "ticket_url must be empty"):
            self.validate(
                self.evidence_text(
                    ticket_id="NO-TICKET",
                    ticket_status="waived",
                    ticket_completion="waived",
                    remaining_prs="",
                )
            )

    def test_rejects_arbitrary_ticket_waiver_identifier(self) -> None:
        with self.assertRaisesRegex(GATE.GateError, "be NO-TICKET"):
            self.validate(
                self.evidence_text(
                    ticket_id="SKIPPED",
                    ticket_url="",
                    ticket_status="waived",
                    ticket_completion="waived",
                    remaining_prs="",
                )
            )

    def test_no_ticket_waiver_rejects_remaining_pull_requests(self) -> None:
        with self.assertRaisesRegex(GATE.GateError, "remaining_prs must be empty"):
            self.validate(
                self.evidence_text(
                    ticket_id="NO-TICKET",
                    ticket_url="",
                    ticket_status="waived",
                    ticket_completion="waived",
                )
            )

    def test_no_ticket_waiver_requires_waived_status_and_completion(self) -> None:
        for field, value in (
            ("ticket_status", "In Review"),
            ("ticket_completion", "complete"),
        ):
            with (
                self.subTest(field=field),
                self.assertRaisesRegex(GATE.GateError, f"{field} must be waived"),
            ):
                overrides = {
                    "ticket_id": "NO-TICKET",
                    "ticket_url": "",
                    "ticket_status": "waived",
                    "ticket_completion": "waived",
                    "remaining_prs": "",
                }
                overrides[field] = value
                self.validate(self.evidence_text(**overrides))

    def test_ref_contains_file_rejects_tree_objects(self) -> None:
        GATE.run(["git", "init"], cwd=self.root)
        GATE.run(["git", "add", "docs"], cwd=self.root)
        GATE.run(
            [
                "git",
                "-c",
                "user.name=Workflow Test",
                "-c",
                "user.email=workflow@example.test",
                "commit",
                "-m",
                "test fixtures",
            ],
            cwd=self.root,
        )
        self.assertTrue(
            GATE.ref_contains_file(
                self.root, "HEAD", PurePosixPath("docs/plans/plan.md")
            )
        )
        self.assertFalse(
            GATE.ref_contains_file(self.root, "HEAD", PurePosixPath("docs/plans"))
        )

    def test_trusted_review_comments_flattens_all_pages(self) -> None:
        def fake_gh(root: Path, *args: str) -> str:
            del root
            if args == ("api", "user", "--jq", ".login"):
                return "reviewer\n"
            self.assertIn("--paginate", args)
            self.assertIn("--slurp", args)
            return json.dumps([[{"id": 1}], [{"id": 101}]])

        with mock.patch.object(GATE, "gh", side_effect=fake_gh):
            actor, comments = GATE.trusted_review_comments(self.root, "owner/repo", 42)
        self.assertEqual(actor, "reviewer")
        self.assertEqual([comment["id"] for comment in comments], [1, 101])

    def test_accepts_documented_ideation_and_plan_waivers(self) -> None:
        self.validate(
            self.evidence_text(
                ideation_status="waived",
                ideation_path="",
                ideation_notion_url="",
                ideation_waiver_reason="긴급 회귀 수정이라 별도 아이디에이션을 생략했다.",
                plan_status="waived",
                plan_path="",
                plan_notion_url="",
                plan_waiver_reason="기존 Linear 티켓의 승인된 수정 범위를 그대로 사용했다.",
            )
        )

    def test_rejects_missing_notion_url(self) -> None:
        with self.assertRaisesRegex(GATE.GateError, "ideation_notion_url"):
            self.validate(self.evidence_text(ideation_notion_url=""))

    def test_accepts_app_notion_urls(self) -> None:
        self.validate(
            self.evidence_text(
                ideation_notion_url="https://app.notion.com/p/idea",
                plan_notion_url="https://app.notion.com/p/plan",
                work_notion_url="https://app.notion.com/p/work",
            )
        )

    def test_rejects_placeholder_section(self) -> None:
        text = self.evidence_text().replace(
            "- API 계약과 실행 경계의 변경 지점을 파일 단위로 정리했다.",
            "[작성 필요]",
        )
        with self.assertRaisesRegex(GATE.GateError, "주요 변경 지점"):
            self.validate(text)

    def test_accepts_go_recursive_package_pattern_in_verification(self) -> None:
        text = self.evidence_text().replace(
            "- 관련 단위 테스트와 문서 검사를 실행해 결과를 기록했다.",
            "- `go test ./...`와 문서 검사를 실행해 결과를 기록했다.",
        )
        self.validate(text)

    def test_rejects_standalone_ellipsis_placeholder(self) -> None:
        text = self.evidence_text().replace(
            "- 관련 단위 테스트와 문서 검사를 실행해 결과를 기록했다.",
            "- ...",
        )
        with self.assertRaisesRegex(GATE.GateError, "검증"):
            self.validate(text)

    def test_pre_merge_requires_both_latest_head_review_markers(self) -> None:
        repo = "owner/repo"
        pr = 42
        head_sha = "a" * 40
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.evidence_text(
                ticket_status="In Review",
                pr_url=f"https://github.com/{repo}/pull/{pr}",
            ),
        )
        metadata = {
            "state": "OPEN",
            "isDraft": False,
            "url": f"https://github.com/{repo}/pull/{pr}",
            "headRefOid": head_sha,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }
        code_marker = (
            "코드 리뷰에서 실행 경계, 오류 처리, 테스트 결과와 회귀 위험을 확인했으며 "
            "merge를 막을 blocker가 남아 있지 않습니다.\n\n"
            f"<!-- ce-review:v1 type=code ticket=ZZA-123 "
            f"head_sha={head_sha} verdict=pass -->"
        )
        comments = [
            {
                "id": 1,
                "body": code_marker,
                "user": {"login": "reviewer"},
                "author_association": "OWNER",
            }
        ]
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "pr_metadata", return_value=metadata),
            mock.patch.object(
                GATE,
                "trusted_review_comments",
                return_value=("reviewer", comments),
            ),
            self.assertRaisesRegex(GATE.GateError, "doc review"),
        ):
            GATE.validate_pre_merge(self.root, "docs/works/work.md", repo, pr)

    def test_pre_merge_accepts_both_latest_head_review_markers(self) -> None:
        repo = "owner/repo"
        pr = 42
        head_sha = "b" * 40
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.evidence_text(
                ticket_status="In Review",
                pr_url=f"https://github.com/{repo}/pull/{pr}",
            ),
        )
        metadata = {
            "state": "OPEN",
            "isDraft": False,
            "url": f"https://github.com/{repo}/pull/{pr}",
            "headRefOid": head_sha,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }
        comments = [
            {
                "id": index,
                "body": (
                    f"{review_type} 리뷰에서 변경 범위, 계약, 검증 결과와 회귀 위험을 "
                    "확인했으며 merge를 막을 blocker가 남아 있지 않습니다.\n\n"
                    f"<!-- ce-review:v1 type={review_type} ticket=ZZA-123 "
                    f"head_sha={head_sha} verdict=pass -->"
                ),
                "user": {"login": "reviewer"},
                "author_association": "OWNER",
            }
            for index, review_type in enumerate(("code", "doc"), start=1)
        ]
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "pr_metadata", return_value=metadata),
            mock.patch.object(
                GATE,
                "trusted_review_comments",
                return_value=("reviewer", comments),
            ),
        ):
            self.assertEqual(
                GATE.validate_pre_merge(self.root, "docs/works/work.md", repo, pr),
                head_sha,
            )

    def test_v2_pre_merge_binds_issue_and_root_evidence_revision(self) -> None:
        repo = "owner/blog"
        pr = 42
        head_sha = "b" * 40
        evidence_commit = "c" * 40
        evidence_blob = "d" * 40
        evidence_path = "docs/works/work.md"
        evidence = GATE.parse_evidence_text(
            PurePosixPath(evidence_path),
            self.v2_evidence_text(
                work_status="complete",
                pr_url=f"https://github.com/{repo}/pull/{pr}",
            ),
        )
        metadata = {
            "state": "OPEN",
            "isDraft": False,
            "url": f"https://github.com/{repo}/pull/{pr}",
            "headRefOid": head_sha,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }
        issue = {
            "number": 7,
            "url": "https://github.com/owner/control/issues/7",
            "state": "OPEN",
            "stateReason": None,
            "labels": [{"name": "status:in-review"}, {"name": "feature"}],
        }
        comments = [
            {
                "id": index,
                "body": (
                    f"{review_type} 리뷰에서 변경 범위, 계약, 검증 결과와 회귀 위험을 "
                    "확인했으며 merge를 막을 blocker가 남아 있지 않습니다.\n\n"
                    f"<!-- ce-review:v2 type={review_type} ticket=GH-7 "
                    f"head_sha={head_sha} evidence_commit={evidence_commit} "
                    f"evidence_blob={evidence_blob} verdict=pass -->"
                ),
                "user": {"login": "reviewer"},
                "author_association": "OWNER",
            }
            for index, review_type in enumerate(("code", "doc"), start=1)
        ]
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "pr_metadata", return_value=metadata),
            mock.patch.object(GATE, "issue_metadata", return_value=issue),
            mock.patch.object(
                GATE,
                "evidence_revision",
                return_value=(evidence_commit, evidence_blob),
            ),
            mock.patch.object(
                GATE,
                "trusted_review_comments",
                return_value=("reviewer", comments),
            ),
        ):
            self.assertEqual(
                GATE.validate_pre_merge(self.root, evidence_path, repo, pr),
                head_sha,
            )

    def test_review_context_prints_exact_v2_revision_inputs(self) -> None:
        evidence_path = "docs/works/work.md"
        evidence = GATE.parse_evidence_text(
            PurePosixPath(evidence_path),
            self.v2_evidence_text(
                work_status="complete",
                pr_url="https://github.com/owner/blog/pull/42",
            ),
        )
        head_sha = "b" * 40
        evidence_commit = "c" * 40
        evidence_blob = "d" * 40
        output = io.StringIO()
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(
                GATE,
                "pr_metadata",
                return_value={
                    "url": "https://github.com/owner/blog/pull/42",
                    "headRefOid": head_sha,
                },
            ),
            mock.patch.object(
                GATE,
                "evidence_revision",
                return_value=(evidence_commit, evidence_blob),
            ),
            contextlib.redirect_stdout(output),
        ):
            GATE.print_review_context(self.root, evidence_path, "owner/blog", 42)

        rendered = output.getvalue()
        self.assertIn(f"HEAD_SHA={head_sha}", rendered)
        self.assertIn(f"EVIDENCE_COMMIT={evidence_commit}", rendered)
        self.assertIn(f"EVIDENCE_BLOB={evidence_blob}", rendered)
        self.assertIn("CODE_MARKER_TEMPLATE=<!-- ce-review:v2 type=code", rendered)
        self.assertIn("DOC_MARKER_TEMPLATE=<!-- ce-review:v2 type=doc", rendered)
        self.assertIn("verdict=<pass-or-fail>", rendered)

    def test_v2_pre_merge_rejects_wrong_or_multiple_lifecycle_labels(self) -> None:
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                pr_url="https://github.com/owner/blog/pull/42",
            ),
        )
        for labels in (
            [],
            [{"name": "status:in-progress"}],
            [{"name": "status:in-review"}, {"name": "status:blocked"}],
        ):
            with (
                self.subTest(labels=labels),
                self.assertRaisesRegex(GATE.GateError, "exactly one lifecycle label"),
            ):
                GATE.validate_issue_state(
                    evidence.fields,
                    {
                        "number": 7,
                        "url": "https://github.com/owner/control/issues/7",
                        "state": "OPEN",
                        "stateReason": None,
                        "labels": labels,
                    },
                    expected_state="OPEN",
                    expected_label="status:in-review",
                )

    def test_v2_pre_merge_rejects_stale_root_evidence_marker(self) -> None:
        marker = GATE.review_marker_pattern(
            "compound-work/v2",
            review_type="code",
            ticket_id="GH-7",
            head_sha="a" * 40,
            evidence_commit="b" * 40,
            evidence_blob="c" * 40,
        )
        self.assertIsNone(
            marker.search(
                "<!-- ce-review:v2 type=code ticket=GH-7 "
                f"head_sha={'a' * 40} evidence_commit={'b' * 40} "
                f"evidence_blob={'d' * 40} verdict=pass -->"
            )
        )

    def test_pre_merge_accepts_no_ticket_review_markers(self) -> None:
        repo = "owner/repo"
        pr = 42
        head_sha = "9" * 40
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.evidence_text(
                ticket_id="NO-TICKET",
                ticket_url="",
                ticket_status="waived",
                ticket_completion="waived",
                remaining_prs="",
                pr_url=f"https://github.com/{repo}/pull/{pr}",
            ),
        )
        metadata = {
            "state": "OPEN",
            "isDraft": False,
            "url": f"https://github.com/{repo}/pull/{pr}",
            "headRefOid": head_sha,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }
        comments = [
            {
                "id": index,
                "body": (
                    f"{review_type} 리뷰에서 변경 범위, 계약, 검증 결과와 회귀 위험을 "
                    "확인했으며 merge를 막을 blocker가 남아 있지 않습니다.\n\n"
                    f"<!-- ce-review:v1 type={review_type} ticket=NO-TICKET "
                    f"head_sha={head_sha} verdict=pass -->"
                ),
                "user": {"login": "reviewer"},
                "author_association": "OWNER",
            }
            for index, review_type in enumerate(("code", "doc"), start=1)
        ]
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "pr_metadata", return_value=metadata),
            mock.patch.object(
                GATE,
                "trusted_review_comments",
                return_value=("reviewer", comments),
            ),
        ):
            self.assertEqual(
                GATE.validate_pre_merge(self.root, "docs/works/work.md", repo, pr),
                head_sha,
            )

    def test_no_ticket_closeout_preserves_waived_status(self) -> None:
        self.assertEqual(
            GATE.expected_closeout_ticket_status(
                {
                    "ticket_id": "NO-TICKET",
                    "ticket_completion": "waived",
                    "remaining_prs": "",
                }
            ),
            "waived",
        )

    def test_pre_merge_reads_new_evidence_from_verified_pr_head(self) -> None:
        repo = "owner/repo"
        pr = 42
        head_sha = "c" * 40
        evidence_path = "docs/works/work.md"
        evidence = GATE.parse_evidence_text(
            PurePosixPath(evidence_path),
            self.evidence_text(
                ticket_status="In Review",
                pr_url=f"https://github.com/{repo}/pull/{pr}",
            ),
        )
        metadata = {
            "state": "OPEN",
            "isDraft": False,
            "url": f"https://github.com/{repo}/pull/{pr}",
            "headRefOid": head_sha,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }
        comments = [
            {
                "id": index,
                "body": (
                    f"{review_type} 리뷰에서 변경 범위, 계약, 검증 결과와 회귀 위험을 "
                    "확인했으며 merge를 막을 blocker가 남아 있지 않습니다.\n\n"
                    f"<!-- ce-review:v1 type={review_type} ticket=ZZA-123 "
                    f"head_sha={head_sha} verdict=pass -->"
                ),
                "user": {"login": "reviewer"},
                "author_association": "OWNER",
            }
            for index, review_type in enumerate(("code", "doc"), start=1)
        ]
        evidence_refs: list[str | None] = []

        def fake_read_evidence(
            root: Path, raw_path: str, *, ref: str | None = None
        ) -> GATE.Evidence:
            del root, raw_path
            evidence_refs.append(ref)
            return evidence

        def fake_ref_contains_file(
            root: Path, ref: str | None, path: PurePosixPath
        ) -> bool:
            del root, path
            return ref == head_sha

        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", side_effect=fake_read_evidence),
            mock.patch.object(
                GATE, "ref_contains_file", side_effect=fake_ref_contains_file
            ),
            mock.patch.object(GATE, "pr_metadata", return_value=metadata),
            mock.patch.object(
                GATE,
                "trusted_review_comments",
                return_value=("reviewer", comments),
            ),
        ):
            self.assertEqual(
                GATE.validate_pre_merge(self.root, evidence_path, repo, pr),
                head_sha,
            )

        self.assertEqual(evidence_refs, [head_sha])

    def test_pre_merge_rejects_untrusted_comment_author(self) -> None:
        repo = "owner/repo"
        pr = 42
        head_sha = "e" * 40
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.evidence_text(
                ticket_status="In Review",
                pr_url=f"https://github.com/{repo}/pull/{pr}",
            ),
        )
        metadata = {
            "state": "OPEN",
            "isDraft": False,
            "url": f"https://github.com/{repo}/pull/{pr}",
            "headRefOid": head_sha,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }
        comments = [
            {
                "id": index,
                "body": (
                    "공격자가 충분히 긴 리뷰 요약을 흉내 내지만 신뢰할 수 없는 댓글입니다. "
                    "변경 범위와 검증 결과도 거짓으로 작성했습니다.\n\n"
                    f"<!-- ce-review:v1 type={review_type} ticket=ZZA-123 "
                    f"head_sha={head_sha} verdict=pass -->"
                ),
                "user": {"login": "attacker"},
                "author_association": "NONE",
            }
            for index, review_type in enumerate(("code", "doc"), start=1)
        ]
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "pr_metadata", return_value=metadata),
            mock.patch.object(
                GATE,
                "trusted_review_comments",
                return_value=("reviewer", comments),
            ),
            self.assertRaisesRegex(GATE.GateError, "trusted code review"),
        ):
            GATE.validate_pre_merge(self.root, "docs/works/work.md", repo, pr)

    def test_pre_merge_latest_fail_overrides_earlier_pass(self) -> None:
        repo = "owner/repo"
        pr = 42
        head_sha = "f" * 40
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.evidence_text(
                ticket_status="In Review",
                pr_url=f"https://github.com/{repo}/pull/{pr}",
            ),
        )
        metadata = {
            "state": "OPEN",
            "isDraft": False,
            "url": f"https://github.com/{repo}/pull/{pr}",
            "headRefOid": head_sha,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }

        def comment(
            comment_id: int, review_type: str, verdict: str
        ) -> dict[str, object]:
            return {
                "id": comment_id,
                "body": (
                    "최신 head의 변경 범위와 검증 결과를 상세히 검토한 리뷰 요약입니다. "
                    "blocker 여부와 남은 위험도 함께 기록했습니다.\n\n"
                    f"<!-- ce-review:v1 type={review_type} ticket=ZZA-123 "
                    f"head_sha={head_sha} verdict={verdict} -->"
                ),
                "user": {"login": "reviewer"},
                "author_association": "OWNER",
            }

        comments = [
            comment(1, "code", "pass"),
            comment(2, "doc", "pass"),
            comment(3, "code", "fail"),
        ]
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "pr_metadata", return_value=metadata),
            mock.patch.object(
                GATE,
                "trusted_review_comments",
                return_value=("reviewer", comments),
            ),
            self.assertRaisesRegex(
                GATE.GateError, "latest trusted code review verdict is fail"
            ),
        ):
            GATE.validate_pre_merge(self.root, "docs/works/work.md", repo, pr)

    def test_pre_merge_rejects_combined_review_comment(self) -> None:
        repo = "owner/repo"
        pr = 42
        head_sha = "d" * 40
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.evidence_text(
                ticket_status="In Review",
                pr_url=f"https://github.com/{repo}/pull/{pr}",
            ),
        )
        metadata = {
            "state": "OPEN",
            "isDraft": False,
            "url": f"https://github.com/{repo}/pull/{pr}",
            "headRefOid": head_sha,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }
        markers = "\n".join(
            (
                f"<!-- ce-review:v1 type={review_type} ticket=ZZA-123 "
                f"head_sha={head_sha} verdict=pass -->"
            )
            for review_type in ("code", "doc")
        )
        comments = [
            {
                "id": 1,
                "body": (
                    "두 리뷰를 한 댓글에 합친 잘못된 증빙이며 변경 범위, 계약, 검증 결과와 "
                    "회귀 위험을 모두 확인했다는 충분히 긴 본문을 흉내 냅니다.\n"
                    f"{markers}"
                ),
                "user": {"login": "reviewer"},
                "author_association": "OWNER",
            }
        ]
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "pr_metadata", return_value=metadata),
            mock.patch.object(
                GATE,
                "trusted_review_comments",
                return_value=("reviewer", comments),
            ),
            self.assertRaisesRegex(GATE.GateError, "separate PR comments"),
        ):
            GATE.validate_pre_merge(self.root, "docs/works/work.md", repo, pr)

    def test_record_closeout_creates_debt_before_merge(self) -> None:
        repo = "owner/repo"
        pr = 42
        GATE.run(["git", "init"], cwd=self.root)
        GATE.record_closeout(self.root, "docs/works/work.md", repo, pr)
        records = list(GATE.pending_records(self.root))
        self.assertEqual([(record.repo, record.pr) for record in records], [(repo, pr)])

    def test_cancel_closeout_only_clears_unmerged_attempt(self) -> None:
        repo = "owner/repo"
        pr = 42
        GATE.run(["git", "init"], cwd=self.root)
        GATE.record_closeout(self.root, "docs/works/work.md", repo, pr)
        with mock.patch.object(
            GATE,
            "pr_metadata",
            return_value={"state": "OPEN", "mergedAt": None},
        ):
            GATE.cancel_closeout(self.root, repo, pr)
        self.assertEqual(list(GATE.pending_records(self.root)), [])

    def test_kb_document_must_match_evidence_and_have_substantive_sections(
        self,
    ) -> None:
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.evidence_text(
                merge_commit="c" * 40,
                notion_feature_status_url="https://www.notion.so/feature",
                notion_ticket_url="https://www.notion.so/ticket",
            ),
        )
        kb_text = f"""---
title: ZZA-123 Example
ticket: ZZA-123
merged_pr: https://github.com/owner/repo/pull/42
merge_commit: {"c" * 40}
work_evidence: docs/works/work.md
notion_feature_status: https://www.notion.so/feature
notion_ticket: https://www.notion.so/ticket
last_verified: 2026-07-14
---

# ZZA-123 Example

## 현재 기능 상태

기능이 merge되어 현재 main에서 사용할 수 있는 상태다.

## 주요 동작과 경계

입력 계약과 실패 경계, 외부 연동 제한을 현재 코드 기준으로 설명한다.

## 검증 결과

단위 테스트와 통합 검증 명령 및 결과를 구체적으로 기록한다.

## 운영 및 사용 시 주의사항

운영자가 알아야 하는 설정, 제한, rollback 조건을 명시한다.
"""
        path = PurePosixPath("docs/kb/features/ZZA-123-example.md")
        with mock.patch.object(GATE, "read_artifact_text", return_value=kb_text):
            GATE.validate_kb_document(
                self.root,
                "HEAD",
                path,
                evidence,
                "https://github.com/owner/repo/pull/42",
            )

        placeholder = kb_text.replace(
            "기능이 merge되어 현재 main에서 사용할 수 있는 상태다.",
            "[작성 필요]",
        )
        with (
            mock.patch.object(GATE, "read_artifact_text", return_value=placeholder),
            self.assertRaisesRegex(GATE.GateError, "현재 기능 상태"),
        ):
            GATE.validate_kb_document(
                self.root,
                "HEAD",
                path,
                evidence,
                "https://github.com/owner/repo/pull/42",
            )

    def test_v2_kb_document_matches_github_native_evidence(self) -> None:
        merge_sha = "c" * 40
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                ticket_completion="complete",
                pr_url="https://github.com/owner/blog/pull/42",
                closeout_status="complete",
                merged_pr_url="https://github.com/owner/blog/pull/42",
                merge_commit=merge_sha,
                kb_paths="docs/kb/features/GH-7-example.md",
                closeout_completed_at="2026-08-24T12:00:00Z",
            ),
        )
        kb_text = f"""---
title: GH-7 Example
ticket: GH-7
ticket_url: https://github.com/owner/control/issues/7
merged_pr: https://github.com/owner/blog/pull/42
merge_commit: {merge_sha}
work_evidence: docs/works/work.md
last_verified: 2026-08-24
---

# GH-7 Example

## 현재 기능 상태

기능이 merge되어 현재 기본 브랜치에서 사용할 수 있다.

## 주요 동작과 경계

Issue와 저장소 문서의 책임 및 실패 경계를 설명한다.

## 검증 결과

단위 테스트와 통합 검증 명령 및 결과를 기록한다.

## 운영 및 사용 시 주의사항

운영자가 알아야 하는 상태 전이와 복구 절차를 기록한다.
"""
        with mock.patch.object(GATE, "read_artifact_text", return_value=kb_text):
            GATE.validate_kb_document(
                self.root,
                "HEAD",
                PurePosixPath("docs/kb/features/GH-7-example.md"),
                evidence,
                "https://github.com/owner/blog/pull/42",
            )

    def test_closeout_requires_remote_merge_commit_and_kb(self) -> None:
        repo = "owner/repo"
        pr = 42
        merge_sha = "c" * 40
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.evidence_text(
                ticket_status="Done",
                ticket_completion="complete",
                remaining_prs="",
                pr_url=f"https://github.com/{repo}/pull/{pr}",
                closeout_status="complete",
                merged_pr_url=f"https://github.com/{repo}/pull/{pr}",
                merge_commit=merge_sha,
                kb_paths="docs/kb/features/ZZA-123-example.md",
                notion_feature_status_url="https://www.notion.so/feature",
                notion_ticket_url="https://www.notion.so/ticket",
                closed_at="2026-07-14T12:00:00Z",
            ),
        )
        metadata = {
            "state": "MERGED",
            "mergedAt": "2026-07-14T11:00:00Z",
            "mergeCommit": {"oid": merge_sha},
        }
        with (
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "validate_kb_document"),
            mock.patch.object(GATE, "pr_metadata", return_value=metadata),
        ):
            GATE.validate_closeout(
                self.root,
                "docs/works/work.md",
                repo,
                pr,
                ref="HEAD",
            )

    def test_finalize_v2_issue_reconciles_partial_state_and_is_idempotent(self) -> None:
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                ticket_completion="complete",
                pr_url="https://github.com/owner/blog/pull/42",
                closeout_status="complete",
                merged_pr_url="https://github.com/owner/blog/pull/42",
                merge_commit="c" * 40,
                kb_paths="docs/kb/features/GH-7-example.md",
                closeout_completed_at="2026-08-24T12:00:00Z",
            ),
        )
        states = iter(
            [
                {
                    "number": 7,
                    "url": "https://github.com/owner/control/issues/7",
                    "state": "OPEN",
                    "stateReason": None,
                    "labels": [{"name": "status:in-review"}],
                    "body": self.issue_pr_index_body(
                        "https://github.com/owner/blog/pull/42"
                    ),
                },
                {
                    "number": 7,
                    "url": "https://github.com/owner/control/issues/7",
                    "state": "OPEN",
                    "stateReason": None,
                    "labels": [],
                    "body": self.issue_pr_index_body(
                        "https://github.com/owner/blog/pull/42"
                    ),
                },
                {
                    "number": 7,
                    "url": "https://github.com/owner/control/issues/7",
                    "state": "CLOSED",
                    "stateReason": "COMPLETED",
                    "labels": [],
                    "body": self.issue_pr_index_body(
                        "https://github.com/owner/blog/pull/42"
                    ),
                },
            ]
        )
        calls: list[tuple[str, ...]] = []

        def fake_gh(root: Path, *args: str) -> str:
            del root
            calls.append(args)
            return ""

        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(
                GATE, "issue_metadata", side_effect=lambda *_: next(states)
            ),
            mock.patch.object(
                GATE,
                "pr_metadata",
                return_value={"state": "MERGED", "mergedAt": "2026-08-24T12:00:00Z"},
            ),
            mock.patch.object(GATE, "gh", side_effect=fake_gh),
        ):
            GATE.finalize_github_issue(
                self.root,
                "docs/works/work.md",
                dry_run=False,
            )

        self.assertEqual(
            calls,
            [
                (
                    "issue",
                    "edit",
                    "7",
                    "--repo",
                    "owner/control",
                    "--remove-label",
                    "status:in-review",
                ),
                (
                    "issue",
                    "close",
                    "7",
                    "--repo",
                    "owner/control",
                    "--reason",
                    "completed",
                ),
            ],
        )

        completed = {
            "number": 7,
            "url": "https://github.com/owner/control/issues/7",
            "state": "CLOSED",
            "stateReason": "COMPLETED",
            "labels": [],
            "body": self.issue_pr_index_body("https://github.com/owner/blog/pull/42"),
        }
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(GATE, "issue_metadata", return_value=completed),
            mock.patch.object(
                GATE,
                "pr_metadata",
                return_value={"state": "MERGED", "mergedAt": "2026-08-24T12:00:00Z"},
            ),
            mock.patch.object(GATE, "gh") as gh_mock,
        ):
            GATE.finalize_github_issue(
                self.root,
                "docs/works/work.md",
                dry_run=False,
            )
        gh_mock.assert_not_called()

    def test_finalize_v2_issue_rejects_incomplete_closeout_before_mutation(
        self,
    ) -> None:
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                ticket_completion="complete",
                pr_url="https://github.com/owner/blog/pull/42",
                closeout_status="pending",
            ),
        )
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "issue_metadata") as issue_mock,
            mock.patch.object(GATE, "gh") as gh_mock,
        ):
            with self.assertRaisesRegex(
                GATE.GateError,
                "ticket_completion cannot be complete while closeout_status is pending",
            ):
                GATE.finalize_github_issue(
                    self.root,
                    "docs/works/work.md",
                    dry_run=False,
                )
        issue_mock.assert_not_called()
        gh_mock.assert_not_called()

    def test_finalize_v2_issue_dry_run_does_not_mutate(self) -> None:
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                ticket_completion="complete",
                pr_url="https://github.com/owner/blog/pull/42",
                closeout_status="complete",
                merged_pr_url="https://github.com/owner/blog/pull/42",
                merge_commit="c" * 40,
                kb_paths="docs/kb/features/GH-7-example.md",
                closeout_completed_at="2026-08-24T12:00:00Z",
            ),
        )
        issue = {
            "number": 7,
            "url": "https://github.com/owner/control/issues/7",
            "state": "OPEN",
            "stateReason": None,
            "labels": [{"name": "status:in-review"}],
            "body": self.issue_pr_index_body("https://github.com/owner/blog/pull/42"),
        }
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(GATE, "issue_metadata", return_value=issue),
            mock.patch.object(
                GATE,
                "pr_metadata",
                return_value={"state": "MERGED", "mergedAt": "2026-08-24T12:00:00Z"},
            ),
            mock.patch.object(GATE, "gh") as gh_mock,
        ):
            GATE.finalize_github_issue(
                self.root,
                "docs/works/work.md",
                dry_run=True,
            )
        gh_mock.assert_not_called()

    def test_finalize_v2_issue_requires_remote_pr_index_and_merged_entries(
        self,
    ) -> None:
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                ticket_completion="complete",
                pr_url="https://github.com/owner/blog/pull/42",
                closeout_status="complete",
                merged_pr_url="https://github.com/owner/blog/pull/42",
                merge_commit="c" * 40,
                kb_paths="docs/kb/features/GH-7-example.md",
                closeout_completed_at="2026-08-24T12:00:00Z",
            ),
        )
        issue_without_index = {
            "number": 7,
            "url": "https://github.com/owner/control/issues/7",
            "state": "OPEN",
            "stateReason": None,
            "labels": [{"name": "status:in-review"}],
            "body": "No canonical PR index here.",
        }
        issue_with_stacked_pr = {
            **issue_without_index,
            "body": self.issue_pr_index_body(
                "https://github.com/owner/blog/pull/42",
                "https://github.com/owner/blog/pull/43",
            ),
        }

        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(GATE, "issue_metadata", return_value=issue_without_index),
            mock.patch.object(GATE, "pr_metadata") as pr_mock,
            mock.patch.object(GATE, "gh") as gh_mock,
        ):
            with self.assertRaisesRegex(GATE.GateError, "canonical PR index"):
                GATE.finalize_github_issue(
                    self.root,
                    "docs/works/work.md",
                    dry_run=False,
                )
        pr_mock.assert_not_called()
        gh_mock.assert_not_called()

        def stacked_metadata(root: Path, repo: str, pr: int) -> dict[str, object]:
            del root, repo
            if pr == 42:
                return {"state": "MERGED", "mergedAt": "2026-08-24T12:00:00Z"}
            return {"state": "OPEN", "mergedAt": None}

        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(
                GATE, "issue_metadata", return_value=issue_with_stacked_pr
            ),
            mock.patch.object(GATE, "pr_metadata", side_effect=stacked_metadata),
            mock.patch.object(GATE, "gh") as gh_mock,
        ):
            with self.assertRaisesRegex(GATE.GateError, "unmerged PR"):
                GATE.finalize_github_issue(
                    self.root,
                    "docs/works/work.md",
                    dry_run=False,
                )
        gh_mock.assert_not_called()

    def test_acknowledge_v2_intermediate_closeout_keeps_issue_open(self) -> None:
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                ticket_completion="pending",
                remaining_prs="https://github.com/owner/blog/pull/43",
                pr_url="https://github.com/owner/blog/pull/42",
                closeout_status="complete",
                merged_pr_url="https://github.com/owner/blog/pull/42",
                merge_commit="c" * 40,
                kb_paths="docs/kb/features/GH-7-example.md",
                closeout_completed_at="2026-08-24T12:00:00Z",
            ),
        )
        issue = {
            "number": 7,
            "url": "https://github.com/owner/control/issues/7",
            "state": "OPEN",
            "stateReason": None,
            "labels": [{"name": "status:in-review"}],
        }
        record = GATE.PendingCloseout(
            section=GATE.closeout_section("owner/blog", 42),
            repo="owner/blog",
            pr=42,
            evidence="docs/works/work.md",
        )
        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "pending_records", return_value=[record]),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "issue_metadata", return_value=issue),
            mock.patch.object(GATE, "git") as git_mock,
        ):
            GATE.acknowledge_closeout(self.root, "owner/blog", 42)
        git_mock.assert_called_once_with(
            self.root,
            "config",
            "--local",
            "--remove-section",
            record.section,
        )

    def test_pending_closeout_allows_first_publish_then_requires_issue_finalization(
        self,
    ) -> None:
        target = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                ticket_completion="complete",
                pr_url="https://github.com/owner/blog/pull/42",
                closeout_status="complete",
                merged_pr_url="https://github.com/owner/blog/pull/42",
                merge_commit="c" * 40,
                kb_paths="docs/kb/features/GH-7-example.md",
                closeout_completed_at="2026-08-24T12:00:00Z",
            ),
        )
        published_pending = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                ticket_completion="pending",
                pr_url="https://github.com/owner/blog/pull/42",
            ),
        )
        record = GATE.PendingCloseout(
            section=GATE.closeout_section("owner/blog", 42),
            repo="owner/blog",
            pr=42,
            evidence="docs/works/work.md",
        )

        def first_publish_read(
            root: Path, path: str, *, ref: str | None = None
        ) -> GATE.Evidence:
            del root, path
            return published_pending if ref == "origin/main" else target

        with (
            mock.patch.object(GATE, "pending_records", return_value=[record]),
            mock.patch.object(GATE, "read_evidence", side_effect=first_publish_read),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "issue_metadata") as issue_mock,
        ):
            GATE.validate_pending_closeouts(self.root, "HEAD")
        issue_mock.assert_not_called()

        open_issue = {
            "number": 7,
            "url": "https://github.com/owner/control/issues/7",
            "state": "OPEN",
            "stateReason": None,
            "labels": [{"name": "status:in-review"}],
        }
        with (
            mock.patch.object(GATE, "pending_records", return_value=[record]),
            mock.patch.object(GATE, "read_evidence", return_value=target),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "ref_contains_file", return_value=True),
            mock.patch.object(GATE, "issue_metadata", return_value=open_issue),
        ):
            with self.assertRaisesRegex(GATE.GateError, "Issue must be CLOSED"):
                GATE.validate_pending_closeouts(self.root, "HEAD")

    def test_acknowledge_v2_final_closeout_requires_completed_issue(self) -> None:
        evidence = GATE.parse_evidence_text(
            PurePosixPath("docs/works/work.md"),
            self.v2_evidence_text(
                work_status="complete",
                ticket_completion="complete",
                pr_url="https://github.com/owner/blog/pull/42",
                closeout_status="complete",
                merged_pr_url="https://github.com/owner/blog/pull/42",
                merge_commit="c" * 40,
                kb_paths="docs/kb/features/GH-7-example.md",
                closeout_completed_at="2026-08-24T12:00:00Z",
            ),
        )
        record = GATE.PendingCloseout(
            section=GATE.closeout_section("owner/blog", 42),
            repo="owner/blog",
            pr=42,
            evidence="docs/works/work.md",
        )
        open_issue = {
            "number": 7,
            "url": "https://github.com/owner/control/issues/7",
            "state": "OPEN",
            "stateReason": None,
            "labels": [{"name": "status:in-review"}],
        }
        completed_issue = {
            "number": 7,
            "url": "https://github.com/owner/control/issues/7",
            "state": "CLOSED",
            "stateReason": "COMPLETED",
            "labels": [],
        }

        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "pending_records", return_value=[record]),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(GATE, "issue_metadata", return_value=open_issue),
            mock.patch.object(GATE, "git") as git_mock,
        ):
            with self.assertRaisesRegex(GATE.GateError, "Issue must be CLOSED"):
                GATE.acknowledge_closeout(self.root, "owner/blog", 42)
        git_mock.assert_not_called()

        with (
            mock.patch.object(GATE, "refresh_origin_main"),
            mock.patch.object(GATE, "pending_records", return_value=[record]),
            mock.patch.object(GATE, "read_evidence", return_value=evidence),
            mock.patch.object(GATE, "validate_closeout"),
            mock.patch.object(GATE, "issue_metadata", return_value=completed_issue),
            mock.patch.object(GATE, "git") as git_mock,
        ):
            GATE.acknowledge_closeout(self.root, "owner/blog", 42)
        git_mock.assert_called_once_with(
            self.root,
            "config",
            "--local",
            "--remove-section",
            record.section,
        )


if __name__ == "__main__":
    unittest.main()
