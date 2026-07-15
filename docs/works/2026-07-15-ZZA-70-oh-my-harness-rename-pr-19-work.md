---
workflow_schema: compound-work/v1
ticket_id: ZZA-70
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-70/oh-my-harness-4개-코딩-에이전트용-compound-engineering-호환-코어
ticket_status: In Review
ticket_completion: pending
remaining_prs: implementation PRs for U1-U18
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: merged planning contract와 사용자의 명시적 rename 순서 결정으로 목표·범위가 확정된 identity migration이라 별도 아이디에이션을 생략함
plan_status: complete
plan_path: docs/plans/2026-07-15-ZZA-70-oh-my-harness-plan.md
plan_notion_url: https://www.notion.so/39eef22ad4fc8134bdbcd7de4afec13a
plan_waiver_reason:
work_status: complete
work_notion_url: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
pr_url: https://github.com/zzanghyunmoo/oh-my-harness/pull/19
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url: https://www.notion.so/39eef22ad4fc819db113ce1029c899a4
notion_ticket_url: https://www.notion.so/39eef22ad4fc81c4a4bce021fa26b92b
closed_at:
---

# ZZA-70 Oh My Harness identity rename 작업 기록

## 작업 목표

구현 시작 전에 repository, workspace directory와 package identity를 `oh-my-harness`로
일치시키고 기존 Pi 사용자의 `oh-my-pi` 명령·환경변수 호환 surface를 보존한다.

## 주요 변경 지점

- `package.json`, `package-lock.json`: package identity와 설명을 `oh-my-harness`로
  전환했다.
- `scripts/profile-pack.mjs`, `docs/profiles/`: core install spec, generated lock 이름과
  profile identity를 새 repository 이름으로 전환했다.
- `docs/blueprints/`: secret-free blueprint 파일, schema ID와 설치 재현 경로를 새 이름으로
  전환했다.
- `extensions/setup-doctor/`, `extensions/capability-registry.ts`, `skills/omp/SKILL.md`: `/oh-my-harness`, `/oh-my-harness-doctor`, `oh-my-harness:` canonical surface를 추가하고 기존 `/oh-my-pi`, `/oh-my-pi-doctor`, `oh-my-pi:` alias를 보존했다.
- `README.md`, `AGENTS.md`, `settings.example.json`: 새 install source와 프로젝트 identity,
  기존 `omp:`, `OH_MY_PI_*` 호환 경계를 문서화했다.

## 검증

- `npm run profile:verify`: 4개 profile과 `oh-my-harness.profile-lock.json`의 deterministic,
  secret-free 상태를 확인했다.
- `npm run test:workspace-connectors`: canonical·legacy command/prefix를 포함한 31개 테스트 통과.
- `npm pack --dry-run --json`: package `oh-my-harness@0.1.0`, archive `oh-my-harness-0.1.0.tgz` 확인.
- `git diff --check`: 통과.
- 변경한 JavaScript, JSON, Markdown LSP primary diagnostics 0건을 확인했다.
- GitHub repository와 workspace directory rename은 완료했으며, 기존 사용자 install spec migration은 PR #19 merge 뒤 수행한다.

## 외부 동기화

- GitHub rename PR: <https://github.com/zzanghyunmoo/oh-my-harness/pull/19>
- Canonical Notion ticket: <https://app.notion.com/p/39eef22ad4fc81c4a4bce021fa26b92b>
- Linear ZZA-70은 후속 구현 PR이 남아 있어 `In Review`를 유지한다.

## Merge closeout

PR #19가 열려 있어 closeout은 pending이다. Merge 뒤 package identity 상태, KB, Notion과
work evidence를 새 `oh-my-harness` repository URL 및 merge commit 기준으로 갱신한다.
