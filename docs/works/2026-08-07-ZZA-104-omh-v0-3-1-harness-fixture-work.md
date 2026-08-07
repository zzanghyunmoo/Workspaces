---
workflow_schema: compound-work/v1
ticket_id: ZZA-104
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-104
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/oh-my-harness/pull/44
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
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/44
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url:
closed_at:
---

# ZZA-104 OMH v0.3.1 하네스 픽스처 릴리스 CI 작업 기록

## 작업 목표

v0.3.1 릴리스 CI가 이전 0.3.0 테스트 픽스처와 충돌해 실패하는 문제를 해소한다.

## 주요 변경 지점

- `oh-my-harness/tests/harness/install.test.mjs`: managed harness registration path와 정상 Claude/OpenCode plugin fixture를 현재 package identity `0.3.1`로 맞춘다.
- `oh-my-harness/tests/harness/omh-cli.test.mjs`: root `omh` launcher의 release-version assertion을 `0.3.1`로 맞춘다.

## 검증

- PASS: `npm run test:harness` — 76 passed, 13 Windows/POSIX fixture skipped, 0 failed.
- PASS: `npm run package:verify` — 36 passed, 0 failed.
- CI root cause: release run `31137160354`가 source/catalog/package contract 단계에서 위 세 legacy fixture 때문에 실패했으며, artifact publication 전에 중단됐다.

## 외부 동기화

ZZA-104는 In Review를 유지한다. PR #44 merge, immutable v0.3.1 artifact publication, MDS lock 및 Windows apply 증명이 모두 끝난 뒤 Done으로 전환한다.

## Merge closeout

Merge 후 release URL, MDS lock follow-up, Windows validation, KB 및 Notion closeout을 기록한다.
