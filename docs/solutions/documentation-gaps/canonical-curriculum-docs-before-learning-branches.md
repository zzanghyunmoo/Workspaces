---
title: Canonical curriculum docs before learning branches
date: 2026-07-03
category: documentation-gaps
module: dotnet-foundation-lab
problem_type: documentation_gap
component: documentation
severity: medium
applies_when:
  - "Starting a project-based learning repo that will evolve across branches"
  - "Separating exploratory examples from TDD-first project code"
  - "Using main as a curriculum index while implementation happens on branches"
tags: [curriculum, documentation, learning-repo, tdd, branching, dotnet]
---

## Context

`projects/dotnet-foundation-lab` needed to support a daily C#/.NET
foundation routine without turning `main` into a half-built Sokoban
implementation.
The goal was to learn by building, but still preserve a clear sequence:
Microsoft Learn concept, small example, Sokoban TDD application, reflection,
and later branch-based expansion.

A flat README could state the intent, but it could not carry enough operating
detail for branch naming, test policy, track boundaries, and future extension
topics.
The solved shape was to create a canonical curriculum spine before writing
project code.

## Guidance

For a project-based learning repo, keep `main` documentation-first until the
learning system is clear.
Create a canonical curriculum subtree that defines the learning loop, branch
taxonomy, templates, test policy, domain rulebook, and expansion tracks before
creating implementation branches.

Use this split:

```text
main
└── docs/curriculum/        # canonical learning system
    ├── index.md            # entrypoint and learning loop
    ├── mslearn-index.md    # official source links
    ├── chapter-template.md
    ├── daily-note-template.md
    ├── branching.md
    ├── testing-policy.md
    ├── sokoban-rulebook.md
    ├── expansion-map.md
    └── tracks/*.md

learning branches
└── base/ch01-string-map    # implementation snapshot for one learning step
```

The curriculum docs should answer these questions before the first code branch:

- What is the daily learning loop?
- Which source is authoritative for syntax or framework behavior?
- Which examples may be exploratory, and which project code must be TDD-first?
- What branch names represent learning snapshots?
- What does the foundation project deliberately postpone?
- Which later topics are introduced only when the project creates pressure?

For the Sokoban C# curriculum, the useful contract became:

1. **MS Learn first** — official documentation anchors syntax and .NET concepts.
2. **Small example second** — a tiny example isolates the concept without TDD
   ceremony.
3. **Sokoban application third** — project behavior starts from tests.
4. **Reflection last** — each chapter records why the new structure is better
   than the previous one.

## Why This Matters

A project-based curriculum can fail in two opposite ways.
If code starts too early, `main` becomes an accidental implementation branch and
the learner loses the map of what each step was supposed to teach.
If documentation stays too abstract, the curriculum becomes a syllabus detached
from concrete project pressure.

A canonical curriculum spine keeps both sides connected.
It makes the repository safe to revisit after a break, because the next action
is discoverable from docs rather than inferred from stale branches.
It also prevents premature scaffolding: contributors can see that code belongs
on learning branches after the chapter contract exists.

## When to Apply

- Starting a new learning repo where `main` should remain stable and
  documentation-first.
- Teaching fundamentals through one small project rather than isolated exercises.
- Separating exploratory syntax examples from TDD-first project behavior.
- Planning multiple future tracks such as OOP, data structures, algorithms,
  networking, database work, or design patterns.
- Avoiding premature `.sln`, `.csproj`, `src/`, or `tests/` scaffolding before
  the learning contract is explicit.

## Examples

Before the curriculum spine, the repo could only express broad intent:

```text
README.md
└── "Build Sokoban to learn C#"
```

After the curriculum spine, the repo expresses an operating system for learning:

```text
docs/curriculum/index.md          # how to use the curriculum
docs/curriculum/mslearn-index.md  # official C#/.NET references
docs/curriculum/branching.md      # branch families and first branch
docs/curriculum/testing-policy.md # examples vs project-code gates
docs/curriculum/tracks/base.md    # first procedural learning track
docs/curriculum/tracks/oop.md     # later pressure-driven OOP transition
```

This made the first implementation branch explicit:

```text
base/ch01-string-map
```

It also made the first PR safe to merge as documentation-only: no `.sln`,
`.csproj`, `.cs`, `src/`, or `tests/` files were introduced.

## Related

- `docs/brainstorms/2026-07-03-sokoban-csharp-foundation-curriculum-requirements.md`
- `docs/plans/2026-07-03-sokoban-csharp-foundation-curriculum-plan.md`
- `docs/ideation/2026-07-03-sokoban-csharp-foundation-lab-ideation.html`
- `projects/dotnet-foundation-lab/docs/curriculum/index.md`
- `projects/dotnet-foundation-lab/docs/curriculum/branching.md`
- `projects/dotnet-foundation-lab/docs/curriculum/testing-policy.md`
- GitHub PR: <https://github.com/zzanghyunmoo/dotnet-foundation-lab/pull/1>
