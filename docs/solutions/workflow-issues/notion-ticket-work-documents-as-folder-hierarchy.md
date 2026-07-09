---
title: Notion 티켓 작업 문서는 폴더형 계층으로 만든다
date: 2026-07-09
category: workflow-issues
module: replaceme-notion-workspace
problem_type: workflow_issue
component: documentation
severity: medium
applies_when:
  - "Creating or updating Notion work documents for a Linear ticket or work item"
  - "Ticket content has grown beyond a concise summary and link collection"
  - "Lifecycle-specific notes need to stay navigable across ideation, planning, development, validation, and follow-up"
symptoms:
  - "Ticket documentation is captured as one long monolithic Notion page"
  - "Repeated QA or runbook content is placed under ticket pages instead of the Operator Guide"
  - "Parent and child page ancestry is not verified after reorganizing Notion docs"
root_cause: missing_workflow_step
resolution_type: workflow_improvement
related_components:
  - development_workflow
  - notion-ticket-docs
  - linear-ticket-sync
tags:
  - notion
  - ticket-docs
  - folder-hierarchy
  - external-work-surface-sync
  - operator-guide
---

# Notion 티켓 작업 문서는 폴더형 계층으로 만든다

## Context

ReplaceMe Notion 티켓 문서는 긴 단일 페이지가 아니라, 부모 페이지를 목차 겸
폴더로 두고 단계별 하위 페이지를 붙이는 구조가 맞다. 이 학습은 ZZA-56과
ZZA-57 Notion 티켓 페이지를 보강하는 과정에서 드러났다. 처음에는 각 티켓
문서에 아이디에이션, 범위 결정, 플랜, 개발 내용, 검증 결과를 한 페이지에 계속
붙였고, 사용자는 “폴더 형태로 만들어줘야지?”라고 바로잡았다.

복구하면서 채택한 구조는 두 티켓 부모 페이지를 `ReplaceMe / DevAutomation 프로젝트 위키
> 개발 문서 > 티켓` 아래의 간결한 index page로 두는 것이다. “ZZA-56 Run Passport
minimum schema/interface”와 “ZZA-57 Dev Docker broker image fix” 같은 부모 페이지는
요약, Linear 링크, GitHub PR 링크, 핵심 결정, 현재 상태 또는 계약 요약, child page
목차만 담는다. 상세한 lifecycle 내용은 “01 아이디에이션”, “02 브레인스토밍과 범위
결정”, “03 구현 플랜”, “04 개발 내용”, “05 검증과 현재 상태” 같은 child page에 둔다.

세션 히스토리에서도 같은 방향의 전조가 있었다. 이전 작업은 로컬 ideation/plan/QA
산출물을 만들고, ZZA-51 아래에 QA child folder를 두는 방식으로 Notion hierarchy를
맞추려 했다(session history). 이후 운영자 가이드가 생기면서 QA/runbook은 ticket
work page가 아니라 operator guide 아래에 두는 것이 더 정확해졌다(session history).
따라서 이 문서는 두 규칙을 분리한다. 티켓 작업 문서는 ticket parent 아래에
folder-shaped child pages로 둔다. 반복 QA/runbook 문서는 `가이드 > 운영자 가이드 >
QA 문서` 아래에 둔다.

이 학습은 `docs/solutions/workflow-issues/notion-operator-guide-qa-document-hierarchy.md`와
상호 보완된다. 그 문서는 QA 문서의 owning surface를 설명하고, 이 문서는 티켓
작업 문서 자체의 page shape를 설명한다.

## Guidance

Linear ticket이나 work item에 대응하는 Notion 문서를 만들 때는 먼저 티켓 부모
페이지를 `개발 문서 > 티켓` 아래에 만들거나 재사용한다. 그 부모 페이지는 폴더이자
목차다. “이 티켓은 무엇이고, 관련 work surface는 어디이며, 어떤 결정이 중요하고,
다음에 어디를 보면 되는가?”를 짧게 답해야 한다. 아이디에이션, 전체 플랜, 구현
상세, 검증 로그, follow-up 진단을 모두 한 body에 이어 붙이지 않는다.

