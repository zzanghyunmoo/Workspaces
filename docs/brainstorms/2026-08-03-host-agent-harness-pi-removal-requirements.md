---
title: "Host Agent Harness 기본 설치와 Pi 제거 - Requirements"
type: feat
date: 2026-08-03
topic: host-agent-harness-pi-removal
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
execution: code
notion_source: https://app.notion.com/p/3b1ef22ad4fc81a69238fb03cf4b3438
ticket: ZZA-103
target_repositories:
  - projects/oh-my-harness
  - projects/my-desk-setup
---

# Host Agent Harness 기본 설치와 Pi 제거 - Requirements

## Goal Capsule

- **Objective:** macOS와 Windows host에서 `my-desk-setup`의 한 번의 plan/apply로 `oh-my-harness`, 공통 workflow, OpenCode OMO와 Codex LazyCodex를 기본 설치한다.
- **Product authority:** [Notion canonical requirements](https://app.notion.com/p/3b1ef22ad4fc81a69238fb03cf4b3438)
- **Tracking:** [Linear ZZA-103](https://linear.app/zzanghyunmoo/issue/ZZA-103/host-agent-harness-%EA%B8%B0%EB%B3%B8-%EC%84%A4%EC%B9%98-%EB%B0%8F-pi-%EC%99%84%EC%A0%84-%EC%A0%9C%EA%B1%B0)
- **Execution:** `oh-my-harness`에서 Pi를 먼저 제거하고 release를 만든 뒤 `my-desk-setup`이 그 exact release를 설치한다.
- **Open blockers:** 없음. 인증은 사용자가 직접 수행하며 기존 사용자 home의 Pi 데이터는 자동 삭제하지 않는다.

---

## Product Contract

### Summary

macOS와 Windows host의 AI coding agent 환경은 `my-desk-setup`의 동일한 resolver와 preview-first apply 경로로 `oh-my-harness` 및 공통 workflow를 기본 설치한다.
OpenCode에는 OMO Ultimate를, Codex에는 LazyCodex OMO Light를 exact pin으로 설치하며, `oh-my-harness`의 maintained tree에서는 Pi 제품·호환·migration 흔적을 완전히 제거한다.

### Problem Frame

`my-desk-setup`은 현재 Claude Code, OpenCode, Codex executable을 설치하지만 agent별 공통 workflow나 add-on을 합성하지 않는다.
`oh-my-harness` 최신 main은 OMO와 LazyCodex 기본 add-on을 구현했지만 release artifact가 없고 Pi dependency, migration inspector, removal preview, 문서와 테스트가 남아 있다.
따라서 새 macOS 또는 Windows host는 승인된 단일 설치로 현재 agent workflow를 재현할 수 없다.

### Key Decisions

- **Host 기본 설치:** macOS와 Windows host profile은 `oh-my-harness`와 공통 workflow를 기본 선택한다.
- **선택 설치 유지:** all, profile, component, interactive 선택은 기존 `my-desk-setup` resolver 하나를 사용하며 harness만 선택하거나 제외할 수 있다.
- **공통 workflow 집합:** `goal`, `deep-research`, `ideation`, `brainstorm`, `plan`, `code-review`, `doc-review`, `skill-creator`, `ralph-loop`, `security-guidance`를 기본 집합으로 둔다.
- **Agent add-on:** OpenCode는 OMO Ultimate, Codex는 LazyCodex OMO Light를 `oh-my-harness` agent catalog의 required exact pin으로 설치한다.
- **Pi 완전 제거:** Pi runtime, adapter, package dependency, v1/Pi migration inspector, removal preview, profile/catalog/receipt contract, docs, tests, scripts와 vocabulary를 maintained tree에서 제거한다.
- **사용자 데이터 보존:** 기존 사용자 home의 Pi 파일이나 설정은 자동 탐지·삭제하지 않는다.
- **하나의 승인 사슬:** `my-desk-setup` plan이 exact `oh-my-harness` release와 child preview digest를 고정하고 확인한 digest에 대한 apply만 실행한다.
- **충돌 안전성:** 기존 사용자 소유 plugin/config는 덮어쓰지 않으며 source, version 또는 registration 충돌은 mutation 전에 실패한다.
- **인증 분리:** agent 및 외부 CLI의 login, auth, token 저장은 자동화하지 않는다.
- **Guest 경계 유지:** Linux guest의 CLI, 언어, build tool, Neovim/NvChad, agent와 Docker 범위는 유지하며 이번 변경은 host harness 기본화와 선행 release에 집중한다.

### Requirements

**Host composition**

- R1. macOS와 Windows의 기본 host plan은 `oh-my-harness`와 공통 workflow를 포함해야 한다.
- R2. 사용자는 전체 설치와 동일한 resolver를 통해 harness와 agent를 선택적으로 설치할 수 있어야 한다.
- R3. OpenCode에는 OMO Ultimate가, Codex에는 LazyCodex OMO Light가 exact provenance와 digest로 설치되어야 한다.
- R4. Claude Code, OpenCode, Codex의 공통 workflow contract는 runtime-native surface로 적용되어야 한다.

**Pi removal and ownership**

- R5. `oh-my-harness`의 maintained working tree에는 Pi product, compatibility, migration, dependency, documentation 또는 test contract가 남지 않아야 한다.
- R6. 기존 사용자 소유 설정과 plugin registration은 보존되며 불일치 충돌은 첫 mutation 전에 실패해야 한다.

**Release and lifecycle**

- R7. `my-desk-setup`은 released `oh-my-harness` artifact와 exact child preview digest를 outer plan digest에 결합해야 한다.
- R8. normal apply는 pinned release를 몰래 올리지 않으며 update만 reviewable lock change로 version을 이동해야 한다.

**Verification and security**

- R9. auth, login, token 또는 credential 상태는 plan, apply, receipt, log와 doctor 범위에서 제외해야 한다.
- R10. macOS와 Windows 실제 대상에서 기본 설치, 선택 설치, repeat apply와 conflict-preservation 증거를 남겨야 한다.

### Key Flows

- F1. Host default apply
  - **Trigger:** 사용자가 macOS 또는 Windows host의 기본 profile을 plan한 뒤 exact digest로 apply한다.
  - **Steps:** `my-desk-setup`이 pinned `oh-my-harness`를 준비하고 child preview를 얻어 outer plan에 결합한 뒤, agent와 workflow를 runtime-native surface에 적용한다.
  - **Outcome:** 세 agent와 공통 workflow가 ready이며 OpenCode OMO와 Codex LazyCodex가 exact add-on pin과 일치한다.
  - **Covered by:** R1, R3, R4, R7
- F2. Selective apply
  - **Trigger:** 사용자가 profile 대신 component 또는 interactive selection을 사용한다.
  - **Steps:** 기본 설치와 같은 resolver가 dependency closure를 계산하고 선택하지 않은 host component를 제외한다.
  - **Outcome:** 선택 범위만 변경되며 동일한 digest와 ownership 규칙이 적용된다.
  - **Covered by:** R2, R6, R8
- F3. Conflict refusal
  - **Trigger:** 같은 plugin ID가 다른 source, version 또는 registration으로 사용자 설정에 존재한다.
  - **Steps:** preflight가 충돌을 식별하고 child와 outer apply를 첫 mutation 전에 중단한다.
  - **Outcome:** 사용자 파일은 그대로 유지되고 conflict와 복구 지침이 보고된다.
  - **Covered by:** R6, R9
- F4. Release handoff
  - **Trigger:** `oh-my-harness`의 Pi-free release candidate가 canonical gate를 통과한다.
  - **Steps:** immutable release identity와 checksum/provenance를 발행하고 `my-desk-setup` lock을 명시적 update로 이동한다.
  - **Outcome:** host install은 검토된 release만 사용하며 normal apply는 pin을 바꾸지 않는다.
  - **Covered by:** R5, R7, R8, R10

### Acceptance Examples

- AE1. 깨끗한 macOS host에서 기본 profile을 plan/apply하면 Claude Code, OpenCode, Codex와 `oh-my-harness` 공통 workflow가 준비되고 OpenCode/Codex add-on이 exact pin과 일치한다.
- AE2. 깨끗한 Windows host에서 같은 profile을 적용하면 macOS와 같은 logical inventory가 native path와 launcher를 통해 준비된다.
- AE3. harness만 선택한 plan은 agent executable을 임의로 추가하지 않고 필요한 harness 계약만 계산한다.
- AE4. 이미 같은 source와 version의 plugin이 등록된 host에서 repeat apply는 no-op이다.
- AE5. 같은 plugin ID가 다른 source 또는 version으로 사용자 설정에 존재하면 plan/apply는 파일을 덮어쓰지 않고 conflict를 보고한다.
- AE6. source tree 검사에서 Pi 관련 maintained code, dependency, contract, test, script와 documentation reference가 발견되면 release gate가 실패한다.

### Scope Boundaries

- 기존 사용자 home의 Pi 데이터 자동 삭제
- agent와 외부 CLI의 인증 자동화
- Linux guest component inventory 재설계
- Codex LSP unsupported 경계를 ready로 승격
- 현재 한 사용자의 전체 개인 plugin inventory를 기본 profile에 그대로 복제
- Git history rewrite로 과거 Pi commit 자체를 제거

### Success Criteria

- `oh-my-harness` release artifact가 macOS와 Windows 지원 identity와 checksum/provenance를 제공한다.
- `my-desk-setup` catalog와 certification profile이 같은 release를 고정한다.
- canonical tests와 macOS/Windows actual-target verification이 모두 통과한다.
- Linear, Notion, local plan/work/KB와 두 child PR의 evidence가 같은 범위와 결과를 가리킨다.

### Sources and Research

- [My Desk Setup 프로젝트 위키](https://app.notion.com/p/3acef22ad4fc816ba9f3f61dd5b42a4f)
- [Oh My Harness v2 프로젝트 위키](https://app.notion.com/p/3a7ef22ad4fc81509f5cf9e2bc817226)
- [Linear ZZA-97](https://linear.app/zzanghyunmoo/issue/ZZA-97/oh-my-harness-v2-claude-first-profile-driven-environment-manager)
- `projects/my-desk-setup/internal/catalog/catalog_v1.json`
- `projects/my-desk-setup/profiles/certification-macos-all.json`
- `projects/my-desk-setup/profiles/certification-windows-all.json`
- `projects/oh-my-harness/harness/catalog/agents.json`
- `projects/oh-my-harness/src/migration/v1.ts`
