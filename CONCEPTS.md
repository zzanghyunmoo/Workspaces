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

### Oversized PR

A pull request whose scope combines multiple deployable concerns so review order,
validation scope, or rollback responsibility becomes unclear.

An Oversized PR should be replaced by Deployable Slices when the bundled work can
be split into a clear Stacked PR sequence.
