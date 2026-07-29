---
title: "My Desk Setup - Plan"
type: feat
date: 2026-07-29
topic: my-desk-setup
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
execution: code
ideation: docs/ideation/2026-07-29-cross-platform-development-environment-ideation.html
---

# My Desk Setup - Plan

## Goal Capsule

### Objective

새 macOS·Windows 머신을 준비한 뒤 WSL 또는 Lima Linux guest를 개발 실행 환경으로 삼을 수 있도록, 저장소를 확보하고 몇 개의 안정된 명령만 실행하면 전체 또는 선택한 개발 환경을 계획·설치·검증·갱신할 수 있게 한다.

### Product Authority

- 제품 소유자: 개인 개발 환경을 직접 운영하는 저장소 소유자
- 확정 일자: 2026-07-29
- 확정 상태: 이 문서의 제품 범위와 주요 결정은 사용자 확인을 마쳤다.
- 기준 아이디에이션: `docs/ideation/2026-07-29-cross-platform-development-environment-ideation.html`

### Open Blockers

- 구현 전 기존 `settings` 원격 저장소의 보호 규칙, 기본 브랜치, rename 가능 여부와 force-push 절차를 읽기 전용으로 확인해야 한다.
- 기존 이력을 교체하기 직전에 복구 가능한 Git bundle과 정확한 변경 대상을 제시하고, 프로젝트 `main` 직접 반영 및 원격 이력 교체에 대한 실행 승인을 다시 받아야 한다.
- 각 컴포넌트의 공식 배포 경로, 지원 OS·architecture, 검증 가능한 버전 식별자와 무인 설치 가능 범위는 `ce-plan`에서 조사·고정해야 한다.
- WSL과 Lima에서 Docker CLI가 사용할 엔진 및 host integration 경계는 구현 계획에서 확정해야 한다.

---

## Product Contract

### Summary

`my-desk-setup`은 하나의 Environment Intent Graph에서 host와 Linux guest의 목표 상태를 계산하는 개인용 환경 control plane이다.
`all`과 선택 설치, 대화형 선택과 자동화용 인자는 모두 같은 계획 경로를 사용하며, 성공은 설치 명령의 종료 코드가 아니라 컴포넌트별 기능 검증으로 판정한다.

### Problem Frame

- 새 데스크톱마다 패키지 관리자, 스크립트, 설정 순서와 설치 여부를 다시 기억해야 한다.
- macOS, Windows, WSL, Lima는 같은 도구라도 설치 방식과 실행 책임이 다르다.
- 전체 설치와 선택 설치가 별도 스크립트로 성장하면 대상 목록, 의존성, 버전과 검증 기준이 쉽게 어긋난다.
- host GUI와 Linux 개발 도구를 한 목록으로 취급하면 guest에 GUI 앱을 설치하거나 host에 중복 toolchain을 두는 잘못된 결과가 생긴다.
- 설치 성공만 확인하면 첫 빌드나 첫 편집 시점에 PATH, 플러그인, compiler, runtime integration 실패가 뒤늦게 드러난다.
- AI agent와 협업 CLI 인증까지 자동화하면 설치 제품이 credential 수명주기와 secret 저장 책임을 떠안게 된다.

### Key Decisions

