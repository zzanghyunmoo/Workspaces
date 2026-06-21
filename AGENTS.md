# AGENTS.md — 글로벌 가드레일

이 워크스페이스(`zWorkspaces`)에서 작업하는 모든 에이전트가 따라야 하는 규칙.

## Compound Engineering 산출물 저장 위치

각 스킬의 결과물은 다음 경로에 저장한다. 다른 경로에 흩뿌리지 말 것.

| 스킬 | 저장 위치 | 파일명 패턴 |
|---|---|---|
| `ce-brainstorm` | `docs/brainstorms/` | `<YYYY-MM-DD>-<topic>-requirements.md` |
| `ce-plan` | `docs/plans/` | `<YYYY-MM-DD>-<topic>-plan.md` |
| 그 외 (solution 등) | `docs/solutions/<category>/` | 해당 스킬 규약 따름 |

## Compound Engineering 활용 흐름

- 거대하거나 방향성이 열려 있는 작업은 먼저 `$compound-engineering:ce-ideate`로 후보와 트레이드오프를 좁힌다.
- 단일 기능/문서/프로젝트 작업은 `$compound-engineering:ce-brainstorm` -> `$compound-engineering:ce-plan` -> `$compound-engineering:ce-doc-review` -> `$compound-engineering:ce-work` -> `$compound-engineering:ce-code-review` -> `$compound-engineering:ce-compound` 순서로 진행하는 것을 기본 흐름으로 삼는다.
- 오류, 실패, 회귀, 원인 추적 작업은 사용자가 `/ce-debug`라고 부를 수 있게 안내하고, 해당 경우 `compound-engineering:ce-debug`를 사용한다.
- 검증이 끝난 비반복 지식, 워크플로 결정, 프로젝트 운영 규칙은 `ce-compound`로 `docs/solutions/`에 남긴다.

## 작업 디렉터리 규칙

- `blogs/` — 기술 블로그 (`zzanghyunmoo.github.io`). 디렉터리 자체는 유지, 내용물 교체는 허용.
- `projects/` — 개별 프로젝트 작업 공간.
- `projects/money-pipeline/` — 지속 가능한 사이드 인컴 파이프라인 프로젝트. 작업 전 하위 `AGENTS.md`, `CONCEPTS.md`, `docs/solutions/`를 확인한다.
- `projects/random-tower-defense/` — Unity 6 LTS 계열 랜덤 타워 디펜스 프로젝트. 작업 전 하위 `AGENTS.md`를 확인하고 Unity/C# 가드레일을 따른다.
- `runbooks/` — 운영/실행 절차 문서.
- `docs/` — 워크스페이스 레벨 문서 (`brainstorms/`, `plans/`, `solutions/`).

## 일반 원칙

- 한국어로 응답한다 (사용자가 영어로 물으면 영어).
