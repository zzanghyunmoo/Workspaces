---
title: Notion 인프라 아이디에이션은 배경에, 실행 계획은 개발 문서 계획 폴더에 둔다
date: 2026-07-13
category: workflow-issues
module: replaceme-notion-workspace
problem_type: workflow_issue
component: documentation
severity: medium
applies_when:
  - "ReplaceMe Notion workspace에서 아이디에이션과 실행 계획을 동시에 정리할 때"
  - "프로젝트 루트에 임시 계획 문서가 생겨 문서 구조가 흐트러졌을 때"
  - "Linear 티켓 선후관계와 아키텍처 배경을 같은 문서에 섞을지 판단할 때"
symptoms:
  - "인프라 아키텍처 판단과 티켓 실행 순서가 같은 Notion 문서에 섞인다"
  - "프로젝트 루트 아래에 임시 로드맵 문서가 생겨 배경/개발 문서 taxonomy를 우회한다"
  - "날짜별 실행 계획이 개발 문서 아래에서 찾기 어렵다"
root_cause: missing_workflow_step
resolution_type: workflow_improvement
tags: [notion, ideation, planning, documentation-hierarchy, replaceme, linear]
related_components: [development_workflow, notion-workspace, linear-ticket-sync]
---

<!-- markdownlint-disable MD013 MD025 -->

# Notion 인프라 아이디에이션은 배경에, 실행 계획은 개발 문서 계획 폴더에 둔다

## Context

ReplaceMe 인프라 로드맵을 정리하면서 처음에는 `ReplaceMe / DevAutomation 프로젝트 위키` 루트 아래에 `ReplaceMe 인프라 로드맵과 티켓 선후관계` 문서를 만들었다. 내용은 유용했지만 문서 성격이 섞여 있었다. Langfuse, LiteLLM, OTel Collector, Docker socket hardening 같은 인프라 아키텍처 판단은 왜 이 방향을 택하는지 설명하는 배경/아이디에이션이고, ZZA-58부터 ZZA-64와 ZZA-52/55/53/54를 어떤 순서로 진행할지는 개발 실행 계획이다.

사용자는 이 구분을 바로잡았다. 인프라 아키텍처는 `배경` 쪽에 있어야 하고, 실행 계획은 `개발 문서` 하위에 `계획` 폴더를 만들어 오늘 날짜 문서로 남기면 된다는 피드백이었다. 이에 따라 Notion 문서를 두 개로 분리했다.

- `배경 > 인프라 아키텍처 아이디에이션` — 문제의식, 현재 구조, 권장 아키텍처 방향, 핵심 결정을 담는다.
- `개발 문서 > 계획 > 2026-07-13 인프라 로드맵과 티켓 선후관계` — 실행 순서, dependency map, 티켓별 역할, 운영 규칙을 담는다.

루트에 처음 만든 임시 문서는 삭제하지 않고 `이동됨 - ReplaceMe 인프라 로드맵과 티켓 선후관계`로 바꿔 canonical 문서 두 개를 가리키게 했다. 로컬 계획 문서 `projects/ReplaceMe/docs/plans/2026-07-13-001-feat-infra-foundation-roadmap-plan.md`와 Linear 프로젝트 댓글도 새 Notion 링크를 가리키도록 갱신했다.

## Guidance

ReplaceMe Notion에서 아이디에이션과 실행 계획이 동시에 생기면 먼저 문서의 성격을 둘로 나눈다.

**배경 문서**는 “왜 이 방향인가?”를 답한다. 프로젝트 요구사항, 문제의식, 아이디에이션, 초기 범위, 아키텍처 선택지, adoption/hold/reject 판단은 `배경` 아래에 둔다. 이번 인프라 작업에서는 다음이 배경 문서에 속했다.

- 현재 ReplaceMe runtime 구조
- API와 worker가 묶여 있을 때의 문제
- Kafka retry/DLQ가 필요한 이유
- OTel과 Langfuse의 역할 분리
- LiteLLM을 spike로만 다루는 이유
- Docker socket runner를 local-only로 보는 이유

**계획 문서**는 “어떤 순서로 진행할 것인가?”를 답한다. 날짜가 붙은 실행 계획, 티켓 dependency, phase, 티켓별 역할, 운영 순서는 `개발 문서 > 계획` 아래에 둔다. 제목은 `YYYY-MM-DD 주제` 형식으로 둔다.

문서 작성 순서는 다음과 같다.

1. Notion에서 `배경`과 `개발 문서`의 existing child structure를 fetch해 확인한다.
2. `개발 문서` 아래에 `계획` 폴더가 없으면 먼저 만든다.
3. 아이디에이션/아키텍처 배경은 `배경` 아래 focused page로 만든다.
4. 실행 순서와 티켓 선후관계는 `개발 문서 > 계획` 아래 날짜별 page로 만든다.
5. 처음 잘못 만든 루트 문서가 있으면 canonical 문서 링크를 담은 이동 안내로 바꾸거나, 가능한 경우 move한다.
6. Linear 프로젝트 댓글과 로컬 plan 문서가 새 canonical Notion 문서를 가리키게 맞춘다.

새 계획 문서를 만들 때는 문서 body에 다시 긴 아키텍처 배경을 붙이지 않는다. 대신 `배경 > <아이디에이션 문서>` 링크를 두고, 실행 순서와 dependency map만 유지한다.

## Why This Matters

