# a3ip-creator

A Cowork skill and supporting Python scripts that guide an AI through authoring a new A3IP package from scratch. Conducts a structured intake conversation, generates the complete package directory, runs completeness validation, and produces the distributable bundle.

## Workflows

- **"create a package"** — Guides through creating a new A3IP package from scratch: intake conversation, scaffold, validate, and build.
- **"cut a new version"** — Cuts a new package version: bumps manifest, prepends changelog entry, validates, and rebundles.

## Installation

This is an A3IP package. To install it, give the `.a3ip.bundle` file to
your AI assistant and say: "Install this package."

The AI will read the instructions and set everything up in your skills directory.
No configuration wizard needed — just Python 3.9+ on your machine.

## Platforms

- cowork
- claude-code
- codex
- cursor

## Author

Maksym Prydorozhko <maksym.prydorozhko@gmail.com>
