---
title: 티켓 작업 PR은 문서와 코드를 분리하고 외부 작업면까지 동기화한다
date: 2026-07-09
last_updated: 2026-07-14
category: conventions
module: replace-me-pr-workflow
problem_type: convention
component: development_workflow
severity: medium
applies_when:
  - 하나의 Linear 티켓에서 계약/계획 문서와 코드 구현이 함께 나올 때
  - 문서 PR이 먼저 리뷰되어야 코드 PR의 기준 계약이 안정되는 때
  - GitHub PR을 나눈 뒤 Linear 이슈와 Notion 설계 노트에도 같은 상태를 남겨야 할 때
  - PR 제목만 ticket identity 규칙과 다르고 branch, body, evidence, lifecycle은 유효할 때
tags: [pull-request, stacked-prs, linear, notion, ticket-workflow, pr-title]
related_components: [documentation, assistant, tooling]
---

<!-- markdownlint-disable MD013 MD025 -->

# 티켓 작업 PR은 문서와 코드를 분리하고 외부 작업면까지 동기화한다

## Context

ZZA-56 Run Passport minimum schema/interface 작업은 처음에 문서 변경과 코드 변경을
한 PR에 담아 열렸다. 사용자는 이전에 학습한 PR 분리 규칙을 지적하며, 이 작업을
**문서 PR**과 **코드 PR**로 나누라고 요구했다. 또한 PR 제목도 일반 Conventional
Commit 제목이 아니라 티켓 단위 규칙을 따라야 했다.

2026-07-14의 유지보수 PR `#24`에서도 더 좁은 형태의 같은 문제가 반복됐다. branch,
base, 본문, work evidence, Linear/Notion 연결은 유효했지만 최초 제목만
`docs: 병합된 인프라 티켓 상태 동기화`로 생성됐다. 이 경우 PR 구조 전체를 무효로
간주하지 않고 같은 PR의 제목만 `[ZZA-69] ZZA-65~68 merge closeout 문서 동기화`로
수정했다. 이전 ZZA-56 세션에서도 제목 correction과 이미 유효한 branch·PR·외부 작업면
보존은 별도 판단으로 다뤄졌다. (session history)

최종 정리는 다음처럼 바뀌었다.

- 문서 PR: `#9` — `[ZZA-56] Run Passport minimum schema/interface (문서)`
  - base: `main`
  - 범위: Run Passport v0 계약, nullable placeholder, 비목표, 구현 계획 문서
- 코드 PR: `#8` — `[ZZA-56] Run Passport minimum schema/interface (코드)`
  - base: `ZZA-56/run-passport-contract-docs`
  - 범위: API endpoint, response contract, contract tests

이후 Linear 이슈 `ZZA-56`에는 두 PR 링크와 검증 결과를 댓글로 남겼고, Notion의
`Run Passport 설계 노트`에도 같은 PR split, v0 결정, 비목표, 검증 결과를 append했다.
이는 GitHub만 정리하면 끝나는 작업이 아니라, Linear/Notion 같은 외부 작업면도 같은
상태를 공유해야 한다는 점을 드러냈다.

## Guidance

하나의 티켓에서 문서 계약과 코드 구현이 모두 나올 때는 먼저 PR을 두 surface로
분리할지 판단한다. 계약, 요구사항, 설계 노트, 기능 문서가 코드 리뷰의 기준이 되는
경우에는 문서 PR을 먼저 만들고 코드 PR을 그 위에 쌓는다.

권장 순서:

1. 티켓 제목을 canonical title로 삼는다.
2. 문서 변경만 담은 PR을 `main` 또는 현재 release base 위에 연다.
3. 코드 변경만 담은 PR을 문서 PR branch 위에 stack한다.
4. 두 PR 제목은 같은 티켓 제목을 공유하고 suffix만 다르게 쓴다.
5. PR body는 한국어 4섹션 구조를 유지하되, 각 PR의 scope와 base 관계를 명시한다.
6. Linear 이슈에 split 결과, PR 링크, 검증 결과, 아직 유지해야 할 상태를 댓글로 남긴다.
7. 관련 Notion 설계/라이프사이클 문서에도 같은 PR 링크, 결정 사항, 검증 결과를 반영한다.

PR 제목의 기본 형식은 다음을 따른다.

```text
[티켓 번호] canonical 티켓 제목
```

