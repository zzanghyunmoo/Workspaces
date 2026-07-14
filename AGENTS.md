# AGENTS.md — 글로벌 가드레일

이 워크스페이스(`zWorkspaces`)에서 작업하는 모든 에이전트가 따라야 하는 규칙.

## Compound Engineering 산출물 저장 위치

각 단계의 결과물은 다음 경로에 저장한다. 다른 경로에 흩뿌리지 말 것.
`/ce-ideation` 요청은 설치된 `$compound-engineering:ce-ideate`로 실행한다.

<!-- markdownlint-disable MD013 -->
| 단계/스킬 | 저장 위치 | 파일명 패턴 |
| --- | --- | --- |
| `ce-ideate` (`/ce-ideation`) | `docs/ideation/` | `<YYYY-MM-DD>-<topic>-ideation.md` 또는 `.html` |
| `ce-brainstorm` | `docs/brainstorms/` | `<YYYY-MM-DD>-<topic>-requirements.md` |
| `ce-plan` | `docs/plans/` | `<YYYY-MM-DD>-<TICKET>-<topic>-plan.md` |
| `ce-work` | `docs/works/` | `<YYYY-MM-DD>-<TICKET>-<topic>-work.md` |
| merge closeout | `docs/kb/<category>/` | `<YYYY-MM-DD>-<TICKET>-<topic>.md` |
| `ce-compound` | `docs/solutions/<category>/` | 해당 스킬 규약 따름 |
<!-- markdownlint-enable MD013 -->

## Compound Engineering 활용 흐름

- 거대하거나 방향성이 열려 있는 작업은 먼저
  `$compound-engineering:ce-ideate`로 후보와 트레이드오프를 좁힌다.
- 단일 기능/문서/프로젝트 작업은 `ce-brainstorm` → `ce-plan` → 계획
  `ce-doc-review` → `ce-work` → PR 생성 → PR `ce-code-review`와
  `ce-doc-review` → merge closeout → `ce-compound` 순서를 기본으로 한다.
- 오류, 실패, 회귀, 원인 추적 작업은 사용자가 `/ce-debug`라고 부를 수 있게
  안내하고, 해당 경우 `compound-engineering:ce-debug`를 사용한다.
- 검증이 끝난 비반복 지식, 워크플로 결정, 프로젝트 운영 규칙은
  `ce-compound`로 `docs/solutions/`에 남긴다.
- `docs/solutions/`는 과거 문제의 검증된 해결책을 카테고리별로 모아둔
  검색 가능한 지식 저장소다. 각 문서는 YAML frontmatter(`module`, `tags`,
  `problem_type`)를 가진다. 문서화된 영역에서 구현·디버깅·결정할 때
  참고할 만하다.

## 티켓 기반 단계별 필수 가드레일

이 가드레일은 `projects/` 아래 프로젝트의 티켓 기반 변경에 적용한다. 긴급 수정이나
아이디에이션·계획이 불필요한 작은 작업도 단계를 조용히 생략하지 않고 work evidence에
`waived`와 구체적인 이유를 남긴다.

1. **Ideation**
   - `ce-ideate` 결과를 `docs/ideation/`에 저장한다.
   - 같은 내용을 Notion `배경`의 canonical 문서에 먼저 생성하거나 갱신한다.
2. **Plan**
   - Linear 티켓을 새로 만들거나 기존 티켓을 확정한 뒤 `ce-plan`을 실행한다.
   - 로컬 `docs/plans/`와 Notion `개발 문서 > 계획`에 같은 범위와 링크를 남긴다.
3. **Work**
   - 구현 전에 티켓을 `In Progress`로 바꾼다.
   - `docs/works/`의 work evidence와 Notion `개발 문서 > 티켓` 구현 문서를 갱신한다.
   - work 문서의 `주요 변경 지점`에는 개발 로직, 계약, 설정, 데이터 흐름 등 리뷰어가
     확인할 핵심을 파일·심볼 단위로 요약하고, 검증 결과와 미실행 검증을 함께 적는다.
