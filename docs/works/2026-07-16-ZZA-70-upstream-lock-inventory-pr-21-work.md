---
workflow_schema: compound-work/v1
ticket_id: ZZA-70
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-70/oh-my-harness-4개-코딩-에이전트용-compound-engineering-호환-코어
ticket_status: In Review
ticket_completion: pending
remaining_prs: https://github.com/zzanghyunmoo/oh-my-harness/pulls
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: merged ZZA-70 planning contract에서 U1 범위와 불변 upstream 기준점이 이미 확정되어 별도 아이디에이션을 반복하지 않음
plan_status: complete
plan_path: docs/plans/2026-07-16-ZZA-70-upstream-lock-inventory-plan.md
plan_notion_url: https://www.notion.so/39eef22ad4fc8134bdbcd7de4afec13a
plan_waiver_reason:
work_status: complete
work_notion_url: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/21
closeout_status: complete
merged_pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/21
merge_commit: 143c2e827245c46f4ec367567126f1b255ac7e00
kb_paths: docs/kb/architecture/2026-07-16-ZZA-70-ce-3.19-upstream-lock-inventory.md
notion_feature_status_url: https://www.notion.so/39eef22ad4fc819db113ce1029c899a4
notion_ticket_url: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
closed_at: 2026-07-16T05:24:14Z
---

# ZZA-70 CE 3.19.0 upstream lock·inventory 작업 기록

## 작업 목표

ZZA-70의 첫 구현 단위 U1로 Compound Engineering 3.19.0의 불변 upstream 기준점과
29개 직접 스킬 inventory를 고정한다. 이 PR은 runtime adapter, 실행 기능, OCI lane 및
conformance matrix를 포함하지 않는다.

## 주요 변경 지점

- `harness/contracts/upstream-lock.schema.json`: owner/repository/tag/commit/tree,
  manifest, GitHub verification receipt, dependency lock, executable set, package script와
  inventory digest를 닫힌 1.0.0 계약으로 정의했다.
- `harness/locks/compound-engineering-v3.19.0.lock.json`: CE 3.19.0 tag의 commit
  `1756c0b9f3cf94493f287ea29ae766ad668fb7cf`와 tree
  `808d20cc08a2b45e0200e68f5b9f604c55cf8a06`, signed payload receipt, `bun.lock`,
  executable 및 package-script identity를 고정했다.
- `harness/inventory/compound-engineering-v3.19.0.json`: `skills/*/SKILL.md`에서 직접
  노출되는 29개 스킬을 lexicographic order와 Git blob object ID로 기록했으며 `lfg`를
  포함한다. upstream skill 본문은 복사하지 않는다.
- `scripts/harness/canonical.mjs`: canonical JSON/SHA-256과 secret-bearing key,
  authorization value, token/private-key/credential URL 거부를 제공한다.
- `scripts/harness/upstream.mjs`: npm-modified `PATH`를 신뢰하지 않는 host Git 선택,
  Git config·replacement·alternates·promisor 격리, `git fsck --strict` object integrity,
  pinned-object derivation, closed-shape 및 cross-artifact 검증, symlink·stale pre-image·
  parent replacement 방어, inventory-first/lock-last atomic publication을 구현했다.
- `tests/harness/inventory.test.mjs`: pinned derivation, drift, corrupt object database,
  hostile Git/path, credential, mixed generation, same-size edit 및 parent swap 회귀를 검증한다.

## 검증

- `npm run test:harness`: 15/15 통과.
- canonical CE checkout에서 `harness:upstream:generate --write` 후
  `harness:upstream:verify`와 `git diff --exit-code -- harness/`: 29개 스킬과 고정
  commit 기준 byte-identical no-op 검증 통과.
- `npm run profile:verify`: 4개 profile 및 profile lock deterministic·secret-free 검증 통과.
- `npm run test:workspace-connectors`: 31/31 통과.
- `git diff --check`: 통과.
- Pi Lens diagnostics: 변경 JavaScript 3개 파일에서 이슈 없음.
- 브라우저 테스트: UI·route 변경이 없어 해당 없음.
- 구조화 code review에서 발견한 ambient `PATH` Git trust, same-size stale pre-image,
  artifact semantic digest, credential shape, Windows Git path, Git object integrity,
  symbolic tag, subprocess timeout/overflow 문제를 수정하고 targeted review와 전체 검증을
  반복했다. Follow-up issue #20은 검증 완료 뒤 종료했다.
- 독립 cross-model adversarial pass는 Claude, Grok(Cursor route), Composer route가 모두
  usable schema output을 반환하지 않아 결과를 fold-in하지 못했다.

## 외부 동기화

- GitHub 구현 PR: <https://github.com/zzanghyunmoo/oh-my-harness/pull/21>
- Merge commit: `143c2e827245c46f4ec367567126f1b255ac7e00`
- Code review: <https://github.com/zzanghyunmoo/oh-my-harness/pull/21#issuecomment-4988090441>
- Latest doc review: <https://github.com/zzanghyunmoo/oh-my-harness/pull/21#issuecomment-4988403392>
- Canonical Notion plan: <https://app.notion.com/p/39eef22ad4fc8134bdbcd7de4afec13a>
- Canonical Notion feature status: <https://app.notion.com/p/39eef22ad4fc819db113ce1029c899a4>
- Canonical Notion ticket: <https://app.notion.com/p/39eef22ad4fc81c4a4bce021fa26b92b>
- Notion 기능 현황과 티켓 문서를 PR #21 merge 및 U1 완료 상태로 갱신했다.
- Linear ZZA-70은 후속 U2-U18 때문에 `In Review`를 유지한다.

## Merge closeout

PR #21은 `143c2e827245c46f4ec367567126f1b255ac7e00`으로 squash merge됐다. U1의 현재 기능
상태, trust boundary와 운영 주의사항을
`docs/kb/architecture/2026-07-16-ZZA-70-ce-3.19-upstream-lock-inventory.md`에 기록하고,
Notion 기능 현황·티켓 문서를 U1 완료 상태로 동기화했다. 후속 U2-U18 PR은 아직 열리지
않았으며 repository pull queue를 `remaining_prs`에 기록했다. 따라서
`ticket_completion: pending`, Linear `In Review`를 유지한다.