1. Linux guest가 직접 개발의 기준 환경이며 source checkout, build, test와 editor 실행을 소유한다.
2. macOS·Windows host는 GUI, 플랫폼 전용 도구, Linux guest 진입과 host-side AI agent orchestration을 소유한다.
3. AI coding agent는 host와 guest 모두에 설치한다.
4. `all`은 별도 설치 구현이 아니라 선택한 target에 적합한 모든 컴포넌트를 고르는 preset이다.
5. 대화형 선택과 non-interactive profile/component 선택은 같은 Environment Intent Graph와 planner를 사용한다.
6. v1의 공개 명령은 `plan`, `apply`, `doctor`, `update` 네 개로 제한한다.
7. `apply`는 버전을 몰래 올리지 않으며, 버전 이동은 명시적인 `update`에서만 시작한다.
8. 언어·빌드 도구·Neovim 설정은 pin을 사용하고, CLI·AI agent·GUI 앱은 명시적인 update에서 latest stable 정책을 적용한다.
9. account/service 인증은 제품 밖에서 사용자가 직접 수행한다. 제품은 `auth` 명령을 제공하지 않고 credential을 수집·저장·검사하지 않는다.
10. 기존 `settings` 저장소의 정체성을 `my-desk-setup`으로 rename하고, 복구 지점을 만든 뒤 orphan 기반 새 이력으로 교체한다.
11. workspace의 submodule 경로는 `projects/settings`에서 `projects/my-desk-setup`으로 이동한다.
12. 기존 Ansible 구현은 조사 자료로만 사용하며 새 저장소 이력과 제품 구현에는 포함하지 않는다.

### Actors

- **A1. Owner:** 기본 profile과 component catalog를 관리하고 새 머신을 구성하는 주 사용자다.
- **A2. Profile Adapter:** 친구가 저장소를 clone 또는 fork한 뒤 자신의 profile과 component 선택을 조정하는 2차 사용자다.
- **A3. Host Target:** macOS 또는 Windows로, GUI·플랫폼 전용 도구·host agent·guest integration을 실행한다.
- **A4. Guest Target:** WSL 또는 Lima로 실행한 Linux 환경으로, CLI·toolchain·editor·guest agent와 실제 개발 작업을 실행한다.
- **A5. Upstream Provider:** 공식 package manager, release channel 또는 tool vendor로, 설치 artifact와 version metadata를 제공한다.

### Target and Component Contract

| Concern | macOS/Windows host | WSL/Lima Linux guest |
| --- | --- | --- |
| Terminal | WezTerm | Herdr |
| Languages | 플랫폼 예외만 설치 | Java, Kotlin, Go, Python, TypeScript, C, Dart/Flutter |
| Build tools | 플랫폼 예외만 설치 | Gradle, uv, Bun |
| Editor | 선택적 host 보조 사용은 후속 범위 | Neovim과 NvChad 기반 설정 |
| AI coding agents | Claude Code, OpenCode, Codex | Claude Code, OpenCode, Codex |
| Collaboration CLI | guest 진입에 필요한 최소 도구만 | jira-cli, confluence-cli, notion-cli, linear-cli, gh, glab |
| Desktop apps | Slack, KakaoTalk, Notion, Linear, Chrome | 설치하지 않음 |
| Containers | Docker Desktop 또는 host engine/integration | Docker CLI와 선택된 engine 접속 검증 |
| Platform exception | macOS Xcode와 iOS toolchain | iOS toolchain을 소유하지 않음 |

Herdr와 각 upstream CLI의 실제 지원 target이 이 표와 충돌하면 구현이 지원을 가장하지 않고 `unsupported` 또는 `action required`로 표시하며, 대체 경로는 별도 제품 결정으로 다룬다.

### Requirements

#### Repository Identity and Bootstrap

- **R1. Repository transition:** 현재 `settings` standalone repository를 `my-desk-setup`으로 rename하고, 기존 commit을 부모로 갖지 않는 새 기본 브랜치 이력에서 구현을 시작해야 한다.
- **R2. Recoverable rewrite:** 기존 이력 교체 전에 원격 refs와 working tree 상태를 확인하고, 독립적으로 보관 가능한 Git bundle을 만들고 검증해야 한다.
- **R3. Explicit destructive approval:** remote rename, default-branch 교체, force-push와 기존 branch 정리 같은 파괴적 동작은 대상·branch·변경·복구 경로를 제시한 별도 승인 전에는 실행하지 않아야 한다.
- **R4. Workspace link:** root workspace는 새 repository를 `projects/my-desk-setup` submodule로 연결하고 `.gitmodules` URL, path와 pointer를 함께 갱신해야 한다.
- **R5. Fresh-machine entry:** 사용자는 지원 host에서 저장소 확보 후 문서화된 소수의 OS-native bootstrap 명령으로 `plan`을 실행할 수 있어야 한다.
- **R6. Legacy exclusion:** 기존 Ansible source와 과거 설정은 참고 자료일 뿐 새 orphan history의 제품 source 또는 default profile에 자동으로 복사하지 않아야 한다.

