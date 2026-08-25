# AGENTS.md — 글로벌 가드레일

이 워크스페이스(`zWorkspaces`)에서 작업하는 모든 에이전트가 따라야 하는 규칙이다.

## 워크스페이스 경계

- 루트 저장소 `zzanghyunmoo/Workspaces`와 현재 연결된 모든 콘텐츠 저장소는 공개
  저장소다. credential, token, private key, password, 복구 코드, 내부 호스트,
  개인 로컬 경로와 공개하면 안 되는 원문을 추적하지 않는다.
- 루트 `docs/` 디렉터리는 사용하지 않으며 새로 만들지 않는다.
- 워크스페이스 공용 장기 지식은 공개 `notes/` 서브모듈에 일반 Markdown으로
  기록한다. 특정 프로젝트의 설계·계획·검증 문서는 해당 프로젝트 저장소가
  소유하고 하위 `AGENTS.md` 규약을 따른다.
- GitHub Issue와 PR은 목표, 상태, 변경과 검증을 추적하는 제어면이다. 문서 본문을
  Issue에 중복 복사하지 않는다.

## 작업 디렉터리

- `blogs/` — 기술 블로그 `zzanghyunmoo/zzanghyunmoo.github.io` 서브모듈.
- `notes/` — 공개 Markdown 노트 `zzanghyunmoo/notes-private` 서브모듈.
- `projects/my-desk-setup/` — macOS·Windows·Lima·WSL 개발 환경 control plane.
- `projects/oh-my-harness/` — Claude Code·OpenCode·Codex 환경 관리자.
- `projects/` — 개별 프로젝트 작업 공간. 각 프로젝트의 하위 가드레일이 우선한다.
- `runbooks/` — 루트 저장소 운영·검증 절차와 실행 도구.
- `CONCEPTS.md` — 워크스페이스 공유 도메인 용어집.

## Compound Engineering 활용

- 방향이 열려 있는 작업은 `compound-engineering:ce-ideate` 또는
  `compound-engineering:ce-brainstorm`으로 범위를 좁힌다.
- 구체적인 다단계 작업은 `ce-plan` → `ce-doc-review` → `ce-work` →
  `ce-code-review` 흐름을 기본으로 하되, 산출물 저장 위치는 작업 대상 프로젝트의
  규약을 따른다.
- 루트 저장소 작업을 위해 `docs/ideation`, `docs/plans`, `docs/works`, `docs/kb`,
  `docs/solutions`를 다시 만들지 않는다. 지속 보존이 필요한 루트 수준 지식은
  `notes/`에 기록할지 사용자와 범위를 확정한다.
- 오류, 실패, 회귀와 원인 추적에는 `compound-engineering:ce-debug`를 사용한다.
- 검증된 프로젝트 지식은 해당 프로젝트의 `ce-compound` 규약에 따라 남긴다.

## 공개 노트 규칙

- `notes/`는 public-first 저장소다. commit 전 파일명, frontmatter, 본문, 첨부파일과
  전체 diff에 민감정보나 개인 경로가 없는지 확인한다.
- `.obsidian/workspace*`, `.trash/`, `.env*`, OS 임시 파일과 credential 파일은
  추적하지 않는다.
- 노트는 가능한 한 표준 Markdown 링크를 사용한다. 공개 블로그 글은
  `runbooks/public-notes-publishing.md`를 확인하고, `notes/`를 build input이나
  content loader로 직접 연결하지 않은 채 검토한 글만 `blogs/`의 기존 branch/PR
  절차로 옮긴다.
- `notes/`의 저장소 URL이나 gitlink 공개는 허용하지만, 공개 전환 이전의 private
  가정이나 민감정보가 다시 유입되지 않게 한다.

## 서브모듈 작업

- `.gitmodules`의 URL과 branch를 source of truth로 사용하고, 최신화 전 각
  서브모듈의 dirty 상태와 upstream을 확인한다.
- 서브모듈 내부 변경과 루트 gitlink 변경을 구분한다. child 변경을 먼저 검증하고
  반영한 뒤 루트 포인터를 갱신한다.
