---
title: ZZA-103 OMH Pi-free release 기반 상태
ticket: ZZA-103
merged_pr: https://github.com/zzanghyunmoo/oh-my-harness/pull/38
merge_commit: 95882328d339e7336e8a60a90f3e2640c1244da3
work_evidence: docs/works/2026-08-05-ZZA-103-oh-my-harness-release-followup-work.md
notion_feature_status: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436
notion_ticket: https://app.notion.com/p/3b1ef22ad4fc8171ae2fe9b74843f4fb
last_verified: 2026-08-05
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

후속 PR [#38](https://github.com/zzanghyunmoo/oh-my-harness/pull/38)은 merge commit
`95882328d339e7336e8a60a90f3e2640c1244da3`로 병합됐다. OpenCode OMO는 reviewed
`4.19.2` tarball과 upstream `^4.4.3` range를 만족하는 exact `zod@4.4.3`을 하나의
content-addressed offline snapshot으로 materialize한다. source archive, manifest, entry
point와 전체 tree digest가 일치해야 native registration을 계획한다.

`mds-host` composition profile은 package와 인증을 소유하지 않는다. MDS가 제공한
caller-owned agent executable을 exact digest로 검증한 뒤 공통 workflow 10개와 reviewed
OMO/LazyCodex add-on을 runtime-native surface에 합성한다. agent가 없으면 mutation 없는
stable empty plan을 만든다.

## 주요 동작과 경계

- v0.3.0 builder는 reviewed main source commit/tree, exact production dependency closure,
  full file manifest와 sidecar를 검증하는 self-contained artifact를 만든다.
- published release와 asset은 overwrite/delete하지 않는다.
- auth, login, token과 provider credential은 자동화하지 않고 사용자가 직접 관리한다.
- 기존 user-owned native registration과 config는 소유권/identity가 다르면 보존하고
  mutation 전에 collision으로 중단한다. 충돌 결과는 `native-registration:<runtime>` stable
  code와 관련 없는 사용자 설정을 보존하는 수동 복구 안내를 JSON/text에 함께 제공한다.
- exact prior `oh-my-openagent@4.19.2` registration만 reviewed local snapshot으로 교체한다.
- receipt는 canonical resolution 뒤 실제 변경 target을 기록한다. 새 recovery journal은
  environment selection을 필수로 결합하고 PR #37 이전 selection-less journal은 기존
  operation/target identity 안에서만 호환 복구한다.
- publish 전 실패한 exact owned release draft는 자동 삭제하지 않고 수동 점검·재시도를
  위해 보존한다.

## 검증 결과

- PR latest head의 Node 22.19 macOS, Ubuntu, Windows GitHub Actions가 모두 성공했다.
- local canonical gate에서 typecheck/build, catalog, unit, contracts, integration,
  Claude/OpenCode/Codex runtime, harness, package/release와 diff check가 통과했다.
- PR #38 latest head 기준 unit 59/59, contracts 26/26, integration 98/98,
  runtime/harness 117 pass와 Windows fixture 3 skip, package/release 36/36이 통과했다.
- merge commit `95882328d339e7336e8a60a90f3e2640c1244da3`은 PR #38의 reviewed latest
  head와 두 trusted review marker를 포함한다.

## 후속 작업

실제 OMH merge commit 기준으로 MDS local release fixture의 source commit/tree, archive,
sidecar와 digest를 재생성했고 child preview/exact-digest apply를 통과했다. 후속 MDS host
harness PR [#6](https://github.com/zzanghyunmoo/my-desk-setup/pull/6)이 남아 있어 Linear
ZZA-103은 `In Review`를 유지한다.

## 운영 및 사용 시 주의사항

- v0.3.0 릴리스는 tag가 가리키는 reviewed merge commit과 MDS에서 검증한 archive digest가
  일치할 때만 발행한다.
- OMH는 인증 정보를 만들거나 갱신하지 않는다. Claude Code, OpenCode와 Codex 인증은
  사용자가 각 runtime에서 직접 수행한다.
- 기존 user-owned native registration 충돌은 자동 덮어쓰기하지 않는다. JSON/text 결과의
  stable blocker code와 수동 복구 안내를 확인한 뒤 사용자가 정리한다.

Canonical Notion 기능 상태는
[기능 현황](https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436), 구현 설명은
[03-1 OMH Pi-free release 구현 설명](https://app.notion.com/p/3b1ef22ad4fc816299bbc1445da68856)을
따른다.
