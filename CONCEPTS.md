# Concepts

Shared domain vocabulary for this project — entities, named processes, and status
concepts with project-specific meaning. Seeded with core domain vocabulary, then
accretes as ce-compound and ce-compound-refresh process learnings; direct edits
are fine. Glossary only, not a spec or catch-all.

## Workspace Structure

### Workspace Container

A repository whose purpose is to organize multiple working areas and durable
documentation rather than own every product's source history directly.

A Workspace Container may reference independently owned projects, but its own
history should stay focused on workspace-level documentation, pointers, and
coordination metadata.

### Standalone Project

A project whose code, issues, pull requests, releases, and automation should be
owned by its own repository rather than by the Workspace Container.

Standalone Projects are appropriate for apps, services, libraries, and long-lived
product experiments that need an independent lifecycle.

### Workspace Submodule

A Standalone Project linked from the Workspace Container through a git submodule
pointer.

A Workspace Submodule lets the workspace record which project revision belongs
in the local workspace while keeping implementation history in the Standalone
Project's repository.

### Submodule Pointer

The commit reference recorded by the Workspace Container for a Workspace
Submodule.

Updating a Standalone Project does not update the Workspace Container until the
Submodule Pointer is advanced and committed in the container repository.

## Notion Documentation

### Ticket-scoped Documentation

Documentation owned by a single ticket or work item and kept under that ticket's
Notion page rather than a generic project document folder.

Ticket-scoped Documentation keeps requirements, decisions, review notes,
verification results, and ticket-specific follow-up discoverable from the same
work item. It should link to canonical operating procedures rather than become
the home for repeated runbooks.

### Ticket Work Document Folder

A ticket-scoped Notion parent page that acts as the concise index for one work
item and owns stage-specific child pages.

A Ticket Work Document Folder keeps its parent page short: summary, external
work-surface links, key decisions, current status, and a child-page table of
contents. Ideation, brainstorming, planning, development notes, validation, and
follow-up diagnostics live in ordered child pages beneath it.

### QA Document Folder

A Notion page that acts as the container for reusable QA runbooks, test
checklists, and manual verification procedures.

For ReplaceMe, the canonical QA Document Folder belongs under the Operator Guide.
Ticket pages record ticket-specific QA outcomes and link to the canonical QA
procedures instead of owning duplicate runbooks.

### Notion Ancestry Verification

The practice of checking a Notion page's parent chain before creating or moving
related documentation.

Notion Ancestry Verification prevents follow-up artifacts from landing in a
nearby but wrong workspace area, and it is the confirmation step after moving a
misplaced page.

### Dual-published Documentation

A documentation artifact maintained on both the Notion project wiki and the
local repository docs for the same work stage or knowledge area.

Dual-published Documentation is not two independent sources of truth: the Notion
page owns the document taxonomy and current content shape, while the local copy
keeps repository history and code-review context aligned to that Notion source.

### Notion-first Documentation Sync

The workflow of choosing or updating the canonical Notion page first, then
mirroring its title, scope, section structure, links, and current status into the
local repository documentation.

Notion-first Documentation Sync applies when a work stage needs both a
collaborative Notion surface and a versioned local record; duplicate Notion pages
are redirected to the canonical page instead of becoming parallel sources.

### Feature Status Document

A Notion document that centralizes the product or design-facing map of what a
project can do, what is implemented, and what remains planned.

For ReplaceMe, a Feature Status Document belongs under design documentation.
Ticket-specific implementation notes may link to it, but they do not become the
canonical feature map.

### Background Document

A Notion page that records why a project direction exists: problem framing,
ideation, early scope, architecture options, and decision rationale.

Background Documents are not execution trackers. They explain why a plan is
reasonable, while dated execution plans and ticket documents own the operational
order of work.

### Development Plan Folder

A Notion folder under a project's development documentation that groups dated
execution plans and cross-ticket roadmaps.

A Development Plan Folder is distinct from ticket-scoped documentation: it owns
phase order, dependencies, and roadmap sequencing across tickets rather than the
lifecycle notes for a single work item.

## ReplaceMe Automation

### Readiness Profile

A pre-run capability check that decides whether a personal automation mode is
safe to use before an agent starts code-changing work.

A Readiness Profile reports blocking failures and warnings across the local
environment and configured external work surfaces, so later automation does not
discover missing access only after a run has started.

### Run Passport

A durable identity card for one automation run that ties the controlling issue,
code-review surface, documentation surface, verification evidence, approvals,
and final outcome into one traceable record.

A Run Passport is the shared reference that downstream comments, review packets,
and lifecycle documents point to; it should summarize evidence without exposing
secrets, local-only paths, or provider tokens.

### Run Passport Contract

The minimal shared field and link semantics that Run Passport consumers agree to
before full storage, rerun lineage, or analytics exist.

A Run Passport Contract lets parallel consumers render the same run identity,
status, evidence summary, and backlinks without inventing incompatible field
names or nullability rules.

### PR Review Packet

A reviewer-facing summary package for an automated code change.

A PR Review Packet explains the problem, change, verification evidence, demo or
non-demo reason, linked work item, linked documentation, Run Passport reference,
and residual risks in a form that is ready for human review.

### Notion Lifecycle Document

A ticket-scoped Notion document created when automation work starts and updated
as the run moves through approval waiting, PR creation, failure, completion, and
lessons learned.

A Notion Lifecycle Document is memory, not just a copied ticket body: it should
preserve why the work happened, what happened during the run, and what future
runs should learn from it.

### Linear Issue Execution Grammar

The project-specific rules that decide whether a Linear issue contains enough
information to become executable automation work.

When the issue is not runnable, the grammar should produce a focused
clarification path instead of starting an agent run from ambiguous requirements.

## Review Workflow

### Deployable Slice

A review unit that can be understood, verified, merged, and deployed without
requiring unrelated changes from the same oversized work batch.

A Deployable Slice may depend on an earlier slice, but it should still have a
clear boundary, validation story, and rollback implication of its own.

### Stacked PR

A sequence of pull requests where each later branch uses the previous slice
branch as its base so reviewers can follow dependent work in deployment order.

A Stacked PR sequence preserves dependency order without forcing all changes into
one oversized review.

### Ticket-scoped PR Pair

A matched documentation/code pull-request pair for one ticket, where the
documentation PR establishes the review contract and the code PR stacks on that
contract.

A Ticket-scoped PR Pair shares the ticket identifier and title across both PRs;
only the review-surface suffix distinguishes the documentation slice from the
code slice.

### External Work Surface Sync

The handoff step that mirrors GitHub PR structure, verification evidence, and
current status back into the external work surfaces that own the ticket context.

External Work Surface Sync keeps Linear issues and Notion design or lifecycle
notes aligned with the actual PR stack, so reviewers and future automation runs
do not rely on stale ticket or document state.

### Oversized PR

A pull request whose scope combines multiple deployable concerns so review order,
validation scope, or rollback responsibility becomes unclear.

An Oversized PR should be replaced by Deployable Slices when the bundled work can
be split into a clear Stacked PR sequence.
