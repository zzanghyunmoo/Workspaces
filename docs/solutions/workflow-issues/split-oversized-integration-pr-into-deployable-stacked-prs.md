---
title: 거대한 통합 PR은 배포 가능한 스택 PR로 분해한다
date: 2026-07-07
category: workflow-issues
module: replace-me-pr-workflow
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - 단일 통합 PR이 여러 배포 관심사를 한꺼번에 포함할 때
  - 의존성이 있는 변경을 순서대로 리뷰하고 배포해야 할 때
  - oversized PR을 닫고 대체 PR 목록과 리뷰 순서를 남겨야 할 때
symptoms:
  - 하나의 PR에 큐 전환, provider 분리, 외부 연동, telemetry 변경이 함께 들어간다
  - 리뷰어가 어떤 변경부터 머지하거나 배포할지 판단하기 어렵다
  - PR 제목이 워크스페이스 convention과 다르게 Conventional Commit prefix를 포함한다
root_cause: missing_workflow_step
resolution_type: workflow_improvement
tags: [git, pull-request, stacked-prs, pr-hygiene, integration-workflow, replace-me]
related_components: [documentation, assistant, tooling]
---

# 거대한 통합 PR은 배포 가능한 스택 PR로 분해한다

## Context

`ReplaceMe` 통합 작업을 한 번에 담은 거대한 PR `#1`이 만들어졌다. 이 PR은 리뷰 범위가 크고, 변경 간 의존성이 섞여 있어 개별 배포·검증·롤백 단위를 판단하기 어려웠다. 해결 과정에서는 `#1`을 닫고, 동일한 변경을 배포 가능한 순서의 stacked PR로 재구성했다.

최종 스택은 다음과 같다.

1. `#2`: `main <- feat/kafka-agent-queue`
2. `#3`: `feat/kafka-agent-queue <- feat/provider-agent-notifier`
3. `#4`: `feat/provider-agent-notifier <- feat/issue-document-integrations`
4. `#5`: `feat/issue-document-integrations <- feat/telemetry-docs`

닫힌 `#1`에는 후속 PR 링크를 남겨 맥락을 보존했다. 그리고 워크스페이스 PR 제목 규칙에 맞게 PR 제목에서 `feat(...)` 같은 Conventional Commit 접두사를 제거했다. PR 본문과 제목은 기본적으로 한국어로 작성하는 규칙을 따랐다.

## Guidance

거대한 통합 PR은 그대로 리뷰하지 말고, 먼저 **배포 가능한 slice** 단위로 나눈다. 각 slice는 독립적으로 이해·검증·배포 가능한 의미 단위여야 한다.

권장 절차는 다음과 같다.

1. 큰 PR의 변경을 배포 순서대로 나눈다.
   - 기반 인프라 또는 큐 변경
   - 그 위에 얹히는 provider 또는 runtime 선택 기능
   - 외부 연동 기능
   - 관측성, 문서, 운영 보강
2. 첫 PR은 `main`을 base로 둔다.
3. 다음 PR부터는 직전 feature branch를 base로 둔다.
   - 예: `main <- A`, `A <- B`, `B <- C`.
4. 각 PR 본문에 해당 PR이 담당하는 범위와 후속 PR 의존성을 적는다.
5. 원래의 oversized PR은 닫고, 닫는 코멘트에 대체 PR 목록과 리뷰 순서를 링크한다.
6. PR 제목은 워크스페이스 convention에 맞춘다.
   - 제목에는 `feat(...)`, `fix(...)` 같은 Conventional Commit 접두사를 붙이지 않는다.
   - 사람이 읽기 쉬운 한국어 제목을 사용한다.
7. PR 본문은 한국어 4섹션 구조를 따른다.
   - 해결하려는 문제가 무엇인가요?
   - 변경 사항
   - 테스트 체크리스트
   - 데모

기존 큰 PR을 닫는 이유는 변경을 버리기 위해서가 아니라, 리뷰 가능하고 배포 가능한 단위로 재구성하기 위해서임을 명시한다.

