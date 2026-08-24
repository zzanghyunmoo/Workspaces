# Knowledge Base

`docs/kb/` is the canonical repository knowledge base for the current behavior
and operating facts of merged work. It is intentionally separate from the
ticket timeline: the GitHub Issue links to the KB entry, while the KB preserves
the versioned, reviewable result.

## Boundary with `docs/solutions/`

- `docs/kb/`: verified current feature state, usage, operating boundaries, and
  current limitations after merge.
- `docs/solutions/`: reusable causes, fixes, and workflow learnings discovered
  while solving a problem.

Do not duplicate the same prose. Link between the current-state KB and a reusable
solution when both are useful.

## File rules

- Path: `docs/kb/<category>/<YYYY-MM-DD>-GH-<number>-<topic>.md`.
- Start from `docs/kb/_template.md`.
- Link the canonical GitHub Issue, merged PR and commit, and work evidence.
- Record only behavior confirmed in code and actual verification results.
- Do not describe a plan or unimplemented goal as current behavior.

For `compound-work/v2`, required frontmatter is `title`, `ticket`, `ticket_url`,
`merged_pr`, `merge_commit`, `work_evidence`, and `last_verified`. Notion and
Linear fields are neither required nor interpreted.

`runbooks/compound_workflow_gate.py closeout` verifies that `kb_paths` resolves
to real `docs/kb/` Markdown committed at local `HEAD`, that the Issue/PR/commit
identity matches the work evidence, and that the current-state, boundary,
verification, and operations sections are present.

Existing KB entries linked from `compound-work/v1` remain historical evidence
and keep their legacy Notion/Linear fields; do not rewrite them in bulk.
