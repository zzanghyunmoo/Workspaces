---
date: 2026-07-03
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
execution: code
source_ideation: >-
  docs/ideation/2026-07-03-sokoban-csharp-foundation-lab-ideation.html
---

# Sokoban C# Foundation Curriculum - Requirements

## Goal Capsule

- **Objective:** `projects/dotnet-foundation-lab`를 Sokoban을 만들며 C# 기본
  프로그래밍, TDD, 객체지향, DDD-lite를 단계적으로 익히는 학습 repo로
  정리한다.
- **Product authority:** 사용자의 학습 운영 원칙이 우선한다. 매일 1시간,
  공식 문서 기반, 간단 예제 후 프로젝트 적용, 프로젝트 코드는 TDD-first다.
- **Open blockers:** 실제 코드/solution 생성은 이 문서 범위가 아니다. 구현
  브랜치 시작 전 ce-plan 또는 별도 작업 계획이 필요하다.

---

## Product Contract

### Summary

Sokoban C# Foundation Curriculum은 Microsoft Learn 기반의 C# 기본 문법 학습을
작은 예제로 먼저 익히고, 같은 개념을 Sokoban 프로젝트 코드에 TDD-first로
적용하는 학습 시스템이다.
커리큘럼은 절차지향 코드에서 시작해 불편함이 생기는 지점마다 객체지향과
DDD-lite로 리팩터링하며, 이후 자료구조/알고리즘, 네트워크, 데이터베이스,
디자인 패턴 확장 트랙으로 이어진다.

### Problem Frame

사용자는 만들면서 배우는 방식을 선호하지만, 곧장 프로젝트 구현으로 들어가면
C# 기본 문법과 .NET 생태계의 기초가 빈 채로 넘어갈 수 있다.
반대로 공식 문서와 예제만 따라가면 학습이 제품적 맥락과 분리되어 오래 지속되기
어렵다.
이 커리큘럼은 공식 문서의 신뢰도와 프로젝트 기반 학습의 몰입감을 연결한다.

### Key Decisions

- **KD1. Sokoban is the foundation project.** Sokoban은 턴 기반 격자
  퍼즐이라 실시간 루프와 UI 부담 없이 배열, 좌표, 이동 규칙, 충돌 판정,
  승리 조건, 테스트 가능한 순수 로직을 다룰 수 있다.
- **KD2. Microsoft Learn is the syntax authority.** C# 기본 문법,
  객체지향, 비동기, 테스트 기초는 Microsoft 공식 문서를 기준 출처로 삼는다.
- **KD3. Examples and project code use different quality gates.** 작은 문법
  예제는 빠르게 실험해도 되지만, Sokoban 프로젝트 코드는 테스트를 먼저
  작성하는 TDD-first 흐름을 따른다.
- **KD4. Procedural code comes first.** 초반에는 절차지향 코드로 시작하고,
  중복·상태 복잡도·테스트 불편함이 생길 때 객체지향과 DDD-lite로 전환한다.
- **KD5. Expansion topics are pressure-driven.** 자료구조/알고리즘,
  네트워크, 데이터베이스, 디자인 패턴은 별도 이론 단원으로 던지지 않고
  Sokoban에서 필요가 생길 때 확장 트랙으로 도입한다.

### Requirements

#### Chapter contract

- R1. 각 챕터는 `MS Learn 공식 문서 확인 → 작은 예제 → Sokoban 프로젝트
  적용 → 회고` 순서를 따라야 한다.
- R2. 각 챕터는 해당 C# 개념에 대응하는 Microsoft Learn 공식 문서 링크를
  포함해야 한다.
- R3. 작은 예제는 프로젝트 코드보다 앞에 위치해야 하며, 개념을 최소 단위로
  관찰할 수 있어야 한다.
- R4. Sokoban 적용 단계는 해당 개념이 게임 규칙, 상태, 입력, 출력, 테스트 중
  어디에 쓰이는지 설명해야 한다.
- R5. 각 챕터는 “왜 이전 구조보다 나은가”를 기록하는 회고 질문을 포함해야
  한다.

#### TDD policy

- R6. 문법 탐색용 작은 예제에는 TDD를 강제하지 않는다.
- R7. Sokoban 프로젝트의 규칙, 파서, 상태 전이, 승리 조건, validation은
  테스트를 먼저 작성해야 한다.
- R8. 테스트는 UI나 콘솔 입출력보다 domain logic을 우선 검증해야 한다.
- R9. 테스트 이름은 게임 규칙을 설명하는 문장으로 읽혀야 한다.
- R10. 회귀가 발견되면 해당 사례를 regression test로 남기는 흐름을 챕터에
  포함해야 한다.

#### Procedural to OOP progression

