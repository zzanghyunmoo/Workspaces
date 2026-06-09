---
title: Submodule edit workflow — branch in submodule, then bump pointer in parent
category: workflow
severity: high
tags: [submodule, monorepo, git, blogs, zworkspaces, parent-pointer]
applies_when:
  - Working inside zWorkspaces where `blogs/`, `projects/*` 등 일부 디렉터리가 git submodule
  - Submodule 안에서 큰 작업(마이그레이션/리팩터링)을 진행
  - PR 흐름으로 머지 후 부모 워크스페이스 동기화 필요
---

# Problem

`zWorkspaces`의 `blogs/`처럼 일부 디렉터리가 git submodule인 환경에서,
submodule 내부 변경만 커밋하고 끝내면 **부모 워크스페이스는 여전히 옛 커밋을 가리킨다.**
다른 머신에서 `git pull && git submodule update`해도 새 작업이 반영되지 않는 사고가 발생.

# Context

- `blogs/.git` 은 `gitdir: ../.git/modules/blogs` 형태 — 부모의 `.git/modules/` 아래 실제 git 디렉터리가 있음.
- 부모 워크스페이스 입장에서 submodule은 "특정 커밋 SHA를 가리키는 포인터"일 뿐.
- submodule에서 push/merge 했다고 해서 부모의 포인터가 저절로 갱신되지 않음.

# Solution

표준 절차 (zWorkspaces submodule 작업 시):

```bash
# 1) submodule 내부에서 작업
cd blogs
git checkout -b migrate/<feature>
git tag pre-<feature>-migration   # 롤백 포인트
# ... 변경 + 커밋들 ...

# 2) push + PR (gh CLI)
git push -u origin migrate/<feature>
gh pr create --base v4 --head migrate/<feature> --title "..." --body "..."

# 3) PR 머지 후 로컬 default 브랜치 sync
git checkout v4 && git pull --ff-only
git branch -d migrate/<feature>

# 4) ★ 부모 워크스페이스에서 pointer bump (필수)
cd ..
git add blogs
git commit -m "chore: bump blogs submodule to <feature>"
git push
```

확인:
```bash
# 부모에서 어떤 변경인지 보이는 명령
git diff --submodule blogs
# → Submodule blogs <old>..<new>:
#     > Merge pull request #N from ...
```

# Why this works

- Submodule pointer는 부모 레포의 일반 파일처럼 staged → committed → pushed가 되어야 다른 클론에 전파됨.
- `git submodule update --remote`는 *부모가 가리키는 SHA로* 끌어오는 명령. 포인터가 안 올라갔으면 옛것만 받음.
- PR 흐름을 거치면 default 브랜치(v4)에 머지 커밋(`edfd3c0`)이 생기므로, 그 SHA를 부모가 가리키도록 박아두는 게 정답.

# Prevention

- **체크리스트:** submodule 작업 마무리 단계에 *항상* "부모 워크스페이스 pointer bump" 1줄 추가.
- 02-plan 단계에서 작업 대상이 submodule이면 (Unit F 같은) "parent submodule bump" 별도 unit으로 분리.
- `gh pr merge` 직후 자동으로 `cd .. && git add <submodule> && git commit` 하는 습관.
- 머지 직후 README 자동 포맷팅(prettier) 등이 들어가서 submodule 로컬과 origin이 살짝 어긋날 수 있음 → `git pull --ff-only` 전에 `git checkout -- <auto-formatted-files>`로 충돌 회피.
- Pages 같은 배포 워크플로가 submodule 안에 있다면, 부모 pointer가 안 올라가도 배포 자체는 동작함 — 그래서 "배포 됐는데 동기화 안 된다"는 사고가 늦게 발견됨. 발견 시점을 앞당기려면 PR 머지 직후 부모 bump를 의식적으로 수행.

# 참고 — zWorkspaces 현재 submodule 구성

- `blogs/` — `github.com/zzanghyunmoo/zzanghyunmoo.github.io` (default branch `v4`)
- 그 외 `projects/*` 일부도 submodule일 수 있음 — 동일 절차 적용.