#### Environment Intent Graph and Selection

- **R7. Single source of intent:** component identity, dependencies, target eligibility, version policy, installer ownership과 verification contract는 하나의 Environment Intent Graph에서 선언해야 한다.
- **R8. One planning path:** `all`, profile, 개별 component와 대화형 선택은 동일한 dependency resolver와 action planner를 사용해야 한다.
- **R9. Target-eligible all:** `all`은 선택한 target에서 eligible인 catalog component의 합집합이어야 하며, 모든 OS에 모든 항목을 강제 설치한다는 뜻이 아니어야 한다.
- **R10. Interactive selection:** 사람이 실행할 때 category, profile 또는 component를 탐색하고 선택할 수 있는 interactive chooser를 제공해야 한다.
- **R11. Non-interactive selection:** 자동화와 재실행을 위해 target, profile과 component를 안정된 command argument로 지정할 수 있어야 한다.
- **R12. Deterministic resolution:** 같은 catalog revision, target facts, profile과 selection은 같은 ordered action plan을 생성해야 한다.
- **R13. Single state owner:** 하나의 실행 파일, 설정 파일 또는 package state는 하나의 component adapter만 소유해야 하며, manager 간 중복 소유를 허용하지 않아야 한다.

#### Host and Guest Boundaries

- **R14. Host ownership:** macOS·Windows host profile은 WezTerm, GUI 앱, Docker Desktop 또는 host engine, 플랫폼 전용 도구와 host AI agent를 소유해야 한다.
- **R15. Guest ownership:** WSL·Lima guest profile은 CLI, language/build toolchain, Herdr, Neovim/NvChad, Docker CLI와 guest AI agent를 소유해야 한다.
- **R16. Linux development authority:** project checkout, dependency installation, compile, build, test와 primary editor work는 Linux guest에서 실행하는 구성을 기본으로 해야 한다.
- **R17. Dual agent placement:** Claude Code, OpenCode와 Codex는 host와 guest 모두 선택 가능한 catalog component여야 하며, host copy는 orchestration, guest copy는 Linux project의 직접 작업을 담당할 수 있어야 한다.
- **R18. GUI exclusion from guest:** Notion GUI, Linear GUI, Slack, KakaoTalk, Chrome와 Docker Desktop은 Linux guest의 `all`에 포함하지 않아야 한다.
- **R19. CLI distinction:** notion-cli와 linear-cli 같은 collaboration CLI는 동일 서비스의 desktop app과 별도 component로 모델링하고 Linux guest에서 선택·설치할 수 있어야 한다.
- **R20. Platform exceptions:** Xcode와 iOS build/signing은 macOS host 예외로 드러내고 Linux guest에서 지원하는 것처럼 표시하지 않아야 한다.

#### Lifecycle Commands

- **R21. Plan:** `plan`은 local state를 변경하지 않고 target facts, selection, dependency expansion, version decision, ordered actions, blockers, unsupported와 manual action을 보여줘야 한다.
- **R22. Apply:** `apply`는 확인된 desired state로 수렴해야 하며 재실행 시 이미 충족된 항목을 기능적으로 검증하고 불필요하게 다시 설치하지 않아야 한다.
- **R23. Doctor:** `doctor`는 executable, version, configuration, PATH, integration과 최소 기능 검사를 수행하고 component별 ready, blocked, unsupported 또는 action-required 결과와 해결 단서를 제공해야 한다.
- **R24. Update:** `update`는 변경 후보와 영향을 먼저 계획으로 보여주고 사용자 확인 뒤 허용된 version policy 범위에서만 새 version으로 이동해야 한다.
- **R25. No hidden mutation:** `plan`과 `doctor`는 read-only이고, `apply`와 `update`만 명시된 target state를 변경할 수 있어야 한다.
- **R26. Partial failure and resume:** 독립 component의 설치는 계속 진행할 수 있고, 실패한 node와 의존 node만 차단하며 재실행 시 성공한 node를 검증한 뒤 중단 지점부터 수렴할 수 있어야 한다.
- **R27. Action receipt:** mutation 결과는 catalog revision, target, selection, resolved versions, component outcome과 verification 결과를 secret 없이 기록해야 한다.