부모 페이지에는 다음만 남긴다.

- 티켓 제목과 짧은 요약
- Linear issue 링크
- GitHub PR 링크, 특히 문서/코드 분리 또는 stacked PR 관계
- 핵심 결정과 명시적 non-goals
- 현재 상태 또는 핵심 contract 요약
- 하위 페이지 목차

단계별 내용은 숫자 prefix가 붙은 child page로 나눈다. 기본 형태는 다음과 같다.

- `01 아이디에이션`
- `02 브레인스토밍과 범위 결정` 또는 `02 브레인스토밍과 선택지`
- `03 구현 플랜`
- `04 개발 내용`
- `05 검증과 현재 상태`
- 필요하면 `06 NuGet Docker build 진단`, `07 후속 작업`처럼 focused child page 추가

페이지를 만든 뒤에는 Notion fetch 결과가 parent chain을 제공하는 도구에서 부모
페이지와 대표 child page의 `ancestor-path`를 확인한다. 이번 세션에서는 Notion MCP
fetch 결과의 `ancestor-path`를 사용했다. 기대 형태는 다음과 같다.

```text
ReplaceMe / DevAutomation 프로젝트 위키
└─ 개발 문서
   └─ 티켓
      └─ <ticket id + ticket title>
         └─ 01 아이디에이션
```

이미 다른 위치에 만든 페이지가 있다면 새 placeholder를 만들기보다 move나 명확한
link로 정리한다. Notion page는 title만 맞아도 검색 결과에서는 그럴듯하게 보이기
때문에, ancestry 확인 없이 “찾았다”고 판단하면 같은 이름의 문서가 여러 곳에
흩어질 수 있다.

운영 문서와의 경계도 같이 지킨다. Ticket child page에는 “이 티켓에서 어떤 QA를
실행했고 결과가 무엇이었는지”를 기록할 수 있다. 하지만 canonical QA runbook 자체는
티켓 folder로 복사하지 않는다. 반복 실행 절차, health check, provider smoke test,
장애 대응 runbook은 운영자 가이드 아래의 QA 문서로 관리하고, ticket page에서는
그 결과와 링크만 남긴다.

## Why This Matters

Notion hierarchy는 문서의 의미를 결정한다. 긴 단일 티켓 페이지는 초반 아이디어,
최종 scope, 구현 상세, 검증 결과, 후속 진단이 한 scroll 안에서 경쟁하게 만든다.
리뷰어는 지금 필요한 stage를 찾기 어렵고, 다음 에이전트는 어디에 새 내용을
붙여야 할지 판단하기 어렵다. 반대로 folder-shaped ticket page는 parent를 안정적인
entry point로 만들고, 각 stage를 독립적으로 읽고 갱신할 수 있게 한다.

소유권도 분리된다. Ticket work document는 한 work item의 기억이다. Operator QA
문서는 반복 실행 절차다. 이 둘을 ticket page 아래에 섞으면 티켓이 끝난 뒤에도
운영자가 runbook을 찾기 어렵고, 다음 ticket에서는 같은 QA 절차를 다시 만들게 된다.
Ticket page는 work item의 결정과 결과를 담고, Operator Guide는 반복 절차를 담는
구조가 External Work Surface Sync를 더 안정적으로 만든다.

Ancestor verification은 duplication을 막는 마지막 안전장치다. `ZZA-56 ... > 01
아이디에이션`처럼 보이는 페이지가 실제로 ZZA-56 parent 아래에 있는지 확인해야
한다. 위치가 틀린 문서는 title만 맞아도 나중에 stale work surface가 된다.

## When to Apply

이 지침은 ReplaceMe workspace에서 Linear ticket, GitHub PR pair, 또는 자동화 work
item에 대응하는 Notion ticket document를 만들거나 갱신할 때 적용한다. 특히 다음
상황에서 필요하다.

