# GitHub-native work workflow

This runbook applies only to project repositories that explicitly retain the
`compound-work/v2` staged `docs/` contract in their own `AGENTS.md`. It is not
the workflow for the `zWorkspaces` root, whose `AGENTS.md` forbids root `docs/`.
For participating projects, GitHub Issues and pull requests are the control
plane and repository Markdown is the canonical documentation and evidence.

## Source-of-truth map

<!-- markdownlint-disable MD013 -->

| Concern | Canonical surface |
| --- | --- |
| Work identity and open/closed lifecycle | GitHub Issue |
| Requirements and implementation plan | `docs/brainstorms/`, `docs/plans/` |
| Implementation and verification evidence | `docs/works/` |
| Review and merge | GitHub PR and trusted review comments |
| Current merged behavior | `docs/kb/` |
| Reusable solution knowledge | `docs/solutions/` |
| Cross-repository overview | Optional GitHub Project |

<!-- markdownlint-enable MD013 -->

Keep the Issue body as an index: objective, current status, target repositories,
and links to canonical docs and PRs. Do not paste full plan or work-log prose into
the Issue.

## Lifecycle labels

An open Issue has exactly one lifecycle label:

- `status:planned`
- `status:in-progress`
- `status:in-review`
- `status:blocked`

Read the current remote state before a transition. Preserve every non-lifecycle
label, remove only the observed lifecycle label, add the next label in the same
mutation, and then read the Issue again to verify exactly one lifecycle label.

```bash
gh issue view 123 --repo OWNER/REPO --json state,stateReason,labels,url
gh issue edit 123 --repo OWNER/REPO \
  --remove-label 'status:planned' \
  --add-label 'status:in-progress'
gh issue view 123 --repo OWNER/REPO --json state,stateReason,labels,url
```

Do not invent `status:closeout` or `status:complete`. Keep
`status:in-review` through merge closeout. The guarded finalizer removes the
lifecycle label and closes the Issue with reason `completed`; cancellation uses
reason `not planned`.

## Start and plan work

1. Create the Issue from `.github/ISSUE_TEMPLATE/work.yml`.
2. Use `GH-<number>` in filenames and frontmatter. `ticket_url` is the full
   GitHub Issue URL and its owner/repo/number must match `ticket_id`.
3. Create canonical requirements and plan documents in their designated
   `docs/` directories, then add their paths to the Issue Index.
4. Transition the Issue from `status:planned` to `status:in-progress` before
   implementation.
5. Copy `docs/works/_template.md` and replace every placeholder. Use
   `workflow_schema: compound-work/v2`.

`validate-work` checks local structure without calling GitHub:

```bash
python3 runbooks/compound_workflow_gate.py validate-work \
  --evidence docs/works/<work-file>.md
```

## Open and review a PR

The PR body follows the four-section template and links the Issue without an
auto-close keyword:

```markdown
- Ticket: [`GH-123`](https://github.com/OWNER/REPO/issues/123)
- Work evidence: `docs/works/<work-file>.md`
```

Do not use `Closes`, `Fixes`, or `Resolves`; a merge is not final closeout.
After PR creation:

1. Record the full `pr_url` and any stacked `remaining_prs` in work evidence.
2. Add every PR URL to the Issue's canonical PR index between the
   `compound-pr-index` markers, then publish the evidence to the evidence
   repository's default branch.
3. Transition the Issue to `status:in-review`.
4. Run `ce-code-review` and `ce-doc-review` on the latest head and publish
   separate trusted comments.
5. Bind each `ce-review:v2` verdict to `head_sha`, `evidence_commit`, and
   `evidence_blob`. A change to code or evidence makes the verdict stale.

For a cross-repository PR, `evidence_commit` identifies the explicitly selected
project evidence repository revision and `evidence_blob` identifies the exact
work file in that revision. The gate must verify both before accepting the marker.

## Merge and closeout

Use the approval packet and guarded merge command required by `AGENTS.md`; never
invoke `gh pr merge` directly. While another stacked PR remains, keep the Issue
open, keep `status:in-review`, set `ticket_completion: pending`, and list the
remaining full PR URLs.

After the final merge:

1. Create the current-state KB entry from `docs/kb/_template.md`.
2. Set `closeout_status: complete`, `ticket_completion: complete`, and record
   `merged_pr_url`, `merge_commit`, `kb_paths`, and `closeout_completed_at`.
3. Publish the KB and work closeout to the default branch.
4. Dry-run the guarded Issue finalizer, then run it only within the approved
   workflow. It verifies default-branch evidence and that every PR in the remote
   Issue index is merged before it removes the lifecycle label and closes with
   reason `completed`.
5. Run `ack-closeout` after remote and local closeout state agree.

If any approval is pending, leave `ticket_completion: pending`, record the real
`remaining_prs`, and stop at `status:blocked` or `status:in-review`. Do not report
the overall work as complete.

## Optional Project projection

Project membership or field updates may be reconciled when the token has Project
scope. A projection failure is reported as pending but never rolls back or blocks
the Issue/PR/docs lifecycle. The Project must not become a second source of truth.

## Legacy evidence

Do not rewrite historical `compound-work/v1` files. Their Linear, Notion,
`NO-TICKET`, and `ce-review:v1` fields remain valid only under the legacy
validator branch. Every new work document starts from the v2 template.