#### Version and Update Policy

- **R28. Pinned development core:** Java, Kotlin, Go, Python, TypeScript, C toolchain, Dart/Flutter, Gradle, uv, Bun과 Neovim/NvChad configuration은 reviewable pin 또는 lock으로 재현할 수 있어야 한다.
- **R29. Explicit latest-stable movement:** general CLI, AI agent와 GUI app은 normal `apply`에서 silently upgrade하지 않고 명시적인 `update`가 latest stable 후보를 해석할 때만 version이 이동해야 한다.
- **R30. Version transparency:** `plan`, `doctor`와 action receipt는 requested, installed와 verified version을 구분해 보여줘야 한다.
- **R31. Unsupported truthfulness:** 공식 installer나 검증 가능한 version source가 없는 target은 성공으로 추정하지 않고 unsupported 또는 manual action으로 남겨야 한다.

#### Authentication and Sensitive Data

- **R32. No auth command:** v1은 `auth`, `login` 또는 account bootstrap 명령을 제공하지 않아야 한다.
- **R33. User-owned authentication:** Claude Code, OpenCode, Codex, gh, glab, Jira, Confluence, Notion, Linear와 desktop app의 account/service 인증은 설치 이후 사용자가 각 도구에서 직접 수행해야 한다.
- **R34. No auth diagnostics:** `doctor`는 service login 상태, token 유효성 또는 organization access를 readiness 기준으로 검사하지 않아야 한다.
- **R35. No credential custody:** repository, profile, catalog, plan, log와 receipt는 API key, OAuth token, password, cookie 또는 인증 header를 수집·출력·저장하지 않아야 한다.
- **R36. Privilege boundary:** OS package 설치에 필요한 관리자 권한 상승은 실행 전에 명시하되 account/service 인증과 구분하고, 가능한 최소 범위에서 사용자가 직접 승인하도록 해야 한다.

#### Personal Adaptation and Verification

- **R37. Personal-first defaults:** 기본 catalog와 profile은 owner의 환경을 우선하며 모든 사람을 위한 public package/plugin platform을 목표로 하지 않아야 한다.
- **R38. Adaptable profiles:** 친구는 orchestration core를 fork하지 않고 profile 또는 component declaration을 조정해 자신의 조합을 만들 수 있어야 한다.
- **R39. Functional verification:** component 설치 성공은 installer exit code만으로 판정하지 않고 대표 기능을 실행하는 verification contract를 통과해야 한다.
- **R40. Target evidence:** macOS host, Windows host, WSL guest와 Lima guest의 지원 주장은 target별 plan fixture와 실제 환경의 apply/doctor evidence로 구분해 관리해야 한다.

### Key Flows

#### F1. New-machine bootstrap

1. 사용자는 지원 host에서 bootstrap entry를 실행해 repository와 최소 runtime을 준비한다.
2. 시스템은 host facts와 연결 가능한 WSL 또는 Lima guest를 탐지한다.
3. 사용자는 먼저 `plan`으로 기본 profile 또는 `all` 결과를 확인한다.
4. 사용자는 `apply`를 실행하고 OS 권한 상승과 manual action을 직접 승인한다.
5. 시스템은 설치된 component를 검증하고 secret-free receipt를 남긴다.
6. 사용자는 계정 인증이 필요한 도구에 이후 직접 로그인한다.

