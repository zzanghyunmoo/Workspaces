---
workflow_schema: compound-work/v1
ticket_id: ZZA-104
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-104
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/oh-my-harness/pull/45
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: "PR #44 이후 immutable tag를 보존해야 하는 좁은 release-blocker 후속이므로 별도 ideation을 생략함"
plan_status: complete
plan_path: docs/plans/2026-08-06-ZZA-104-runtime-ownership-plan.md
plan_notion_url: https://app.notion.com/p/3b3ef22ad4fc8130b011e4567db4d0ab?pvs=204
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/45
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

- `package.json`, `npm-shrinkwrap.json`, native plugin manifest와 marketplace version을
  `0.3.2`로 일치시켰다.
- `harness/catalog/release.json`의 archive, sidecar, tag, compatibility를 `v0.3.2`에
  결합하고 runtime plugin bytes의 SHA-256 digest를
  `de31d918a4320eb56f791d53b87dbc64666e6e6f8c539877420fb3b905a2248b`로 갱신했다.
- release, native registration, integration 및 harness fixture의 package identity를
  같은 version으로 동기화했다.
- `src/environment/native-registration.ts#claudeManagedPluginVersion`과
  `ClaudeManagedNativeRegistration`: bounded regular manifest에서 root별 exact version을 읽고,
  current root에는 `0.3.2`, receipt-owned predecessor에는 검증된 `0.3.1` identity를 결합한다.
- `src/environment/orchestrator.ts#claudeNativeRegistration`: root-specific version 계약을 CLI
  preflight, action 실행, native recovery capture, rollback, doctor에 동일하게 전달한다.
- `src/environment/orchestrator.ts#exactReceiptManagedPayloadIdentity`: receipt-owned predecessor를 단일
  managed runtime/package ownership, state-root 내부 경로, 존재하는 directory와 전체 receipt
  digest에 결합한다. preflight·action 실행·rollback 직전에 identity를 다시 확인해 use-time
  drift를 fail-closed한다.
- `src/environment/orchestrator.ts#receiptManagedPayloadDisposition`: receipt payload를
  `current | previous | invalid | unmanaged`로 구분해 exact current `--clean` 재실행은 허용하고
  손상된 predecessor만 차단한다.
- `planActions`, `prepareActionRollback`, `rollbackNativeRegistration`: predecessor digest를
  plan과 recovery journal에 캡처한다. 재시작 전에 payload와 receipt digest가 함께 바뀌어도
  캡처 digest와 다르면 interrupted recovery를 fail-closed한다.
- Claude·Codex predecessor recovery journal은 root와 digest를 필수 쌍으로 요구하고,
  digest가 없는 구형 previous-recovery record는 native mutation 전에 거부한다.
- OpenCode previous recovery에도 root·digest identity를 기록한다. rollback은 캡처한
  predecessor를 먼저 재검증한 뒤에만 config snapshot을 복원하므로, drift가 있으면 현재
  config와 pending recovery를 그대로 보존한다.
- `src/environment/native-registration.ts#ClaudeManagedNativeRegistration`: predecessor root와
  expected version이 함께 존재하거나 함께 부재하도록 union type으로 계약을 강화했다.
- `tests/integration/omh-cli.test.ts`: 실제 receipt-owned `0.3.1` payload의 clean preview와
  apply가 `0.3.2` native registration으로 수렴하는 시나리오와, 그 뒤 후속 Codex 필수
  action 실패 시 이전 root·`0.3.1`·receipt를 복원하고 recovery queue를 비우는 실제
  orchestrator/journal rollback 시나리오를 검증한다. predecessor가 state root 밖에 있으면
  mutation 전에 차단하고, recovery capture 이후 bytes가 바뀌면 rollback을 중단해 journal을
  보존한 뒤 다음 실행에서 exact prior payload로 복구하는 경계도 검증한다. payload와 receipt
  digest를 함께 바꾼 재시작도 캡처 digest 불일치로 거부한다. prepare와 execute 사이의
  microtask drift, digest 없는 legacy previous-recovery, OpenCode predecessor drift도 각각
  mutation 또는 config snapshot 복원 전에 거부하며 exact payload 복구 후 재시도가 수렴한다.
- `tests/integration/environment-runtime-expansion.test.ts`: exact current receipt payload의 clean
  preview가 idempotent하게 plan을 만들고 predecessor identity를 전달하지 않는지 검증한다.
- `tests/unit/native-registration.test.ts`: `0.3.1 → 0.3.2`와 역방향 복구를 검증하고,
  exact predecessor bytes라도 reported version이 `9.9.9`이면 mutation 전에 거부한다.

## 검증

- PASS: `npm run typecheck`, `npm run build`, `git diff --check origin/main...HEAD`.
- PASS: `npm run catalog:verify` — 26 passed, 0 failed.
- PASS: `npm run test:unit` — 61 passed, 0 failed.
- PASS: `npm run test:contracts` — 26 passed, 0 failed.
- PASS: `npm run test:integration` — 102 passed, 0 failed.
- PASS: `npm run test:runtime:claude` — 8 passed, 0 failed.
- PASS: `npm run test:runtime:opencode` — 13 passed, 0 failed.
- PASS: `npm run test:runtime:codex` — 10 passed, 0 failed.
- PASS: `npm run test:harness` — 86 passed, 3 platform fixture skipped, 0 failed.
- PASS: `npm run package:verify` — 36 passed, 0 failed.
- PASS: code/doc review finding을 반영한 최신 branch head
  `d0016e362f2aa1bd2ddefc97f48925f569a005cd`에서 위 canonical gate 전체를 재실행했다.
