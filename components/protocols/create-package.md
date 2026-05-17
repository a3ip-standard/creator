---
name: create-package
trigger: "create a package"
aliases:
  - "make an a3ip package"
  - "new a3ip package"
  - "package this workflow"
---

## What this protocol does

Guides through creating a new A3IP package from scratch: intake conversation, scaffold, validate, and build.

## Steps

1. Read SKILL.md completely.
2. Conduct the Phase 1 intake conversation with the user (Groups 1-8).
3. Write intake.json to the output directory.
4. Run script scaffold to generate the full package directory.
5. Run script validate and fix any errors until it reports ok: true.
6. Ask whether this is for external distribution (embed spec) or internal use.
7. Run script bundle (with --spec if external distribution).
8. Optionally run script zip_package.
9. Present the Completion Summary to the user.

## Outputs

TODO: List what this protocol produces (files written, messages sent, etc.)
