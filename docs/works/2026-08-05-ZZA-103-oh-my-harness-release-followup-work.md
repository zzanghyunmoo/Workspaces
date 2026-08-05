---
workflow_schema: compound-work/v1
ticket_id: ZZA-103
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-103/host-agent-harness-%EA%B8%B0%EB%B3%B8-%EC%84%A4%EC%B9%98-%EB%B0%8F-pi-%EC%99%84%EC%A0%84-%EC%A0%9C%EA%B1%B0
ticket_status: In Review
ticket_completion: pending
remaining_prs: my-desk-setup-host-harness
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: "PR #37의 Windows 검증 후속 결함을 닫는 동일 product contract 작업으로 새 후보 탐색이 중복됨"
plan_status: complete
plan_path: docs/plans/2026-08-03-ZZA-103-host-agent-harness-pi-removal-plan.md
plan_notion_url: https://app.notion.com/p/3b1ef22ad4fc8197842cc7b8a27d6660
plan_waiver_reason:
work_status: in_progress
work_notion_url: https://app.notion.com/p/3b1ef22ad4fc816299bbc1445da68856
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/38
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url: https://app.notion.com/p/3b1ef22ad4fc8171ae2fe9b74843f4fb
closed_at:
---

# ZZA-103 OMH v0.3.0 release follow-up 작업 기록

## 작업 목표

Windows에서 먼저 검증·병합한 OMH/MDS 변경을 기준으로 `oh-my-harness`의 v0.3.0
릴리스 경로를 다시 점검한다. OpenCode OMO가 네트워크 없이 실제로 load 가능한 complete
snapshot인지, 기존 `4.19.2` registration이 안전하게 local snapshot으로 이동하는지,
receipt/recovery/release draft 계약이 실제 mutation target과 실패 상태를 보존하는지 닫은 뒤
reviewed main merge commit에서 릴리스한다. 인증은 사용자가 직접 수행한다.

## 주요 변경 지점

- `harness/catalog/agents.json`, `src/catalog/{load,types}.ts`: OpenCode OMO source archive,
  materialized tree, entry point와 exact dependency identity를 closed catalog contract로
  고정한다. 새 필드는 legacy catalog parse 호환을 위해 optional type로 읽되 embedded
  v0.3.0 catalog load에서는 반드시 검증한다.
- `src/install/runtime-addon-acquisition.ts`: reviewed OMO tarball과 OMH의 exact
  upstream range를 만족하는 exact `zod@4.4.3` dependency tree를 staging에서 결합하고,
  package/dependency manifests와 전체
  tree digest를 검증한 뒤 content-addressed root로 원자 발행한다. 검증 실패는 native
  config mutation 전에 끝나며 staging은 정상 오류 경로에서 정리된다.
- `src/environment/native-registration.ts`, `src/environment/orchestrator.ts`: snapshot과
  native registration이 모두 정확해야 ready이다. exact prior
  `oh-my-openagent@4.19.2`만 local `file:` spec으로 교체하고 user plugin, malformed,
  duplicate, foreign registration은 collision으로 보존한다. 충돌 preview는
  `native-registration:<runtime>` stable blocker code와 관련 없는 사용자 설정을 보존하는
  secret-free 수동 복구 안내를 JSON/text 양쪽에 제공한다. receipt에는 canonical resolution
  뒤 실제 변경 target을 기록한다.
- `src/planning/apply.ts`, `src/environment/orchestrator.ts`: recovery record에 당시 selection을
  묶어 profile/agent/state-root drift를 막고, selection-less legacy
  `verify-opencode-addon-source` journal을 제한적으로 계속 읽는다.
- `src/catalog/release-publication.ts`: pre-publish 실패 시 owned draft를 자동 삭제하지 않고
  exact draft ID를 포함해 점검·재시도 가능 상태로 보존한다. published release는 계속
  overwrite/delete하지 않는다.
- `scripts/vendor-runtime-addons.mjs`: catalog가 가리키는 두 embedded runtime archive의
  regular-file/size/SHA-256 identity를 독립 실행으로 확인하는 `verify` mode를 추가한다.
- `CONCEPTS.md`와 canonical Notion 구현 문서: Offline Runtime Add-on Snapshot과 Preserved
  Release Draft를 현재 제품 계약으로 동기화한다.

## 검증

- Commits: `7f1588f fix(release): close v0.3.0 runtime safety gaps`,
  `062871d fix(release): satisfy the reviewed OMO dependency range`,
  `3d60130 fix(cli): explain native registration conflicts`.
- Green: typecheck/build, unit 58/58, contracts 26/26, integration 98/98.
- Runtime: Claude Code 8/8, OpenCode 13/13, Codex 10/10.
- Harness: 86 pass, Windows-only fixture 3 skip. Descriptor verify와 `git diff --check` 통과.
- Package/release: 36/36. exact committed HEAD에서 self-contained artifact를 만들고 임의
  CWD offline install 뒤 help와 read-only `mds-host --agents none` preview를 실행했다.
- Green: OpenCode snapshot direct offline import, exact predecessor upgrade, native collision,
  add-on preview/apply와 embedded archive identity focused tests.
- Green: native registration 충돌의 stable blocker code와 secret-free 수동 복구 안내를
  JSON 결과와 CLI text renderer에서 검증했다.
- 재현: raw upstream OMO tarball은 Bun `--no-install`에서 `zod` 부재로 실패했다. complete
  managed snapshot은 Node file-URL import로 외부 설치 없이 성공한다.
- Pending: PR latest-head code/doc review와 macOS/Ubuntu/Windows CI.
- Release precondition: OMH merge 뒤 tag 전에 merge commit 기준 MDS local release fixture를
  재생성하고 source commit/tree, archive, sidecar, digest가 tag 대상과 같은 상태에서 child
  preview/apply를 다시 검증한다. 이 gate가 green이 아니면 v0.3.0을 발행하지 않는다.

## 외부 동기화

- Linear ZZA-103은 dependent MDS PR이 남아 있어 `In Review`를 유지한다.
- Pull request: https://github.com/zzanghyunmoo/oh-my-harness/pull/38
- Canonical Notion 구현 문서를 v0.3.0 follow-up branch, offline dependency closure, exact
  predecessor migration, actual receipt target, legacy recovery와 preserved draft 계약으로
  갱신했다: https://app.notion.com/p/3b1ef22ad4fc816299bbc1445da68856

## Merge closeout

Merge 뒤 OMH KB, Notion 기능 현황·티켓 문서, merge commit과 v0.3.0 release URL을 기록한다.
MDS 후속 PR이 남아 있으므로 이 PR closeout에서도 Linear는 `In Review`를 유지한다.