같은 티켓을 문서/코드 surface로 나눈 경우에만 suffix로 구별한다.

```text
[티켓 번호] 티켓 제목 (문서)
[티켓 번호] 티켓 제목 (코드)
```

예:

```text
[ZZA-69] ZZA-65~68 merge closeout 문서 동기화
[ZZA-56] Run Passport minimum schema/interface (문서)
[ZZA-56] Run Passport minimum schema/interface (코드)
```

제목 불일치를 발견하면 다음 차원을 독립적으로 확인한다.

1. **Ticket identity/title** — `[TICKET] canonical title`인가.
2. **Branch/base와 diff scope** — head와 base, 변경 범위가 의도와 맞는가.
3. **Body/evidence** — PR 본문, work evidence, review 댓글이 갖춰졌는가.
4. **Lifecycle state** — Linear/Notion 상태와 merge/closeout 기록이 실제 상태와 맞는가.

title만 틀리고 나머지 차원이 유효하면 기존 PR 번호와 연결을 보존한 채
`gh pr edit <number> --title "[TICKET] canonical title"`로 제목만 수정한다. title 오류를
근거로 PR 취소·재생성, branch 재작성, evidence 재구축, lifecycle rollback까지 확대하지
않는다. 이러한 조치는 각각의 차원에서 실제 결함이 확인될 때만 수행한다.

문서 PR에는 코드 파일이 들어가지 않아야 하고, 코드 PR에는 문서 PR에서 이미 다룬
계약/계획 문서가 다시 섞이지 않아야 한다. `gh pr view --json files`나 GitHub file list로
각 PR의 파일 범위를 확인한다.

Linear/Notion 동기화는 PR 생성 뒤의 선택 작업이 아니라 handoff의 일부다. 최소한 다음을
`docs/works` evidence와 Notion 티켓 문서에 남긴다.

- 어떤 PR이 문서이고 어떤 PR이 코드인지
- 각 PR의 base/head 관계
- 각 PR이 책임지는 범위와 주요 구현 변경 지점
- 실제 실행한 검증
- PR 최신 head의 `ce-code-review`와 `ce-doc-review` 댓글
- PR merge 전이라면 Linear 상태를 완료로 바꾸지 않는 이유

각 PR은 자신의 `docs/works` evidence와 최신 head SHA를 가진 code/doc review marker를
별도로 충족해야 한다. Parent merge 뒤 child를 retarget하거나 새 commit을 push하면 이전
marker를 재사용하지 않는다. 중간 PR을 merge한 뒤에는 KB·Notion closeout을 하되 Linear는
`In Review`와 `remaining_prs`를 유지한다. 마지막 PR의 closeout이 끝난 뒤에만 Linear를
`Done`으로 전환한다.

## Why This Matters

문서와 코드를 한 PR에 담으면 리뷰어가 먼저 합의해야 할 계약과 그 계약을 구현한 코드를
동시에 판단해야 한다. 작은 작업처럼 보여도, 후속 티켓이 같은 계약을 소비하는 경우에는
문서 PR이 기준면이 되고 코드 PR은 그 기준을 구현하는 별도 검증 단위가 된다.

제목 형식도 중요하다. `[티켓 번호] 티켓 제목 (문서/코드)`를 쓰면 GitHub PR 목록만 봐도
같은 티켓의 paired PR인지, 어느 쪽을 먼저 봐야 하는지 드러난다. Conventional Commit
prefix만 붙인 제목은 commit intent는 말해도 ticket identity와 review surface를 충분히
보여 주지 못한다.

동시에 제목은 PR의 metadata일 뿐 branch, diff, evidence, lifecycle 전체의 유효성을
대신하지 않는다. title-only 문제에 close/recreate 해법을 적용하면 PR 번호와 review
history, Linear/Notion/work evidence 링크까지 불필요하게 흔든다. 차원을 분리하고 최소
수정하면 유효한 추적 관계는 보존하면서 잘못된 metadata만 바로잡을 수 있다.

Linear와 Notion을 업데이트하지 않으면 외부 작업면은 여전히 낡은 상태를 보여 준다.
자동화 작업에서는 Linear 이슈가 실행의 control plane이고 Notion 문서가 설계/라이프사이클
memory가 되므로, GitHub에서 PR을 정리한 뒤에도 두 표면에 같은 링크와 결정 내용을
반영해야 다음 실행자가 맥락을 잃지 않는다.

