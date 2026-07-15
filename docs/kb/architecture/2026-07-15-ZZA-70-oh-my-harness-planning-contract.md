---
title: ZZA-70 Oh My Harness planning contract
ticket: ZZA-70
merged_pr: https://github.com/zzanghyunmoo/oh-my-harness/pull/18
merge_commit: 31c7fee6d1bc3c2da04bfba8d4306cb30fc54de9
work_evidence: docs/works/2026-07-15-ZZA-70-oh-my-harness-planning-pr-18-work.md
notion_feature_status: https://www.notion.so/39eef22ad4fc819db113ce1029c899a4
notion_ticket: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
last_verified: 2026-07-15
---

<!-- markdownlint-disable MD025 -->

# ZZA-70 Oh My Harness planning contract

## 현재 기능 상태

PR #18에서 Oh My Harness의 요구사항과 구현 계획을 확정했다. Compound Engineering
3.19.0의 29개 기능을 Codex, OpenCode, Claude Code, Pi의 native surface에 제공한다는
계약은 merge됐지만 runtime adapter, installer, doctor, evaluator와 conformance runner는
아직 구현되지 않았다. ZZA-70은 후속 PR이 남아 있어 `In Review` 상태다.

## 주요 동작과 경계

- Linux x64 release는 29 × 4의 116-cell OCI lane을 통과해야 한다.
- Darwin arm64 personal readiness는 별도 116-cell Tart/macOS VM lane을 통과해야 한다.
- 각 runtime은 첫 model request 전에 readiness를 fail-closed로 확인해야 한다.
- native plugin/package lifecycle과 harness-owned project 파일 transaction은 분리한다.
- 중앙 사용자 runner와 기존 connector/provider의 전면 이식은 v1 범위 밖이다.
- 구현 전에 repository, workspace directory와 package identity를 `oh-my-harness`로
  전환하되 기존 `oh-my-pi` 명령과 설치 사용자는 migration alias로 보존한다.

## 검증 결과

- Product Contract ID R1-R21, A1-A5, F1-F5, AE1-AE6의 연속성과 유일성을 확인했다.
- U1-U18 dependency 순서와 Linux/Darwin 각각 116-cell cardinality를 확인했다.
- 최신 PR head에서 code/doc review marker와 guarded merge gate가 통과했다.
- `npm run profile:verify`, `git diff --check`, Markdown LSP diagnostics가 통과했다.
- 실제 runtime gate, OCI/Tart backend와 232개 platform cell은 아직 실행하지 않았다.

## 운영 및 사용 시 주의사항

현재 merge는 구현 완료나 runtime 지원을 의미하지 않는다. U16 characterization에서 exact
runtime의 pre-model seam, scripted provider 또는 isolation backend가 실패하면 해당 lane은
약한 fallback 없이 blocked로 남겨야 한다. repository rename 뒤에는 GitHub redirect에만
의존하지 말고 local remote, workspace submodule, package install source와 문서 링크를 함께
갱신해야 한다.

## 관련 문서

- Work evidence: `docs/works/2026-07-15-ZZA-70-oh-my-harness-planning-pr-18-work.md`
- Notion canonical feature status: <https://www.notion.so/39eef22ad4fc819db113ce1029c899a4>
- Notion canonical ticket document: <https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b>
- Canonical plan: `docs/plans/2026-07-15-ZZA-70-oh-my-harness-plan.md`
