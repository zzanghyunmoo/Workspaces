---
workflow_schema: compound-work/v1
ticket_id: ZZA-103
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-103/host-agent-harness-%EA%B8%B0%EB%B3%B8-%EC%84%A4%EC%B9%98-%EB%B0%8F-pi-%EC%99%84%EC%A0%84-%EC%A0%9C%EA%B1%B0
ticket_status: In Review
ticket_completion: pending
remaining_prs:
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: "승인된 단일 product contract와 ce-brainstorm에서 범위가 확정되어 별도 후보 생성이 중복됨"
plan_status: complete
plan_path: docs/plans/2026-08-03-ZZA-103-host-agent-harness-pi-removal-plan.md
plan_notion_url: https://app.notion.com/p/3b1ef22ad4fc8197842cc7b8a27d6660
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b1ef22ad4fc81e990c2df7dc995ebfc
pr_url: https://github.com/zzanghyunmoo/my-desk-setup/pull/6
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url: https://app.notion.com/p/3b1ef22ad4fc8171ae2fe9b74843f4fb
closed_at:
---

# ZZA-103 MDS Host Harness 통합 작업 기록

## 작업 목표

reviewed `oh-my-harness`와 dependency-only Node runtime을 macOS/Windows host의
default/all/profile/component resolver에 통합하고 child preview, one-digest approval,
plan-wide preflight, repeat no-op와 actual-target evidence를 완성한다.

## 주요 변경 지점

- U4 catalog/fixture (`e3ab976`): `catalog.Component.SelectionPolicy`와
  `dependency-only`를 추가해 OMH 전용 Node를 direct/profile/interactive/`--all` root에서
  숨기고 `oh-my-harness` dependency closure에서만 포함한다. `SelectionCandidates`와
  `SelectionRoots`를 plan/apply/doctor picker와 all resolver가 공유한다.
- U4 native identity: `catalog.Artifact.ExecutableSHA256`과 closed schema validation을
  추가해 agent archive뿐 아니라 extracted executable bytes까지 고정한다. pre-publish
  fixture는 실제 OMH merge commit `9588232`에서 생성한 self-contained archive SHA-256,
  Node 22.19.0 공식 archive checksum과 OMH adapter의 Claude/OpenCode/Codex native
  archive/executable identity를 담되 `production: false`로 production lock과 분리한다.
- U5 artifact snapshot (`internal/artifact/snapshot.go`): release sidecar와 archive의
  source commit/tree, catalog revision, file manifest, archive/executable digest를 검증하고
  staging에서 content-addressed snapshot으로 원자 발행한다. 실패한 staging은 정리하고 이미
  검증된 snapshot은 재사용한다.
- U5 preview (`internal/harness/preview.go`, `internal/planning/compose.go`): MDS plan 전에
  caller-owned agent executable을 검증하고 OMH child preview를 격리된 state root에서
  실행한다. preview digest 하나를 부모 계획에 결합하고 child blocker와 mutation target을
  plan-wide preflight로 승격한다.
- U6 apply (`internal/harness/apply.go`, `internal/execution/runner.go`): 승인된 exact digest로만
  OMH apply를 실행하고 agent 설치보다 먼저 harness readiness를 확정한다. apply 결과와 actual
  target을 MDS receipt/evidence에 기록하며 동일 실행은 no-op으로 수렴한다.
- U7 host/guest 경계 (`internal/adapters/host`, fixture profile): 호스트에는 OMH와 agent
  executable만 합성하고 guest에는 CLI·언어·Neovim·agent 도구를 유지한다. 인증은 자동화하지
  않고 사용자가 직접 수행한다.
- Release gate (`tests/contracts/host_harness_release_gate_test.go`): OMH PR #38 merge commit에서
  생성한 실제 v0.3.0 아카이브와 sidecar를 snapshotter로 검증한 뒤 빈 `mds-host` 선택의
  preview와 exact-digest apply를 실제 child process로 통과시킨다.

## 검증

- Green: `go test ./...`, `go test -race ./...`, `go vet ./...`, macOS build와
  `GOOS=windows GOARCH=amd64` build, `git diff --check`가 통과했다.
- Green: 실제 OMH v0.3.0 아카이브와 sidecar를 제공한
  `TestHostHarnessReleaseArtifactDrivesRealPreviewAndApply`가 macOS에서 preview/apply를
  9.04초에 통과했다.
- Green: artifact snapshot, isolated preview, exact-digest apply, failure recovery,
  plan composition, receipt/evidence와 dependency-only selection의 unit/contract/integration
  테스트가 통과했다.
- Node 22.19.0의 macOS arm64/x64와 Windows arm64/x64 archive SHA-256은 `nodejs.org`
  공식 `SHASUMS256.txt`와 대조했다.
- 미실행: 실제 Windows/macOS 사용자 홈에 대한 destructive install과 각 agent의 auth/login은
  범위 밖이다. Windows 경로는 크로스 빌드와 기존 Windows 사용자 검증을 근거로 유지한다.

## 외부 동기화

- Linear ZZA-103: `In Review`
- Pull request: <https://github.com/zzanghyunmoo/my-desk-setup/pull/6>
- Canonical plan: <https://app.notion.com/p/3b1ef22ad4fc8197842cc7b8a27d6660>
- Notion 구현 문서: <https://app.notion.com/p/3b1ef22ad4fc81e990c2df7dc995ebfc>

## Merge closeout

마지막 PR merge 후 KB, 기능 현황·티켓 문서, merge commit, Linear Done과 root pointer를
기록한다.
