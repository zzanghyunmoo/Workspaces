---
workflow_schema: compound-work/v1
ticket_id: ZZA-104
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-104
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/my-desk-setup/pull/7
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: Existing installation blocker and explicit runtime-ownership decision were sufficiently bounded.
plan_status: complete
plan_path: docs/plans/2026-08-06-ZZA-104-runtime-ownership-plan.md
plan_notion_url: https://app.notion.com/p/3b3ef22ad4fc8130b011e4567db4d0ab?pvs=204
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/41
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url:
closed_at:
---

# ZZA-104 OMH v0.3.1 immutable release 작업 기록

## 작업 목표

MDS runtime identity 합성 검증이 포함된 OMH main을 immutable v0.3.1 artifact로 발행해, MDS가 실제 Windows 설치에 사용할 수 있는 정확한 archive와 provenance를 제공한다.

## 주요 변경 지점

- `oh-my-harness/package.json`, `npm-shrinkwrap.json`: 배포 package identity를 `0.3.1`로 갱신한다.
- `oh-my-harness/harness/catalog/release.json`: plugin tree digest와 immutable archive/tag/compatibility 계약을 `v0.3.1`에 결합한다.
- `oh-my-harness/plugins/oh-my-harness/`: Claude/Codex plugin과 MCP server의 노출 버전을 package identity와 일치시킨다.
- `oh-my-harness/tests/release/`, `tests/unit/`: release artifact와 native registration fixture의 version contract를 검증한다.

## 검증

- PASS: `npm run typecheck`.
- PASS: `npm run package:verify` (36 tests).
- PASS: PR #41 code/doc review marker가 head `68743254fabce87a2dce18c42572647e0df09611`에 게시됐다.
- 대기: merge 이후 immutable release workflow가 만든 archive/sidecar SHA-256을 MDS lock에 반영하고 Windows에서 apply를 검증한다.

## 외부 동기화

Linear ZZA-104는 In Review를 유지한다. Notion ticket 및 기능 현황 페이지에는 선행 OMH/MDS 구현 병합과 다음 immutable release 단계가 기록되어 있다.

## Merge closeout

Merge 후 release URL, tag commit, MDS follow-up PR, KB 및 Notion closeout을 기록한다.