- PASS: 최신 head 독립 correctness/security와 testing/adversarial 재리뷰에서 actionable
  P0/P1/P2/P3 0건을 확인했다. `ce-doc-review`도 legacy recovery, OpenCode snapshot 순서,
  검증 수치와 merge/tag 후속 경계가 코드·release workflow와 일치해 actionable 0건으로
  통과했다. Code review artifact는
  `/tmp/compound-engineering/ce-code-review/20260807-165211-v032-final/`에 있다.
- 최초 package gate는 release source materialization이 미커밋 working tree가 아니라 Git
  object를 사용해 이전 `0.3.1` archive를 만든다는 계약 때문에 1건 실패했다. 변경을
  branch commit `ddd9316525e6e6eee941434c1f7d369bf589e26b`에 고정한 뒤 같은 gate가
  36/36으로 통과해 source identity 경계를 확인했다.
- `ce-code-review`가 이전 root fixture를 이미 `0.3.2`로 둬 실제 `0.3.1 → 0.3.2`
  Claude managed upgrade 충돌을 숨기는 P1을 발견했고, 독립 validator가 확인했다. 소유권을
  exact previous-root bytes에 결합하는 1차 수정 뒤에도 CLI preflight와 rollback이 전역
  `HARNESS_VERSION`을 요구하는 P1이 남아 있음을 최신-head 재리뷰와 독립 validator가 다시
  확인했다. root-specific version 계약과 실제 orchestrator 전환 회귀 테스트를 적용한 뒤
  전체 gate를 재통과했다.
- 다음 최신-head testing/adversarial 리뷰에서 실제 transaction rollback lifecycle 증명이
  저수준 역방향 등록 테스트에만 머문 P2를 확인했다. Claude upgrade 뒤 Codex action 실패를
  주입해 prior root/version/receipt 복원과 journal recovery 정리를 검증한 뒤 전체 gate를
  최신 head에서 다시 통과했다.
- work evidence security review에서 receipt가 가리키는 predecessor의 state-root containment와
  digest가 실제 사용 시점까지 결합되지 않은 P2를 확인했다. predecessor resolver에 exact
  ownership/path/digest 검증을 추가하고 실행·rollback 직전 다시 확인하도록 보강했으며,
  state-root escape와 post-capture drift 회귀 테스트를 포함해 전체 gate를 재통과했다.
- 최신-head correctness 리뷰에서 exact current payload와 invalid predecessor가 같은 `null`로
  합쳐져 정상 same-version `--clean` 재실행을 막는 P1을 발견했다. disposition을 분리하고
  current-payload idempotence 회귀 테스트를 추가했다. testing/adversarial 리뷰가 interrupted
  recovery가 캡처 digest를 보존하지 않는 P2를 추가로 확인해 plan/journal digest 결합과
  payload+receipt 동시 drift 재현을 보강했다. maintainability 리뷰의 predecessor optional-field
  상관관계도 union type으로 닫은 뒤 최신 head에서 전체 gate를 다시 통과했다.
- 후속 최신-head correctness 리뷰는 OpenCode recovery가 config snapshot을 먼저 복원한 뒤
  predecessor를 확인하는 P2를, testing/adversarial 리뷰는 prepare와 execute 사이 drift를
  직접 실행 경로에서 증명하지 않은 P2를, document review는 digest 없는 legacy
  previous-recovery가 허용되는 계약 공백을 각각 확인했다. 모든 runtime의 predecessor
  root·digest를 recovery precondition으로 통일하고 OpenCode snapshot 복원 순서를 바꿨으며,
  세 경계를 재현하는 회귀 테스트를 추가한 뒤 최신 head에서 전체 gate를 재통과했다.
- 미실행: 실제 `v0.3.2` GitHub Release publication, MDS catalog lock과 Windows apply는
  PR merge 이후 후속 검증이다.

## 외부 동기화

- Linear ZZA-104를 `In Progress`로 전환하고 v0.3.2 release 후속 시작 댓글을 남긴 뒤,
  PR #45 생성과 함께 `In Review`로 전환하고 검증 결과 댓글을 추가했다.
- Canonical Notion 티켓에 immutable tag 보존, target version, PR #45, 전체 검증 결과와
  merge 이후 후속 경계를 기록했다.
- PR: https://github.com/zzanghyunmoo/oh-my-harness/pull/45

## Merge closeout

PR merge 전에는 pending이며 `remaining_prs`는 현재 미병합 PR #45를 가리킨다. Guarded
merge 완료 뒤 GitHub가 반환한 PR #45 squash merge commit SHA를 먼저 기록하고,
`v0.3.2` tag는 그 merge commit에 한 번만 생성·push한다. 이어 release workflow를 해당 tag
ref로 실행해 archive·sidecar·source identity와 GitHub Release를 검증한다. 이 검증 전에는
MDS catalog lock을 갱신하지 않는다. Release publication 뒤 MDS lock/Windows apply 후속 PR을
생성해 `remaining_prs`를 그 URL로 교체하고, release URL, KB, Notion 기능 현황·티켓과
Linear 상태를 갱신한다.
