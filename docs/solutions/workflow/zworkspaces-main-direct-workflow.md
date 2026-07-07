---
title: zWorkspaces 루트 메타 작업은 main에서 직접 수행한다
date: 2026-07-07
category: workflow
module: workspace-git-workflow
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - zWorkspaces 루트 저장소에서 메타 문서, 서브모듈 포인터, 워크스페이스 설정을 바꿀 때
  - 사용자가 zWorkspaces 루트 작업을 요청했지만 별도 브랜치나 PR을 명시하지 않았을 때
  - 개별 프로젝트 저장소가 아니라 워크스페이스 컨테이너 자체를 정리할 때
symptoms:
  - zWorkspaces 루트 메타 변경에 불필요한 feature branch와 PR이 생긴다
  - 사용자가 main 직접 작업을 기대했는데 PR 정리와 브랜치 삭제가 추가로 필요해진다
  - 독립 프로젝트 repo 작업과 워크스페이스 포인터 작업의 git 흐름이 섞인다
root_cause: missing_workflow_step
resolution_type: workflow_improvement
tags: [zworkspaces, main-branch, git-workflow, workspace, pr-hygiene]
related_components: [documentation, tooling, assistant]
---

<!-- markdownlint-disable MD025 -->

# zWorkspaces 루트 메타 작업은 main에서 직접 수행한다

## Context

zWorkspaces 루트 저장소는 제품 코드가 모이는 일반 monorepo라기보다 여러
프로젝트, 블로그, 운영 문서, Compound Engineering 산출물을 묶는 Workspace
Container다. 따라서 루트 저장소의 변경은 대개 워크스페이스 메타데이터,
문서, 서브모듈 포인터, 프로젝트 등록 정보를 정리하는 성격이다.

일반적인 기능 개발 습관대로 브랜치를 만들고 PR을 열면 이 저장소에서는 오히려
불필요한 정리 비용이 생긴다. `ReplaceMe`를 별도 저장소로 분리하고
`projects/ReplaceMe` 서브모듈로 등록하는 과정에서도 처음에는 브랜치와 PR을
열었다가, 사용자의 운영 규칙에 맞춰 main에 직접 반영하고 PR/브랜치를 닫아야
했다.

## Guidance

zWorkspaces 루트 저장소 자체의 메타 작업은 기본적으로 `main`에서 직접 한다.
별도 브랜치와 PR은 사용자가 명시적으로 요청했거나, 장시간 검토가 필요한 위험한
변경일 때만 사용한다.

기본 흐름:

```bash
cd /path/to/zWorkspaces
git checkout main
git pull --ff-only origin main

# 문서, 서브모듈 포인터, 워크스페이스 메타데이터 변경

git status
git add <changed-files>
git commit -m "docs: ..."  # 또는 chore: ...
git push origin main
```

적용 대상 예시:

- `AGENTS.md`, `CLAUDE.md`, `CONCEPTS.md` 같은 루트 안내 문서 변경
- `docs/solutions/`, `docs/plans/`, `docs/brainstorms/`의 워크스페이스 레벨 문서
- `.gitmodules` 변경과 `projects/<name>` 서브모듈 gitlink 등록 또는 갱신
- 워크스페이스 루트의 README, runbook, 공통 메타데이터 정리

예외적으로 브랜치/PR을 사용해도 되는 경우:

- 사용자가 “PR 열어”, “브랜치 따서”, “리뷰 받자”처럼 명시한 경우
- 루트 저장소 구조를 크게 바꾸는 위험한 변경
- 여러 사람이 리뷰해야 하는 정책 변경
- 개별 프로젝트 저장소 내부의 제품 코드 작업. 이 경우에는 해당 프로젝트 repo의
  규칙을 따른다.

## Why This Matters

이 규칙은 zWorkspaces의 역할을 분명하게 유지한다.

- 루트 저장소는 Workspace Container로서 포인터와 문서를 빠르게 최신화한다.
- 불필요한 PR, remote branch, stale branch 정리가 줄어든다.
- 독립 프로젝트의 코드 리뷰와 워크스페이스 메타 변경이 섞이지 않는다.
- 새 세션의 에이전트가 기본 기능 개발 관성 때문에 브랜치를 남발하는 일을 줄인다.

핵심은 “제품 코드는 각 프로젝트 저장소에서, 워크스페이스 메타는 zWorkspaces
main에서”라는 경계를 유지하는 것이다.

## When to Apply

다음 조건이 모두 맞으면 main 직접 작업을 기본값으로 삼는다.

- 현재 작업 디렉터리가 zWorkspaces 루트다.
- 변경 대상이 워크스페이스 문서, 설정, 서브모듈 포인터, 프로젝트 등록 정보다.
- 사용자가 별도 브랜치, PR, 리뷰 흐름을 명시하지 않았다.
- 변경이 즉시 되돌릴 수 있는 메타 작업이다.

다음 조건이면 잠시 멈추고 별도 흐름을 고려한다.

- 변경 대상이 `projects/<name>` 내부의 독립 프로젝트 코드다.
- 장기 기능 개발, 대형 리팩터링, 외부 리뷰가 필요한 변경이다.
- 사용자가 명시적으로 PR 또는 브랜치 작업을 요청했다.

## Examples

잘못된 흐름:

```bash
cd /path/to/zWorkspaces
git checkout -b chore/register-replaceme-submodule
# .gitmodules, AGENTS.md, docs/solutions 변경
git commit -m "chore: register ReplaceMe submodule"
git push -u origin HEAD
gh pr create ...
```

이 흐름은 일반 기능 개발에는 자연스럽지만, zWorkspaces 루트 메타 작업에는
불필요한 PR과 브랜치를 만든다.

올바른 흐름:

```bash
cd /path/to/zWorkspaces
git checkout main
git pull --ff-only origin main
# .gitmodules, AGENTS.md, docs/solutions 변경
git add .gitmodules AGENTS.md docs/solutions/workflow/...
git commit -m "chore: register ReplaceMe submodule"
git push origin main
```

개별 프로젝트 repo 작업은 별개다.

```bash
cd /path/to/zWorkspaces/projects/ReplaceMe
# 여기서는 ReplaceMe 저장소의 브랜치/PR 규칙을 따른다.
```

## Related

- `docs/solutions/workflow-issues/independent-projects-as-standalone-repos-submodules.md` —
  독립 프로젝트 생성 후 Workspaces에 서브모듈로 연결하는 절차.
- `docs/solutions/workflow/submodule-edit-and-pointer-bump.md` — 서브모듈 내부 작업 후
  부모 워크스페이스 포인터를 갱신하는 절차.
