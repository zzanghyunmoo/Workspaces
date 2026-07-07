---
title: 독립 프로젝트는 별도 GitHub 저장소로 만들고 워크스페이스에는 서브모듈로 연결한다
date: 2026-07-07
category: workflow-issues
module: workspace-project-registration
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - zWorkspaces에서 새 독립 프로젝트 또는 새 GitHub 저장소 생성을 요청받았을 때
  - projects/ 아래에 개별 프로젝트 작업공간을 배치해야 할 때
  - 워크스페이스 컨테이너 저장소와 실제 제품 또는 프로젝트 저장소의 이력을 분리해야 할 때
symptoms:
  - 새 프로젝트 구현 파일이 Workspaces 루트 저장소의 projects/<project> 경로에 직접 커밋된다
  - 독립 프로젝트 변경인데 Workspaces 저장소 PR로 열린다
  - 나중에 별도 GitHub 저장소 생성, 기존 PR 종료, 브랜치 삭제, 서브모듈 등록을 수동으로 정리해야 한다
root_cause: missing_workflow_step
resolution_type: workflow_improvement
tags: [workspace, git-submodule, github-repository, project-creation, pr-hygiene]
related_components: [documentation, tooling, assistant]
---

<!-- markdownlint-disable MD025 -->

# 독립 프로젝트는 별도 GitHub 저장소로 만들고 워크스페이스에는 서브모듈로 연결한다

## Context

`ReplaceMe`를 새 프로젝트로 만들어 달라는 요청을 처리하는 과정에서,
독립 프로젝트로 관리되어야 할 코드가 워크스페이스 루트 저장소의 일반
추적 파일로 잘못 구현되었다. 잘못된 위치는 `projects/ReplaceMe`였고,
이 디렉터리 전체가 Workspaces 저장소의 일반 파일처럼 커밋되어 잘못된
Workspaces PR #3까지 열렸다.

올바른 해결은 `ReplaceMe`를 독립 GitHub 저장소로 분리한 뒤,
zWorkspaces에는 `projects/ReplaceMe` 서브모듈로 등록하는 것이었다.
최종 상태는 다음과 같다.

- 독립 저장소: `https://github.com/zzanghyunmoo/ReplaceMe`
- 로컬 프로젝트 원격: `projects/ReplaceMe`의 `origin`이
  `https://github.com/zzanghyunmoo/ReplaceMe.git`
- 잘못 열린 Workspaces PR #3: closed
- 올바른 Workspaces PR #4: `.gitmodules`와 `projects/ReplaceMe` gitlink만
  포함하여 서브모듈 등록
- 바깥 Workspaces 저장소: 서브모듈 등록 브랜치에는 `.gitmodules`와
  gitlink만 존재

## Guidance

zWorkspaces에서 `projects/` 아래에 새 독립 프로젝트를 만들 때는 먼저
“이 코드가 Workspaces 자체의 일부인가, 아니면 별도 제품/서비스/라이브러리인가?”를
판단한다. 별도 제품·서비스·라이브러리라면 Workspaces 저장소에 일반 파일로
구현하지 말고, 독립 Git 저장소로 만든 뒤 Workspaces에는 서브모듈로 연결한다.

권장 흐름은 다음과 같다.

1. 새 프로젝트 디렉터리를 만들되, 독립 저장소로 초기화한다.
2. GitHub에 독립 저장소를 만든다.
3. `projects/<name>` 안에서 커밋하고 독립 저장소로 push한다.
4. 바깥 Workspaces 저장소에서는 프로젝트 파일 전체가 아니라
   서브모듈 메타데이터만 커밋한다.
5. Workspaces PR에는 `.gitmodules`와 `projects/<name>` gitlink만
   포함되는지 확인한다.

예시 명령:

```bash
# 독립 프로젝트 생성
mkdir -p projects/ReplaceMe
cd projects/ReplaceMe

# 프로젝트 자체를 별도 git repo로 초기화
git init -b main
git add .
git commit -m "Initial commit"

# GitHub 저장소 생성 후 원격 연결
gh repo create zzanghyunmoo/ReplaceMe --public --source=. --remote=origin --push
```

이미 `projects/ReplaceMe`가 Workspaces의 일반 파일로 잘못 커밋되었다면,
Workspaces 쪽 변경은 되돌리고 독립 저장소로 분리한다.

```bash
# 바깥 Workspaces 저장소에서 잘못 추적된 프로젝트 파일 제거 또는 되돌림
cd /path/to/zWorkspaces
git status

# 상황에 따라 잘못된 브랜치/PR은 닫고 main을 clean 상태로 복구
# 이후 독립 repo가 준비된 상태에서 서브모듈로 등록
git submodule add https://github.com/zzanghyunmoo/ReplaceMe.git projects/ReplaceMe
git add .gitmodules projects/ReplaceMe
git commit -m "Register ReplaceMe as submodule"
git push
```

