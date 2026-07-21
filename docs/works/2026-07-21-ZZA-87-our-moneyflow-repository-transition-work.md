---
workflow_schema: compound-work/v1
ticket_id: ZZA-87
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-87/u1-sre-ai-lab을-our-moneyflow-저장소로-직접-전환
ticket_status: Done
ticket_completion: complete
remaining_prs:
ideation_status: complete
ideation_path: docs/ideation/2026-07-21-our-moneyflow-ideation.html
ideation_notion_url: https://app.notion.com/p/3a4ef22ad4fc8144a07afe36f395b47d
ideation_waiver_reason:
plan_status: complete
plan_path: docs/plans/2026-07-21-ZZA-86-our-moneyflow-first-release-plan.md
plan_notion_url: https://app.notion.com/p/3a4ef22ad4fc8154b087c4a6a6c65396
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3a4ef22ad4fc81d79240cc3aeeb09453
pr_url: https://github.com/zzanghyunmoo/our-moneyflow/pull/1
closeout_status: complete
merged_pr_url: https://github.com/zzanghyunmoo/our-moneyflow/pull/1
merge_commit: 5c86d8f9765d512e8cb89acd58df7a890150bbaf
kb_paths: docs/kb/repository-transitions/2026-07-21-ZZA-87-our-moneyflow-repository-transition.md
notion_feature_status_url: https://app.notion.com/p/3a4ef22ad4fc810c901aeeeda170de57
notion_ticket_url: https://app.notion.com/p/3a4ef22ad4fc81d79240cc3aeeb09453
closed_at: 2026-07-21T12:37:03Z
---

# ZZA-87 저장소 직접 전환 작업 기록

## 작업 목표

`projects/sre-ai-lab` 저장소를 별도 이력 보존 절차 없이
`projects/our-moneyflow` 제품 저장소로 직접 전환한다. Git history rewrite는 하지 않고,
보호된 프로젝트 `main`이 아닌 ZZA-87 ticket branch에서 제품 정체성과 workflow 경계를
교체한다.

## 주요 변경 지점

- Linear ZZA-87과 canonical Notion 계획의 U1 계약을 저장소 직접 전환으로 갱신했다.
- 프로젝트 checkout을 `feat/ZZA-87-our-moneyflow-repository-transition` 브랜치로 전환한
  뒤 워크스페이스 경로를 `projects/our-moneyflow`로 이동했다.
- 프로젝트 README·AGENTS·project-local ideation/plan/work 문서, 루트 gitlink 설정과
  main-guard 설치 대상을 Our Moneyflow 기준으로 갱신했다.
- public `zzanghyunmoo/our-moneyflow` 저장소와 PR #1을 만들고 최신-head review·guarded
  squash merge를 완료했다.
- canonical Notion `디자인 문서 > 기능 현황`에 ZZA-87의 현재 상태와 운영 경계를
  기록했다.

## 검증

- PASS: old path가 없고 `projects/our-moneyflow/.git`이 독립 Git checkout으로 존재한다.
- PASS: project PR #1은 OWNER code/doc passing marker와 pre-merge gate를 통과했고 merge
  commit `5c86d8f9765d512e8cb89acd58df7a890150bbaf`로 squash merge됐다.
- PASS: 루트 index가 project merge commit을 mode `160000` gitlink로 가리킨다.
- PASS: project `main` 보호 hook은 feature branch를 허용하고 보호 대상으로 모의한
  같은 branch를 차단했다.
- PASS: root·project `git diff --check`, project/root work evidence validation,
  workflow shell guard test와 변경한 install script의 ShellCheck가 통과했다.
- PASS: active project 파일의 SRE AI Lab·Alert Rule Clinic identity 검색 결과가 0건이고
  ReplaceMe staged/unstaged diff가 없다.
- PASS: feature branch clean clone에서 Git object와 필수 project-local 문서를 확인했다.
- PASS: project closeout commit
  `b89f3b556000ed53525d0b3547957770f7386174`를 `our-moneyflow/main`에 반영하고 closeout
  debt를 해제했다.
- PASS: root pointer finalization commit
  `bd824c95c17f7454d162307412730c9d368a6e44`가 project closeout commit을 가리킨다.
- PASS: root 원격 clean clone과 submodule init에서 project commit, old path 부재,
  project-local KB와 완료된 work evidence를 확인했다.
- SKIP: `markdownlint-cli2`와 `npx`가 설치되어 있지 않아 Markdown lint는 실행하지 못했다.

## 외부 동기화

Linear ZZA-87을 `Done`으로 전환했다. canonical Notion 계획·프로젝트 위키·티켓 구현
문서와 기능 현황 문서에 merge commit, project closeout commit, root pointer commit과
최종 검증 결과를 동기화했다.

## Merge closeout

Project PR merge, project-local KB/work evidence publication, root pointer 원격 반영,
Notion·Linear 동기화와 clean clone 검증을 완료했다. 현재 runtime은 의도적으로 없으며
Flutter 골격 구현은 후속 티켓 ZZA-88의 범위다.
