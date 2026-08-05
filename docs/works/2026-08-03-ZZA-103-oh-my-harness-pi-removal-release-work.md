---
workflow_schema: compound-work/v1
ticket_id: ZZA-103
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-103/host-agent-harness-%EA%B8%B0%EB%B3%B8-%EC%84%A4%EC%B9%98-%EB%B0%8F-pi-%EC%99%84%EC%A0%84-%EC%A0%9C%EA%B1%B0
ticket_status: Done
ticket_completion: complete
remaining_prs:
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: "승인된 단일 product contract와 ce-brainstorm에서 범위가 확정되어 별도 후보 생성이 중복됨"
plan_status: complete
plan_path: docs/plans/2026-08-03-ZZA-103-host-agent-harness-pi-removal-plan.md
plan_notion_url: https://app.notion.com/p/3b1ef22ad4fc8197842cc7b8a27d6660
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b1ef22ad4fc816299bbc1445da68856
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/37
closeout_status: complete
merged_pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/37
merge_commit: cb0bde5d727c1f7d08fc2f5d778ea92acc2f0978
kb_paths: docs/kb/releases/2026-08-05-ZZA-103-oh-my-harness-pi-free-release.md
notion_feature_status_url: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436
notion_ticket_url: https://app.notion.com/p/3b1ef22ad4fc8171ae2fe9b74843f4fb
closed_at: 2026-08-05T11:21:59+09:00
---

# ZZA-103 OMH Pi-free release 작업 기록

## 작업 목표

`oh-my-harness`의 maintained product tree와 release payload에서 Pi product,
compatibility, migration surface를 제거하고 Claude/OpenCode/Codex 3-runtime contract,
`mds-host` composition-only profile, exact OMO/LazyCodex add-on과 self-contained `0.3.0`
release artifact를 만든다.

## 주요 변경 지점

- U1 (`b0342ac`): maintained tree를 Claude Code, OpenCode, Codex 정확히 세 runtime으로
  축소했다. `extensions/**`, `src/migration/v1.ts`, Pi/v1 설정·프로필·테스트·과거 문서를
  삭제하고 `AGENTS.md`, `README.md`, `CONCEPTS.md`와 두 durable solution을 3-runtime
  계약으로 다시 썼다.
- U1 계약: `tests/release/product-surface.test.ts`가 runtime adapter/profile/evidence의
  exact 3-runtime 집합, tracked tree의 retired identifier 0건, npm package input allowlist와
  제거된 migration/extension 부재를 고정한다. 기존 Pi 전용 negative fixture는 generic
  unknown-agent fail-closed 계약으로 교체했다.
- U2 (`c73a78f`): `package.json`에서 파생하는 `HARNESS_VERSION`을 도입하고 package,
  shrinkwrap, marketplace/plugin/MCP, release catalog와 native registration을 `0.3.0`으로
  동기화했다. OMO/LazyCodex pin과 provenance는 `4.19.2` 그대로 유지했다.
- U2 composition: `harness/profiles/mds-host.json`을 package-free, workflow exact-10,
  caller-agent override 전용 프로필로 추가했다. agent가 비면 preflight/action/native
  registration 0건의 안정 plan을 만들고, agent가 있으면 MDS가 PATH에 제공한 실행 파일의
  실제 SHA-256이 reviewed adapter digest와 같을 때만 `verify-agent`를 허용한다. 이 모드의
  agent acquisition은 fail closed하며 일반 profile의 기존 acquisition 규칙은 유지한다.
- U2 contract: apply plan/profile/receipt schema가 `mds-host + agent 0개`에만 빈 agent와 빈
  runtime readiness를 허용한다. preview→apply→repeat/status, exact digest mismatch, version
  surface coherence를 새 unit/integration tests로 고정했다.
- U3 (`3a03129`, `ec40c46`): `npm pack`의 direct production dependency closure를
  shrinkwrap에 번들하고, package/archive 전체 파일 manifest, SHA-256, size, source
  commit/tree를 담는 bounded release sidecar와 immutable output publication을 구현했다.
  tag workflow는 package/tag/main/merged-PR identity를 확인하고 canonical gate 전체와
  base-to-head `git diff --check`를 실행한 뒤 검증된 archive/sidecar를 한 번만 publish한다.
