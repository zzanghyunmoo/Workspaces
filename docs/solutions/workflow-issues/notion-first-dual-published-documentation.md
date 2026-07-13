---
title: Notion을 기준으로 로컬 문서를 이중 발행하고 동기화한다
date: 2026-07-13
category: workflow-issues
module: replaceme-documentation-workflow
problem_type: workflow_issue
component: documentation
severity: medium
applies_when:
  - "ReplaceMe 작업 단계별 산출물을 Notion과 로컬 docs에 함께 남길 때"
  - "Notion 문서 구조가 canonical이고 로컬 docs를 그 구조와 내용에 맞춰 동기화해야 할 때"
  - "기능 현황 또는 기능 상태 문서의 owning surface를 개발 문서와 디자인 문서 중 어디로 둘지 판단할 때"
  - "잘못 만든 중복 Notion 문서를 이동 또는 중복 안내로 정리해야 할 때"
symptoms:
  - "작업 단계 산출물이 Notion에만 있거나 로컬 docs에만 있어 두 표면이 갈라진다"
  - "로컬 docs가 Notion canonical 구조와 내용을 반영하지 않고 독립 사본처럼 작성된다"
  - "기능 현황이 디자인 문서 아래가 아니라 개발 문서 아래에 중복 생성된다"
root_cause: missing_workflow_step
resolution_type: workflow_improvement
tags: [notion, local-docs, documentation-sync, canonical-structure, feature-status, replaceme]
related_components: [notion-workspace, local-documentation, development_workflow]
---

<!-- markdownlint-disable MD013 MD025 -->

# Notion을 기준으로 로컬 문서를 이중 발행하고 동기화한다

## Context

ReplaceMe 인프라 문서 배치 이후, 사용자는 작업 계획과 구현 설명이 충분히 남지 않았고 현재 기능 상태를 한눈에 볼 수 있는 문서도 빠져 있다고 지적했다. 보완 과정에서 `개발 문서 > 티켓` 아래에는 티켓별 하위 페이지를 추가했지만, `기능 현황`을 `개발 문서` 아래에 새로 만들면서 정보 구조를 잘못 확장했다.

사용자는 `기능 현황`은 이미 `디자인 문서` 아래에 중앙화되어 있다고 바로잡았다. 이후 `디자인 문서 > 기능 현황`을 canonical 위치로 유지한 채 기능 문서를 그 아래에 생성하고, 중복 생성된 `개발 문서 > 기능 현황`은 `이동됨 - 기능 현황`으로 이름을 바꿔 canonical 안내만 남겼다.

이 사례의 학습은 하나다. 각 작업 단계마다 Notion 문서와 로컬 문서를 모두 발행하되, 구조와 내용의 기준은 Notion으로 삼고 로컬 문서는 Notion에서 동기화한 사본으로 유지해야 한다.

Notion counterpart: `KB > 문서 이중 발행과 Notion 기준 동기화`.

## Guidance

작업 계획, 구현 설명, 티켓별 상세, 기능 현황처럼 프로젝트 지식을 남길 때는 Notion과 로컬 문서를 둘 다 갱신한다. 단, 두 저장소를 독립적으로 작성하지 않는다. Notion을 정보 구조와 본문 내용의 canonical source로 삼고, 로컬 문서는 Notion의 구조와 내용을 반영하는 동기화 사본으로 관리한다.

권장 흐름은 다음과 같다.

1. 새 문서를 만들기 전에 Notion의 기존 상위 페이지와 중앙화된 문서 위치를 먼저 확인한다.
2. Notion에서 canonical 위치를 정하고, 필요한 페이지를 해당 위치에 먼저 생성하거나 갱신한다.
3. 로컬 문서는 Notion에서 확정한 제목, 범위, 섹션, 링크 관계를 따라 작성한다.
4. 로컬 문서에는 원본 Notion 페이지 링크나 동기화 기준을 남겨, 로컬 문서가 독립 원본처럼 보이지 않게 한다.
5. 같은 주제의 Notion 페이지가 중복 생성되면 새 사본을 계속 확장하지 말고, canonical 링크를 담은 이동/중복 안내로 바꾸거나 폐기 표시한다.

작업 단계별 최소 확인 항목은 다음과 같다.

- **배경/아이디에이션:** Notion `배경`에 먼저 남기고, 로컬 산출물이 있으면 Notion 링크와 함께 동기화한다.
- **실행 계획:** Notion `개발 문서 > 계획`에 날짜별 계획을 만들고, 로컬 plan 문서는 같은 제목·범위·링크를 반영한다.
- **티켓 작업:** Notion `개발 문서 > 티켓` 아래 티켓 parent와 child pages를 만들고, 로컬 티켓/계획 문서가 있으면 같은 상태와 검증 결과를 반영한다.
- **기능 상태:** Notion `디자인 문서 > 기능 현황`을 canonical으로 삼고, 기능별 세부 문서도 그 아래에 둔다. 개발 문서에는 필요한 경우 canonical 기능 현황 링크만 둔다.
- **검증/회고:** 실행 결과와 lessons learned를 Notion과 로컬 docs/solutions에 모두 남기되, Notion에 확정된 구조를 로컬 문서가 따른다.

## Why This Matters