- R11. 초반 챕터는 `string`, `char[,]`, 좌표 변수, 조건문, 반복문, 메서드
  중심의 절차지향 구현을 허용해야 한다.
- R12. 객체지향 전환은 중복, 상태 꼬임, 테스트 어려움 같은 학습자가 관찰
  가능한 불편함 뒤에 제시해야 한다.
- R13. `Position`, `Direction`, `Board`, `MoveResult`, `GameState` 같은
  이름은 필요가 생기는 순간 도입해야 한다.
- R14. DDD-lite는 폴더 구조가 아니라 도메인 언어를 코드에 반영하는
  리팩터링으로 설명해야 한다.
- R15. Repository, Domain Service, Domain Event 같은 무거운 DDD 개념은 초반
  본편에서 강제하지 않아야 한다.

#### Branch model

- R16. `main`은 커리큘럼, 로드맵, 문서 인덱스를 유지하고 직접 구현 브랜치로
  사용하지 않아야 한다.
- R17. 구현 브랜치는 학습 스냅샷으로 사용하며, 브랜치 이름은 학습 축과
  챕터를 드러내야 한다.
- R18. 기본 브랜치 축은 `base`, `csharp`, `tdd`, `oop`, `datastructure`,
  `algorithm`, `network`, `database`, `patterns`를 기준으로 한다.
- R19. 브랜치는 너무 작은 문법 하나마다 만들지 않고, 학습자가 diff로 의미
  있는 전환을 볼 수 있는 단위로 제한해야 한다.
- R20. 각 구현 브랜치는 해당 브랜치에서 배운 개념, 이전 구조의 한계, 다음
  확장 지점을 기록해야 한다.

#### Expansion runway

- R21. 자료구조 확장은 Sokoban 충돌 판정, 위치 조회, undo, solver 같은
  필요에서 출발해야 한다.
- R22. 알고리즘 확장은 map validation, BFS solver, deadlock detection처럼
  Sokoban 문제 해결과 연결되어야 한다.
- R23. 네트워크 확장은 레벨 다운로드, 점수 제출, timeout/retry 같은 명확한
  학습 목적이 생긴 뒤 도입해야 한다.
- R24. 데이터베이스 확장은 클리어 기록, 진행 상황, 레벨 메타데이터 저장 같은
  요구가 생긴 뒤 도입해야 한다.
- R25. 디자인 패턴은 먼저 문제를 겪은 뒤 Command, State, Strategy 같은 이름을
  붙이는 방식으로 소개해야 한다.

### Key Flows

- F1. **Daily learning loop**
  - **Trigger:** 사용자가 매일 1시간 학습을 시작한다.
  - **Steps:** 이전 노트를 읽고, MS Learn 개념을 확인하고, 작은 예제를
    실험하고, Sokoban 적용 항목을 TDD-first로 진행하고, 회고를 기록한다.
  - **Outcome:** 하루 학습 결과가 코드 변화 또는 노트로 남고 다음 1시간
    작업이 분명해진다.
  - **Covers:** R1, R2, R3, R5, R6, R7

- F2. **Concept application loop**
  - **Trigger:** 새로운 C# 문법 또는 .NET 개념을 배운다.
  - **Steps:** 공식 문서에서 개념을 확인하고, 작은 예제에서 동작을 관찰하고,
    Sokoban에서 해당 개념이 필요한 위치를 찾고, 테스트로 기대 동작을 고정한다.
  - **Outcome:** 개념이 암기가 아니라 프로젝트 맥락 안에서 사용된다.
  - **Covers:** R1, R4, R7, R8

- F3. **Refactoring transition loop**
  - **Trigger:** 절차지향 구현에서 중복, 상태 꼬임, 테스트 어려움이 관찰된다.
  - **Steps:** 불편함을 노트에 적고, 새 도메인 이름을 붙이고, 기존 테스트를
    유지한 채 구조를 바꾸고, 왜 나아졌는지 회고한다.
  - **Outcome:** 객체지향과 DDD-lite가 이론이 아니라 필요에 의한 전환으로
    학습된다.
  - **Covers:** R11, R12, R13, R14

- F4. **Expansion track loop**
  - **Trigger:** 본편 Sokoban 구현이 특정 개념 없이는 불편하거나 기능 확장이
    막힌다.
  - **Steps:** 문제를 명명하고, 필요한 개념을 고르고, 별도 확장 브랜치에서
    적용하고, 본편과 확장 트랙의 차이를 기록한다.
  - **Outcome:** 자료구조/알고리즘/네트워크/DB/패턴이 Sokoban에서 자연스럽게
    확장된다.
  - **Covers:** R21, R22, R23, R24, R25

### Acceptance Examples

- AE1. **Chapter structure**
  - **Given:** 사용자가 `csharp/ch01` 챕터를 연다.
  - **When:** 챕터 문서를 읽는다.
  - **Then:** Microsoft Learn 링크, 작은 예제, Sokoban 적용 과제, 회고 질문을
    모두 확인할 수 있다.
  - **Covers:** R1, R2, R3, R5

