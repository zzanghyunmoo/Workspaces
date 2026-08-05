---
title: ZZA-103 Host Agent Harness 최종 기능 상태
ticket: ZZA-103
merged_pr: https://github.com/zzanghyunmoo/my-desk-setup/pull/6
merge_commit: 7e29369364f7ae535688e6d379b43aedc91bba64
work_evidence: docs/works/2026-08-03-ZZA-103-my-desk-setup-host-harness-work.md
notion_feature_status: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436
notion_ticket: https://app.notion.com/p/3b1ef22ad4fc8171ae2fe9b74843f4fb
last_verified: 2026-08-05
module: host-agent-harness
tags: zza-103, oh-my-harness, host-profile, release-identity
problem_type: feature-state
---

# ZZA-103 Host Agent Harness 최종 기능 상태

## 현재 기능 상태

`oh-my-harness`(OMH)는 Claude Code, OpenCode와 Codex 세 runtime만 유지하며 Pi/OMP
product·compatibility·migration surface를 release payload에서 제거했다. PR
[#37](https://github.com/zzanghyunmoo/oh-my-harness/pull/37),
[#38](https://github.com/zzanghyunmoo/oh-my-harness/pull/38),
[#39](https://github.com/zzanghyunmoo/oh-my-harness/pull/39)가 차례로 병합됐고, immutable
[v0.3.0](https://github.com/zzanghyunmoo/oh-my-harness/releases/tag/v0.3.0)이 공개됐다.

`my-desk-setup` PR [#6](https://github.com/zzanghyunmoo/my-desk-setup/pull/6)은 merge
commit `7e29369364f7ae535688e6d379b43aedc91bba64`로 병합됐다. macOS/Windows host의
owner·기본·certification profile은 OMH v0.3.0과 native Claude Code/OpenCode/Codex를
선택하며, OMH 전용 Node는 직접 선택 항목이 아니라 dependency closure로만 포함한다.
`all`, profile, component와 interactive 선택은 기존 resolver를 공유한다.

Linux guest의 책임은 기존처럼 CLI, 프로그래밍 언어·빌드 도구, NvChad 기반 Neovim,
AI coding agent와 guest-local Docker다. Notion 데스크톱 앱은 guest에 설치하지 않고
`notion-cli` 같은 CLI만 guest component로 관리한다.

## 주요 동작과 경계

- MDS는 공개 OMH archive와 sidecar의 source commit/tree, catalog revision, archive
  digest와 size를 검증한 뒤 content-addressed snapshot으로 발행한다.
- 공개 OMH archive 안의 세 native agent adapter identity를 MDS release fixture와 대조하고,
  fixture의 version·네 host platform별 archive/executable identity를 production lock과 다시
  대조한다.
- agent archive를 설치할 때 extracted executable SHA-256도 다시 검증하고 archive 내부
  파일명과 무관한 `claude`, `opencode`, `codex` stable command path로 발행한다.
- child OMH preview digest를 MDS outer plan에 결합하며, plan-wide preflight 뒤 승인된 exact
  digest로만 apply한다. receipt/evidence는 실제 mutation target을 기록하고 반복 apply는
  no-op으로 수렴한다.
- OMH는 공통 workflow 10개와 reviewed OpenCode OMO/Codex LazyCodex add-on을 agent-native
  surface에 합성한다. package 자체와 인증 정보는 MDS/OMH가 소유하지 않는다.
- 기존 user-owned config나 native registration identity가 다르면 자동 덮어쓰지 않고
  mutation 전에 충돌로 중단한다.
- 인증, login, token과 provider credential은 자동화하지 않으며 사용자가 직접 수행한다.

## 검증 결과

- OMH v0.3.0 canonical archive SHA-256은
  `da805da0130e937913706f98ddb415f5e4b4bc12d04505b269f08bf66237ea73`이다. archive와
  sidecar를 업로드 후 다시 내려받아 원본 bytes와 일치함을 확인했다.
- OMH PR #38의 Node 22.19 macOS, Ubuntu, Windows CI와 package/release 36/36이 통과했고,
  PR #39는 canonical `uploads.github.com` full URL 회귀 테스트와 세 OS CI를 통과했다.
- MDS PR #6의 `go test ./...`, `go test -race ./...`, `go vet ./...`, macOS/Windows build,
  Windows scanner와 GitHub Actions가 통과했다.
- 실제 공개 OMH archive/sidecar를 사용한 macOS 격리 환경에서 child preview와
  exact-digest apply가 통과했다.
- 공개 OMH adapter → fixture → production lock identity chain이 Codex macOS x64
  executable digest 오타를 발견했고 공개 archive의 canonical 값으로 수정했다.

## 운영 및 사용 시 주의사항

- 실제 macOS/Windows 사용자 홈에 대한 destructive install은 이 closeout에서 실행하지
  않았다. 새 머신에서는 먼저 `plan`과 digest를 확인한 뒤 사용자가 `apply`를 승인한다.
- 각 agent의 auth/login은 설치 뒤 사용자가 직접 수행한다.
- published OMH release와 asset은 overwrite/delete하지 않는다. publish 전 실패한 exact
  owned draft만 보존 후 재검증·수동 복구한다.
- Windows 경로는 Windows CI, cross-build와 사용자가 앞서 수행한 Windows 검증을 근거로
  한다. 이번 최종 merge head의 실제 Windows 사용자 홈 설치는 미실행이다.

Canonical Notion 문서는 [기능 현황](https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436),
[티켓 결과](https://app.notion.com/p/3b1ef22ad4fc8171ae2fe9b74843f4fb),
[OMH 구현 설명](https://app.notion.com/p/3b1ef22ad4fc816299bbc1445da68856),
[MDS 구현 설명](https://app.notion.com/p/3b1ef22ad4fc81e990c2df7dc995ebfc)을 따른다.
