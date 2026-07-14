---
title: 거대한 통합 PR은 배포 가능한 스택 PR로 분해하고 순차 병합한다
date: 2026-07-07
last_updated: 2026-07-14
category: workflow-issues
module: replace-me-pr-workflow
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - "단일 통합 PR이 여러 배포 관심사를 한꺼번에 포함할 때"
  - "의존성이 있는 변경을 순서대로 리뷰하고 배포해야 할 때"
  - "oversized PR을 닫고 대체 PR 목록과 리뷰 순서를 남겨야 할 때"
  - "부모 PR을 squash merge한 뒤 다음 child PR을 main에 안전하게 retarget해야 할 때"
symptoms:
  - "하나의 PR에 큐 전환, provider 분리, 외부 연동, telemetry 변경이 함께 들어간다"
  - "리뷰어가 어떤 변경부터 merge하거나 배포할지 판단하기 어렵다"
  - "PR 제목이 워크스페이스 convention과 다르게 Conventional Commit prefix를 포함한다"
  - "child PR을 main으로 retarget하자 이미 병합된 parent 파일이 다시 충돌한다"
  - "child diff에 parent review-fix 이전 파일이 섞여 원래 slice 경계가 흐려진다"
root_cause: missing_workflow_step
resolution_type: workflow_improvement
tags: [git, pull-request, stacked-prs, pr-hygiene, integration-workflow, replace-me, squash-merge, conflict-resolution]
related_components: [documentation, assistant, tooling]
---

<!-- markdownlint-disable MD013 MD025 -->

# 거대한 통합 PR은 배포 가능한 스택 PR로 분해하고 순차 병합한다

## Context

`ReplaceMe` 통합 작업을 한 번에 담은 거대한 PR `#1`은 큐 전환, provider 분리, 외부 연동, telemetry를 함께 포함해 개별 배포·검증·롤백 단위를 판단하기 어려웠다. 당시 작업 기록은 이를 닫고 다음 순서의 deployable stacked PR로 재구성했다고 남겼다. (session history)

1. `#2`: `main <- feat/kafka-agent-queue`
2. `#3`: `feat/kafka-agent-queue <- feat/provider-agent-notifier`
3. `#4`: `feat/provider-agent-notifier <- feat/issue-document-integrations`
4. `#5`: `feat/issue-document-integrations <- feat/telemetry-docs`

이전 세션은 스택 생성, parent-first merge order, 전체 병합 후 `main`의 fast-forward 동기화까지 확인했지만, parent를 squash merge한 직후 각 child를 어떻게 재조정할지는 검증하지 않았다. (session history)