- AE2. **Project code uses TDD**
  - **Given:** 사용자가 Sokoban 이동 규칙을 구현하려 한다.
  - **When:** 브랜치의 작업 순서를 확인한다.
  - **Then:** 벽 이동 불가, 상자 밀기, 승리 조건 같은 테스트가 구현보다 먼저
    요구된다.
  - **Covers:** R7, R8, R9

- AE3. **Procedural first is allowed**
  - **Given:** 사용자가 초반 `base` 브랜치를 진행한다.
  - **When:** 구현 접근을 확인한다.
  - **Then:** `char[,]`, 조건문, 반복문, 메서드 중심의 단순 절차형 구현이
    허용된다.
  - **Covers:** R11

- AE4. **OOP transition has a reason**
  - **Given:** 사용자가 `oop` 브랜치로 넘어간다.
  - **When:** 전환 근거를 확인한다.
  - **Then:** 어떤 불편함 때문에 `Position`, `Board`, `GameState` 같은 개념이
    생겼는지 설명되어 있다.
  - **Covers:** R12, R13, R14

- AE5. **Expansion remains connected**
  - **Given:** 사용자가 `algorithm/ch01-bfs-solver` 같은 확장 브랜치를 연다.
  - **When:** 챕터 목표를 확인한다.
  - **Then:** BFS가 추상 알고리즘 문제가 아니라 Sokoban solver 필요에서
    등장했다는 설명이 있다.
  - **Covers:** R21, R22

### Success Criteria

- S1. 사용자는 하루 1시간 단위로 다음 학습 행동을 정할 수 있다.
- S2. 각 챕터는 공식 문서 기반 개념과 Sokoban 적용 사이의 연결을 보여준다.
- S3. Sokoban 프로젝트 코드는 테스트가 학습 흐름의 일부로 남는다.
- S4. 절차지향에서 객체지향으로 넘어가는 이유가 코드 변화와 회고로 설명된다.
- S5. 확장 트랙은 본편을 흐리지 않고 자료구조/알고리즘, 네트워크, DB,
  디자인 패턴 학습으로 이어진다.

### Scope Boundaries

#### In scope

- C# 기본 문법 학습 커리큘럼 구조
- Sokoban 프로젝트 기반 적용 흐름
- TDD-first 프로젝트 코드 정책
- 절차지향에서 객체지향/DDD-lite로 이동하는 학습 설계
- 브랜치 네이밍과 확장 축의 요구사항

#### Deferred for later

- 실제 .NET solution/project 생성
- 각 브랜치의 구체 구현 계획
- 챕터별 상세 일일 일정표
- Blazor, GUI, Unity 등 UI 구현
- DB schema, API endpoint, 파일 구조 같은 구현 상세

#### Outside this curriculum's identity

- SRE AI Lab 제품 개발
- 경제/금융 콘텐츠 프로젝트
- 완성형 게임 출시 목적의 게임 개발

### Dependencies / Assumptions

- A1. 사용자는 C# 기본 문법의 기준 자료로 Microsoft Learn을 따른다.
- A2. 사용자는 매일 1시간 학습 리듬을 유지한다.
- A3. `projects/dotnet-foundation-lab`의 `main`은 구현보다 문서와 커리큘럼
  중심으로 유지한다.
- A4. 실제 구현은 별도 브랜치에서 진행한다.
- A5. 코드 생성은 이 requirements-only 문서의 범위가 아니다.

### Outstanding Questions

#### Resolve before planning

- OQ1. 첫 구현 브랜치를 `base/ch01-string-map`으로 시작할지,
  `csharp/ch01-console-variables-io`로 시작할지 결정해야 한다.
- OQ2. 챕터 문서를 repo root의 `docs/`에 둘지, 각 브랜치별 README 중심으로
  둘지 결정해야 한다.

#### Deferred to planning

- OQ3. 실제 테스트 프레임워크와 프로젝트 구조를 어떤 순서로 도입할지 계획해야
  한다.
- OQ4. Microsoft Learn 링크 목록을 챕터별로 어떤 문서에 관리할지 정해야 한다.
- OQ5. 브랜치 완료 기준과 태그 전략을 정해야 한다.

### Sources / Research

- `projects/dotnet-foundation-lab/README.md`
- `projects/dotnet-foundation-lab/docs/project-kata-roadmap.md`
- `docs/ideation/2026-07-03-sokoban-csharp-foundation-lab-ideation.html`
- Microsoft Learn: C# tour and tutorials
- Microsoft Learn: C# object-oriented programming fundamentals
- Microsoft Learn: .NET unit testing with xUnit and `dotnet test`
