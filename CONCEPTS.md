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
