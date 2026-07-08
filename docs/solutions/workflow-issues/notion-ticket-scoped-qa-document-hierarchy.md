---
title: Notion QA 문서는 티켓 스코프 계층에 맞춘다
date: 2026-07-08
category: workflow-issues
module: replaceme-notion-workspace
problem_type: workflow_issue
component: documentation
severity: medium
applies_when:
  - ReplaceMe Notion workspace에서 특정 티켓의 QA 문서 폴더나 QA 페이지를 생성하거나 재배치할 때
  - 티켓 페이지가 이미 개발 문서 > 티켓 아래에 있고 관련 QA 문서도 같은 티켓 하위 트리에 있어야 할 때
  - notion-fetch로 페이지 ancestry를 검증한 뒤 Notion MCP로 QA 폴더를 이동할 때
  - notion-move-pages 호출에서 pages/parent 인자 shape가 validation 실패하고 page_or_database_ids/new_parent shape가 필요할 때
symptoms:
  - QA 문서 폴더가 티켓 페이지 아래가 아니라 개발 문서 같은 상위 문서 공간에 남는다
  - 티켓별 산출물을 보려는 사용자가 QA 문서를 같은 티켓 트리에서 찾지 못한다
root_cause: missing_workflow_step
resolution_type: workflow_improvement
tags: [notion, notion-mcp, qa-documentation, ticket-scoped-docs, page-hierarchy, zza-51]
related_components: [development_workflow, tooling]
---

<!-- markdownlint-disable MD025 -->

# Notion QA 문서는 티켓 스코프 계층에 맞춘다

## Context

ReplaceMe Notion 워크스페이스에서 QA 폴더와 QA 페이지를 만들 때, 프로젝트 최상위나 문서 최상위만 보고 배치하면 티켓 단위 문맥을 놓칠 수 있다. 이번 사례에서는 사용자가 `ZZA-51 personal-github-linear-notion readiness profile` 페이지를 `티켓` 페이지 아래에 두었고, QA 자료도 그 티켓 범위 안에 중첩되기를 원했다.

작업 중 `ZZA-51...` 페이지를 다시 가져와 `ancestor-path`를 확인했더니 경로가 `개발 문서 > 티켓 > ZZA-51...`였다. 반면 생성된 `QA 문서` 페이지는 검색과 fetch 결과상 여전히 `개발 문서` 아래에 있었기 때문에, 티켓 페이지 아래로 이동해야 했다.

세션 히스토리에서도 같은 주의점이 드러났다. 이전 ReplaceMe 작업은 QA 문서를 `projects/ReplaceMe/docs/qa/`에 정리하고 Notion 리뷰 페이지를 남겼지만, skeleton 기록에는 해당 Notion 페이지들이 ZZA-51 티켓 스코프 아래에 있는지 `ancestor-path`로 검증했다는 증거가 없었다(session history). 즉, Notion 산출물을 만들었다는 사실만으로는 올바른 티켓 계층에 배치됐다고 볼 수 없다.

## Guidance

Notion 프로젝트 산출물을 생성하거나 이동하기 전에는 먼저 목표 티켓 페이지를 fetch하고 `ancestor-path`를 확인한다. 사용자가 특정 티켓, 이슈, 작업 단위 아래에서 문서를 관리하고 있다면 후속 산출물도 같은 티켓 스코프에 둔다.

배치 기준은 다음 순서로 잡는다.

1. 사용자가 언급한 티켓 또는 작업 페이지를 fetch한다.
2. 응답에서 `ancestor-path`를 확인해 실제 부모 체인을 파악한다.
3. QA 문서, 설계 문서, 점검표 등 후속 산출물은 그 티켓 페이지를 parent로 삼아 생성하거나 이동한다.
4. 이미 잘못된 위치에 만들어진 페이지는 새로 만들기보다 move로 위치만 정정한다.
5. 이동 후에는 부모 페이지와 이동된 페이지를 모두 fetch해 최종 `ancestor-path`와 자식 페이지 유지 여부를 검증한다.

