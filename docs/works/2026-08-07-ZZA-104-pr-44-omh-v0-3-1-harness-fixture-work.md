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
ideation_waiver_reason: This is a focused release-blocker remediation with a runtime-confirmed cause.
plan_status: complete
plan_path: docs/plans/2026-08-06-ZZA-104-runtime-ownership-plan.md
plan_notion_url: https://app.notion.com/p/3b3ef22ad4fc8130b011e4567db4d0ab?pvs=204
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/44
closeout_status: complete
merged_pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/44
merge_commit: c6699db16a43075cd9d9fb22140a1294cf79a2b9
kb_paths: docs/kb/releases/2026-08-07-ZZA-104-omh-v0-3-1-harness-fixture.md
notion_feature_status_url: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436?pvs=204
notion_ticket_url: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
closed_at: 2026-08-07T05:29:27Z
---

# ZZA-104 OMH v0.3.1 하네스 픽스처 릴리스 CI 작업 기록

## 작업 목표

v0.3.1 릴리스 CI가 이전 0.3.0 테스트 픽스처와 충돌해 실패하는 문제를 해소한다.

## 주요 변경 지점

- `oh-my-harness/tests/harness/install.test.mjs`: managed harness registration path와 정상 Claude/OpenCode plugin fixture를 현재 package identity `0.3.1`로 맞춘다.
- `oh-my-harness/tests/harness/omh-cli.test.mjs`: root `omh` launcher의 release-version assertion을 `0.3.1`로 맞춘다.

## 검증

- PASS: `npm run test:harness` — 76 passed, 13 Windows/POSIX fixture skipped, 0 failed.
- PASS: macOS follow-up `npm run test:harness` — 86 passed, 3 platform fixture skipped,
  0 failed.
- PASS: `npm run package:verify` — 36 passed, 0 failed.
- PASS: macOS, Ubuntu, Windows GitHub Actions checks.
- PASS: PR 최신 head `5bcd1572e2a34977e2810db63f45a48de09d1748`의 code/doc
  review marker와 guarded merge preflight.
- CI root cause: release run `31137160354`가 source/catalog/package contract 단계에서 위 세 legacy fixture 때문에 실패했으며, artifact publication 전에 중단됐다.
- 로컬 macOS에서 처음 재실행한 package gate는 순환 `node_modules/node_modules`
  symlink와 stale `dist/migration` 산출물 때문에 실패했다. `npm ci`와 clean build로
  source 변경 없이 복구한 뒤 36/36을 재확인했다.

## 외부 동기화

- PR #44는 squash commit `c6699db16a43075cd9d9fb22140a1294cf79a2b9`로
  merge됐다.
- Linear의 자동 `Done` 전환은 미완료 release/MDS lock/Windows apply 조건 때문에
  `In Review`로 되돌리고 원인과 다음 단계를 댓글로 남겼다.
- Notion `디자인 문서 > 기능 현황`과 `개발 문서 > 티켓`에 merge identity,
  검증 결과와 immutable release 경계를 동기화했다.
- `v0.3.1` tag는 PR #44 이전 commit
  `e76d7e0c7700332bb3c2fce402d974514d0ff581`을 가리키고 GitHub Release는
  발행되지 않았다. 이 tag는 이동하거나 덮어쓰지 않는다.

## Merge closeout

PR #44의 merge closeout은
`docs/kb/releases/2026-08-07-ZZA-104-omh-v0-3-1-harness-fixture.md`와 두 canonical
Notion 문서에 기록했다. PR #44를 포함하는 새 immutable OMH release PR, MDS catalog
lock PR과 실제 Windows apply가 남아 있고 실제 4-target 인증은 MDS PR #4에서 추적하므로
ZZA-104는 `ticket_completion: pending`, Linear `In Review`를 유지한다.