Notion의 위치는 문서의 의미를 결정한다. 루트 아래에 로드맵 문서가 바로 생기면 일시적으로는 찾기 쉽지만, 시간이 지나면 `배경`, `디자인 문서`, `개발 문서`, `가이드`라는 프로젝트 위키 taxonomy를 우회한 예외가 된다. 예외 문서는 다음 에이전트가 따라 하기 쉽고, 같은 주제의 후속 문서가 여러 위치에 흩어질 가능성이 높다.

아키텍처 배경과 실행 계획을 분리하면 읽는 목적도 선명해진다. Langfuse와 LiteLLM의 역할 판단을 다시 보고 싶으면 `배경`을 보면 된다. 오늘 어떤 티켓부터 진행해야 하는지 알고 싶으면 `개발 문서 > 계획`을 보면 된다. Linear 댓글과 로컬 plan은 실행 관리를 돕고, Notion 배경 문서는 왜 그 실행 순서가 맞는지를 보존한다.

이 규칙은 기존 Notion ticket document hierarchy 규칙과도 맞물린다. 티켓 작업 문서는 `개발 문서 > 티켓` 아래 folder-shaped hierarchy로 두고, 반복 QA/runbook은 운영자 가이드 아래에 둔다. 여기에 더해, cross-ticket roadmap과 dependency plan은 `개발 문서 > 계획` 아래에 둔다. 즉 `개발 문서` 안에서도 티켓별 작업 기억과 날짜별 실행 계획을 섞지 않는다.

## When to Apply

- Notion에 새 인프라 로드맵, 아키텍처 아이디에이션, 실행 순서 문서를 만들 때.
- Linear 티켓 묶음의 선후관계를 정리하면서 배경 설명도 같이 필요할 때.
- 루트 위키 페이지 아래에 임시 문서가 생겼고, 위키 taxonomy에 맞게 재배치해야 할 때.
- `배경`, `개발 문서`, `디자인 문서`, `가이드` 중 어디에 문서를 둘지 애매할 때.
- 로컬 plan 파일과 Notion 문서, Linear 프로젝트 댓글을 같은 canonical 링크로 동기화해야 할 때.

적용하지 않아도 되는 경우도 있다. 단일 Linear 티켓의 lifecycle 기록은 `개발 문서 > 티켓` 아래 티켓 parent page와 child pages가 맞다. 반복 QA 절차는 `가이드 > 운영자 가이드 > QA 문서`가 맞다. API/feature 설명은 `개발 문서` 또는 `디자인 문서`의 기능 문서 구조를 따른다.

## Examples

좋은 구조:

```text
ReplaceMe / DevAutomation 프로젝트 위키
├─ 배경
│  └─ 인프라 아키텍처 아이디에이션
└─ 개발 문서
   └─ 계획
      └─ 2026-07-13 인프라 로드맵과 티켓 선후관계
```

배경 문서에는 다음을 둔다.

```markdown
## 문제의식
- API serving과 worker lifecycle이 한 host에 묶여 있다.
- Kafka retry/DLQ가 없다.
- OTel exporter는 있지만 collector/backend profile이 없다.

## 권장 아키텍처 방향
- Runtime foundation
- Queue reliability
- Infrastructure observability
- AI observability
- LLM gateway spike
- Agent safety
```

계획 문서에는 다음을 둔다.

```markdown
## 실행 순서
1. ZZA-58
2. ZZA-59
3. ZZA-61
4. ZZA-64
5. ZZA-62
6. ZZA-60
7. ZZA-63

## Dependency map
- ZZA-59 → ZZA-61, ZZA-62, ZZA-64
- ZZA-61 + ZZA-62 + ZZA-64 → ZZA-60
```

나쁜 구조:

```text
ReplaceMe / DevAutomation 프로젝트 위키
└─ ReplaceMe 인프라 로드맵과 티켓 선후관계
   ├─ Langfuse/LiteLLM/OTel 아키텍처 판단
   ├─ ZZA-58~ZZA-64 실행 순서
   ├─ ZZA-52/55/53/54 선후관계
   └─ 로컬 plan 링크
```

이 구조는 루트에 예외 문서를 만들고, 배경과 실행 계획을 한 문서에 섞는다. 이미 이렇게 만들었다면 삭제보다 안전한 이동 안내 문서로 바꾼 뒤 canonical 문서 두 개를 링크한다.

## Related

- `docs/solutions/workflow-issues/notion-ticket-work-documents-as-folder-hierarchy.md` — 티켓별 작업 문서는 `개발 문서 > 티켓` 아래 folder-shaped hierarchy로 둔다.
- `docs/solutions/workflow-issues/notion-operator-guide-qa-document-hierarchy.md` — 반복 QA/runbook 문서는 운영자 가이드 아래에 둔다.
- `docs/solutions/conventions/ticket-code-doc-pr-split-and-tracker-sync.md` — GitHub PR, Linear, Notion, 로컬 문서를 같은 티켓 context로 동기화한다.
- `docs/solutions/workflow-issues/run-passport-contract-before-dependent-follow-ups.md` — 여러 후속 티켓이 공통 계약을 소비할 때 먼저 dependency boundary를 세운다.
- `projects/ReplaceMe/docs/plans/2026-07-13-001-feat-infra-foundation-roadmap-plan.md` — 이번 실행 계획의 repo-local source of truth.

<!-- markdownlint-enable MD013 MD025 -->
