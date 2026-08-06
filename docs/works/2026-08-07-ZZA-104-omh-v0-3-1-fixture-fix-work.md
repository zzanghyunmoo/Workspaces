---
workflow_schema: compound-work/v1
ticket_id: ZZA-104
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-104
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/oh-my-harness/pull/43
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: This is a focused release-blocker remediation with a runtime-confirmed cause.
plan_status: complete
plan_path: docs/plans/2026-08-06-ZZA-104-runtime-ownership-plan.md
plan_notion_url: https://app.notion.com/p/3b3ef22ad4fc8130b011e4567db4d0ab?pvs=204
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/43
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url:
closed_at:
---

# ZZA-104 OMH v0.3.1 native fixture 정합성 작업 기록

## 작업 목표

v0.3.1 immutable release의 clean CI에서 native registration fixture가 이전 plugin version을 보고 충돌하는 문제를 제거한다.

## 주요 변경 지점

- `oh-my-harness/tests/integration/omh-cli.test.ts`: native plugin fixture의 초기값과 collision test 뒤 복원값을 package identity `0.3.1`에 맞춘다.

## 검증

- PASS: clean `npm ci --ignore-scripts` 후 `node --test --test-name-pattern 'U13 CLI closes preview' tests/integration/omh-cli.test.ts` (7 passed).
- PASS: mds-host Claude native registration, recovery, status가 end-to-end로 `ready`에 수렴했다.
- 대기: PR #43 merge 후 tag의 immutable release workflow가 전체 clean CI와 artifact/sidecar publication을 완료한다.

## 외부 동기화

ZZA-104는 In Review를 유지한다. artifact와 MDS lock 및 Windows apply 증명이 모두 끝난 뒤 Done으로 전환한다.

## Merge closeout

Merge 후 release URL, MDS lock follow-up, Windows validation, KB 및 Notion closeout을 기록한다.
