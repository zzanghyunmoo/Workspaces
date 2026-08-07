---
workflow_schema: compound-work/v1
ticket_id: ZZA-104
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-104
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/my-desk-setup/pull/4
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: "PR #44 이후 immutable tag를 보존하며 새 patch release identity를 만드는 범위가 기존 ZZA-104 계획 U4에 이미 확정됨"
plan_status: complete
plan_path: docs/plans/2026-08-06-ZZA-104-runtime-ownership-plan.md
plan_notion_url: https://app.notion.com/p/3b3ef22ad4fc8130b011e4567db4d0ab?pvs=204
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/45
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url:
closed_at:
---

# ZZA-104 OMH v0.3.2 immutable release 작업 기록

## 작업 목표

PR #44의 하네스 픽스처 수정을 포함하는 새 immutable OMH `v0.3.2` release identity를
준비한다. 기존 `v0.3.1` tag는 이동하거나 덮어쓰지 않는다.

## 주요 변경 지점

- `package.json`, `npm-shrinkwrap.json`, native plugin manifest와 marketplace version을
  `0.3.2`로 일치시켰다.
- `harness/catalog/release.json`의 archive, sidecar, tag, compatibility를 `v0.3.2`에
  결합하고 runtime plugin bytes의 SHA-256 digest를
  `de31d918a4320eb56f791d53b87dbc64666e6e6f8c539877420fb3b905a2248b`로 갱신했다.
- release, native registration, integration 및 harness fixture의 package identity를
  같은 version으로 동기화했다.

## 검증

- PASS: `npm run typecheck`, `npm run build`, `git diff --check origin/main...HEAD`.
- PASS: `npm run catalog:verify` — 26 passed, 0 failed.
- PASS: `npm run test:unit` — 60 passed, 0 failed.
- PASS: `npm run test:contracts` — 26 passed, 0 failed.
- PASS: `npm run test:integration` — 98 passed, 0 failed.
- PASS: `npm run test:runtime:claude` — 8 passed, 0 failed.
- PASS: `npm run test:runtime:opencode` — 13 passed, 0 failed.
- PASS: `npm run test:runtime:codex` — 10 passed, 0 failed.
- PASS: `npm run test:harness` — 86 passed, 3 platform fixture skipped, 0 failed.
- PASS: `npm run package:verify` — 36 passed, 0 failed.
- 최초 package gate는 release source materialization이 미커밋 working tree가 아니라 Git
  object를 사용해 이전 `0.3.1` archive를 만든다는 계약 때문에 1건 실패했다. 변경을
  branch commit `ddd9316525e6e6eee941434c1f7d369bf589e26b`에 고정한 뒤 같은 gate가
  36/36으로 통과해 source identity 경계를 확인했다.
- 미실행: 실제 `v0.3.2` GitHub Release publication, MDS catalog lock과 Windows apply는
  PR merge 이후 후속 검증이다.

## 외부 동기화

- Linear ZZA-104를 `In Progress`로 전환하고 v0.3.2 release 후속 시작 댓글을 남긴 뒤,
  PR #45 생성과 함께 `In Review`로 전환하고 검증 결과 댓글을 추가했다.
- Canonical Notion 티켓에 immutable tag 보존, target version, PR #45, 전체 검증 결과와
  merge 이후 후속 경계를 기록했다.
- PR: https://github.com/zzanghyunmoo/oh-my-harness/pull/45

## Merge closeout

PR merge 전에는 pending이다. Merge 뒤 실제 `v0.3.2` tag와 GitHub Release publication을
검증하고 release URL, KB, Notion 기능 현황·티켓, MDS lock 후속과 Linear 상태를 갱신한다.
