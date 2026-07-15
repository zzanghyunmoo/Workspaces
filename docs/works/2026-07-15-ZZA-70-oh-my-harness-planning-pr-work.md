---
workflow_schema: compound-work/v1
ticket_id: ZZA-70
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-70/oh-my-harness-4개-코딩-에이전트용-compound-engineering-호환-코어
ticket_status: In Progress
ticket_completion: pending
remaining_prs: implementation PRs for U1-U18
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: 세션에서 ce-brainstorm 요구사항으로 범위와 트레이드오프를 직접 확정해 별도 아이디에이션 후보 비교가 계획 품질을 바꾸지 않음
plan_status: complete
plan_path: docs/plans/2026-07-15-ZZA-70-oh-my-harness-plan.md
plan_notion_url: https://www.notion.so/39eef22ad4fc8134bdbcd7de4afec13a
plan_waiver_reason:
work_status: in_progress
work_notion_url: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
pr_url:
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url: https://www.notion.so/39eef22ad4fc819db113ce1029c899a4
notion_ticket_url: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
closed_at:
---

# ZZA-70 Oh My Harness planning PR 작업 기록

## 작업 목표

Compound Engineering 3.19.0의 29개 기능을 Codex, OpenCode, Claude Code, Pi에서 같은 워크플로와 산출물 계약으로 제공하기 위한 요구사항, 구현 계획, 공통 도메인 용어를 독립 planning PR로 확정한다.

## 주요 변경 지점

- `projects/oh-my-pi/docs/brainstorms/2026-07-15-oh-my-harness-requirements.md`: R1-R21, A1-A5, F1-F5, AE1-AE6과 범위 경계를 고정했다.
- `projects/oh-my-pi/docs/plans/2026-07-15-ZZA-70-oh-my-harness-plan.md`: CE 3.19.0 lock, runtime/platform tuple, native gate, OCI hermetic lane, 116-cell matrix와 U1-U18 실행 순서를 정의했다.
- `projects/oh-my-pi/CONCEPTS.md`: Runtime-Neutral Harness Core, Runtime Adapter, Conformance Matrix 용어를 추가했다.
- 이번 PR은 구현 코드를 포함하지 않으며, merge 뒤 최신 `main`에서 후속 구현 브랜치를 새로 만든다.

## 검증

- 문서 ID 연속성: R1-R21, A1-A5, F1-F5, AE1-AE6, U1-U18 통과.
- Implementation Unit dependency 위상 순서와 116-cell cardinality 검증 통과.
- `git diff --check` 통과.
- Markdown LSP diagnostics 0건.
- 두 차례 `ce-doc-review`와 최종 blocker recheck에서 P0/P1 구현 준비 blocker 없음.
- 런타임·OCI·116-cell 검증은 구현 전 planning PR이므로 실행하지 않았으며 U16 이후의 후속 PR 검증 범위다.

## 외부 동기화

- Linear ZZA-70을 `In Progress`로 전환했다.
- Notion `Oh My Harness 프로젝트 위키 > 개발 문서 > 계획`과 `개발 문서 > 티켓`을 최신 계획 및 planning PR 상태로 갱신했다.
- Canonical plan: <https://app.notion.com/p/39eef22ad4fc8134bdbcd7de4afec13a>
- Canonical ticket: <https://app.notion.com/p/39eef22ad4fc81c4a4bce021fa26b92b>

## Merge closeout

Planning PR merge 뒤에도 U1-U18 구현 PR이 남으므로 Linear는 `In Review`와 `ticket_completion: pending`을 유지한다. 최종 구현 PR merge 뒤 KB, Notion 기능 현황, 티켓 결과와 merge commit을 정리한다.
