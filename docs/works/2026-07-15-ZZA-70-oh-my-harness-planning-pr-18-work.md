---
workflow_schema: compound-work/v1
ticket_id: ZZA-70
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-70/oh-my-harness-4개-코딩-에이전트용-compound-engineering-호환-코어
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/oh-my-pi/pull/19
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: 세션에서 ce-brainstorm 요구사항으로 범위와 트레이드오프를 직접 확정해 별도 아이디에이션 후보 비교가 계획 품질을 바꾸지 않음
plan_status: complete
plan_path: docs/plans/2026-07-15-ZZA-70-oh-my-harness-plan.md
plan_notion_url: https://www.notion.so/39eef22ad4fc8134bdbcd7de4afec13a
plan_waiver_reason:
work_status: complete
work_notion_url: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
pr_url: https://github.com/zzanghyunmoo/oh-my-pi/pull/18
closeout_status: complete
merged_pr_url: https://github.com/zzanghyunmoo/oh-my-pi/pull/18
merge_commit: 31c7fee6d1bc3c2da04bfba8d4306cb30fc54de9
kb_paths: docs/kb/architecture/2026-07-15-ZZA-70-oh-my-harness-planning-contract.md
notion_feature_status_url: https://www.notion.so/39eef22ad4fc819db113ce1029c899a4
notion_ticket_url: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
closed_at: 2026-07-15T09:10:00Z
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
- `npm run profile:verify` 통과: 4개 profile과 lock이 deterministic·secret-free 상태다.
- 두 차례 `ce-doc-review`, latest-head inline contract audit와 최종 blocker recheck에서 P0/P1 구현 준비 blocker 없음.
- PR #18 code-review findings 7건을 계획에 반영하고 최신 head `228a284b30937791cb150ad8d0d1d107c2448f87`에서 behavioral final pass가 blocker 0건임을 확인했다.
- Structural reviewer의 `docs/works` 누락 finding은 project diff가 아닌 workspace root `origin/main`의 이 문서를 canonical evidence로 사용하는 규약을 확인해 해소했다.
- 최신 head code review와 doc review marker 게시 뒤 `compound_workflow_gate.py pre-merge`가 `MERGEABLE/CLEAN` head를 검증했다.
- 런타임·Linux OCI·Darwin Tart VM·116-cell 검증은 구현 전 planning PR이므로 실행하지 않았으며 U16 이후의 후속 PR 검증 범위다.

## 외부 동기화

- Linear ZZA-70을 planning PR 생성 뒤 `In Review`로 전환했다.
- GitHub planning PR: <https://github.com/zzanghyunmoo/oh-my-pi/pull/18>
- Code review: <https://github.com/zzanghyunmoo/oh-my-pi/pull/18#issuecomment-4977830581>
- Doc review: <https://github.com/zzanghyunmoo/oh-my-pi/pull/18#issuecomment-4977830586>
- Notion `Oh My Harness 프로젝트 위키 > 개발 문서 > 계획`과 `개발 문서 > 티켓`을 최신 계획 및 planning PR 상태로 갱신했다.
- Canonical plan: <https://app.notion.com/p/39eef22ad4fc8134bdbcd7de4afec13a>
- Canonical ticket: <https://app.notion.com/p/39eef22ad4fc81c4a4bce021fa26b92b>

## Merge closeout

PR #18은 squash commit `31c7fee6d1bc3c2da04bfba8d4306cb30fc54de9`로 merge됐다. 현재 기능 상태와 미구현 경계를 `docs/kb/architecture/2026-07-15-ZZA-70-oh-my-harness-planning-contract.md` 및 Notion 기능 현황·티켓 문서에 동기화했다. U1-U18 구현과 rename/package PR이 남아 있으므로 Linear는 `In Review`, `ticket_completion: pending`을 유지한다.
