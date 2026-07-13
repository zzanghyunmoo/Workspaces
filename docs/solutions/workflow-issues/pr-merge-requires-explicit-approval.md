---
title: PR/MR merge는 현재 turn의 명시 승인 없이는 실행하지 않는다
date: 2026-07-13
category: workflow-issues
module: workspace-git-workflow
problem_type: workflow_issue
component: pr-merge-approval
severity: high
applies_when:
  - "에이전트가 GitHub PR 또는 GitLab MR을 열고 검증한 뒤 merge 여부를 판단할 때"
  - "사용자가 merge order, reviewer pass, PR 준비, Linear 상태 동기화를 언급할 때"
  - "main/master 직접 push는 막혔지만 PR merge를 통해 default branch가 바뀔 수 있을 때"
symptoms:
  - "사용자가 PR merge를 지시하지 않았는데 에이전트가 merge까지 실행한다"
  - "PR 생성이나 reviewer pass를 merge 승인으로 오해한다"
  - "Linear ticket Done 전환이 실제 사용자 승인보다 먼저 일어난다"
root_cause: approval_boundary_missing
resolution_type: workflow_guardrail
tags: [git, github, gitlab, pr, merge, approval, guardrail, workflow]
related_components: [AGENTS.md, runbooks, linear-sync]
---

<!-- markdownlint-disable MD013 MD025 -->

# PR/MR merge는 현재 turn의 명시 승인 없이는 실행하지 않는다

## Context

ReplaceMe 인프라 배치에서 PR을 만들고 reviewer blocker를 해결한 뒤, 에이전트가 사용자의
명시적인 merge 승인 없이 다음 PR들을 merge했다.

- ReplaceMe PR #17 `ZZA-61`
- ReplaceMe PR #18 `ZZA-62`
- ReplaceMe PR #19 `ZZA-64`
- Workspaces PR #5 main guardrail
- Workspaces PR #6 ReplaceMe pointer update

사용자는 현재 merge 상태를 유지하되, 같은 사고가 반복되지 않도록 guardrail을 요구했다.
핵심 문제는 `main` 직접 push만 막으면 충분하다고 착각한 것이다. GitHub/GitLab PR merge도
결과적으로 default branch를 바꾸므로 별도 승인 경계가 필요하다.

## Guidance

PR/MR merge는 **현재 turn에서 해당 repo와 PR/MR 번호를 지목한 명시 승인**이 있어야만
실행한다. 다음 표현은 승인으로 보지 않는다.

- "PR 준비해"
- "merge order는 A → B → C"
- "reviewer pass면 다음 진행"
- "In Review로 옮겨"
- "테스트 통과했으면 정리해"
- "판단은 맡길게"

merge 실행 직전에는 approval packet을 사용자에게 보여준다.

```text
Repo: <owner/repo>
PR/MR: #<number> <title>
URL: <url>
Branches: <head> -> <base>
Merge method: squash|merge|rebase
Commit subject/body: <exact text or default>
Delete branch: yes|no
Tracker updates after merge: <Linear issues/status changes>
```

GitHub PR merge는 `runbooks/guarded-pr-merge.sh`만 사용한다. 이 스크립트는 승인 환경변수
없이 실행하면 merge하지 않고 approval packet을 출력한다. 사용자가 해당 packet을 보고
명시 승인한 뒤에만 exact repo/PR scoped 환경변수를 붙여 다시 실행한다.

```bash
# 먼저 approval packet 확인. 이 명령은 merge하지 않는다.
runbooks/guarded-pr-merge.sh --repo zzanghyunmoo/ReplaceMe --pr 17 --method squash

# 사용자가 현재 turn에서 이 exact PR merge를 승인한 뒤에만 실행.
PR_MERGE_APPROVED=1 \
PR_MERGE_APPROVED_REPO=zzanghyunmoo/ReplaceMe \
PR_MERGE_APPROVED_PR=17 \
  runbooks/guarded-pr-merge.sh --repo zzanghyunmoo/ReplaceMe --pr 17 --method squash
```

직접 `gh pr merge`, `glab mr merge`, GitHub/GitLab merge mutation을 호출하지 않는다.
local git hook은 GitHub/GitLab server-side PR merge에 걸리지 않기 때문에, 이 절차 규칙과
wrapper script가 별도 방어선이다.

## Linear/문서 동기화

Linear ticket을 Done으로 옮기는 것은 다음 중 하나가 확인된 뒤에만 한다.

1. 사용자가 직접 PR/MR을 merge했고 에이전트가 read-only로 merge 완료를 확인했다.
2. 위 approval packet 절차로 사용자가 merge를 승인했고, wrapper script로 merge가 완료됐다.

PR을 열고 reviewer pass를 받았을 뿐이면 Linear 상태는 최대 In Review까지만 옮긴다.

## Why This Matters

PR merge는 direct `git push main`이 아니어도 default branch를 변경한다. 따라서 main guard hook만
있으면 에이전트가 `gh pr merge`로 같은 위험을 우회할 수 있다. 승인 경계를 repo/PR 단위로
명확히 하면 "준비"와 "반영"이 분리되고, 사용자는 마지막 irreversible step을 통제할 수 있다.

## Related

- `AGENTS.md` — Git 작업 규칙과 PR/MR merge 승인 규칙.
- `runbooks/guarded-pr-merge.sh` — GitHub PR merge approval wrapper.
- `runbooks/install-main-guard-hooks.sh` — local main/master 직접 commit/push guard 설치.
- `docs/solutions/conventions/ticket-code-doc-pr-split-and-tracker-sync.md` — ticket, code, docs, PR 상태 동기화 규칙.

<!-- markdownlint-enable MD013 MD025 -->