#### F2. All installation across host and guest

1. 사용자는 host target과 Linux guest target을 선택한다.
2. planner는 각 target의 `all` preset을 같은 graph에서 해석한다.
3. host plan에는 GUI, platform tool과 host agent가 포함된다.
4. guest plan에는 CLI, toolchain, editor, Herdr, Docker CLI와 guest agent가 포함된다.
5. guest plan에는 Notion GUI, Slack, KakaoTalk, Chrome와 Docker Desktop이 포함되지 않는다.
6. apply와 doctor는 target별 결과를 분리해 보고한다.

#### F3. Selective installation

1. 사용자는 interactive chooser 또는 component argument로 원하는 항목을 선택한다.
2. planner는 필요한 dependency만 확장한다.
3. 사용자는 unwanted component가 없는 계획을 확인한다.
4. apply는 정확한 선택과 dependency만 설치·구성·검증한다.

#### F4. Idempotent repair

1. 사용자는 이전 apply 뒤 같은 desired state로 다시 `plan` 또는 `apply`한다.
2. 시스템은 이미 검증된 state와 drift를 구분한다.
3. 만족한 component는 재설치하지 않고, missing 또는 drifted managed state만 복구한다.
4. user-owned 파일과 manager 밖의 설정은 변경하지 않는다.

#### F5. Explicit update

1. 사용자는 `update`로 eligible component의 최신 후보를 조회한다.
2. 시스템은 pin 변경, stable channel 이동, dependency 영향과 unsupported 항목을 계획으로 표시한다.
3. 사용자는 변경을 확인한 뒤 update를 승인한다.
4. 시스템은 새 version을 설치하고 기능 검증을 수행하며 새 receipt를 기록한다.
5. 실패한 component는 기존 성공 상태와 분리해 보고하고 재실행 경로를 제공한다.

#### F6. Doctor without authentication

1. 사용자는 설치 직후 또는 문제 발생 시 `doctor`를 실행한다.
2. 시스템은 executable, version, PATH, config와 local integration을 검사한다.
3. 로그인하지 않은 CLI나 agent도 설치 기능이 정상이라면 auth failure로 처리하지 않는다.
4. 사용자는 각 도구에서 필요한 계정 인증을 별도로 수행한다.

#### F7. Repository identity transition

1. 실행자는 기존 `settings` remote, branches, tags, protection과 local submodule state를 읽기 전용으로 확인한다.
2. 실행자는 모든 refs를 포함한 recovery bundle을 만들고 복원 가능성을 검사한다.
3. 실행자는 repo rename, orphan history, force-push, branch 정책과 submodule 이동을 포함한 approval packet을 제시한다.
4. 사용자 승인 뒤에만 remote history와 workspace pointer를 변경한다.
5. 새 repository는 branch/PR workflow에서 첫 구현을 시작한다.

### Acceptance Examples