- 사용자 변경, 삭제된 원격 branch와 복구 지점을 덮어쓰지 않는다.
- 서브모듈을 제거할 때는 원격 삭제 여부와 로컬 전용 commit을 확인하고 가능한 한
  복구 가능한 위치로 이동한다.

## 프로젝트 작업 흐름

- 프로젝트 작업 전 해당 저장소의 `AGENTS.md`, `README`, 현재 branch, dirty 상태를
  확인한다.
- `projects/` 아래 저장소에서는 `main`/`master`에 직접 commit 또는 push하지 않는다.
  문서·메타 작업도 별도 branch와 PR을 사용한다.
- 사용자가 프로젝트 기본 branch 직접 반영을 요구해도 실행 직전에 대상 repo,
  branch, 변경 파일, commit message와 push 대상을 한 번 더 제시하고 확인받는다.
- 명시 승인 없이 `MAIN_GUARD_APPROVED=1` 같은 보호 hook 우회 변수를 설정하지 않는다.
- 실제 OS·VM 검증은 대상과 결과를 기록하고, 실행하지 못한 검증은 이유를 명시한다.

## Pi tmux 병렬 워커

- 여러 Pi 세션은 `runbooks/pi-tmux-workers.md`와
  `runbooks/pi_tmux_workers.py`를 기본 제어면으로 사용한다.
- 쓰기 워커는 독립 Git worktree와 비중첩 `--scope`를 사용한다. 포트, DB,
  package install, browser session 같은 환경 singleton은 `--resource`로 예약한다.
- 병렬 워커는 stage, commit, push, merge, rebase 또는 하위 worker 생성을 하지 않는다.
  코디네이터가 diff, scope와 검증 결과를 확인한 뒤 한 slice씩 통합한다.
- 동일 파일, 공용 API/type/schema, migration, lockfile, generated artifact 또는 환경
  singleton을 건드리는 작업은 직렬 실행한다. 기본 동시성은 4개 이하로 유지한다.
- scope 위반, 광범위한 예상 밖 변경, 반복 충돌 또는 공유 환경 오염이 발견되면
  병렬 실행을 중단한다.

## Git 작업 규칙

- 루트 저장소는 운영·가드레일·서브모듈 포인터 저장소이므로 `main`에서 직접
  작업하고 commit/push할 수 있다.
- 기존 dirty 파일과 사용자가 만든 미추적 파일은 명시된 범위 밖에서 수정·삭제하지
  않는다.
- 파괴적 명령 전 exact target을 읽기 전용으로 확인하고, material한 삭제는 복구
  가능 여부를 결과에 알린다.
- 로컬 main 보호 hook은 `runbooks/install-main-guard-hooks.sh`로 설치한다.

## PR/MR merge 승인

- PR/MR 생성, reviewer pass, merge 가능 상태 확인과 merge 순서 정리는 merge 승인으로
  해석하지 않는다.
- merge는 현재 turn에서 사용자가 대상 repo와 PR/MR 번호를 명시해 승인한 경우에만
  실행한다.
- 실행 직전 repo, 번호와 제목, head→base, merge method, commit subject/body,
  branch 삭제 여부와 후속 정리 계획을 한 번에 제시하고 다시 승인받는다.
- 사용자 승인 없는 우회 환경변수나 직접 API mutation으로 보호 절차를 건너뛰지 않는다.

## PR/MR 작성

- 본문은 기본적으로 한국어로 작성하며 사용자가 영어를 명시하면 영어를 사용한다.
- 문제·변경·테스트·데모의 4개 섹션을 기본 구조로 사용하고 관련 Issue를 non-closing
  링크로 연결한다. stacked 작업이 남아 있으면 `Closes`, `Fixes`, `Resolves`를 쓰지 않는다.
- 자동 생성 안내 문구, 예시 blockquote, API key/token/내부 호스트/개인 경로를 남기지
  않는다.

## 일반 원칙

- 한국어로 응답한다. 사용자가 영어로 물으면 영어로 응답한다.
