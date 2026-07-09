---
title: Run Passport 최소 계약을 후속 자동화 작업 전에 먼저 정의한다
date: 2026-07-09
category: workflow-issues
module: replace-me-run-passport-workflow
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - ZZA-51 readiness 완료 뒤 ZZA-52, ZZA-55, ZZA-56 후속 작업을 계획할 때
  - 여러 후속 티켓이 동일한 실행 식별자, 산출물 URL, PR/Notion backlink를 참조해야 할 때
  - Run Passport를 아직 구현하지 않았지만 PR 리뷰 패킷 또는 Notion lifecycle 문서가 Passport 필드나 링크를 요구할 때
  - Linear issue execution grammar를 병렬 진행할 수 있는지 의존성 경계를 확인할 때
symptoms:
  - ZZA-52와 ZZA-55가 같은 실행 기록을 참조해야 하지만 공통 필드명이 아직 없다
  - Notion 문서와 PR 본문이 서로 다른 run link, status, risk wording을 만들 위험이 있다
root_cause: missing_workflow_step
resolution_type: workflow_improvement
tags: [replaceme, run-passport, linear, github-pr, notion, follow-up-sequencing, developer-workflow]
related_components: [documentation, tooling, assistant]
---

# Run Passport 최소 계약을 후속 자동화 작업 전에 먼저 정의한다

## Context

ReplaceMe의 `personal-github-linear-notion` 작업은 먼저 readiness profile을 세우고,
그 밖의 end-to-end 자동화 표면은 후속 이슈로 분리했다. ZZA-51 계획은 Linear
issue execution, Run Passport schema, PR packet generation, Notion lifecycle
documents의 product scope를 변경하기 전에 멈추라고 명시한다
(`projects/ReplaceMe/docs/plans/2026-07-08-001-feat-personal-github-linear-notion-profile-plan.md:23`).
같은 계획은 readiness를 먼저 검증하고 Linear execution rules, Run Passport detail,
PR packet generation, Notion lifecycle documents는 각각 follow-up issue에 남긴다고
정한다
(`projects/ReplaceMe/docs/plans/2026-07-08-001-feat-personal-github-linear-notion-profile-plan.md:45`).

후속 소유권도 이미 나뉘어 있다. Linear issue execution grammar는 ZZA-53,
Run Passport field detail/persistence/rerun lineage는 ZZA-56, GitHub PR review
packet generation은 ZZA-55, Notion lifecycle documents와 pattern bank behavior는
ZZA-52가 맡는다
(`projects/ReplaceMe/docs/plans/2026-07-08-001-feat-personal-github-linear-notion-profile-plan.md:142-147`).
문제는 이 네 작업이 완전히 독립적이지 않다는 점이다. Ideation 문서는 Run Passport가
Linear 이슈, GitHub 브랜치/PR, Notion 문서, 실행 컨테이너, 설정, 승인 기록,
로그 요약, 테스트 결과, 실패 이유를 담고, Linear 댓글·GitHub PR 본문·Notion 문서가
모두 이 Passport를 가리킨다고 설명한다
(`projects/ReplaceMe/docs/ideation/2026-07-08-replaceme-github-linear-notion-dev-automation-ideation.html:878-881`).

세션 히스토리에서도 같은 위험이 보였다. ZZA-51 구현·QA·PR 흐름은 readiness check,
Notion QA 계층, 코드/문서 PR 분리까지 보강했지만, ZZA-52/ZZA-55가 공유할
Run Passport 최소 handoff artifact는 아직 없었다(session history). 따라서 ZZA-56을
바로 큰 persistence 작업으로 시작하기보다, 먼저 병렬 소비자들이 참조할 얇은 계약을
정해야 한다.

## Guidance

ZZA-51 readiness foundation이 끝난 뒤에는 후속 작업을 바로 병렬로 흩뿌리지 말고,
ZZA-56의 첫 slice로 **최소 Run Passport 계약**을 먼저 정의한다. 이 계약은 전체
Run Passport 제품이 아니라, ZZA-52와 ZZA-55가 같은 이름과 링크를 소비하게 만드는
작은 공통 언어다.

