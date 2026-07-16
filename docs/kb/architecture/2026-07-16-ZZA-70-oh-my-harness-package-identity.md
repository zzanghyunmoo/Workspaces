---
title: ZZA-70 Oh My Harness package identity
ticket: ZZA-70
merged_pr: https://github.com/zzanghyunmoo/oh-my-harness/pull/19
merge_commit: f23d040a7f3abfb5adfa2c63a1a61abd51ff771a
work_evidence: docs/works/2026-07-15-ZZA-70-oh-my-harness-rename-pr-19-work.md
notion_feature_status: https://www.notion.so/39eef22ad4fc819db113ce1029c899a4
notion_ticket: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
last_verified: 2026-07-16
---

<!-- markdownlint-disable MD025 -->

# ZZA-70 Oh My Harness package identity

## 현재 기능 상태

PR [#19](https://github.com/zzanghyunmoo/oh-my-harness/pull/19)이 squash merge되어
repository, workspace directory, npm package metadata, profile install source와 generated
profile receipt의 canonical identity가 `oh-my-harness`로 일치한다. Merge commit은
`f23d040a7f3abfb5adfa2c63a1a61abd51ff771a`이다.

## 주요 동작과 경계

- 새 설치와 profile lock은 `zzanghyunmoo/oh-my-harness`를 canonical Git source로 사용한다.
- `/oh-my-harness`, `/oh-my-harness-doctor`, `oh-my-harness:`가 canonical Pi surface다.
- `/oh-my-pi`, `/oh-my-pi-doctor`, `oh-my-pi:`, `omp:`와 `OH_MY_PI_*`는 v1 compatibility
  surface로 유지한다.
- 이 변경은 identity migration만 완료한다. Compound Engineering upstream lock,
  runtime adapter, native gate와 conformance matrix는 후속 ZZA-70 구현 단위다.
- 기존 로컬 설치를 자동으로 이동하지 않는다. 기존 사용자는 새 repository install spec으로
  다시 연결해야 한다.

## 검증 결과

- `npm run profile:verify`: 4개 profile과 `oh-my-harness.profile-lock.json`의 deterministic,
  secret-free 상태를 확인했다.
- `npm run test:workspace-connectors`: canonical·legacy command/prefix를 포함한 31개 테스트가
  통과했다.
- `npm pack --dry-run --json`: `oh-my-harness@0.1.0` package identity를 확인했다.
- `git diff --check`와 변경 파일 diagnostics가 통과했다.
- 최신 merge head의 code/doc review marker가 blocker 없이 게시된 뒤 guarded merge됐다.

## 운영 및 사용 시 주의사항

- 새 문서·profile·설치 안내에는 `oh-my-harness`만 canonical 이름으로 사용한다.
- `oh-my-pi` 문자열을 일괄 삭제하지 않는다. historical 문맥과 명시적인 v1 alias는 유지한다.
- compatibility alias 제거는 별도 deprecation 계약과 migration evidence 없이는 수행하지 않는다.
- ZZA-70은 후속 구현 PR이 남아 있으므로 Linear 상태를 `In Review`로 유지한다.

## 관련 문서

- Work evidence: `docs/works/2026-07-15-ZZA-70-oh-my-harness-rename-pr-19-work.md`
- Planning contract: `docs/kb/architecture/2026-07-15-ZZA-70-oh-my-harness-planning-contract.md`
- Notion canonical feature status: <https://app.notion.com/p/39eef22ad4fc819db113ce1029c899a4>
- Notion canonical ticket document: <https://app.notion.com/p/39eef22ad4fc81c4a4bce021fa26b92b>
