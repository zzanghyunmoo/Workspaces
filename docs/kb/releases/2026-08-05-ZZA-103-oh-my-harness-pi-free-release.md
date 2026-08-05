---
module: oh-my-harness-release
tags:
  - zza-103
  - pi-free
  - composition-profile
  - immutable-release
problem_type: feature-state
---

# ZZA-103 OMH Pi-free release 기반 상태

## 현재 기능 상태

`oh-my-harness` PR [#37](https://github.com/zzanghyunmoo/oh-my-harness/pull/37)은
merge commit `cb0bde5d727c1f7d08fc2f5d778ea92acc2f0978`로 병합됐다. maintained
product와 release surface는 Claude Code, OpenCode, Codex 세 runtime만 포함하며 Pi/OMP
product, compatibility, migration surface는 제거됐다.

`mds-host` composition profile은 package와 인증을 소유하지 않는다. MDS가 제공한
caller-owned agent executable을 exact digest로 검증한 뒤 공통 workflow 10개와 reviewed
OMO/LazyCodex add-on을 runtime-native surface에 합성한다. agent가 없으면 mutation 없는
stable empty plan을 만든다.

## 릴리스와 운영 경계

- v0.3.0 builder는 reviewed main source commit/tree, exact production dependency closure,
  full file manifest와 sidecar를 검증하는 self-contained artifact를 만든다.
- published release와 asset은 overwrite/delete하지 않는다.
- auth, login, token과 provider credential은 자동화하지 않고 사용자가 직접 관리한다.
- 기존 user-owned native registration과 config는 소유권/identity가 다르면 보존하고
  mutation 전에 collision으로 중단한다.

## 검증 결과

- PR latest head의 Node 22.19 macOS, Ubuntu, Windows GitHub Actions가 모두 성공했다.
- local canonical gate에서 typecheck/build, catalog, unit, contracts, integration,
  Claude/OpenCode/Codex runtime, harness, package/release와 diff check가 통과했다.
- merge commit은 PR #37의 reviewed latest head를 포함한다.

## 후속 작업

후속 actual/offline 검증에서 raw OpenCode OMO tarball이 runtime dependency를 자체 포함하지
않는 문제를 재현했다. v0.3.0 발행 전 exact dependency closure를 포함한 content-addressed
snapshot, exact prior registration upgrade, actual receipt target, legacy recovery와 preserved
release draft 계약을 별도 OMH follow-up PR에서 닫는다. MDS host harness PR도 남아 있어
Linear ZZA-103은 `In Review`를 유지한다.

Canonical Notion 기능 상태는
[기능 현황](https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436), 구현 설명은
[03-1 OMH Pi-free release 구현 설명](https://app.notion.com/p/3b1ef22ad4fc816299bbc1445da68856)을
따른다.