이 공백은 후속 [PR #20](https://github.com/zzanghyunmoo/ReplaceMe/pull/20) → [#21](https://github.com/zzanghyunmoo/ReplaceMe/pull/21) → [#22](https://github.com/zzanghyunmoo/ReplaceMe/pull/22) → [#23](https://github.com/zzanghyunmoo/ReplaceMe/pull/23) 체인을 병합할 때 드러났다. Parent를 squash merge하면 `main`에는 같은 최종 내용을 가진 새 commit이 생기지만 parent source commit ancestry는 보존되지 않는다. Child를 `main`으로 retarget하면 이미 반영된 parent 변경이나 child가 아직 받지 못한 parent review-fix가 충돌로 다시 나타날 수 있다.

해결은 child를 rebase/force-push하는 것이 아니라, 체인을 한 단계씩 처리하면서 현재 `main`을 다음 child에 일반 merge하고 child 고유 diff를 다시 증명하는 것이었다. 2026-07-14 확인 시 PR #20~#23은 모두 이 순서로 `main`에 병합됐다.

## Guidance

### 스택을 만드는 단계

거대한 통합 PR은 그대로 리뷰하지 말고 먼저 **deployable slice**로 나눈다. 각 slice는 독립적으로 이해·검증·배포·롤백할 수 있는 의미 단위여야 한다.

1. 큰 PR의 변경을 배포 순서대로 나눈다.
   - 기반 인프라 또는 큐 변경
   - 그 위에 얹히는 provider 또는 runtime 선택 기능
   - 외부 연동 기능
   - 관측성, 문서, 운영 보강
2. 첫 PR은 `main`을 base로 둔다.
3. 다음 PR부터는 직전 feature branch를 base로 둔다.
   - 예: `main <- A`, `A <- B`, `B <- C`.
4. 각 PR 본문에 담당 범위, base/head 관계, 검증, 후속 의존성을 적는다.
5. 원래 oversized PR은 닫고 대체 PR 목록과 리뷰 순서를 링크한다.
6. PR 제목과 본문은 워크스페이스 convention을 따른다.

기존 큰 PR을 닫는 이유는 변경을 버리기 위해서가 아니라 리뷰 가능하고 배포 가능한 단위로 재구성하기 위해서임을 명시한다.

### squash merge된 스택을 landing하는 단계

#### 1. Parent merge를 원격에서 확인한다

한 번에 parent 하나만 처리한다. 승인된 guard를 통해 parent를 merge한 뒤 원격 상태가 실제 `MERGED`이고 merge commit이 `origin/main`에 포함됐는지 확인한다. 이 확인 전에는 child retarget이나 Linear `Done` 전환을 진행하지 않는다.

```bash
repo=zzanghyunmoo/ReplaceMe
parent_pr=20

merge_oid=$(gh pr view "$parent_pr" --repo "$repo" \
  --json state,mergedAt,mergeCommit \
  --jq 'select(.state == "MERGED" and .mergedAt != null) | .mergeCommit.oid')

git fetch origin main
git merge-base --is-ancestor "$merge_oid" origin/main
```

#### 2. Parent branch를 지우기 전에 child 의도를 기록한다

Retarget 전에 old parent와 child branch의 three-dot diff를 비추적 위치에 기록한다. 이 목록이 conflict path가 parent-only인지 child-owned인지 판단하는 기준이 된다.

```bash
old_parent=ZZA-65/infra-batch-polish
child=ZZA-66/run-passport-v1-hardening
child_pr=21

mkdir -p "/tmp/stack-pr-$child_pr"
git fetch origin "$old_parent" "$child" main

git diff --name-status "origin/$old_parent...origin/$child" \
  > "/tmp/stack-pr-$child_pr/intended.name-status"
git diff --no-renames --name-only -z \
  "origin/$old_parent...origin/$child" \
  > "/tmp/stack-pr-$child_pr/intended.paths.z"
git diff --binary "origin/$old_parent...origin/$child" \
  > "/tmp/stack-pr-$child_pr/intended.patch"
```

`intended.name-status`는 사람이 검토하는 목록이고, `intended.paths.z`는 rename의 양쪽 경로까지 분리해 exact path membership을 판정하는 입력이다.

Source branch 삭제는 전체 descendant가 `main`으로 retarget되고 병합될 때까지 미룬다. Parent branch를 먼저 지우면 open child가 참조하는 base와 intended diff를 재구성할 안정적인 기준을 잃는다.

#### 3. 다음 child만 main으로 retarget하고 read-only preflight를 실행한다

```bash
gh pr edit "$child_pr" --repo "$repo" --base main
git fetch origin main "$child"

git merge-tree --write-tree origin/main "origin/$child"
```

`git merge-tree --write-tree`는 worktree와 index를 바꾸지 않고 예상 merge와 conflict path를 보여 준다. Conflict가 나오면 바로 merge하지 말고 intended diff와 대조해 mechanical인지 semantic인지 먼저 분류한다.

#### 4. Rebase나 force-push 대신 main을 child에 merge한다

```bash
git switch "$child"
git merge --no-ff origin/main \
  -m "Merge main into $child after parent PR"
```

이 merge commit은 기존 child commit identity와 리뷰 맥락을 보존하면서 parent squash 결과를 ancestry에 명시적으로 연결한다. Landing 중에는 rebase, reset, force-push로 공개 branch history를 다시 쓰지 않는다.

#### 5. Mechanical conflict와 semantic conflict를 구분한다

**Mechanical conflict**는 conflict path가 child의 intended diff에 없고 이미 병합된 parent 또는 parent review-fix만 소유한 경우다. 이때는 검증된 `origin/main` 내용을 보존한다.

```bash
path=docs/plans/2026-07-13-001-feat-infra-foundation-roadmap-plan.md
paths_file="/tmp/stack-pr-$child_pr/intended.paths.z"

if ! python3 - "$path" "$paths_file" <<'PY'
import os
import sys

with open(sys.argv[2], "rb") as file:
    paths = file.read().split(b"\0")
raise SystemExit(0 if os.fsencode(sys.argv[1]) in paths else 1)
PY
then
  git restore --source=origin/main --staged --worktree -- "$path"
fi
```

**Semantic conflict**는 parent와 child가 같은 파일·계약·상태 전이·문서 사실을 의도적으로 수정한 경우다. Blanket `ours` 또는 `theirs`를 선택하지 않고 현재 `main`, child의 원래 patch, 요구사항을 함께 읽어 수동 조합한다. 의도를 증명할 수 없거나 계약이 양립하지 않으면 merge를 중단하고 owner 결정을 받는다.

모든 해결 후 unresolved path가 없어야 한다.

```bash
test -z "$(git diff --name-only --diff-filter=U)"
git diff --check
git commit
```

#### 6. 최종 diff가 child slice만 포함하는지 증명한다

```bash
git fetch origin main
git diff --name-status origin/main...HEAD \
  | tee "/tmp/stack-pr-$child_pr/final.name-status"
git diff --stat origin/main...HEAD
git diff --check origin/main...HEAD
```

`intended.name-status`와 `final.name-status`의 차이는 모두 설명 가능해야 한다. 예상하지 못한 parent 파일이 남으면 parent scope를 되살렸거나 child를 잘못된 순서로 재조정한 것이므로 stop condition이다. 파일 목록이 같아도 실제 patch를 검토해 parent review-fix가 사라지지 않았는지 확인한다.

그다음 child 범위의 focused test, 전체 test, lint, 문서 링크 검사를 다시 실행한다.

#### 7. Push 뒤 GitHub의 live merge state를 다시 확인한다

```bash
git push origin "$child"

gh pr view "$child_pr" --repo "$repo" \
  --json state,baseRefName,headRefName,mergeable,mergeStateStatus
```

Push 직후 GitHub가 `UNKNOWN`을 반환하면 계산이 끝날 때까지 다시 조회한다. `MERGEABLE/CLEAN`이 아니면 merge하지 않는다. `CLEAN`은 시점 의존 상태이므로 이전 push나 이전 PR에서 확인한 결과를 재사용할 수 없다.

#### 8. Exact approval 뒤 guarded squash merge한다

`runbooks/guarded-pr-merge.sh`는 workflow evidence, 최신 head의 code/doc review marker, `MERGEABLE/CLEAN`, exact repo/PR 승인을 순서대로 확인한다. 직전 단계에서 live state를 먼저 확인한 뒤 현재 turn의 approval packet대로 실행한다.

```bash
work_evidence=docs/works/2026-07-14-ZZA-66-run-passport-work.md

PR_MERGE_APPROVED=1 \
PR_MERGE_APPROVED_REPO=zzanghyunmoo/ReplaceMe \
PR_MERGE_APPROVED_PR="$child_pr" \
runbooks/guarded-pr-merge.sh \
  --repo zzanghyunmoo/ReplaceMe \
  --pr "$child_pr" \
  --workflow-evidence "$work_evidence" \
  --method squash \
  --subject "approved squash subject"
```

`--delete-branch`는 생략한다. 명령 완료 후 PR의 `MERGED`와 `mergedAt`을 확인하고, `docs/kb`와 Notion 기능 현황·티켓 문서를 closeout한 뒤에만 해당 Linear issue를 `Done`으로 전환한다. 이어서 새 `main`을 기준으로 다음 direct child에 같은 절차를 반복한다.

## Why This Matters

- **Tree equivalence와 ancestry equivalence는 다르다.** Squash 결과가 parent branch와 같은 내용을 가져도 새 squash commit은 child ancestry에 없다.
- **Mechanical conflict 분류가 parent review-fix를 보존한다.** Child가 건드리지 않은 경로는 검증된 `main`을 유지해야 한다.
- **Semantic conflict는 자동화 경계다.** 같은 계약을 양쪽이 바꾸면 요구사항 판단 없이 한쪽을 선택할 수 없다.
- **일반 merge commit은 reconciliation의 감사 흔적을 남긴다.** Rebase 없이 기존 review history와 normal push를 유지한다.
- **최종 diff scope 검사는 다음 squash의 입력을 통제한다.** Child 고유 변경만 남았는지 증명해야 parent 변경을 중복 반영하지 않는다.
- **Linear `Done`은 merge closeout 결과다.** PR 생성, reviewer pass, merge order 합의, `CLEAN`, merge 완료만으로는 KB·Notion·티켓 동기화가 끝나지 않는다.

## When to Apply

- PR B가 PR A source branch를 base로 하고 A를 squash merge했을 때.
- Child를 `main`으로 retarget한 직후 이미 병합된 parent 파일에서 conflict가 발생했을 때.
- Parent review-fix commit이 descendant branch에 전파되지 않았을 때.
- 공개된 PR branch history를 다시 쓰지 않고 stack을 landing해야 할 때.
- 각 PR을 독립된 squash commit으로 남기면서 child 고유 diff만 유지해야 할 때.

Stack 전체가 아직 공개되지 않았고 팀이 다른 적층 도구나 merge strategy를 합의했다면 해당 도구의 공식 restack 절차를 따른다. 이미 리뷰 중인 branch에서 임의로 history rewrite로 전환하지 않는다.

## Examples

### Oversized PR을 stack으로 바꾸기

```text
main
└── feat/kafka-agent-queue                    (#2)
    └── feat/provider-agent-notifier          (#3)
        └── feat/issue-document-integrations  (#4)
            └── feat/telemetry-docs           (#5)
```

닫힌 oversized PR에는 대체 PR 목록과 review order를 남긴다.

### PR #21: parent-only conflict

PR #20 squash merge 뒤 PR #21을 `main`으로 retarget하자 infra roadmap 한 파일이 conflict했다. 이 파일은 PR #21의 Run Passport intended scope가 아니라 PR #20 review-fix 소유였으므로 `main`을 보존했다. 최종 PR #21 diff는 Run Passport 관련 8개 파일이었고 전체 .NET test 85개가 통과했다.

### PR #22: parent review-fix 다섯 경로

PR #21 review-fix가 PR #22 ancestry에 없어서 Run Passport 문서, roadmap, contract, contract test, endpoint test가 conflict했다. 다섯 경로 모두 PR #22의 Compose intended diff 밖이었으므로 `main`을 보존했다. 최종 diff는 `docker-compose.yml`과 `HostingCompositionTests.cs` 두 파일뿐이었고, PR #22 본문에는 전체 .NET test 76개 통과로 기록돼 있다.

### PR #23: parent 보존과 child 문서의 수동 조합

PR #23에서는 parent-owned Run Passport code/test와 hosting test는 `main`을 보존했다. 세션 기록상 PR #23이 실제로 수정한 문서는 child intent를 유지했고, infra roadmap은 parent의 최신 내용을 바탕으로 child-owned 변경만 수동 반영했다. (session history)

최종 diff는 GitHub PR file list와 Git history에서 문서·scanner를 포함한 PR #23 고유 30개 파일로 재현됐다. PR #23 본문에는 .NET test 76개, Python scanner test 6개, Ruff, Markdownlint, 30개 파일 상대 링크 검사, whitespace diff check가 통과한 것으로 기록돼 있다.

이 사례들의 핵심은 conflict 수를 0으로 만든 것이 아니라 각 conflict를 child intended diff와 대조해 parent-only 변경과 양쪽 소유 변경을 분리하고 최종 slice 경계를 다시 증명한 것이다.

## Related

- `docs/solutions/workflow-issues/pr-merge-requires-explicit-approval.md` — 각 PR의 current-turn approval packet과 guarded merge, merge 이후 Linear `Done` 경계.
- `docs/solutions/conventions/ticket-code-doc-pr-split-and-tracker-sync.md` — 하나의 ticket에서 문서·코드 PR을 stack하고 외부 작업면을 동기화하는 규칙.
- `runbooks/guarded-pr-merge.sh` — workflow evidence, 최신-head review marker, exact repo/PR 승인을 확인하는 wrapper.
- `docs/works/README.md` — ticket work evidence와 post-merge closeout 규약.
- [ReplaceMe PR #20](https://github.com/zzanghyunmoo/ReplaceMe/pull/20), [#21](https://github.com/zzanghyunmoo/ReplaceMe/pull/21), [#22](https://github.com/zzanghyunmoo/ReplaceMe/pull/22), [#23](https://github.com/zzanghyunmoo/ReplaceMe/pull/23) — 2026-07-14에 순서대로 `main`에 병합된 실제 사례.

<!-- markdownlint-enable MD013 MD025 -->