권장 순서는 다음과 같다.

1. ZZA-51 readiness step이 끝났는지 사용자 확인 또는 remote 상태 확인으로 확정한다.
2. ZZA-56을 full persistence/rerun-lineage 구현이 아니라 `run-passport-summary/v0`
   같은 최소 계약 slice로 시작한다.
3. 그 계약을 기준으로 ZZA-52 Notion lifecycle docs와 ZZA-55 PR review packet을
   병렬 진행한다.
4. ZZA-53은 Linear issue grammar/runnable contract를 설계하고, 이후
   Run Passport 연계를 위한 최소 handoff만 남긴다.

최소 계약은 downstream surface가 당장 렌더링해야 하는 질문만 답하면 된다.

- **Canonical identity:** `runPassportId`, 선택적 `runPassportUrl`, contract
  version.
- **Source links:** Linear issue, repository, branch, PR, Notion document의
  id/link.
- **Human summary:** title, status summary, outcome/status, next action.
- **Review support:** test summary, residual-risk summary, failure reason.
- **Phase/nullability:** run phase별 required, nullable, derived,
  not-yet-available 필드.
- **Ownership:** 어느 workflow component가 각 필드를 생성·수정할 수 있는지.
- **Redaction boundary:** secret, local path, token, 내부 host를 Passport에
  남기지 않는 규칙.

이 계약 slice에서 Linear issue grammar, Notion page lifecycle content model,
PR packet body generator, readiness behavior를 다시 설계하지 않는다. 각 상세 제품은
자기 티켓에서 구현하고, 공통 식별자·링크·요약 필드만 Run Passport 최소 계약으로
수렴시킨다.

## Why This Matters

Run Passport는 여러 산출물의 공통 참조점이다. PR review packet 아이디어는 PR 본문에
문제, 변경 사항, 테스트, 데모, Linear 이슈 링크, Notion 문서 링크, Run Passport,
남은 위험을 넣는다고 설명한다
(`projects/ReplaceMe/docs/ideation/2026-07-08-replaceme-github-linear-notion-dev-automation-ideation.html:925-928`).
Notion lifecycle 아이디어도 작업이 시작되면 문서를 만들고, 승인 대기, PR 생성, 실패,
완료, 배운 점까지 계속 업데이트되는 문서를 기대한다
(`projects/ReplaceMe/docs/ideation/2026-07-08-replaceme-github-linear-notion-dev-automation-ideation.html:972-976`).

최소 계약 없이 ZZA-52와 ZZA-55를 동시에 시작하면 두 작업이 각각 `notionRunUrl`,
`passport_link`, status 이름, risk wording을 새로 만들 가능성이 높다. 나중에 ZZA-56이
세 번째 형태를 정의하면, 세 표면을 다시 normalize해야 한다. 반대로 얇은 계약을 먼저
정하면 Notion과 PR surface는 같은 field semantics를 소비하고, ZZA-56은 이후 persistence,
rerun lineage, pattern bank 같은 더 무거운 기능을 안전하게 확장할 수 있다.

이 규칙은 모든 follow-up을 full Run Passport 구현 뒤로 미루라는 뜻이 아니다. 병렬화를
막는 것은 전체 Passport가 아니라 **공유 계약 부재**다. 계약만 얇게 세우면 ZZA-52,
ZZA-53, ZZA-55는 서로 다른 surface를 병렬로 진행할 수 있다.

## When to Apply

다음 조건이 겹칠 때 적용한다.

- ZZA-51 같은 readiness/foundation 작업이 끝나고 follow-up implementation
  wave를 시작할 때.
- 둘 이상의 후속 기능이 같은 run summary, status, evidence, canonical link를
  표시해야 할 때.
- 한 기능은 Notion lifecycle 문서처럼 documentation/reporting surface이고,
  다른 기능은 GitHub PR review packet처럼 review surface일 때.
- Linear issue execution grammar처럼 자기 runnable contract를 먼저 설계하되
  나중에 Passport link를 붙일 최소 handoff가 필요한 기능이 있을 때.