## When to Apply

- 하나의 티켓이 문서 계약과 코드 구현을 모두 포함할 때.
- 문서 변경이 후속 코드 PR의 review 기준이 되는 때.
- 사용자가 “문서와 코드 PR을 분리”하라고 하거나, 기존 PR이 두 관심사를 섞고 있을 때.
- Linear 이슈와 Notion 설계 노트가 이미 작업의 source of truth로 쓰이는 ReplaceMe 작업일 때.
- PR 제목이 ticket identity 없이 Conventional Commit 또는 일반 설명만 담고 있을 때.
- 제목 오류를 발견했지만 같은 PR의 branch, body/evidence, lifecycle은 유지해야 할 때.

적용하지 않아도 되는 경우도 있다. 순수 코드 변경이고 별도 계약/계획 문서가 없거나,
문서 변경이 코드 변경의 부수적인 README 한 줄에 불과하다면 하나의 코드 PR에 포함해도 된다.
문서만 있는 단일 PR도 기본 `[티켓 번호] 티켓 제목`으로 충분하다. `(문서)`와 `(코드)`
suffix는 같은 티켓의 paired surface를 구별할 때만 사용한다.

## Examples

나쁜 흐름:

```text
1. ZZA-56의 기능 문서, 계획 문서, API 코드, 테스트를 한 PR에 담는다.
2. PR 제목을 `feat: add run passport minimum contract`로 둔다.
3. GitHub PR만 고치고 Linear/Notion에는 split 결과를 남기지 않는다.
```

title-only 수정 흐름:

```text
1. PR #24의 title, head/base, body/evidence, lifecycle을 각각 확인한다.
2. title만 `docs: 병합된 인프라 티켓 상태 동기화`로 잘못된 것을 확인한다.
3. 같은 PR을 `[ZZA-69] ZZA-65~68 merge closeout 문서 동기화`로 rename한다.
4. PR 번호, branch, body/evidence, OPEN 상태는 그대로 유지한다.
```

좋은 split 흐름:

```text
1. #9 [ZZA-56] Run Passport minimum schema/interface (문서)
   base: main
   files: README/docs/features/docs/plans only

2. #8 [ZZA-56] Run Passport minimum schema/interface (코드)
   base: ZZA-56/run-passport-contract-docs
   files: src/tests only

3. Linear ZZA-56 댓글에 #9/#8, base 관계, 검증 결과를 남긴다.
4. Notion Run Passport 설계 노트에 v0 결정, 비목표, 검증 결과를 남긴다.
```

Linear 댓글 예시:

```markdown
## 2026-07-09 진행 반영

ZZA-56은 PR을 문서/코드로 분리한 stacked PR로 정리했습니다.

- 문서 PR: #9 — [ZZA-56] Run Passport minimum schema/interface (문서)
- 코드 PR: #8 — [ZZA-56] Run Passport minimum schema/interface (코드)

PR이 열렸으므로 상태는 In Review로 전환하고, 마지막 PR closeout 전까지 유지합니다.
```

## Related

- `docs/solutions/workflow-issues/split-oversized-integration-pr-into-deployable-stacked-prs.md` — 큰 PR을 deployable slice와 stacked PR로 분리하는 기존 workflow.
- `docs/solutions/conventions/pr-description-template.md` — PR 본문은 한국어 4섹션 구조를 따른다.
- `docs/works/README.md` — 티켓 work evidence, 최신-head review marker, merge closeout 규약.
- `docs/kb/README.md` — merge된 기능의 현재 상태와 운영 지식 저장 규약.
- `docs/solutions/workflow-issues/notion-operator-guide-qa-document-hierarchy.md` — QA 문서는 티켓 페이지가 아니라 운영자 가이드 아래에 둔다.
- `docs/solutions/workflow-issues/run-passport-contract-before-dependent-follow-ups.md` — ZZA-56 최소 Run Passport 계약을 후속 작업 전에 먼저 정의해야 하는 이유.
- GitHub PR `#24`: `[ZZA-69] ZZA-65~68 merge closeout 문서 동기화` — title-only correction 사례.
- GitHub PR `#9`: `[ZZA-56] Run Passport minimum schema/interface (문서)`.
- GitHub PR `#8`: `[ZZA-56] Run Passport minimum schema/interface (코드)`.

<!-- markdownlint-enable MD013 MD025 -->