검증할 때는 다음을 확인한다.

```bash
# 프로젝트 내부가 올바른 독립 저장소를 바라보는지 확인
cd projects/ReplaceMe
git remote -v

# 바깥 Workspaces에서는 일반 파일이 아니라 서브모듈 gitlink만 보이는지 확인
cd /path/to/zWorkspaces
git status
git diff --stat main...HEAD
git submodule status projects/ReplaceMe
```

Workspaces PR의 diff에 독립 프로젝트의 소스 파일 전체가 나타나면 잘못된
신호다. 올바른 PR은 보통 `.gitmodules` 변경과 `projects/<name>` gitlink
변경만 포함한다.

## Why This Matters

zWorkspaces는 여러 작업 공간과 프로젝트를 모아 두는 상위 저장소다.
독립 프로젝트를 일반 파일로 넣으면 다음 문제가 생긴다.

- Workspaces 저장소의 변경 이력이 제품 코드 변경으로 오염된다.
- 독립 프로젝트의 이슈, PR, 릴리스, 권한, 배포 흐름을 분리하기 어렵다.
- 실수로 잘못된 저장소에 PR을 열 가능성이 커진다.
- 추후 다른 환경에서 프로젝트만 clone하거나 배포 자동화를 구성하기 어렵다.

반대로 독립 저장소 + 서브모듈 구조를 사용하면 Workspaces는 “어떤 프로젝트를
어느 커밋으로 참조하는지”만 관리하고, 실제 제품 코드는 해당 프로젝트 저장소에서
독립적으로 관리할 수 있다.

## When to Apply

다음 상황에서는 `projects/<name>`을 Workspaces의 일반 디렉터리로 커밋하지 말고
독립 repo + submodule 방식을 사용한다.

- 새 앱, 서비스, 라이브러리, 제품 실험을 시작할 때
- GitHub에서 별도 저장소 URL을 가져야 할 때
- 독립적인 이슈/PR/릴리스/배포 흐름이 필요한 프로젝트일 때
- 다른 사람이 Workspaces 전체가 아니라 해당 프로젝트만 clone해서 작업할 수 있어야 할 때
- `projects/` 아래에 장기적으로 유지할 코드베이스를 추가할 때

반대로 워크스페이스 운영 문서, 공통 runbook, 상위 관리용 스크립트처럼
Workspaces 자체의 일부인 파일은 일반 추적 파일로 둘 수 있다.

## Examples

잘못된 흐름:

```bash
cd /path/to/zWorkspaces
mkdir -p projects/ReplaceMe
# 독립 서비스 코드를 작성
git add projects/ReplaceMe
git commit -m "Add ReplaceMe project"
# Workspaces PR에 ReplaceMe 전체 소스가 포함됨
```

이 흐름은 `ReplaceMe`가 독립 프로젝트인데도 Workspaces 저장소의 일반 파일로
들어가기 때문에 피해야 한다.

올바른 흐름:

```bash
# 1. 프로젝트 자체 저장소 준비
cd /path/to/zWorkspaces/projects/ReplaceMe
git init -b main
git add .
git commit -m "Initial ReplaceMe project"
gh repo create zzanghyunmoo/ReplaceMe --public --source=. --remote=origin --push

# 2. Workspaces에는 서브모듈로 등록
cd /path/to/zWorkspaces
git submodule add https://github.com/zzanghyunmoo/ReplaceMe.git projects/ReplaceMe
git add .gitmodules projects/ReplaceMe
git commit -m "Register ReplaceMe submodule"
```

복구 흐름의 핵심:

```bash
# 잘못된 Workspaces PR은 닫는다.
# 독립 GitHub repo를 만든다.
# projects/ReplaceMe를 자체 repo로 초기화하고 push한다.
# Workspaces에는 submodule 등록 PR만 새로 연다.
```

`ReplaceMe` 사례에서는 잘못 열린 Workspaces PR #3을 닫고,
`zzanghyunmoo/ReplaceMe` 독립 공개 저장소를 만든 뒤, Workspaces PR #4에서
`.gitmodules`와 `projects/ReplaceMe` gitlink만 등록하는 방식으로 정리했다.

## Related

- `docs/solutions/workflow/submodule-edit-and-pointer-bump.md` — 이미 존재하는
  서브모듈 작업 후 parent pointer bump 절차. 이 문서는 그보다 앞선 단계인
  독립 프로젝트 생성과 최초 서브모듈 등록 절차를 다룬다.
- `docs/solutions/conventions/pr-description-template.md` — Workspaces PR을 열 때
  따라야 하는 한국어 PR 본문 구조.