- `개발 문서 > 티켓` 아래에 새 ticket page를 만들 때
- 구현이나 review 뒤 기존 ticket page를 보강할 때
- 문서 PR과 코드 PR을 나눈 ticket의 Notion 상태를 갱신할 때
- 아이디에이션, scope decision, plan, implementation, validation, follow-up이 모두
  필요한 ticket일 때
- title은 맞지만 Notion ancestry가 애매한 페이지를 정리할 때
- focused diagnostic page가 필요하지만 parent summary를 장황하게 만들고 싶지 않을 때

반대로 반복 QA/runbook 자체를 ticket folder로 옮기는 데 이 지침을 쓰면 안 된다.
그런 내용은 `가이드 > 운영자 가이드 > QA 문서`가 canonical home이다. Ticket page에는
해당 QA를 실행했다는 결과와 링크만 남긴다.

## Examples

ZZA-56의 좋은 구조는 다음과 같다.

```text
ReplaceMe / DevAutomation 프로젝트 위키
└─ 개발 문서
   └─ 티켓
      └─ ZZA-56 Run Passport minimum schema/interface
         ├─ 01 아이디에이션
         ├─ 02 브레인스토밍과 범위 결정
         ├─ 03 구현 플랜
         ├─ 04 개발 내용
         └─ 05 검증과 현재 상태
```

ZZA-56 parent page에는 간단한 summary, Linear link, PR #9/#8 링크, 핵심 결정,
Run Passport v0 contract 요약, child page 목차만 둔다. 구현 상세와 검증 결과는
각 child page가 소유한다.

ZZA-57의 좋은 구조는 다음과 같다.

```text
ReplaceMe / DevAutomation 프로젝트 위키
└─ 개발 문서
   └─ 티켓
      └─ ZZA-57 Dev Docker broker image fix
         ├─ 01 아이디에이션
         ├─ 02 브레인스토밍과 선택지
         ├─ 03 구현 플랜
         ├─ 04 개발 내용
         ├─ 05 검증과 추가 발견
         ├─ 06 NuGet Docker build 진단
         └─ 07 후속 작업
```

ZZA-57 parent page는 summary, Linear link, PR #10/#11 링크, key decisions, current
status, child table of contents만 가진다. NuGet Docker build 진단은 parent page의
appendix가 아니라 focused child page로 둔다.

피해야 할 구조는 다음과 같다.

```text
개발 문서
└─ 티켓
   └─ ZZA-57 Dev Docker broker image fix
      └─ one very long page containing ideation, brainstorm, plan,
         implementation notes, validation, NuGet diagnosis,
         follow-up tasks, and copied QA runbook content
```

또한 다음처럼 QA runbook의 canonical home을 ticket folder로 만드는 것도 피한다.

```text
개발 문서
└─ 티켓
   └─ ZZA-57 Dev Docker broker image fix
      └─ QA 문서
         ├─ QA 00. 로컬 실행과 Health Check
         └─ QA 01. provider smoke test
```

Ticket에는 QA 실행 결과를 남기고, 반복 절차는 `운영자 가이드 > QA 문서`로 링크한다.

## Related

- `docs/solutions/workflow-issues/notion-operator-guide-qa-document-hierarchy.md` — QA/runbook 문서는 운영자 가이드 아래에 둔다.
- `docs/solutions/conventions/ticket-code-doc-pr-split-and-tracker-sync.md` — GitHub PR, Linear, Notion을 한 ticket context로 동기화한다.
- `docs/solutions/workflow-issues/run-passport-contract-before-dependent-follow-ups.md` — Run Passport 계약을 downstream Notion/PR 작업 전에 먼저 고정한다.
- `docs/solutions/workflow-issues/split-oversized-integration-pr-into-deployable-stacked-prs.md` — oversized work surface를 reviewable slice로 나누는 유사한 anti-monolith workflow.
