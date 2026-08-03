---
title: ZZA-101 My Desk Setup 실제 target 인증 control plane
ticket: ZZA-101
merged_pr: https://github.com/zzanghyunmoo/my-desk-setup/pull/2
merge_commit: 61ede4860a9a2484a03693e4feed3cccc32c01c2
work_evidence: docs/works/2026-07-31-ZZA-101-my-desk-setup-actual-target-certification-work.md
notion_feature_status: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436
notion_ticket: https://app.notion.com/p/3aeef22ad4fc8183a530d3e72ef3e62c
last_verified: 2026-08-03
---

# ZZA-101 My Desk Setup 실제 target 인증 control plane

## 현재 기능 상태

PR #2는 squash merge commit
`61ede4860a9a2484a03693e4feed3cccc32c01c2`로 병합됐다. `main`에는 네 target별
certification profile, released `mds-evidence` authority, immutable cohort,
verified-only evidence와 deterministic release promotion gate가 포함된다.

## 주요 동작과 경계

- macOS host, Windows host, WSL Ubuntu 26.04 guest와 Lima Ubuntu 26.04
  guest는 target별 `certification-*` profile로 전체 자동화 가능 catalog를
  인증한다.
- Release manifest v2는 target별 production `mds` archive와 raw
  `mds-evidence` asset의 SHA-256을 고정한다. Wrapper는 certifier와 production
  binary를 private snapshot으로 고정한 뒤 실행한다.
- Guest는 host doctor가 owner-only ownership record와 live v3 marker를 먼저
  검증한다. Released prepare의 top-level `guest_creation_nonce_commitment`를
  dispatch하고 certify가 mutation 직전에 marker를 다시 대조한다.
- Raw nonce는 owner-only host record 밖으로 전달하지 않는다. 인증, runner
  registration token과 privileged prerequisite는 사용자가 직접 수행한다.

## 검증 결과

- 최신 review head `4c05c7960bc2c490da89699c98e79bce46af1487`에서 Linux와
  Windows CI, implemented fixture와 Windows scanner fixture가 통과했다.
- `go test ./...`, focused race, `go vet ./...`, cross-build, actionlint,
  shellcheck, deterministic release byte 비교와 Gitleaks 검증이 통과했다.
- 최신 head code/doc review는 P0-P2 없이 PASS했고 trusted OWNER marker가
  별도 댓글로 게시됐다.
- Actual-target workflow는 PR에서 의도대로 skip됐으므로 merge commit의 실제
  네 target evidence는 이 KB의 완료 주장에 포함하지 않는다.

## 운영 및 사용 시 주의사항

실제 macOS, Windows, WSL, Lima certification과 `v0.1.0` promotion은 아직
미실행이다. Draft PR #4의 status document에서 verified evidence가 생성된 target만
체크하고, 네 bundle이 동일 commit/cohort와 freshness/window 계약을 통과하기
전에는 release를 publish하거나 Linear ZZA-101을 `Done`으로 바꾸지 않는다.

## 관련 문서

- Remaining PR: <https://github.com/zzanghyunmoo/my-desk-setup/pull/4>
- Notion feature status:
  <https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436>
- Notion ticket:
  <https://app.notion.com/p/3aeef22ad4fc8183a530d3e72ef3e62c>
