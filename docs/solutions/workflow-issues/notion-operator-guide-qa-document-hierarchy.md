---
title: Notion QA 문서는 운영자 가이드 아래에 둔다
date: 2026-07-09
category: workflow-issues
module: replaceme-notion-workspace
problem_type: workflow_issue
component: documentation
severity: medium
applies_when:
  - ReplaceMe Notion workspace에서 QA 문서 폴더나 QA 페이지를 생성하거나 재배치할 때
  - QA 문서가 특정 티켓 산출물처럼 티켓 페이지 아래에 배치되어 운영자가 찾기 어려워졌을 때
  - notion-fetch로 페이지 ancestry를 검증한 뒤 Notion MCP로 QA 폴더를 이동할 때
  - notion-move-pages 호출에서 pages/parent 인자 shape가 validation 실패하고 page_or_database_ids/new_parent shape가 필요할 때
symptoms:
  - QA 문서 폴더가 운영자 가이드가 아니라 특정 티켓 페이지 아래에 있다
  - 운영자가 로컬 실행, health check, provider QA, 장애 재현 절차를 가이드 영역에서 찾지 못한다
  - 티켓별 작업 기록과 반복 운영 절차가 같은 Notion 트리에 섞인다
root_cause: wrong_document_ownership
resolution_type: workflow_improvement
tags: [notion, notion-mcp, qa-documentation, operator-guide, page-hierarchy, replaceme]
related_components: [development_workflow, tooling, operations]
---

<!-- markdownlint-disable MD025 -->

# Notion QA 문서는 운영자 가이드 아래에 둔다

## Context

ReplaceMe Notion 워크스페이스에서 QA 폴더와 QA 페이지를 만들 때, 특정 티켓의 작업 산출물과 반복 운영 절차를 혼동하면 문서 위치가 잘못된다. 이전에는 QA 문서가 `개발 문서 > 티켓 > ZZA-51...` 아래에 있었고, 이는 readiness profile 티켓 작업 중 만들어진 산출물처럼 보였다.

하지만 QA 문서는 특정 티켓 한 번의 결과물이 아니다. `QA 00. 로컬 실행과 Health Check`부터 `QA 06. 저장소와 관측성`까지는 ReplaceMe를 반복 실행하고 검증하는 운영자용 절차다. 따라서 canonical 위치는 `ReplaceMe / DevAutomation 프로젝트 위키 > 가이드 > 운영자 가이드 > QA 문서`다.

2026-07-09 복구 작업에서 기존 QA 트리를 새로 복사하지 않고 Notion MCP `notion-move-pages`로 운영자 가이드 아래로 이동했다. 이동 후 `QA 문서`와 `QA 00` fetch 결과에서 ancestor path가 운영자 가이드 아래로 바뀐 것을 확인했다.

## Guidance

QA 문서의 owning surface는 **운영자 가이드**다. 티켓 페이지에는 해당 티켓에서 수행한 QA 결과와 링크를 남기되, 반복 실행 절차 자체는 운영자 가이드 아래에 둔다.

배치 기준은 다음 순서로 잡는다.

1. 문서 성격을 먼저 분류한다.
   - 반복 운영 절차, 로컬 실행, health check, provider QA, 장애 대응 runbook → 운영자 가이드
   - 특정 티켓의 요구사항, 결정, PR, 검증 결과 → 티켓 페이지
   - 기능 설명, 아키텍처 설명 → 개발 문서 또는 디자인 문서
2. 운영자 가이드 page를 fetch하고 `ancestor-path`를 확인한다.
3. QA 문서가 이미 다른 위치에 있으면 새로 만들기보다 move로 위치만 정정한다.
4. 이동 후에는 운영자 가이드, QA 문서, 대표 child page(`QA 00`)를 모두 fetch해 최종 `ancestor-path`를 검증한다.
5. 티켓 페이지에는 QA 문서 본문을 복제하지 말고, 티켓별 실행 결과와 canonical QA 문서 링크만 남긴다.

## Notion MCP move shape

2026-07-09 세션에서 동작한 `notion-move-pages` 입력 형태는 다음과 같다.

```json
{
  "page_or_database_ids": ["<qa-document-folder-page-id>"],
  "new_parent": {
    "page_id": "<operator-guide-page-id>"
  }
}
```

여기서 페이지 ID들은 자리표시자다. 다른 작업에서는 반드시 현재 워크스페이스에서 `notion-search` 또는 `notion-fetch`로 확인한 실제 페이지 ID를 사용한다.

반대로 다음과 같은 형태는 이 커넥터에서 실패했다.

```json
{
  "pages": ["..."],
  "parent": "..."
}
```

검증 오류는 `page_or_database_ids`와 `new_parent`가 필요하다는 내용이었다. 따라서 move 도구의 입력 스키마를 임의로 추측하지 말고, 현재 커넥터가 요구하는 필드명을 확인한 뒤 호출한다.

## Why This Matters

Notion 문서는 위치 자체가 문맥이다. QA 문서가 티켓 아래에 있으면 운영자는 반복 실행 절차를 티켓 산출물로 오해하거나, 다음 티켓에서 같은 QA 문서를 찾지 못한다. 반대로 티켓 페이지에는 해당 티켓에서 실제로 수행한 검증 결과만 남겨야 PR/Linear/Notion 동기화 기록이 깔끔해진다.

또한 잘못 배치된 페이지를 다시 생성하면 중복 문서가 생기고 기존 하위 페이지나 링크 관계를 잃을 수 있다. move를 사용하면 `QA 00`부터 `QA 06`까지의 하위 QA 페이지를 유지한 채 위치만 바로잡을 수 있다.

## When to Apply

다음 상황에서 이 지침을 적용한다.

- QA 문서, 수동 테스트 runbook, health check 절차, provider smoke test 문서를 만들거나 옮길 때
- Notion에서 QA 문서를 찾을 수 없거나 특정 티켓 아래에 숨어 있을 때
- 티켓별 작업 기록과 반복 운영 절차가 섞여 있는지 판단해야 할 때
- Notion MCP move 호출에서 입력 검증 오류가 발생한 경우
- 최종 위치를 `ancestor-path` 기반으로 증명해야 하는 경우

## Examples

복구 전후 위치 예시는 다음과 같다.

- 잘못된 위치: `ReplaceMe / DevAutomation 프로젝트 위키 > 개발 문서 > 티켓 > ZZA-51... > QA 문서`
- 올바른 위치: `ReplaceMe / DevAutomation 프로젝트 위키 > 가이드 > 운영자 가이드 > QA 문서`

티켓 페이지에는 다음과 같은 형태로만 연결한다.

```markdown
## 검증

- ZZA-57 Redpanda compose smoke: pass
- 참조 QA 문서: 운영자 가이드 > QA 문서 > QA 00. 로컬 실행과 Health Check
```

## Related

- `docs/solutions/workflow-issues/run-passport-contract-before-dependent-follow-ups.md` — Run Passport 계약을 dependent follow-up 전에 먼저 고정한 사례.
- `docs/solutions/conventions/ticket-code-doc-pr-split-and-tracker-sync.md` — 티켓별 PR/Linear/Notion 동기화 규칙.
- `docs/solutions/workflow/zworkspaces-main-direct-workflow.md` — zWorkspaces 루트 문서/메타데이터 작업의 기본 흐름.
