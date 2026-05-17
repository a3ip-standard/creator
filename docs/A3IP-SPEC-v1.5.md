# A3IP Specification v1.5
**AI Infrastructure Installation Package**

> A platform-agnostic format for packaging and sharing complete AI workspace workflows — a superset of the [SKILL.md](https://agentskills.io) open standard and [Microsoft APM](https://microsoft.github.io/apm/).

**What's new in v1.5:** Registry & Ecosystem — a standardized `registry.yaml` index format that lets packages be discovered, and a formal `## Installing from a Registry` section that defines how an AI browses a registry and installs from it. Packages authored under v1.0–v1.4 remain fully valid.

---

## Overview

*(Unchanged from v1.4.)*

---

## Package Structure

*(Unchanged from v1.2 — see v1.2 spec for directory layout and bundle format.)*

---

## Terminology

*(Unchanged from v1.3 — see v1.3 spec for component definitions and decision table.)*

---

## Platform Conventions

*(Unchanged from v1.3 — see v1.3 spec for platform adapter conventions.)*

---

## Validation

*(Unchanged from v1.4 — see v1.4 spec for the nine normative validation checks.)*

---

## Registry

A3IP packages are distributed as `.a3ip.bundle` files. A registry is an index that makes packages discoverable: it lists available packages with enough metadata for an AI to find what a user needs, retrieve the bundle, and install it without any additional lookups.

A registry is a single `registry.yaml` file. It can be local (a file on the user's machine) or remote (a URL that returns the YAML content). Both are treated identically by the AI installer.

---

### registry.yaml format

```yaml
---
format: a3ip-registry
spec: "1.5"
name: "My Package Registry"        # human-readable name, optional
description: "..."                  # what this registry covers, optional
maintained_by: "Author Name"        # optional
updated: "2026-05-12"               # ISO date of last update, optional
---

packages:

  - name: package-name              # must match manifest.yaml name exactly
    version: "1.0.0"               # current version in this registry entry
    description: "One-sentence description of what this package does."
    author: "Full Name <email>"
    license: proprietary            # or: MIT, Apache-2.0, etc.
    platforms:
      - cowork
      - claude-code
    tags:                           # optional — for browsing and filtering
      - code-review
      - gitlab
    bundle_url: "./packages/package-name.a3ip.bundle"
                                    # Relative path, absolute path, or https:// URL.
                                    # The AI resolves this relative to the registry file's location.
    min_a3ip_spec: "1.0"           # minimum spec version required to install
    changelog_summary: "..."        # optional — one-line summary of latest version's changes
```

**Field reference:**

| Field | Required | Description |
|---|---|---|
| `name` | ✅ | Package name — must match `manifest.yaml name:` exactly |
| `version` | ✅ | Current version string — must match `manifest.yaml version:` |
| `description` | ✅ | One-sentence description for browsing |
| `author` | ✅ | Package author |
| `license` | ✅ | License identifier |
| `platforms` | ✅ | Platforms the package has been tested on |
| `bundle_url` | ✅ | Where to retrieve the bundle — relative path, absolute path, or HTTPS URL |
| `tags` | optional | Keywords for filtering |
| `min_a3ip_spec` | optional | Minimum A3IP spec version required by the package |
| `changelog_summary` | optional | What changed in the latest version — shown during browse |

**`bundle_url` resolution rules:**

- If `bundle_url` starts with `https://` or `http://`: retrieve via HTTP GET.
- If `bundle_url` starts with `./` or `../`: resolve relative to the directory containing `registry.yaml`.
- If `bundle_url` is an absolute path (starts with `/` or a drive letter): use directly.
- The AI must not silently substitute a different URL or path if the bundle is not found at the declared location.

---

### Browsing a registry

When a user asks to install a package from a registry, or when the AI needs to suggest packages, the AI follows this sequence:

1. **Locate the registry.** The user provides a path or URL to `registry.yaml`. Common locations:
   - A local file: `~/registries/my-registry.yaml`
   - A URL: `https://example.com/a3ip-registry.yaml`
   - The workspace registry: `registry.yaml` in the current working directory.

2. **Read and parse `registry.yaml`.** Load the `packages:` list.

3. **Filter by need.** If the user described what they need (e.g. "I want a code review workflow for GitLab"), filter by `tags`, `description`, and `platforms`. Present only relevant matches.

4. **Present the options.** Show each matching package as a brief entry:
   ```
   bliq-code-review-flow  v1.0.0
   Complete code review workflow for GitLab-based .NET microservice teams.
   Platforms: cowork, claude-code  |  License: proprietary
   Latest: initial release
   ```

5. **Ask the user to choose.** If multiple packages match, ask which one to install. If exactly one matches, confirm before proceeding.

6. **Proceed to installation.** Once the user confirms, retrieve the bundle and install it (see below).

---

### Installing from a registry

After the user selects a package:

1. **Retrieve the bundle.** Resolve `bundle_url` per the rules above. Read the bundle file into context (or fetch via HTTP if it is a URL).

2. **Proceed with normal installation.** The bundle is a standard `.a3ip.bundle` file. Follow the standard installation procedure: read `INSTALL.md` from the bundle, run the configuration wizard from `CONFIGURE.md`, apply each install step.

3. **Version check.** Before installing, check `installed.json` in the user's local config directory. If it exists and its `version` matches or exceeds the registry entry's `version`, tell the user the package is already up to date. If the installed version is older, proceed as an upgrade (use `CHANGELOG.md` upgrade steps).

4. **Record the registry source.** After a successful install, add a `registry_source` field to `installed.json`:
   ```json
   {
     "package": "bliq-code-review-flow",
     "version": "1.0.0",
     "installed_at": "2026-05-12T21:00:00Z",
     "platform": "cowork",
     "registry_source": "./registry.yaml"
   }
   ```
   This allows future update checks to re-query the same registry.

---

### Checking for updates

If `installed.json` contains a `registry_source` field, the AI can check for updates:

1. Read `registry_source` to locate the registry.
2. Load `registry.yaml` and find the entry whose `name` matches the installed package.
3. Compare the registry entry's `version` with `installed.json version`.
4. If the registry has a newer version: inform the user and offer to upgrade.
5. If the registry entry's `bundle_url` is unreachable: report the error and do not modify the installed package.

---

### Authoring a registry

To publish your own packages, create a `registry.yaml` file following the format above and place it alongside your `.a3ip.bundle` files. A minimal registry for a single local package:

```yaml
---
format: a3ip-registry
spec: "1.5"
name: "My Workflows"
---

packages:

  - name: my-workflow
    version: "1.0.0"
    description: "A workflow package for my team."
    author: "Me <me@example.com>"
    license: proprietary
    platforms:
      - cowork
    bundle_url: "./my-workflow.a3ip.bundle"
```

No server required — a registry can live entirely on a shared drive, a Git repository, or any file-accessible location.

---

## manifest.yaml, CONFIGURE.md, INSTALL.md, CHANGELOG.md, installed.json

*(Unchanged from v1.2.)*

---

## Component Formats

*(Unchanged from v1.0.)*

---

## Versioning

*(Unchanged from v1.4. Updated spec compatibility table below.)*

### Spec compatibility

| Spec version | Features added |
|---|---|
| `1.0` | Core: manifest, INSTALL.md, CONFIGURE.md, bundle format, `{{config.*}}` substitution |
| `1.1` | Versioning: CHANGELOG.md, installed.json, `## Upgrading` in INSTALL.md, `refresh:` on config keys, `min_a3ip_spec:`, `latest_change:` |
| `1.2` | Security: `trust_level:` on scripts, `permissions:` block, `## Plan` in INSTALL.md, `storage:` on sensitive config keys |
| `1.3` | Terminology: formal component definitions, decision table, platform adapter conventions |
| `1.4` | Validation: nine normative checks every conformant validator must implement |
| `1.5` | Registry: `registry.yaml` format, browsing protocol, install-from-registry, update checks |

---

## Design Principles

*(Unchanged from v1.4, with one addition.)*

1. **Platform agnostic by default.** Components are described at intent level. Platform-specific implementations go in `adapters/<platform>/`.
2. **OS agnostic by default.** Scripts must provide a cross-platform Python implementation. OS-specific alternatives live in `adapters/<os>/scripts/`.
3. **AI-first installation.** The receiving AI reads `INSTALL.md` and performs setup. No human-operated CLI required.
4. **User-configurable.** `CONFIGURE.md` turns installation into a conversation.
5. **Two-variable model.** `{{config.*}}` values are set once at install time. `{{variable}}` values are filled at runtime.
6. **Graceful degradation.** Every dependency declares a fallback. Every artifact ships a markdown fallback.
7. **Delta upgrades, not re-installs.** `CHANGELOG.md` gives the AI a precise, version-scoped upgrade path.
8. **Installation state is local.** `installed.json` lives with the user's config, not in the package.
9. **Composable.** A3IP packages can declare other A3IP packages as dependencies.
10. **Plain text end-to-end.** Every component file is plain text. The `.a3ip.bundle` is a single readable text file.
11. **Superset, not fork.** Any valid SKILL.md skill and any APM-compatible manifest block is valid inside A3IP.
12. **Declare before you act.** Scripts declare their trust level; packages declare their permissions; the AI presents a plan and gets user consent before any side-effecting step runs.
13. **One component, one job.** Each component type has a precise role. Mixing responsibilities makes packages harder to maintain and harder for the receiving AI to reason about.
14. **Validate before you ship.** A package that hasn't passed all nine validation checks is not ready to distribute. Validation is a gate, not a suggestion.
15. **Discoverable by default.** A package without a registry entry can only be installed by direct bundle transfer. Authors should publish to a registry so their packages can be found, updated, and composed into larger ecosystems.

---

*A3IP Specification v1.5*
*Supersedes v1.4. All v1.0, v1.1, v1.2, v1.3, and v1.4 packages remain valid under v1.5.*
*Released: 2026-05-12*