- U3 review close (`4adef65`): raw sidecar를 bounded closed-schema loader로 교체하고
  archive entry 상한, `npm pack` timeout/signal/error 처리, best-effort staging cleanup,
  publish-job asset checksum 재검증을 추가했다. production tag identity와 sidecar
  tampering/oversize/unknown-field 회귀 테스트를 고정했다.
- U1 review close (`4adef65`): 남아 있던 retired `plugins/oh-my-harness/skills/omp/`
  namespace를 물리 삭제하고 tracked/package surface에서 Pi와 OMP 식별자가 다시 생기면
  실패하는 회귀 계약을 추가했다.
- U2 review close (`4adef65`): composition 실행 파일 정책을
  `src/environment/runtime-policy.ts`로 분리했다. `mds-host`는 tool backend가 없는 정상
  ready 상태를 반환하고, custom profile의 `compositionOnly` 사칭과 released
  `mds-host` overwrite를 validate/preview 양쪽에서 거부한다.
- U2/U3 final close (`ec21ce3`): `mds-host`의 package와 tool route desired state를 schema,
  CLI parser, domain resolver와 orchestrator에서 모두 빈 집합으로 닫고, 선택 agent에
  대해서는 외부 exact executable의 `verify-agent`만 계획하는 positive integration을
  추가했다. composition MCP는 null binding에서도 status/setup만 노출한다. 제거된
  profile-pack CLI와 OMP 안내를 package/docs surface에서도 없앴다.
- U3 provenance (`ec21ce3`): release command를 compiled dispatcher로 옮기고, production
  artifact가 dirty/untracked/ignored checkout 대신 exact HEAD commit/tree를 materialize한
  격리 source에서 offline `npm ci`, direct TypeScript compiler, `npm pack`, sidecar 검증을
  수행하도록 바꿨다. alternates, replacement refs, promisor remote, unsafe tar member와
  output overwrite는 fail closed한다.
- U3 adversarial close (`83717b0`): `git archive`가 commit 외부의
  `$GIT_DIR/info/attributes`와 `core.attributesFile`을 적용해 release source를 바꿀 수
  있음을 격리 저장소에서 재현했다. source materialization을 `git ls-tree -z`와
  `git cat-file --batch`의 raw committed blob으로 교체해 external attributes,
  export-ignore/export-subst, checkout state가 release bytes에 개입하지 못하게 했다.
- U2 native collision close (`10bca21`): plan action을 만들기 전에 Claude Code, OpenCode,
  Codex의 current/prior native registration을 read-only로 분류한다. malformed, partial,
  duplicate, foreign 또는 receipt와 맞지 않는 registration은 null plan과 deterministic
  blocker를 반환하며 사용자 설정과 managed state를 변경하지 않는다. preview와 apply
  preparation은 같은 disposition helper를 사용해 판정 drift를 막는다.
- U3 atomic publish close (`4fd7b28`): tag와 source SHA marker가 정확히 일치하는 owned
  draft에 archive와 sidecar를 staging한다. 업로드 뒤 asset identity와 bytes를 다시
  내려받아 검증하고 한 번의 publish transition만 수행한다. publish 전 실패는 이 run이
  소유한 draft만 정리·재시도하고, published release는 overwrite/delete하지 않는다.
- Cross-platform fixture close (`646c447`): simulated Windows preview에 trusted npm/Git
  identity를 제공하고 receipt가 소유했다고 선언한 exact prior OpenCode registration을
  실제 config에도 materialize했다. production fail-closed preflight를 약화하지 않은 채
  macOS/Ubuntu/Windows에서 같은 provenance-complete fixture를 사용한다.
- Release publication review close (`cc05068`): workflow artifact에 실행 시 필요한
  `package.json`을 포함하고 release command가 command별 구현을 지연 import하도록 바꿔
  `node_modules` 없는 publish artifact에서도 시작된다. draft 삭제 직전 ownership을 다시
  관찰하며 created/upload/publish 응답의 release/tag/source/draft identity 불일치를 모두
  fail closed하는 회귀 계약을 추가했다.
- Environment recovery review close (`cd7c035`): pending native registration rollback을 state
  lock 안에서 먼저 복구하고 preview를 다시 계산하므로 crash 뒤 partial Claude/Codex
  registration이 영구 blocker가 되지 않는다. `mds-host`의 선택 agent는 공통
  `verify-agent` 경로를 사용하고, executable drift는 mutation 전에 차단하며, 빈 agent
  remediation은 parse 가능한 `--agents none`을 보존한다.

