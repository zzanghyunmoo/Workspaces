---
workflow_schema: compound-work/v1
ticket_id: ZZA-73
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-73/oh-my-harness-u16-exact-baseline-native-gate-and-isolation-feasibility
ticket_status: In Progress
ticket_completion: pending
remaining_prs: U16 implementation PR not opened; existential substrate and implementation blockers remain
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: parent ZZA-70 plan이 U16 목표·의존성·범위를 이미 고정했고 사용자가 U3/U16 LFG 실행을 지시해 별도 아이디에이션을 반복하지 않음
plan_status: complete
plan_path: docs/plans/2026-07-17-ZZA-73-u16-runtime-feasibility-plan.md
plan_notion_url: https://www.notion.so/3a0ef22ad4fc8134a54af0e4716c28e9
plan_waiver_reason:
work_status: in_progress
work_notion_url: https://www.notion.so/3a0ef22ad4fc81b7b576c2914a5bec3b
pr_url:
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url: https://www.notion.so/3a0ef22ad4fc81b7b576c2914a5bec3b
closed_at:
---

# ZZA-73 U16 exact runtime feasibility 작업 기록

## 작업 목표

ZZA-72의 exact descriptor/resolver를 입력으로 8개 runtime/platform tuple과 Linux OCI,
Darwin Tart backend의 native pre-model gate, provider, trusted evidence, isolation과 teardown을
행동으로 증명하고, 10개 receipt의 truthful generation을 게시한다.

## 주요 변경 지점

- 시작 gate는 ZZA-72 head `01eacf38a61d5937b4cc6ec91c499b598a3a4007`과
  `scripts/harness/descriptors.mjs::loadRuntimeDescriptors`로 충족했고 ZZA-73 branch를 해당
  commit 위에 fast-forward stack했다.
- 조사 단계에서 Tart 2.32.0 archive/member digest와 macOS 15 arm64 base image digest를
  확정했다. OCI image도 exact digest로 로컬에 pull했다.
- Worktree에는 receipt/attestation/transcript/generation schema, substrate manifest,
  acquisition/publication pure logic, availability probe와 blocked generation 초안이 unstaged로
  남아 있다. 이 초안은 commit/push/PR하지 않았다.
- 초안은 10개 complete non-pass receipt를 생성하고 `current.json` pointer로 blocked generation을
  선택할 수 있으나, 독립 리뷰 결과 real non-injectable runtime/OCI/Tart driver와 trusted proof
  경계가 없어 `characterizer-implementation-complete/support-blocked`에도 미달한다.

## 검증

- Pure U16 tests: PASS, 6/6.
- `npm run test:harness`: PASS, 35/35(U16 6 + 기존 29).
- `npm run profile:verify`: PASS.
- `npm run test:workspace-connectors`: PASS, 31/31.
- `npm pack --dry-run`: PASS, 136 files/약 292 kB.
- `npm run harness:characterize -- --write`: 의도대로 exit 2,
  `u16GatePassed:false`; 10개 blocked receipt를 가진 generation을 작성했다.
- `npm run harness:characterize -- --verify`: 의도대로 exit 2,
  `u16GatePassed:false`; static blocked generation을 검증했다.
- `git diff --check`: PASS.
- `CE_SOURCE_DIR` independent upstream verification은 이 실행 환경에서 변수가 없어 미실행했다.
- 브라우저 검증은 CLI/JSON contract 변경으로 대상 route/UI가 없어 해당하지 않는다.

### 독립 리뷰 blocker

- `--live`가 runtime acquisition/execution, CE native discovery, bypass matrix, gate/provider/control
  probe를 호출하지 않고 backend blocker를 8개 runtime reason으로 복사한다.
- OCI/Tart 모듈은 identity/availability stub이며 effective isolation, broker-only network, hostile
  probe와 teardown을 실행하지 않는다.
- Passing evidence가 capability-bound control events나 pinned real-driver identity가 아니라
  재계산 가능한 JSON boolean/digest로 위조될 수 있다.
- Attestation descriptor binding, generation collision/byte durability, disposable-root symlink,
  runtime transcript semantics, provider token/cell/size/timeout 경계와 substrate artifact publication이
  미완성이다.
- 현재 macOS host는 Darwin arm64지만 effective guest PF policy를 적용할 root 권한이 없어
  Tart lane이 `tart-pf-admin-policy-unavailable`로 차단된다. Host 또는 `sandbox-exec` fallback은
  사용하지 않았다.
- U3 PR #24는 mergeable/CLEAN이고 latest-head code/doc review gate를 통과했지만 repository에
  CI check workflow가 없어 `statusCheckRollup`이 비어 있으며 CI green을 증명할 check-run이 없다.

## 외부 동기화

- Linear ZZA-73: `In Progress` 유지.
- Canonical Notion plan: <https://app.notion.com/p/3a0ef22ad4fc8134a54af0e4716c28e9>
- Canonical Notion ticket: <https://app.notion.com/p/3a0ef22ad4fc81b7b576c2914a5bec3b>
- U16 PR은 incomplete/fabricable implementation을 shipping하지 않기 위해 열지 않았다.
- U3 PR: <https://github.com/zzanghyunmoo/oh-my-harness/pull/24>

## Merge closeout

U16은 blocked 상태다. Real drivers와 trusted proof boundary를 완성하고 10개 real receipt가
통과한 뒤에만 PR, review marker, merge closeout과 Linear Done을 진행한다.
