---
workflow_schema: compound-work/v1
ticket_id: ZZA-71
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-71/oh-my-harness-u2-neutral-contracts-and-personal-profile
ticket_status: In Progress
ticket_completion: pending
remaining_prs:
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: parent ZZA-70 plan이 U2 목표·의존성·범위를 이미 고정했고 사용자가 U2 단독 LFG 실행을 지시해 별도 아이디에이션을 반복하지 않음
plan_status: complete
plan_path: docs/plans/2026-07-16-ZZA-71-u2-neutral-contracts-plan.md
plan_notion_url: https://www.notion.so/39fef22ad4fc819690eec79654ddff53
plan_waiver_reason:
work_status: in_progress
work_notion_url: https://www.notion.so/39fef22ad4fc81ee9a61d2f9adb52ee7
pr_url:
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url: https://www.notion.so/39eef22ad4fc819db113ce1029c899a4
notion_ticket_url: https://www.notion.so/39fef22ad4fc81ee9a61d2f9adb52ee7
closed_at:
---

# ZZA-71 U2 neutral contracts 작업 기록

## 작업 목표

네 coding-agent runtime이 공유할 declarative Product Contract와 personal profile을 정의하고,
terminal status, evidence identity, capability/safety/readiness와 stable cross-reference를
runtime-neutral JSON contract로 고정한다.

## 주요 변경 지점

- `harness/contracts/`: harness profile, feature contract, runtime adapter와 conformance result
  schema를 닫힌 draft 2020-12 계약으로 추가할 예정이다.
- `harness/profiles/personal-v1.profile.json`: U1 source identity, Linux x64/Darwin arm64 lane,
  네 runtime exact version과 Pi companion 기대치를 선언할 예정이다.
- `tests/harness/contracts.test.mjs`: valid/invalid schema fixture, fail-closed pass accounting,
  stable cross-reference, evidence identity sensitivity와 secret-free 검증을 추가할 예정이다.
- U3 descriptor instance, U16 feasibility와 runtime 실행 코드는 범위에서 제외한다.

## 검증

- 구현 전 상태: implementation-ready local/Notion plan과 ZZA-71 ticket 생성·동기화 완료.
- 계획된 검증: `npm run test:harness`, canonical U1 verify, `npm run profile:verify`,
  `npm run test:workspace-connectors`, `git diff --check`.
- 브라우저 검증은 JSON contract와 Node test만 변경하므로 대상 route가 없다.
- 실제 구현 검증 결과와 미실행 항목은 work 완료 시 갱신한다.

## 외부 동기화

- Linear ZZA-71: `In Progress`.
- Canonical Notion plan: <https://app.notion.com/p/39fef22ad4fc819690eec79654ddff53>
- Canonical Notion ticket: <https://app.notion.com/p/39fef22ad4fc81ee9a61d2f9adb52ee7>
- Parent ZZA-70은 U2-U18이 남아 있어 `In Review`를 유지한다.

## Merge closeout

구현과 PR 생성 전이므로 closeout은 pending이다. Merge 뒤 U2 contract 상태를 KB와 Notion
기능 현황·티켓 문서에 반영하고, 후속 U3-U18 때문에 ZZA-71 completion 정책과 parent
ZZA-70 `In Review` 상태를 함께 정리한다.