- 병렬 subagent나 stacked PR로 작업을 나누려는데, 공통 field contract가 없어서
  각 slice가 자체 용어를 만들 위험이 있을 때.

적용하지 않아도 되는 경우도 있다. 단일 follow-up이 혼자 소비하는 내부 필드라면 먼저
큰 계약을 세울 필요가 없다. 또한 이미 stable contract가 존재하고 소비자들이 같은
version을 참조한다면, 새 계약 대신 기존 contract를 업데이트한다.

## Examples

좋은 순서:

```text
1. 사용자 또는 release process가 ZZA-51 readiness step 완료를 확인한다.
2. ZZA-56a가 Run Passport summary contract v0를 정의한다.
   - id/link/version
   - Linear/GitHub/Notion links
   - status/summary/next action
   - tests/residual risks/failure reason
   - phase별 required vs nullable fields
   - redaction boundary
3. ZZA-52가 이 contract field로 Notion lifecycle 문서를 렌더링한다.
4. ZZA-55가 같은 contract field로 PR review packet을 렌더링한다.
5. ZZA-53은 Linear issue grammar/runnable contract를 설계하고, 실행 생성 시
   이후 Run Passport 연계를 위한 최소 handoff를 남긴다.
```

나쁜 순서:

```text
1. ZZA-52가 Notion page용 `notionRunUrl`과 자체 status 이름을 만든다.
2. ZZA-55가 PR body용 `passport_link`와 다른 risk wording을 만든다.
3. ZZA-56이 나중에 세 번째 Run Passport schema를 정의한다.
4. 통합 단계에서 세 표면의 field name, nullability, status semantics를 다시 맞춘다.
```

계약 논의를 위한 최소 consumer mock:

```json
{
  "contractVersion": "run-passport-summary/v0",
  "runPassportId": "rp_20260709_001",
  "runPassportUrl": "https://example.invalid/run-passports/rp_20260709_001",
  "linearIssueUrl": "https://linear.app/...",
  "pullRequestUrl": null,
  "notionDocumentUrl": null,
  "status": "running",
  "summary": "Implement selected issue after readiness passed.",
  "testSummary": null,
  "residualRiskSummary": null
}
```

이 JSON은 저장소가 이미 구현한 필드의 증거가 아니라, ZZA-56a에서 합의할 최소 계약의
논의 예시다.

## Related

<!-- markdownlint-disable MD013 -->
- `projects/ReplaceMe/docs/plans/2026-07-08-001-feat-personal-github-linear-notion-profile-plan.md:45` — readiness-first decision과 follow-up boundary.
- `projects/ReplaceMe/docs/plans/2026-07-08-001-feat-personal-github-linear-notion-profile-plan.md:142-147` — ZZA-53, ZZA-56, ZZA-55, ZZA-52의 ownership split.
- `projects/ReplaceMe/docs/ideation/2026-07-08-replaceme-github-linear-notion-dev-automation-ideation.html:878-881` — Run Passport가 Linear, GitHub, Notion surface의 공통 참조점이라는 설명.
- `projects/ReplaceMe/docs/ideation/2026-07-08-replaceme-github-linear-notion-dev-automation-ideation.html:925-928` — PR review packet이 Run Passport와 cross-surface links를 필요로 하는 이유.
- `projects/ReplaceMe/docs/ideation/2026-07-08-replaceme-github-linear-notion-dev-automation-ideation.html:972-976` — Notion lifecycle page가 status와 outcome update를 필요로 하는 이유.
- `docs/solutions/workflow-issues/split-oversized-integration-pr-into-deployable-stacked-prs.md` — 병렬/스택 작업 전에 deployable slice와 review order를 정하는 관련 workflow.
- `docs/solutions/workflow-issues/notion-operator-guide-qa-document-hierarchy.md` — QA 절차는 티켓 페이지가 아니라 운영자 가이드 아래에 두는 placement 규칙.
- `docs/solutions/conventions/pr-description-template.md` — ZZA-55가 Run Passport evidence를 넣더라도 유지해야 할 PR/MR 4섹션 구조.
<!-- markdownlint-enable MD013 -->
