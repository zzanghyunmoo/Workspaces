# Work Evidence

`docs/works/` stores the canonical ticket-scoped implementation record and
Compound Engineering evidence. A GitHub Issue is the work identity and lifecycle
index; it links here instead of duplicating this document.

## File rules

- Path: `docs/works/<YYYY-MM-DD>-GH-<number>-<topic>-work.md`.
- Start from `docs/works/_template.md` for new work.
- When one Issue has multiple pull requests, create one evidence file per PR and
  include `pr-<number>` in its filename. Each file owns one `pr_url` and that
  PR's review and closeout.
- Record real results in `## 주요 변경 지점`, `## 검증`, `## GitHub 추적`,
  and `## Merge closeout`; do not leave placeholders.
- A skipped ideation or plan uses `waived` plus a concrete waiver reason.
- Never record tokens, API keys, internal hosts, private-note contents, or
  personal local paths.

## `compound-work/v2` frontmatter

<!-- markdownlint-disable MD013 -->

| Field | Format and rule |
| --- | --- |
| `workflow_schema` | Always `compound-work/v2`. |
| `ticket_id` | `GH-<positive integer>`; must match the Issue URL number. |
| `ticket_url` | `https://github.com/<owner>/<repo>/issues/<number>`. |
| `ticket_completion` | `pending` before final closeout; `complete` only at final closeout. |
| `remaining_prs` | Comma-separated full GitHub PR URLs; empty when completion is `complete`. |
| `ideation_status`, `plan_status` | `complete` with a repo path, or `waived` with a reason. |
| `work_status` | `in_progress` until implementation/review evidence is complete, then `complete`. |
| `pr_url` | One full GitHub PR URL; required after PR creation and may be cross-repository. |
| `closeout_status` | `pending` before merge; `complete` after verified merge closeout. |
| `merged_pr_url`, `merge_commit`, `kb_paths`, `closeout_completed_at` | Required when closeout is `complete`. |

<!-- markdownlint-enable MD013 -->

`ticket_status`, Linear URLs/states, and Notion URLs are not v2 fields. GitHub
remote state is read from `ticket_url`; durable evidence lives in repository
artifacts.

## Lifecycle

1. Create the GitHub Issue with `status:planned` and link the requirements/plan
   paths as they become available.
2. Before implementation, replace the open lifecycle label with
   `status:in-progress` and create a v2 work document.
3. After PR creation, set `pr_url`, complete the local work evidence, publish it
   to the evidence repository's default branch, add every PR URL to the Issue's
   canonical PR index, and replace the label with `status:in-review`.
4. Keep the Issue open and `status:in-review` while stacked PRs or merge closeout
   remain. List every remaining PR URL in `remaining_prs`.
5. After the final merge, add KB and merge evidence on the default branch. The
   guarded finalizer verifies that every remotely indexed PR is merged, removes
   the lifecycle label, and closes the Issue with reason `completed`. Cancellation
   instead uses reason `not planned`.

An open Issue has exactly one of `status:planned`, `status:in-progress`,
`status:in-review`, or `status:blocked`. A completed closed Issue has none of
these labels.

## Review comment markers

Run `ce-code-review` and `ce-doc-review` on the latest PR head and publish the
results as separate comments. Only a GitHub OWNER/MEMBER/COLLABORATOR trusted by
the merge gate may publish accepted evidence. A new commit makes both verdicts
stale.

For v2, each marker binds the PR head to the exact work-evidence revision:

<!-- markdownlint-disable MD013 -->

```html
<!-- ce-review:v2 type=code ticket=GH-123 head_sha=<pr-head-sha> evidence_commit=<evidence-repo-commit> evidence_blob=<work-file-git-blob> verdict=pass -->
```

```html
<!-- ce-review:v2 type=doc ticket=GH-123 head_sha=<pr-head-sha> evidence_commit=<evidence-repo-commit> evidence_blob=<work-file-git-blob> verdict=pass -->
```

<!-- markdownlint-enable MD013 -->

The comment must contain a substantive review summary, findings, verification
scope, and blocker disposition; a marker-only comment is rejected. Use
`verdict=fail` while a blocker remains. Cross-repository reviews verify that the
recorded evidence blob still exists unchanged in the recorded commit on the
evidence repository's `origin/main`.

## Gate commands

Run gates from the repository that owns the canonical work evidence. For a
cross-repository PR, run the root-owned gate from the root evidence repository;
`--repo` and `--pr` identify the delivery repository. `validate-work` is local
and does not call GitHub.

```bash
python3 runbooks/compound_workflow_gate.py validate-work \
  --evidence docs/works/<work-file>.md

python3 runbooks/compound_workflow_gate.py pre-merge \
  --evidence docs/works/<work-file>.md \
  --repo OWNER/REPO \
  --pr NUMBER

python3 runbooks/compound_workflow_gate.py review-context \
  --evidence docs/works/<work-file>.md \
  --repo OWNER/DELIVERY-REPO \
  --pr NUMBER

python3 runbooks/compound_workflow_gate.py closeout \
  --evidence docs/works/<work-file>.md \
  --repo OWNER/REPO \
  --pr NUMBER

python3 runbooks/compound_workflow_gate.py ack-closeout \
  --repo OWNER/REPO \
  --pr NUMBER
```

`runbooks/guarded-pr-merge.sh` runs the pre-merge gate and records local closeout
debt. The common pre-push hook rejects a push while that debt is incomplete.
These local controls do not replace repository rulesets; GitHub Project remains
an optional projection and GitHub Wiki is not a canonical documentation surface.

## Legacy v1

Existing `compound-work/v1` files remain immutable historical evidence. Their
Linear and Notion fields, `NO-TICKET` waiver, and `ce-review:v1` markers continue
to be interpreted only by the legacy validator branch. Do not convert old work
documents merely to adopt v2.
