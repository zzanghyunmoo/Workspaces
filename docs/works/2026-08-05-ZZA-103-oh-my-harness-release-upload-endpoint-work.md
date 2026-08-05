---
workflow_schema: compound-work/v1
ticket_id: ZZA-103
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-103/host-agent-harness-%EA%B8%B0%EB%B3%B8-%EC%84%A4%EC%B9%98-%EB%B0%8F-pi-%EC%99%84%EC%A0%84-%EC%A0%9C%EA%B1%B0
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/my-desk-setup/pull/6
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: "v0.3.0 publish 실패에서 재현된 단일 GitHub upload endpoint 결함의 최소 후속 수정임"
plan_status: complete
plan_path: docs/plans/2026-08-03-ZZA-103-host-agent-harness-pi-removal-plan.md
plan_notion_url: https://app.notion.com/p/3b1ef22ad4fc8197842cc7b8a27d6660
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b1ef22ad4fc816299bbc1445da68856
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/39
closeout_status: complete
merged_pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/39
merge_commit: ee38c2253d7151e7b31bd4354adfd90c69b54907
kb_paths: docs/kb/releases/2026-08-05-ZZA-103-oh-my-harness-pi-free-release.md
notion_feature_status_url: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436
notion_ticket_url: https://app.notion.com/p/3b1ef22ad4fc8171ae2fe9b74843f4fb
closed_at: 2026-08-05T13:50:43+09:00
---

# ZZA-103 OMH release upload endpoint 수정 기록

## 작업 목표

v0.3.0 release publish job이 존재하지 않는 `api.uploads.github.com`에 연결해 실패한 원인을
닫고, 이후 릴리스가 GitHub의 canonical asset upload endpoint를 사용하도록 한다. 실패 시
보존된 exact-source draft는 삭제하거나 tag를 이동하지 않고 명시적으로 검증·복구한다.

## 주요 변경 지점

- `src/catalog/release-publication.ts`: `gh api --hostname uploads.github.com` 조합을 제거하고
  full `https://uploads.github.com/repos/.../assets` endpoint를 shell-free argument로 전달한다.
  `gh`가 hostname 앞에 `api.`를 붙여 잘못된 host로 변환하는 경로를 없앤다.
- `tests/release/release-publication.test.ts`: production adapter가 `--hostname`을 사용하지
  않고 exact repository/release ID가 포함된 canonical full URL을 전달하는지 검증한다.
- 보존 draft `365277861`: 성공한 build job에서 내려받은 CI canonical archive/sidecar를
  MDS actual preview/apply로 검증한 뒤 올바른 endpoint로 업로드했다. 두 asset을 다시 내려받아
  SHA-256과 bytes를 대조한 후 v0.3.0을 공개했다.

## 검증

- Red: 기존 production adapter test를 강화하자 `--hostname` 사용 때문에 실패했다.
- Green: `npm run typecheck`, `npm run package:verify` 36/36, `git diff --check`가 통과했다.
- Green: canonical CI archive SHA-256
  `da805da0130e937913706f98ddb415f5e4b4bc12d04505b269f08bf66237ea73`, sidecar SHA-256
  `bfce118fec548fa8dfb51eaa052bdc0c49c3efcbd0abb84b9a8ee3f96414cba4`가 업로드 응답과
  재다운로드 파일에 모두 일치했다.
- Green: 공개 release는 tag/source commit `v0.3.0`/
  `95882328d339e7336e8a60a90f3e2640c1244da3`, asset 2개, draft=false 상태다.

## 외부 동기화

- Pull request: https://github.com/zzanghyunmoo/oh-my-harness/pull/39
- Release: https://github.com/zzanghyunmoo/oh-my-harness/releases/tag/v0.3.0
- Linear ZZA-103은 MDS PR #6과 이 후속 리뷰가 남아 있어 `In Review`를 유지한다.
- Canonical Notion 구현 문서:
  https://app.notion.com/p/3b1ef22ad4fc816299bbc1445da68856

## Merge closeout

- PR #39는 `ee38c2253d7151e7b31bd4354adfd90c69b54907`로 squash merge됐다.
- 현재 release 기능 상태와 endpoint 운영 경계를
  `docs/kb/releases/2026-08-05-ZZA-103-oh-my-harness-pi-free-release.md`에 갱신했다.
- Notion `디자인 문서 > 기능 현황`, 티켓 문서와 OMH 구현 문서에 merge 결과를
  동기화했다.
- MDS PR #6이 남아 있으므로 Linear ZZA-103은 `In Review`,
  `ticket_completion: pending`을 유지한다.