4. **PR review**
   - PR 생성 직후 최신 head에 `ce-code-review`와 `ce-doc-review`를 모두 실행한다.
   - 두 결과를 별도 PR 댓글로 게시하고, blocker를 해결한 최신 head 댓글에만
     `docs/works/README.md`의 `ce-review:v1` passing marker를 넣는다. Merge를 실행하는
     인증 GitHub OWNER/MEMBER/COLLABORATOR가 게시한 댓글만 gate 증빙으로 인정한다.
   - 새 commit이 push되면 이전 marker는 stale이다. 두 리뷰를 다시 실행해 댓글을 갱신한다.
5. **Merge closeout**
   - Merge 뒤 `docs/kb/`에 현재 기능 상태·운영 경계·검증 결과를 정리한다.
   - Notion `디자인 문서 > 기능 현황`과 `개발 문서 > 티켓` 결과 문서를 갱신한다.
   - work evidence에 merge commit, KB 경로, Notion 링크를 기록하고
     `closeout_status: complete`로 마감한다. 마지막 PR이면 Linear 티켓을 `Done`으로
     바꾸고, stacked 후속 PR이 남아 있으면 `In Review`와 `remaining_prs`를 유지한다.

`docs/works/_template.md`를 work evidence 시작점으로 사용한다. 하나의 티켓이 여러 PR로
나뉘면 PR마다 evidence를 하나씩 만들고, 마지막 PR 전까지 Linear `In Review`를 유지한다.
PR merge 전에는
`runbooks/guarded-pr-merge.sh --workflow-evidence <docs/works/...>`가 `origin/main`의
ideation/plan/work 증빙과 PR 최신 head의 두 review marker를 검증한다. Merge 성공 후에는
root pre-push가 closeout 완료를 검사하므로 KB·Notion·티켓 정리 전에는 다음 root push를
완료할 수 없다.

## 문서 이중 발행 및 Notion 기준 동기화

- ReplaceMe처럼 Notion 프로젝트 위키와 로컬 repo docs를 함께 쓰는 작업은 단계별
  산출물을 Notion과 로컬 문서에 모두 남긴다.
- 문서 구조와 본문 기준은 Notion을 canonical source로 삼고, 로컬 문서는 Notion에서
  확정한 제목·범위·섹션·링크 관계를 따라 동기화한다.
- 새 문서를 만들기 전에는 Notion의 기존 parent와 같은 역할의 canonical 문서가 있는지
  확인한다. 중복을 만들었으면 새 사본을 확장하지 말고 canonical 링크를 담은
  이동/중복 안내로 정리한다.
- ReplaceMe Notion 기준 위치는 다음을 따른다: 아이디에이션·아키텍처 배경은 `배경`,
  기능 현황과 기능별 설명 및 merge closeout은 `디자인 문서 > 기능 현황`, 날짜별 실행
  계획은 `개발 문서 > 계획`, 티켓별 작업 계획·구현 설명·검증 결과는
  `개발 문서 > 티켓`.
- 로컬 문서에는 가능하면 대응 Notion 원본 링크나 동기화 기준을 남겨, 로컬 문서가
  독립 원본처럼 drift되지 않게 한다.

## 작업 디렉터리 규칙

- `blogs/` — 기술 블로그(`zzanghyunmoo.github.io`). 디렉터리 자체는 유지,
  내용물 교체는 허용.
- `projects/` — 개별 프로젝트 작업 공간.
- `projects/dotnet-foundation-lab/` — 매일 1시간 C#/.NET 기본기 학습 repo.
  제품 구현보다 작은 예제와 학습 노트를 우선한다.
- `projects/sre-ai-lab/` — 주 2~3회 진행하는 AI SRE 제품/콘텐츠 repo.
  첫 제품 wedge는 Alert Rule Clinic이며, 경제 블로그(`money-flow`)와 Unity
  게임 실험은 이 repo 범위에서 제외한다.
- `runbooks/` — 운영/실행 절차 문서.
- `docs/` — 워크스페이스 레벨 문서(`ideation/`, `brainstorms/`, `plans/`, `works/`,
  `kb/`, `solutions/`).
- `CONCEPTS.md` — 워크스페이스 공유 도메인 용어집(엔티티, 명명된 프로세스,
  상태 개념). 코드베이스를 파악하거나 도메인 개념을 논의할 때 참고할 만하다.

