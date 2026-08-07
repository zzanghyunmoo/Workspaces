---
workflow_schema: compound-work/v1
ticket_id: ZZA-104
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-104
ticket_status: In Progress
ticket_completion: pending
remaining_prs:
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: "PR #44 이후 immutable tag를 보존하며 새 patch release identity를 만드는 범위가 기존 ZZA-104 계획 U4에 이미 확정됨"
plan_status: complete
plan_path: docs/plans/2026-08-06-ZZA-104-runtime-ownership-plan.md
plan_notion_url: https://app.notion.com/p/3b3ef22ad4fc8130b011e4567db4d0ab?pvs=204
plan_waiver_reason:
work_status: in_progress
work_notion_url: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
pr_url:
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url:
closed_at:
---

# ZZA-104 OMH v0.3.2 immutable release 작업 기록

## 작업 목표

PR #44의 하네스 픽스처 수정을 포함하는 새 immutable OMH `v0.3.2` release identity를
준비한다. 기존 `v0.3.1` tag는 이동하거나 덮어쓰지 않는다.

## 주요 변경 지점

- 예정: package, native plugin manifest, MCP server와 marketplace version을 `0.3.2`로
  일치시킨다.
- 예정: release catalog의 archive, sidecar, tag, compatibility와 runtime plugin digest를
  새 identity에 결합한다.
- 예정: release, native registration, integration 및 harness fixture를 같은 version으로
  동기화한다.

## 검증

- 예정: `npm run typecheck`, `npm run build`, `npm run test:unit`,
  `npm run test:contracts`, `npm run test:integration`, `npm run test:harness`,
  `npm run package:verify`, `git diff --check`.
- 실제 GitHub Release publication과 MDS lock/Windows apply는 PR merge 이후 후속 검증이다.

## 외부 동기화

- Linear ZZA-104를 `In Progress`로 전환하고 v0.3.2 release 후속 시작 댓글을 남겼다.
- Canonical Notion 티켓에 immutable tag 보존, target version과 후속 경계를 기록했다.

## Merge closeout

PR merge 전에는 pending이다. Merge 뒤 release URL, KB, Notion 기능 현황·티켓,
MDS lock 후속과 Linear 상태를 갱신한다.
