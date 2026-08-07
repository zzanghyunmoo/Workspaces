---
title: "ZZA-104 OMH v0.3.1 harness fixture closeout"
ticket: ZZA-104
component: oh-my-harness
status: merged
merged_pr: https://github.com/zzanghyunmoo/oh-my-harness/pull/44
merge_commit: c6699db16a43075cd9d9fb22140a1294cf79a2b9
work_evidence: docs/works/2026-08-07-ZZA-104-pr-44-omh-v0-3-1-harness-fixture-work.md
notion_feature_status: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436?pvs=204
notion_ticket: https://app.notion.com/p/3b3ef22ad4fc81ad8942d6fc4fe3bc99?pvs=204
last_verified: 2026-08-07
---

# OMH v0.3.1 harness fixture closeout

## 현재 기능 상태

PR #44는 OMH `0.3.1` package identity와 release harness의 managed native
registration·root launcher fixture를 일치시켜 `main`에 merge됐다. Test-only 변경이며
runtime 설치, plugin mutation 또는 사용자 설정 동작은 바꾸지 않는다.

## 주요 동작과 경계

`tests/harness/install.test.mjs`는 managed Claude/OpenCode registration의 정상 identity를
`0.3.1`로 검증하고, `tests/harness/omh-cli.test.mjs`는 root launcher의 현재 package
version을 검증한다. User-owned registration collision과 version drift는 계속 fail-closed다.

`v0.3.1` tag는 PR #44 이전 commit
`e76d7e0c7700332bb3c2fce402d974514d0ff581`을 가리키며 GitHub Release는 발행되지 않았다.
Immutable tag를 이동하거나 덮어쓰지 않으므로 PR #44를 포함하려면 새 release identity가
필요하다.

## 검증 결과

- macOS local `npm run test:harness`: 86 pass, 3 platform fixture skip, 0 fail.
- macOS local `npm run package:verify`: 36 pass, 0 fail.
- macOS, Ubuntu, Windows GitHub Actions checks: pass.
- PR head `5bcd1572e2a34977e2810db63f45a48de09d1748` code/doc review marker와
  guarded merge preflight: pass.
- Squash merge commit: `c6699db16a43075cd9d9fb22140a1294cf79a2b9`.

## 운영 및 사용 시 주의사항

ZZA-104는 아직 완료가 아니다. PR #44를 포함하는 새 immutable OMH release를 발행하고,
MDS catalog lock을 그 archive/sidecar identity로 갱신한 뒤 실제 Windows apply를 검증해야
한다. 실제 4-target certification은 MDS PR #4에서 계속 추적한다. Auth, login, token과
사용자 소유 runtime/plugin 설정은 자동으로 읽거나 변경하지 않는다.
