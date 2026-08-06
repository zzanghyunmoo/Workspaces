---
workflow_schema: compound-work/v1
ticket_id: ZZA-104
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-104
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/my-desk-setup/pull/7
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: Existing installation blocker and explicit runtime-ownership decision were sufficiently bounded.
plan_status: complete
plan_path: docs/plans/2026-08-06-ZZA-104-runtime-ownership-plan.md
plan_notion_url: https://app.notion.com/p/3b3ef22ad4fc8130b011e4567db4d0ab?pvs=204
plan_waiver_reason: User requested Linear and Notion external updates be deferred.
work_status: complete
work_notion_url: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/40
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url:
closed_at:
---

# ZZA-104 MDS runtime ownership 작업 기록

## 작업 목표

MDS가 선택한 Windows agent runtime의 정확한 identity를 OMH `mds-host`에 전달해, OMH가 자체 runtime catalog pin과 충돌하지 않고 명시된 native plugin/add-on만 합성하도록 한다.

## 주요 변경 지점

- `my-desk-setup/internal/planning/compose.go`: verified snapshot의 agent version·archive digest·executable digest를 outer MDS plan에 결합하고 child preview에 전달한다.
- `my-desk-setup/internal/harness/preview.go`, `internal/adapters/host/harness.go`: preview와 apply가 동일한 `MDS_RUNTIME_IDENTITIES`를 isolated child environment로 전달한다.
- `oh-my-harness/src/environment/runtime-policy.ts`: `mds-host`에서만 전달 identity의 executable digest와 실제 trusted-PATH executable bytes를 비교해 ready를 결정한다. 일반 profile의 pin/acquisition 정책은 유지한다.
- `oh-my-harness/README.md`, `docs/solutions/workflow/unified-preview-first-management-cli.md`: MDS runtime identity와 OMH plugin-only ownership 경계를 명시한다.

## 검증

- PASS: MDS focused `go test ./internal/harness ./internal/planning ./internal/adapters/host`, `go vet` 같은 범위, `go build ./cmd/mds`, Windows-native CLI `--help` smoke test.
- PASS: OMH `npm run build --silent`, `node --test tests/unit/mds-host-contract.test.ts`, `git diff --check`.
- BLOCKED (환경 기존 문제): MDS `go test ./...`의 symlink 권한 6개와 `PROCESSOR_ARCHITECTURE` 미설정 Windows bootstrap test 1개가 실패했다. 변경 패키지는 통과했고, 이 작업에서 권한 정책이나 bootstrap test를 변경하지 않는다.
- 아직 실행 전: 실제 release artifact로 OpenCode+OMO 및 Codex+LazyCodex apply. 두 repo PR review 후 현재 Windows MDS catalog의 release lock과 함께 수행한다.

## 외부 동기화

Linear ZZA-104는 In Progress 상태다. 사용자가 요청한 대로 Notion 및 외부 tracker 갱신은 PR closeout 전까지 보류한다.

## Merge closeout

PR 생성과 review marker 갱신 후 작성한다.