이번 2026-07-08 Pi/Notion MCP 세션에서는 페이지 이동 시 `notion-move-pages` 호출에 `page_or_database_ids`와 `new_parent`를 사용해야 했다. 커넥터 스키마는 도구 버전에 따라 달라질 수 있으므로, 다른 세션에서는 먼저 사용 가능한 도구 목록이나 스키마를 확인한 뒤 호출한다. 이 세션에서 동작한 형태는 다음과 같다.

```json
{
  "page_or_database_ids": ["<qa-document-folder-page-id>"],
  "new_parent": {
    "page_id": "<ticket-scoped-zza-51-page-id>"
  }
}
```

여기서 페이지 ID들은 자리표시자일 뿐이며 재사용 가능한 상수가 아니다. 다른 작업에서는 반드시 현재 워크스페이스에서 fetch 또는 search로 확인한 실제 페이지 ID를 사용해야 한다.

반대로 다음과 같은 형태는 이 사례에서 실패했다.

```json
{
  "pages": ["..."],
  "parent": "..."
}
```

이 세션의 검증 오류는 `page_or_database_ids`와 `new_parent`가 필요하다는 내용이었다. 따라서 move 도구의 입력 스키마를 임의로 추측하지 말고, 현재 커넥터가 요구하는 필드명을 확인한 뒤 호출한다.

## Why This Matters

Notion 문서는 위치 자체가 문맥이다. 특히 `티켓` 아래의 개별 작업 페이지는 요구사항, QA, 체크리스트, 결정 기록을 묶는 단위가 된다. QA 문서가 티켓 밖의 상위 문서 공간에 남아 있으면 사용자는 관련 자료를 한곳에서 찾기 어렵고, 이후 자동화나 검색 결과에서도 작업 단위 연결성이 약해진다.

또한 잘못 배치된 페이지를 다시 생성하면 중복 문서가 생기고 기존 하위 페이지나 링크 관계를 잃을 수 있다. move를 사용하면 `QA 00`부터 `QA 06`까지의 하위 QA 페이지를 유지한 채 위치만 바로잡을 수 있다.

## When to Apply

다음 상황에서 이 지침을 적용한다.

- 사용자가 특정 Linear 티켓, Notion 티켓 페이지, 작업 페이지 아래에 문서를 두고 있다고 말한 경우
- QA 문서, 테스트 계획, 점검표, 릴리스 노트처럼 티켓 단위에 종속되는 산출물을 만들 때
- 이미 만든 Notion 페이지가 예상보다 상위 문서나 다른 프로젝트 영역에 생성된 경우
- Notion MCP move 호출에서 입력 검증 오류가 발생한 경우
- 최종 위치를 증명해야 하며 `ancestor-path` 기반 검증이 필요한 경우

## Examples

티켓 스코프 확인 예시는 다음과 같다.

- 목표 티켓 페이지 fetch 결과: `개발 문서 > 티켓 > ZZA-51...`
- 잘못 배치된 QA 문서 fetch 결과: `개발 문서 > QA 문서`
- 기대 위치: `개발 문서 > 티켓 > ZZA-51... > QA 문서`

이동은 기존 QA 문서를 대상으로 수행한다. 이번 세션에서는 `QA 문서` 페이지 ID를 `page_or_database_ids`에 넣고, `ZZA-51...` 티켓 페이지 ID를 `new_parent.page_id`에 넣었다. 이동 후 최종 fetch에서 `QA 문서`의 ancestor path가 `ReplaceMe / DevAutomation 프로젝트 위키 > 개발 문서 > 티켓 > ZZA-51... > QA 문서`로 확인되었고, `QA 00`부터 `QA 06`까지의 하위 페이지도 유지된 것으로 관측했다.

## Related

- `docs/solutions/workflow-issues/independent-projects-as-standalone-repos-submodules.md` — ReplaceMe처럼 독립 작업 단위를 올바른 owning surface에 두는 워크스페이스 경계 사례.
- `docs/solutions/workflow/zworkspaces-main-direct-workflow.md` — zWorkspaces 루트 문서/메타데이터 작업의 기본 흐름.
- `docs/solutions/documentation-gaps/canonical-curriculum-docs-before-learning-branches.md` — 후속 작업 전에 canonical 문서 spine을 먼저 두는 문서화 패턴.
