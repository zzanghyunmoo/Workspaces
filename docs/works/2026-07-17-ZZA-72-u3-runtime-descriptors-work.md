---
workflow_schema: compound-work/v1
ticket_id: ZZA-72
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-72/oh-my-harness-u3-runtime-descriptors-and-116-expected-cell-keys
ticket_status: In Review
ticket_completion: pending
remaining_prs:
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: parent ZZA-70 plan과 requirements가 U3 목표·의존성·범위를 이미 고정했고 사용자가 U3/U16 LFG 실행을 지시해 별도 아이디에이션을 반복하지 않음
plan_status: complete
plan_path: docs/plans/2026-07-17-ZZA-72-u3-runtime-descriptors-plan.md
plan_notion_url: https://www.notion.so/3a0ef22ad4fc814c8317f8bd0ba610ed
plan_waiver_reason:
work_status: complete
work_notion_url: https://www.notion.so/3a0ef22ad4fc8158b130fbcc5c09ad3d
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/24
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url: https://www.notion.so/3a0ef22ad4fc8158b130fbcc5c09ad3d
closed_at:
---

# ZZA-72 U3 runtime descriptors 작업 기록

## 작업 목표

네 coding-agent runtime의 immutable Linux x64/Darwin arm64 descriptor와 source-backed native
candidate를 확정하고, U1 inventory 29개 × runtime 4개의 canonical expected key 116개를
하나의 neutral resolver에서 생성·검증한다. Runtime 실행과 readiness proof는 ZZA-73/U16에
남긴다.

## 주요 변경 지점

- `harness/contracts/runtime-adapter.schema.json`: contract를 `1.1.0`으로 migration하고 GitHub
  release owner/repository/tag/asset, provider digest, normalized archive member, runtime variant,
  typed action token, exact pre-model surface/source/configuration/status를 closed shape로 고정했다.
- `harness/adapters/{codex,opencode,claude-code,pi}.json`: 네 runtime의 exact version, 두 platform
  archive/executable SHA-256, native lifecycle candidate와 headless protocol을 선언했다. OpenCode
  gate는 행동 증명 전 `candidate-deny-unproven`으로 유지한다.
- `scripts/harness/acquisition.mjs`: `tar-stream@3.2.0`/`yauzl@3.4.0` 기반 streaming archive
  inspection, GitHub redirect/identity 검증, normalized path/type/mode/size/ratio 제한과 executable
  digest derivation을 구현했다. Exact artifact 관찰 결과 Codex Linux member는 298,553,392 bytes,
  Pi Linux archive는 243 entries였으므로 selected-member/entry cap만 각각 384 MiB/256으로
  상향했고 compressed 256 MiB, total 512 MiB, 100:1 한도는 유지했다.
- `scripts/harness/schema.mjs`, `tests/harness/contracts.test.mjs`: U2 test 내부 bounded schema
  evaluator를 shared module로 추출하고 adapter 1.0 legacy rejection과 1.1 parity를 검증한다.
- `harness/evidence/reviewed-runtime-evidence.json`, `scripts/harness/descriptors.mjs`: reviewed
  release/gate 사실과 descriptor canonical digest를 고정하고 U1 lock/inventory, U2 profile,
  schema와 네 descriptor를 exact compare한다. Adapter directory exact-set, 8 tuple, production-only
  29×4 planner와 `<feature-id>::<runtime-id>` 116-key canonical result를 fail-closed로 반환한다.
- `tests/harness/descriptor.test.mjs`, `descriptor-coverage.test.mjs`: exact tuple, hostile string,
  membership/order/cardinality drift와 deterministic read-only verification을 다룬다.
- `package.json`, `package-lock.json`, `scripts/harness/canonical.mjs`: descriptor verify script,
  exact dev dependencies와 shared secret-free traversal을 연결했다.

## 검증

- Proof-first 과정에서 미완성 schema/descriptor resolver에 대한 targeted harness tests가 실패하는
  것을 관찰한 뒤 production contract/helper를 구현했다. 구현 중 Pi companion drift 검출로
  실패한 semantic test도 수정 후 재실행했다.
- Exact GitHub release archive 8개를 임시 경로에서 다운로드하고 계획의 archive SHA-256을
  검증한 뒤 member/executable digest를 재현했다. 다운로드 artifact는 branch에 남기지 않았다.
- 독립 code review 3개에서 reviewed evidence 미사용, non-116 public planner 허용, redirect
  identity/query 검증, TAR aggregate ratio와 adapter/profile duplicate 경계를 발견했다. 모든 P1/P2를
  수정하고 valid one-field drift, archive bomb, redirect, extra adapter와 duplicate platform test를
  보강했다.
- `npm run test:harness`: PASS, 29/29.
- `npm run harness:descriptors:verify`: PASS — descriptors 4, tuples 8, expectedKeys 116,
  canonical SHA-256 `d3b16d9a99fa19e30f6649c45a71c0bca8312d10acf02e58f629f1f9cdcab0a5`.
- `npm run harness:upstream:verify -- --source <canonical CE checkout>`: PASS, 29 skills at
  `1756c0b9f3cf94493f287ea29ae766ad668fb7cf`.
- `npm run profile:verify`: PASS, profiles 4개와 profile lock deterministic/secret-free.
- `npm run test:workspace-connectors`: PASS, 31/31.
- `npm pack --dry-run`: PASS, 89 files/약 260 kB package로 기존 Pi extension ordering을 보존했다.
- `lsp_diagnostics`: 변경 JS/test 5개 진단 0건.
- `lens_diagnostics mode=all`: 변경 파일 blocking 진단 0건. Full scan의 기존
  `tests/harness/inventory.test.mjs` private-key fixture gitleaks 경고는 이 diff가 수정하지 않은
  intentional hostile fixture다.
- `git diff --check`: PASS.
- Browser 검증은 JSON contract와 Node helper/test 변경으로 route/UI가 없어 대상이 아니다.
- PR CI와 최신-head review marker는 commit/push 후 outer LFG 단계에서 수행한다.

## 외부 동기화

- Linear ZZA-72: PR #24 생성 후 `In Review`.
- Canonical Notion plan: <https://app.notion.com/p/3a0ef22ad4fc814c8317f8bd0ba610ed>
- Canonical Notion ticket: <https://app.notion.com/p/3a0ef22ad4fc8158b130fbcc5c09ad3d>
- Local plan은 exact artifact 관찰에 따른 384 MiB selected-member/256 entry 한도와 동일하게
  동기화했다.

## Merge closeout

PR merge 후 KB, 기능 현황, Notion ticket 결과, merge commit과 Linear 상태를 기록한다.