## Git 작업 규칙

- 루트 워크스페이스 repo(`/Users/gurumee92/Workspaces/zWorkspaces`, GitHub
  `zzanghyunmoo/Workspaces`)는 운영·문서·가드레일 repo이므로 `main`에서 직접 작업하고
  commit/push할 수 있다.
- `projects/` 아래 개별 프로젝트 repo(예: `projects/ReplaceMe`)에서는 `main`/`master`
  브랜치에 직접 commit 또는 push 하지 않는다. 문서·메타 작업도 예외가 아니다.
- 프로젝트 repo의 기본 흐름은 티켓 생성/확인 → 별도 브랜치 작업 → PR/MR 생성이다.
- 사용자가 프로젝트 repo의 `main` 직접 반영을 명시적으로 요구해도, 실행 직전에 반드시 한 번
  더 확인한다. 확인 메시지에는 대상 repo, 현재 브랜치, 변경 파일 요약, commit message,
  push 대상 remote/branch를 포함한다.
- 사용자의 명시 승인 없이는 `MAIN_GUARD_APPROVED=1` 같은 프로젝트 main 보호 hook 우회
  환경변수를 설정하지 않는다. hook이 차단하면 중단하고 사용자에게 승인 또는 브랜치/PR 전환을
  묻는다.
- 로컬 main 보호 hook은 `runbooks/install-main-guard-hooks.sh`로 설치한다. 이 스크립트는
  `core.hooksPath`를 `.githooks/`로 설정하고, root repo는 main 직접 작업을 허용하되
  `projects/ReplaceMe` 같은 프로젝트 repo에는 pre-commit/pre-push 차단 규칙을 적용한다.

## PR/MR Merge 승인 규칙

- PR/MR 생성, reviewer pass, merge 가능 상태 확인, "merge order" 정리, Linear In Review/Done
  전환은 merge 승인으로 해석하지 않는다.
- `gh pr merge`, `glab mr merge`, GitHub/GitLab API mutation 등 PR/MR을 병합하거나
  종료하는 명령은 현재 turn에서 사용자가 해당 repo와 PR/MR 번호를 명시해 merge를 승인한
  경우에만 실행한다.
- merge 실행 직전에는 대상 repo, PR/MR 번호와 제목, head→base branch, merge method,
  commit subject/body, branch 삭제 여부, Linear 상태 변경 계획을 한 번에 제시하고 승인을
  받아야 한다.
- GitHub PR merge는 `runbooks/guarded-pr-merge.sh --workflow-evidence
  docs/works/<work-file>.md`를 통해서만 실행한다. 직접 `gh pr merge`를 호출하지 않는다.
  Guard가 최신 head의 code/doc review marker 또는 단계별 증빙 누락을 보고하면 merge 승인을
  받았더라도 먼저 누락을 보완한다.
- 사용자의 명시 승인 없이는 `PR_MERGE_APPROVED=1` 같은 merge 승인 우회 환경변수를
  설정하지 않는다. guard가 차단하면 중단하고 approval packet을 사용자에게 제시한다.
- Linear ticket을 Done으로 옮기는 것은 PR/MR merge 후 `docs/kb`, Notion 기능 현황·티켓
  문서, work evidence closeout까지 완료한 뒤에만 수행한다. Merge 자체는 완료 보고나
  `Done` 전환의 충분조건이 아니다.

## PR/MR 작성 규칙

- GitHub PR 또는 GitLab MR 본문은 기본적으로 한국어로 작성한다.
  사용자가 영어를 명시하면 영어로 작성한다.
- PR/MR 본문은 `docs/solutions/conventions/pr-description-template.md`의
  4섹션 구조(문제·변경·테스트·데모)를 따르고, ticket ID, `docs/works` evidence,
  canonical Notion 구현 문서 링크를 작업 추적 섹션에 포함한다.
- 자동 생성한 안내 문구, 예시용 blockquote, 민감 정보(API key/token/내부
  호스트/개인 경로)는 본문에 남기지 않는다.

## 일반 원칙

- 한국어로 응답한다. 사용자가 영어로 물으면 영어로 응답한다.
