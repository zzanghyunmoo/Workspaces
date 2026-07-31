---
workflow_schema: compound-work/v1
ticket_id: ZZA-101
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-101/my-desk-setup-실제-4-target-인증-및-release-promotion
ticket_status: In Review
ticket_completion: pending
remaining_prs:
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: ZZA-100의 병합 후 실제 인증 감사에서 확인된 도달성·promotion 결함 수정으로, 새 제품 방향이나 사용자 흐름을 결정하지 않는다.
plan_status: complete
plan_path: docs/plans/2026-07-31-ZZA-101-my-desk-setup-actual-target-certification-plan.md
plan_notion_url: https://app.notion.com/p/3aeef22ad4fc814a99f8e377987be5a8
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3aeef22ad4fc8183a530d3e72ef3e62c
pr_url: https://github.com/zzanghyunmoo/my-desk-setup/pull/2
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url: https://app.notion.com/p/3aeef22ad4fc8183a530d3e72ef3e62c
closed_at:
---

# ZZA-101 실제 4-target 인증 및 첫 release promotion 작업 기록

## 작업 목표

병합본의 actual certification 경로를 막는 selection과 첫-release bootstrap
순환 의존을 제거한다. 새 merge commit을 macOS host, Windows host, WSL Ubuntu
26.04 guest와 Lima Ubuntu 26.04 guest에서 독립적으로 `verified`한 뒤
`v0.1.0`으로 승격하고 모든 추적 문서를 같은 identity로 닫는다.

## 주요 변경 지점

- Catalog/workflow: 네 target별 certification profile과 fail-closed
  target→profile mapping을 추가하고 actual evidence는 `verified`만 허용한다.
- Guest bootstrap: apply-only exact archive 입력을 한 번 연 handle과 bounded
  snapshot으로 검증·전달해 첫 release asset 부재를 안전하게 우회한다.
- Evidence security: raw guest nonce는 runtime에서만 비교하고 plan/evidence에는
  domain-separated commitment만 남긴다. Upload 전 file set, checksum과
  credential/nonce/path leak를 검사한다.
- Retry/promotion: immutable certification cohort 안에서 target kind별
  exactly-one, manifest capture 완료 기준 24시간 freshness, cohort timestamp
  기준 4시간 capture window를 검증하고 target별 capture 시각을 영구 report에 남긴다.
- Control plane/release: protected branch/tag, reviewer-gated secret-free
  environment, 기본 `self-hosted` label을 유지한 one-job ephemeral runner,
  Windows checksum-pinned Gitleaks와 verified draft release를 사용한다.
- 구현 commit:
  - U1 `6f83fc7` — 실제 target certification 경로 도달성 복구
  - U2 `290aeb7` — 동일 release archive의 apply-only guest 전달과 nonce commitment
  - U3 `09a665e` — commit-bound 4-target cohort와 verified-only draft publication
  - 단순화 `c8c52fd` — 중복 identity parsing과 artifact 검증 흐름 정리
  - 리뷰 수정 `dd67276` — Windows scan, fail-closed publication, cohort window,
    archive input error와 runner label 계약 보완
  - Windows preflight `07b1943` — Git for Windows/Bash prerequisite와
    Windows PowerShell 5.1 scanner 경로 명시

## 검증

- 완료:
  - Linear ZZA-101을 `In Progress`로 전환했다.
  - Canonical Notion plan에 `ce-doc-review` 결정과 구현 계약을 동기화했다.
  - Canonical Notion ticket을 `In Progress`로 갱신했다.
  - `origin/main` 기준 `zza-101/actual-target-certification` branch를 만들었다.
  - Local plan에 대한 `git diff --check`를 통과했다.
  - U1–U3의 focused test와 `go test ./...`, `go vet ./...`,
    Windows amd64 cross-build를 통과했다.
  - 리뷰 수정 뒤 `go test ./...`, `go test -race ./...`, `go vet ./...`를
    통과했다. `internal/release` race test도 372.213초에 정상 완료됐다.
  - Windows amd64의 host/release/evidence/contracts test package compile-only와
    `cmd/mds`, `cmd/mds-evidence`, `cmd/mds-release` cross-build를 통과했다.
  - `actionlint`, 전체 shell script의 `shellcheck`, PowerShell parser,
    `git diff --check`를 통과했다.
  - Fake `gh`/`git` executable로 API 500 fail-closed, 404 draft-first
    create→upload→download→byte verify→publish, 기존 published release 무변경 검증,
    remote byte mismatch 미게시를 실행 검증했다.
  - 공개 GitHub release의 실제 `gh api --include --jq` 출력이 HTTP status header와
    tag/draft TSV 순서임을 대조했다.
  - 최신 head `07b1943`의 PR 전 `ce-code-review`에서 correctness/API,
    release/reliability/cohort, Windows runner/security 관점 모두 PASS했다.
- 진행 중:
  - PR 최신 head의 `ce-code-review`와 `ce-doc-review`
- 미실행:
  - macOS/Lima와 Windows/WSL actual certification은 fix merge commit과
    control plane이 준비된 뒤 실행한다.
  - Browser test는 UI가 없는 CLI/automation 변경이므로 해당하지 않는다.

## 외부 동기화

- Linear:
  [ZZA-101](https://linear.app/zzanghyunmoo/issue/ZZA-101/my-desk-setup-실제-4-target-인증-및-release-promotion)
  — `In Review`
- Project PR:
  [my-desk-setup#2](https://github.com/zzanghyunmoo/my-desk-setup/pull/2)
- Canonical plan:
  [Notion](https://app.notion.com/p/3aeef22ad4fc814a99f8e377987be5a8)
- Canonical ticket:
  [Notion](https://app.notion.com/p/3aeef22ad4fc8183a530d3e72ef3e62c)
- Account/service auth, runner registration token 입력과 privileged prerequisite는
  사용자 직접 단계다. Token이나 raw nonce는 문서·artifact에 기록하지 않는다.

## Merge closeout

Pending. PR merge 뒤 KB, Notion 기능 현황·ticket, merge commit, release identity와
Linear `Done` 전환 결과를 기록한다.