## Why This Matters

거대한 PR은 리뷰 지연, 테스트 범위 불명확, 배포 위험 증가, 롤백 곤란을 만든다. 반대로 배포 가능한 slice로 나눈 stacked PR은 각 변경의 목적과 영향 범위를 좁혀 준다.

이 방식의 효과는 다음과 같다.

- 리뷰어가 변경을 순서대로 이해할 수 있다.
- 앞선 기반 변경이 승인·머지된 뒤 다음 변경을 안전하게 검토할 수 있다.
- 배포 단위가 작아져 장애 발생 시 원인 추적과 롤백이 쉬워진다.
- 닫힌 큰 PR의 맥락이 링크로 보존되어 히스토리가 끊기지 않는다.
- PR 제목과 본문 convention을 지켜 저장소의 리뷰 경험이 일관된다.

## When to Apply

다음 상황에서 적용한다.

- 하나의 PR에 인프라, 애플리케이션 로직, 문서, telemetry 등 여러 계층의 변경이 섞여 있을 때
- PR이 너무 커서 리뷰어가 한 번에 검토하기 어렵다고 판단될 때
- 변경 간 의존성이 있어 단순 병렬 PR보다 순차 리뷰가 필요한 때
- 일부 변경만 먼저 배포하거나 검증해야 할 때
- 기존 PR을 유지하면 리뷰 순서, 배포 순서, 책임 범위가 불명확해질 때
- 워크스페이스 PR convention과 다른 제목·본문 형식을 바로잡아야 할 때

## Examples

### Oversized PR 닫기 코멘트 예시

```markdown
이 PR은 ReplaceMe 통합 변경을 한 번에 포함해 리뷰·배포 단위가 너무 큽니다.
배포 가능한 slice 단위로 stacked PR을 다시 만들었으므로 이 PR은 닫습니다.

대체 PR은 아래 순서로 리뷰하면 됩니다.

1. #2: main <- feat/kafka-agent-queue
2. #3: feat/kafka-agent-queue <- feat/provider-agent-notifier
3. #4: feat/provider-agent-notifier <- feat/issue-document-integrations
4. #5: feat/issue-document-integrations <- feat/telemetry-docs
```

### 스택 구성 예시

```text
main
└── feat/kafka-agent-queue                    (#2)
    └── feat/provider-agent-notifier          (#3)
        └── feat/issue-document-integrations  (#4)
            └── feat/telemetry-docs           (#5)
```

### PR 제목 수정 예시

```text
Before: feat(queue): Kafka 기반 에이전트 큐로 전환
After:  Kafka 기반 에이전트 큐로 전환

Before: feat(providers): 저장소와 알림 provider 분리
After:  저장소와 알림 provider 분리
```

### PR 본문 작성 방향

```markdown
## 해결하려는 문제가 무엇인가요?
기존 통합 PR은 리뷰 범위가 커서 변경 의도를 추적하기 어렵습니다.

## 변경 사항
- 이 PR은 Kafka agent queue 기반 변경만 포함합니다.
- 후속 변경은 다음 stacked PR에서 다룹니다.

## 테스트 체크리스트
- [x] `dotnet build DevAutomation.sln --no-restore`
- [x] `dotnet test DevAutomation.sln --no-restore`

## 데모
해당 없음. 내부 실행 경로 변경이며, `/health`로 Kafka 연결을 확인합니다.
```

## Related

- `docs/solutions/conventions/pr-description-template.md` — PR/MR 본문은 한국어 4섹션 구조를 따른다.
- `docs/solutions/workflow/submodule-edit-and-pointer-bump.md` — submodule 작업은 child repo PR 후 parent pointer bump가 필요하다.
- `docs/solutions/workflow-issues/independent-projects-as-standalone-repos-submodules.md` — 독립 프로젝트 변경은 workspace 루트 PR과 분리한다.
- `docs/solutions/workflow/zworkspaces-main-direct-workflow.md` — zWorkspaces 루트 메타 작업과 프로젝트 repo 작업의 경계를 구분한다.