- **AE1 — Target-eligible all:** macOS host와 Lima guest를 대상으로 `all`을 계획하면 host에는 GUI와 host agent가, guest에는 개발 core와 guest agent가 나타나며 guest GUI 설치 action은 0개다.
- **AE2 — CLI and app distinction:** Lima에서 `notion-cli`만 선택하면 Notion desktop app이나 다른 collaboration tool이 설치 계획에 추가되지 않는다.
- **AE3 — Windows and WSL split:** Windows host와 WSL guest를 함께 계획하면 WezTerm·desktop app·host agent는 Windows, toolchain·Neovim·guest agent는 WSL의 action으로 구분된다.
- **AE4 — Complete initial catalog:** 각 target의 `all`은 Target and Component Contract에서 eligible한 초기 component를 누락 없이 resolve하거나, 누락 원인을 unsupported/action-required로 명시한다.
- **AE5 — Repeat apply:** 같은 catalog revision과 selection으로 두 번째 apply를 실행하면 drift가 없는 component의 install action은 0개이고 verification 결과만 갱신된다.
- **AE6 — No silent upgrade:** normal apply 전에 더 최신 CLI나 agent release가 존재해도 committed policy가 바뀌지 않았다면 설치 version을 몰래 올리지 않는다.
- **AE7 — Explicit update:** update는 변경 전 old/new version과 dependency 영향을 보여주고 확인 이후에만 stable candidate를 반영한다.
- **AE8 — Functional proof:** Java, Go, Python, TypeScript, C, Dart/Flutter와 build tool은 version 출력뿐 아니라 최소 compile/run 또는 공식 doctor에 준하는 검증으로 ready를 판정한다.
- **AE9 — Authentication separation:** 인증하지 않은 gh, Notion CLI와 coding agent가 있어도 executable과 local configuration 검사가 통과하면 doctor는 account auth를 blocker로 보고하지 않는다.
- **AE10 — Partial failure:** 한 component download가 실패해도 독립 component는 계속 처리되고, 실패 component 및 그 dependency chain만 blocked로 표시된다.
- **AE11 — Dual agent placement:** 동일한 선택에서 host와 guest의 Claude Code, OpenCode와 Codex가 서로 다른 target state와 receipt로 관리된다.
- **AE12 — Recoverable history replacement:** 기존 remote를 변경하기 전 bundle에서 기존 default branch의 tip을 읽을 수 있고, 별도 clone 복구 절차가 검증되며, 사용자 재승인 전 destructive command가 실행되지 않는다.
- **AE13 — Friend adaptation:** 두 번째 사용자가 profile declaration을 바꿔 component 조합을 변경해도 planner, lifecycle command와 core source를 수정할 필요가 없다.

### Success Criteria

- macOS host, Windows host, WSL guest와 Lima guest에서 각각 `plan`이 결정적으로 생성되고 실제 target evidence가 구분되어 보관된다.
- 초기 catalog의 모든 eligible component가 `all`에서 누락 없이 설치·검증되거나 정직한 unsupported/action-required 결과를 낸다.
- component와 profile 선택 설치가 dependency 외 unwanted component를 추가하지 않는다.
- 같은 desired state의 두 번째 apply가 user-visible state를 불필요하게 변경하지 않는다.
- normal apply가 version을 몰래 올리지 않고 explicit update만 version movement를 일으킨다.
- doctor가 최소 기능 실패를 발견하지만 account authentication 상태를 검사하거나 credential을 요구하지 않는다.
- host와 guest의 역할 경계가 plan, receipt와 documentation에서 일관되게 보인다.
- 친구가 core code 변경 없이 자신의 profile과 component 조합을 만들 수 있다.
- 기존 `settings` 이력은 검증된 recovery bundle로 복원 가능하고, 새 `my-desk-setup` 이력에는 legacy implementation이 섞이지 않는다.

### Scope Boundaries

#### Deferred

- managed component 제거와 `remove` 명령
- offline installer bundle과 package cache 운반
- enterprise policy, 다중 사용자 fleet, 중앙 배포와 원격 machine management
- public profile registry, third-party plugin marketplace와 호환성 보증
- host-native editor/toolchain을 Linux guest와 동등한 primary development environment로 운영하는 기능
- 모든 manual GUI 설정과 app onboarding을 자동화하는 기능

#### Outside Product Identity

- account/service 로그인, OAuth consent, organization 연결과 token lifecycle 관리
- credential manager 또는 secrets vault
- project별 language version, dependency와 build recipe를 대신 소유하는 기능
- WSL, Lima, Docker, Xcode 자체를 재구현하는 virtualization/container/build platform
- 지원되지 않는 upstream artifact를 비공식 mirror 또는 임의 binary로 대체하는 기능

### Dependencies and Assumptions

