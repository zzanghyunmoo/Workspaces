---
workflow_schema: compound-work/v1
ticket_id: ZZA-104
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-104
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/oh-my-harness/pull/42
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: This is a narrowly scoped remediation for a verified release-trigger failure.
plan_status: complete
plan_path: docs/plans/2026-08-06-ZZA-104-runtime-ownership-plan.md
plan_notion_url: https://app.notion.com/p/3b3ef22ad4fc8130b011e4567db4d0ab?pvs=204
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/42
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url:
closed_at:
---

# ZZA-104 OMH immutable release dispatch 작업 기록

## 작업 목표

tag push event가 현재 인증 경로에서 GitHub Actions를 시작하지 못해도, 같은 tag ref를 명시 실행하여 immutable archive/sidecar를 발행할 수 있게 한다.

## 주요 변경 지점

- `oh-my-harness/.github/workflows/release.yml`: `workflow_dispatch` trigger를 추가하되 기존 tag, main ancestor, merged-PR identity 검증은 변경하지 않는다.
- `oh-my-harness/tests/release/package-contents.test.ts`: release workflow contract에 수동 실행 trigger를 고정한다.

## 검증

- PASS: `npm run package:verify` (36 tests).
- PASS: tag `v0.3.1`이 main merge commit `273b4c16c8a50e41580d5ac13baa7627bea562d4`를 가리키며, 자동 push event가 60초 동안 workflow를 만들지 않는 현상을 확인했다.
- 대기: PR #42 merge 후 workflow dispatch로 tag ref를 실행해 archive/sidecar와 GitHub Release를 검증한다.

## 외부 동기화

ZZA-104는 In Review를 유지한다. immutable release 및 MDS lock 갱신이 완료되기 전에는 Done으로 전환하지 않는다.

## Merge closeout

Merge 후 manual dispatch run URL, release URL, MDS lock follow-up, KB 및 Notion closeout을 기록한다.
