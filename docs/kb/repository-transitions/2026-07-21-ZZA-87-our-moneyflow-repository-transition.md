---
title: ZZA-87 Our Moneyflow 저장소 전환
ticket: ZZA-87
merged_pr: https://github.com/zzanghyunmoo/our-moneyflow/pull/1
merge_commit: 5c86d8f9765d512e8cb89acd58df7a890150bbaf
work_evidence: docs/works/2026-07-21-ZZA-87-our-moneyflow-repository-transition-work.md
notion_feature_status: https://app.notion.com/p/3a4ef22ad4fc810c901aeeeda170de57
notion_ticket: https://app.notion.com/p/3a4ef22ad4fc81d79240cc3aeeb09453
last_verified: 2026-07-21
---

<!-- markdownlint-disable MD025 -->

# ZZA-87 Our Moneyflow 저장소 전환

## 현재 기능 상태

기존 `sre-ai-lab` 프로젝트는 public GitHub 저장소
`zzanghyunmoo/our-moneyflow`로 직접 전환됐다. 워크스페이스의 프로젝트 경로와
submodule도 `projects/our-moneyflow`를 사용하며, 이전 경로는 원격 clean clone에
존재하지 않는다. Flutter runtime 골격은 아직 없고 후속 티켓 ZZA-88에서 시작한다.

## 주요 동작과 경계

- 제품 경계는 읽기 전용 다중 은행 가계부·예산·보고서다.
- 기술 방향은 Flutter/Dart Android/iOS 단일 앱이다.
- 송금·결제 기능과 ReplaceMe 변경은 이 저장소 전환 범위에 포함하지 않았다.
- 프로젝트 변경은 ticket branch와 PR을 사용하며 `main` 직접 작업은 보호한다.

## 검증 결과

- PR #1은 code/doc review passing marker와 guarded merge gate를 통과했다.
- squash merge commit은 `5c86d8f9765d512e8cb89acd58df7a890150bbaf`다.
- project closeout commit `b89f3b556000ed53525d0b3547957770f7386174`에 project-local
  KB와 완료된 work evidence가 포함됐다.
- root pointer finalization commit `bd824c95c17f7454d162307412730c9d368a6e44`가 위 project
  closeout commit을 가리킨다.
- root 원격 clean clone과 submodule init에서 project commit, 이전 경로 부재,
  완료된 project closeout 문서를 확인했다.
- `markdownlint-cli2`와 `npx`가 없어 Markdown lint는 실행하지 못했다.

## 운영 및 사용 시 주의사항

현재 저장소는 제품 계약과 개발 workflow 문서만 가진 초기 상태다. 실행 가능한 Flutter
앱은 아직 없다. 후속 개발은 ZZA-88부터 티켓별 branch, PR review와 closeout 가드레일을
동일하게 적용한다.

## 관련 문서

- Work evidence: `docs/works/2026-07-21-ZZA-87-our-moneyflow-repository-transition-work.md`
- Notion canonical feature status:
  <https://app.notion.com/p/3a4ef22ad4fc810c901aeeeda170de57>
- Notion canonical ticket document:
  <https://app.notion.com/p/3a4ef22ad4fc81d79240cc3aeeb09453>