- 사용자는 macOS 또는 Windows의 local administrator이며 필요한 OS 권한 상승을 직접 승인할 수 있다.
- Windows에서는 WSL2, macOS에서는 Lima를 Linux guest로 사용할 수 있거나 bootstrap 범위에서 공식 설치 경로를 선택할 수 있다.
- machine bootstrap pin과 project-level tool version은 서로 다른 책임이며, project repository의 더 구체적인 version declaration이 우선한다.
- package acquisition은 각 tool의 공식 release, 공식 package manager 또는 검증 가능한 upstream channel을 사용한다.
- 인터넷 연결이 가능한 fresh-machine 설치를 v1 기준으로 삼는다.
- GUI app은 OS package manager 정책, store 제한 또는 사용자 상호작용 때문에 일부 단계가 manual action으로 남을 수 있다.
- Docker Desktop host와 guest Docker CLI 사이의 engine 접근은 target별 공식 integration을 따른다.
- 프로젝트 repository의 변경은 ticket, branch, PR과 review gate를 따르며 project `main`에 직접 commit/push하지 않는다.

### Outstanding Questions

#### Deferred to Planning

- `my-desk-setup`의 구현 언어와 bootstrap 최소 dependency를 무엇으로 정할 것인가?
- Environment Intent Graph와 profile/component schema를 어떤 파일 형식과 validation 방식으로 표현할 것인가?
- macOS·Windows·WSL·Lima에서 package manager와 configuration adapter의 정확한 ownership map은 무엇인가?
- `apply`와 `update`가 방금 확인한 plan을 동일한 내용으로 적용했음을 보장하는 confirmation/digest 계약은 무엇인가?
- WSL과 Lima guest의 Docker CLI가 host engine을 사용할지 guest-local engine을 사용할지 target별 정책은 무엇인가?
- 각 component가 ready로 판정되기 위한 최소 기능 검사는 무엇인가?
- GitHub repository rename과 orphan default-branch 교체를 어떤 순서와 복구 절차로 수행할 것인가?

#### Explicitly Deferred Questions

- `remove`가 dependency와 user-owned state를 어떻게 보존할 것인가?
- offline bundle을 신뢰 가능한 provenance와 함께 어떻게 만들 것인가?
- 제3자가 component adapter를 배포하는 public extension model이 필요한가?

### Sources and Research

#### Local Sources

- `.gitmodules`: 현재 `projects/settings` standalone repository의 path, URL과 branch
- `projects/settings/README.md`: 기존 Ansible 기반 macOS·Linux entry flow
- `projects/settings/playbooks/mac.yml`
- `projects/settings/playbooks/linux.yml`
- `projects/settings/playbooks/windows.yml`
- `projects/settings/roles/packages/tasks/neovim.yml`
- `projects/settings/roles/packages/tasks/neovim_config.yml`
- `projects/oh-my-harness/CONCEPTS.md`: Environment Profile, Capability Catalog, exact preview와 secret-free receipt 선례
- `projects/oh-my-harness/src/planning/preview.ts`
- `projects/oh-my-harness/src/planning/apply.ts`
- `projects/oh-my-harness/AGENTS.md`: profile/catalog/preview-first 운영 규칙
- `docs/solutions/workflow-issues/independent-projects-as-standalone-repos-submodules.md`
- `AGENTS.md`: project repository branch/PR, review, merge와 artifact path guardrail
- `CONCEPTS.md`: Standalone Project, Workspace Submodule과 Submodule Pointer

#### External Sources

- [chezmoi User Guide](https://www.chezmoi.io/user-guide/command-overview/): cross-platform dotfile templating과 apply model
- [mise Documentation](https://mise.jdx.dev/): cross-platform development tool version and task management
- [Homebrew Bundle](https://docs.brew.sh/Brew-Bundle-and-Brewfile): macOS package/app declaration
- [WinGet Configuration](https://learn.microsoft.com/windows/package-manager/configuration/): Windows desired-state configuration
- [Development Containers Specification](https://containers.dev/implementors/spec/): project-scoped Linux development environment contract
- [Herdr](https://github.com/herdr/herdr): agent-aware terminal multiplexer의 upstream source