## 검증

- U1 green: `npm run typecheck`, `npm run build`, catalog 23/23, unit 47/47, contracts
  23/23, Claude runtime 8/8, OpenCode runtime 13/13, Codex runtime 10/10, harness 86 pass
  (Windows capability fixture 3 skip), product-surface 3/3, `git diff --check`.
- U1 재검수: product-surface와 catalog/profile/receipt focused suite 18/18, tracked working
  tree의 retired standalone identifier 검색 0건.
- U2 green: `npm run typecheck`, `npm run build`, `npm run catalog:verify` 25/25,
  mds-host/package-version/preview/profile/receipt focused suite 27/27. Agent worker의 broader
  focused suite는 76 pass, Windows capability fixture 1 skip였다.
- U2 보강: 실제 임시 executable의 reviewed SHA-256 일치 시 `external/ready`, digest 또는
  bytes 불일치 시 `drift`; 빈 composition의 preview→apply→repeat/status와 command 0회;
  non-empty mds-host receipt의 runtime readiness 필수 계약을 검증했다.
- U3/review green (`646c447`): typecheck/build, catalog 25/25, unit 55/55, contracts
  25/25, integration 88/88, Claude 8/8, OpenCode 13/13(로컬 loopback sandbox 밖),
  Codex 10/10, harness 86 pass(Windows fixture 3 skip), package/release 17/17,
  actionlint와 `git diff --check`가 통과했다.
  package smoke는 packed artifact를 임의 CWD에서 help, version, `mds-host --agents none`
  preview까지 offline으로 실행했다. release materialization 회귀 테스트는 dirty tracked,
  untracked, ignored 파일과 외부 Git attributes가 있어도 committed blobs만 복원함을
  검증한다.
- Node 26에서 기존 5개 Windows preview fixture 실패와 새 prior-registration fixture
  실패를 재현했다. blocker 관찰로 trusted provenance tool과 receipt/config 불일치를
  원인으로 확정했고 `646c447` 후 integration 88/88이 통과했다. Node 22.19 PR checks는
  Ubuntu, macOS, Windows 세 플랫폼 모두 통과했다.
- `ce-simplify-code`는 native/release 변경에서 재사용 2건, 품질 4건, 효율성 1건을
  동작 보존으로 반영했다. 공급망 검사를 줄이거나 범위를 넓히는 9개 제안은 제외했다.
  CI fixture 후속 pass의 재사용성·품질·효율성 검토에는 추가 finding이 없었다.
- 기존 `ce-code-review` marker는 `83717b0` 기준이라 새 commit 이후 stale이다. 최신
  `cd7c035`에서 code/doc review를 다시 실행하고 두 passing marker를 게시해야 한다.
- 최신 `cd7c035` canonical local gate는 typecheck/build, catalog 25/25, unit 55/55,
  contracts 25/25, integration 94/94, Claude 8/8, OpenCode 13/13, Codex 10/10,
  harness 86 pass(Windows fixture 3 skip), package/release 38/38, actionlint와
  `git diff --check`가 통과했다. PR Node 22.19 CI도 macOS, Ubuntu, Windows에서 모두
  통과했다.

## 외부 동기화

- Linear ZZA-103: `In Review`
- Pull request: <https://github.com/zzanghyunmoo/oh-my-harness/pull/37>
- Canonical plan: <https://app.notion.com/p/3b1ef22ad4fc8197842cc7b8a27d6660>
- Notion 구현 문서: <https://app.notion.com/p/3b1ef22ad4fc816299bbc1445da68856>

## Merge closeout

- PR #37은 `cb0bde5d727c1f7d08fc2f5d778ea92acc2f0978`로 squash merge됐다.
- 현재 기능 상태, 운영 경계와 검증 결과를
  `docs/kb/releases/2026-08-05-ZZA-103-oh-my-harness-pi-free-release.md`에 기록했다.
- Notion `디자인 문서 > 기능 현황`과 canonical 티켓 구현 문서에 merge 결과와 v0.3.0
  후속 경계를 동기화했다.
- OMH follow-up PR #38, endpoint fix PR #39와 MDS PR #6까지 모두 병합·closeout되어
  Linear ZZA-103은 `Done`, `ticket_completion: complete` 상태다.
