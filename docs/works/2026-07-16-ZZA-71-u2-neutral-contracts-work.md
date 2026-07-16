---
workflow_schema: compound-work/v1
ticket_id: ZZA-71
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-71/oh-my-harness-u2-neutral-contracts-and-personal-profile
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/oh-my-harness/pull/23
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: parent ZZA-70 plan이 U2 목표·의존성·범위를 이미 고정했고 사용자가 U2 단독 LFG 실행을 지시해 별도 아이디에이션을 반복하지 않음
plan_status: complete
plan_path: docs/plans/2026-07-16-ZZA-71-u2-neutral-contracts-plan.md
plan_notion_url: https://www.notion.so/39fef22ad4fc819690eec79654ddff53
plan_waiver_reason:
work_status: complete
work_notion_url: https://www.notion.so/39fef22ad4fc81ee9a61d2f9adb52ee7
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/23
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

- `harness/contracts/harness-profile.schema.json`: U1 source identity, contract ref, ownership,
  platform/runtime/companion과 hermetic/personal/hosted tier를 닫힌 draft 2020-12 shape로 정의했다.
- `harness/contracts/feature-contract.schema.json`: workflow artifact/step/handoff, required·optional
  capability readiness, safety class, approval boundary, 7개 scenario kind와 oracle을 분리했다.
- `harness/contracts/runtime-adapter.schema.json`: U3가 채울 immutable executable/acquisition
  tuple, native lifecycle, pre-model gate와 structured headless evidence shape를 정의했다.
- `harness/contracts/conformance-result.schema.json`: 8개 evidence digest와 tier-local terminal
  status를 정의하고 `passed` 이외 상태의 `countsAsPass: true`를 schema conditional로 막았다.
- `harness/profiles/personal-v1.profile.json`: upstream/harness/project/runtime/user ownership,
  Linux x64/Darwin arm64 lane, 네 runtime exact version과 Pi companion 기대치를 고정했다.
- `tests/harness/contracts.test.mjs`: bounded schema evaluator, valid/invalid fixture, stable
  cross-reference, evidence identity sensitivity, closed shape와 secret-free 검증을 추가했다.
- U3 descriptor instance, U16 feasibility와 runtime 실행 코드는 범위에서 제외했다.

## 검증

- `npm run test:harness`: PASS, 21/21(U2 6개와 U1 15개).
- `npm run harness:upstream:verify -- --source /tmp/oh-my-harness-ce-3.19.0`: PASS,
  pinned commit의 29개 skill과 committed lock/inventory가 일치했다.
- `npm run profile:verify`: PASS, 기존 Pi distribution profile 4개가 deterministic·secret-free다.
- `npm run test:workspace-connectors`: PASS, 31/31.
- `node --check tests/harness/contracts.test.mjs`와 `git diff --check`: PASS.
- LSP primary check는 두 차례 timeout되어 확정 진단을 받지 못했고 Node syntax check와 전체
  harness test로 보완했다. 별도 Python `jsonschema` 검증은 module 미설치로 미실행이며,
  committed test-local evaluator가 실제 사용 keyword의 positive/negative fixture를 검증한다.
- 브라우저 검증은 JSON contract와 Node test만 변경하므로 대상 route가 없다.

## 외부 동기화

- Linear ZZA-71: `In Review`.
- PR #23: <https://github.com/zzanghyunmoo/oh-my-harness/pull/23>
- Canonical Notion plan: <https://app.notion.com/p/39fef22ad4fc819690eec79654ddff53>
- Canonical Notion ticket: <https://app.notion.com/p/39fef22ad4fc81ee9a61d2f9adb52ee7>
- Parent ZZA-70은 U2-U18이 남아 있어 `In Review`를 유지한다.

## Merge closeout

PR #23이 open 상태이므로 closeout은 pending이다. Merge 뒤 U2 contract 상태를 KB와
Notion 기능 현황·티켓 문서에 반영하고, ZZA-71을 `Done`으로 전환한다. Parent ZZA-70은
후속 U3-U18 때문에 `In Review`를 유지한다.