Notion과 로컬 문서를 모두 남기면 협업 중에는 탐색성과 공유성이 좋아지고, 저장소 안에서는 변경 이력과 구현 맥락을 추적하기 쉬워진다. 하지만 두 곳을 별도 원본처럼 작성하면 곧바로 drift가 생긴다. 문서 구조가 갈라지면 사용자는 어떤 페이지가 최신인지 판단해야 하고, 기능 현황처럼 중앙화되어야 할 지식이 여러 위치로 흩어진다.

Notion을 canonical source로 정하면 정보 구조를 한 곳에서 유지할 수 있다. 로컬 문서는 그 결정의 사본이므로 코드 변경, 리뷰, 회고에서 참조하기 쉽고, 동시에 제품/디자인/운영 문서의 중심 구조를 깨뜨리지 않는다.

이 규칙은 External Work Surface Sync의 문서 버전이다. GitHub PR, Linear 이슈, Notion, 로컬 docs가 서로 다른 상태를 말하기 시작하면 다음 에이전트는 실행 순서, 기능 범위, 검증 결과를 다시 추론해야 한다. Notion-first dual publishing은 그 재추론 비용을 줄이고, 잘못된 위치의 문서가 다음 작업의 starting point가 되는 것을 막는다.

## When to Apply

- 새 티켓 작업을 시작하거나 작업 계획을 확정할 때.
- 구현 후 설명 문서, 운영 메모, 검증 결과를 남길 때.
- 기능별 상태, 범위, 완료 여부를 정리할 때.
- Notion 문서와 저장소 문서를 모두 요구받는 프로젝트 배치 작업을 수행할 때.
- 이미 존재하는 문서 트리에 새 페이지를 추가해야 할 때.
- Notion 검색 결과에 비슷한 제목의 페이지가 여러 개 나오고 canonical parent를 다시 정해야 할 때.

임시 개인 메모나 폐기 예정의 실험 로그처럼 canonical 문서로 승격하지 않을 자료에는 적용 범위를 명시하고, Notion/로컬 양쪽에 정식 문서처럼 남기지 않는다.

## Examples

좋은 흐름:

```text
1. Notion에서 기존 문서 트리를 fetch한다.
2. `디자인 문서 > 기능 현황`이 기능 상태의 중앙 위치임을 확인한다.
3. 새 기능 설명은 `디자인 문서 > 기능 현황` 아래에 추가한다.
4. `개발 문서 > 티켓`에는 티켓별 계획과 구현 설명을 둔다.
5. 로컬 문서는 Notion에서 확정된 구조를 따라 작성하고, Notion 원본 링크를 남긴다.
```

나쁜 흐름:

```text
1. 기능 현황이 이미 `디자인 문서` 아래에 있는데도 `개발 문서 > 기능 현황`을 새 canonical처럼 만든다.
2. Notion에는 기능 상태를 A 구조로, 로컬 문서에는 B 구조로 따로 작성한다.
3. 나중에 어떤 문서가 최신인지 확인할 수 없게 두 문서를 독립적으로 수정한다.
```

중복을 발견했을 때의 처리:

```text
1. canonical 위치를 먼저 정한다.
2. canonical이 아닌 중복 페이지에는 “이 문서는 이동됨/중복됨”을 표시하고 canonical 페이지로 링크한다.
3. 이후 변경은 canonical Notion 페이지에 먼저 반영하고, 로컬 문서를 그 내용에 맞춰 동기화한다.
4. 개발 문서나 README에 남은 stale 링크가 있으면 canonical Notion 링크로 바꾼다.
```

이번 작업에서 확정한 구조 예시는 다음과 같다. 기능 상태의 canonical map은 `디자인 문서 > 기능 현황` 아래에 두고, 티켓 페이지의 `04 기능 현황`은 해당 티켓의 변경 요약이나 canonical 기능 문서 링크를 담는 비-canonical child page로만 쓴다.

```text
ReplaceMe / DevAutomation 프로젝트 위키
├─ 디자인 문서
│  └─ 기능 현황
│     └─ <기능별 현재 상태와 기능 설명>
└─ 개발 문서
   ├─ 티켓
   │  └─ <ZZA ticket>
   │     ├─ 01 실행 결과와 검증
   │     ├─ 02 작업 계획
   │     ├─ 03 구현 설명
   │     └─ 04 기능 현황 링크와 변경 요약
   └─ 계획
      └─ <dated execution plan>
```

## Related

- `docs/solutions/conventions/ticket-code-doc-pr-split-and-tracker-sync.md` — GitHub PR, Linear, Notion 같은 외부 작업면을 같은 ticket context로 동기화한다.
- `docs/solutions/workflow-issues/notion-background-and-dated-plan-doc-separation.md` — 아이디에이션은 `배경`, 날짜별 실행 계획은 `개발 문서 > 계획` 아래에 둔다.
- `docs/solutions/workflow-issues/notion-ticket-work-documents-as-folder-hierarchy.md` — 티켓별 작업 문서는 `개발 문서 > 티켓` 아래 folder-shaped hierarchy로 둔다.
- `docs/solutions/workflow-issues/notion-operator-guide-qa-document-hierarchy.md` — 반복 QA/runbook 문서는 운영자 가이드 아래에 둔다.
- `docs/solutions/workflow-issues/run-passport-contract-before-dependent-follow-ups.md` — Notion/PR/Linear surfaces가 같은 실행 식별자와 evidence contract를 소비해야 한다.

<!-- markdownlint-enable MD013 MD025 -->
