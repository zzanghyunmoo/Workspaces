# AGENTS.md — 글로벌 가드레일

이 워크스페이스(`zWorkspaces`)에서 작업하는 모든 에이전트가 따라야 하는 규칙.

## Compound Engineering 산출물 저장 위치

각 스킬의 결과물은 다음 경로에 저장한다. 다른 경로에 흩뿌리지 말 것.

<!-- markdownlint-disable MD013 -->
| 스킬 | 저장 위치 | 파일명 패턴 |
| --- | --- | --- |
| `ce-brainstorm` | `docs/brainstorms/` | `<YYYY-MM-DD>-<topic>-requirements.md` |
| `ce-plan` | `docs/plans/` | `<YYYY-MM-DD>-<topic>-plan.md` |
| 그 외 (solution 등) | `docs/solutions/<category>/` | 해당 스킬 규약 따름 |
<!-- markdownlint-enable MD013 -->

## Compound Engineering 활용 흐름

- 거대하거나 방향성이 열려 있는 작업은 먼저
  `$compound-engineering:ce-ideate`로 후보와 트레이드오프를 좁힌다.
- 단일 기능/문서/프로젝트 작업은 `$compound-engineering:ce-brainstorm` →
  `$compound-engineering:ce-plan` → `$compound-engineering:ce-doc-review` →
  `$compound-engineering:ce-work` → `$compound-engineering:ce-code-review` →
  `$compound-engineering:ce-compound` 순서로 진행하는 것을 기본 흐름으로 삼는다.
- 오류, 실패, 회귀, 원인 추적 작업은 사용자가 `/ce-debug`라고 부를 수 있게
  안내하고, 해당 경우 `compound-engineering:ce-debug`를 사용한다.
- 검증이 끝난 비반복 지식, 워크플로 결정, 프로젝트 운영 규칙은
  `ce-compound`로 `docs/solutions/`에 남긴다.
- `docs/solutions/`는 과거 문제의 검증된 해결책을 카테고리별로 모아둔
  검색 가능한 지식 저장소다. 각 문서는 YAML frontmatter(`module`, `tags`,
  `problem_type`)를 가진다. 문서화된 영역에서 구현·디버깅·결정할 때
  참고할 만하다.

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
- `docs/` — 워크스페이스 레벨 문서(`brainstorms/`, `plans/`, `solutions/`).
- `CONCEPTS.md` — 워크스페이스 공유 도메인 용어집(엔티티, 명명된 프로세스,
  상태 개념). 코드베이스를 파악하거나 도메인 개념을 논의할 때 참고할 만하다.

## Git 작업 규칙

- `zWorkspaces` 루트 저장소 자체의 메타 작업은 기본적으로 `main`에서 직접
  수행한다. 사용자가 명시적으로 요청한 경우에만 별도 브랜치/PR을 만든다.

## PR/MR 작성 규칙

- GitHub PR 또는 GitLab MR 본문은 기본적으로 한국어로 작성한다.
  사용자가 영어를 명시하면 영어로 작성한다.
- PR/MR 본문은 `docs/solutions/conventions/pr-description-template.md`의
  4섹션 구조(문제·변경·테스트·데모)를 따른다.
- 자동 생성한 안내 문구, 예시용 blockquote, 민감 정보(API key/token/내부
  호스트/개인 경로)는 본문에 남기지 않는다.

## 일반 원칙

- 한국어로 응답한다. 사용자가 영어로 물으면 영어로 응답한다.
