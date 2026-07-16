---
workflow_schema: compound-work/v1
ticket_id: ZZA-71
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-71/oh-my-harness-u2-neutral-contracts-and-personal-profile
ticket_status: Done
ticket_completion: complete
remaining_prs:
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
closeout_status: complete
merged_pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/23
merge_commit: 32e73af3636bf79e0b2d47dcd4b7ce0cdf9b8c5f
kb_paths: docs/kb/architecture/2026-07-16-ZZA-71-runtime-neutral-harness-contracts.md
notion_feature_status_url: https://www.notion.so/39eef22ad4fc819db113ce1029c899a4
notion_ticket_url: https://www.notion.so/39fef22ad4fc81ee9a61d2f9adb52ee7
closed_at: 2026-07-16T09:32:06Z
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
- `npx --yes ajv-cli@5.0.0 compile --spec=draft2020 --strict=true`: PASS, schema 4개 모두
  strict compile되며 `personal-v1.profile.json`도 Ajv validation을 통과했다. 첫 compile에서
  conditional의 strict-required 경고를 발견해 branch property 선언을 보강한 뒤 재검증했다.
- LSP primary check는 두 차례 timeout되어 확정 진단을 받지 못했고 Node syntax check, Ajv
  strict compile과 전체 harness test로 보완했다.
- 브라우저 검증은 JSON contract와 Node test만 변경하므로 대상 route가 없다.

## 외부 동기화

- Linear ZZA-71: `Done`.
- PR #23: merge commit `32e73af3636bf79e0b2d47dcd4b7ce0cdf9b8c5f`.
- Canonical Notion plan: <https://app.notion.com/p/39fef22ad4fc819690eec79654ddff53>
- Canonical Notion ticket: merge 결과, review gate와 KB 경로 동기화 완료.
  <https://app.notion.com/p/39fef22ad4fc81ee9a61d2f9adb52ee7>
- Canonical Notion 기능 현황: U1-U2 완료와 U3 다음 단계 동기화 완료.
  <https://app.notion.com/p/39eef22ad4fc819db113ce1029c899a4>
- Parent ZZA-70은 U3-U18이 남아 있어 `In Review`를 유지한다.

## Merge closeout

PR #23은 guarded squash merge로 완료되었다. Merge commit은
`32e73af3636bf79e0b2d47dcd4b7ce0cdf9b8c5f`이며 현재 기능 상태·운영 경계·검증 결과는
`docs/kb/architecture/2026-07-16-ZZA-71-runtime-neutral-harness-contracts.md`에 정리했다.
Notion 기능 현황과 ticket 결과 문서도 동기화했고 ZZA-71을 `Done`으로 전환했다. Parent
ZZA-70만 후속 단위 때문에 `In Review`로 남는다.
