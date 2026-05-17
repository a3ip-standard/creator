# A3IP Specification v1.1
**AI Infrastructure Installation Package**

> A platform-agnostic format for packaging and sharing complete AI workspace workflows — a superset of the [SKILL.md](https://agentskills.io) open standard and [Microsoft APM](https://microsoft.github.io/apm/).

**What's new in v1.1:** Package versioning and delta upgrades — `CHANGELOG.md`, `installed.json`, the `## Upgrading` section in `INSTALL.md`, `refresh:` on config fields, and a formal breaking-change taxonomy. Packages authored under spec v1.0 remain fully valid.

---

## Overview

An A3IP package bundles everything needed to reproduce a working AI workflow into a single transferable unit: skills, protocols, UI artifacts, prompt templates, and dependency declarations. Any AI agent on any platform can receive an A3IP package and install it into their workspace.

A3IP extends the existing ecosystem rather than replacing it:

| Layer | Existing standard adopted | A3IP addition |
|---|---|---|
| Skills | SKILL.md (Anthropic open standard) | — |
| Dependencies | APM `apm.yml` model | Artifact + protocol component types |
| Tooling | APM CLI compatible | AI-readable `INSTALL.md` |
| Configuration | — | Installation wizard via `CONFIGURE.md` |
| Versioning | — | `CHANGELOG.md` + `installed.json` delta upgrades |
| Audience | Developer / coding agents | + Knowledge worker / non-developer workspaces |

---

## Package Structure

An A3IP package exists in one of three distribution forms:

| Form | Extension | When to use |
|---|---|---|
| **Directory** | `my-workflow.a3ip/` | Local development and editing |
| **Zip archive** | `my-workflow.a3ip.zip` | Human-to-human file transfer (email, cloud drive) |
| **Bundle** | `my-workflow.a3ip.bundle` | AI-to-AI transfer — a single plain-text file any AI can read directly |

The bundle format is the **primary AI consumption format**. See [Bundle Format](#bundle-format) for details.

The directory layout is:

```
my-workflow.a3ip/
├── manifest.yaml          # Required. Package metadata and dependency declarations.
├── INSTALL.md             # Required. AI-readable installation guide.
├── CONFIGURE.md           # Required if config exists. AI-readable wizard definition.
├── CHANGELOG.md           # Required if version > 1.0.0. AI-readable upgrade history.
├── README.md              # Recommended. Human-readable overview.
│
├── components/
│   ├── skills/
│   │   └── <skill-name>/
│   │       └── SKILL.md
│   ├── artifacts/
│   │   └── <artifact-name>/
│   │       ├── artifact.md
│   │       └── artifact.html
│   ├── protocols/
│   │   └── <protocol-name>.md
│   └── prompts/
│       └── <prompt-name>.md
│
└── adapters/
    ├── windows/
    │   └── scripts/
    ├── macos-linux/
    │   └── scripts/
    ├── claude/
    ├── codex/
    └── generic/
```

`CHANGELOG.md` is required once a package has been publicly distributed and then updated (i.e., any version after the initial release). It is optional for packages that have never left the author's machine.

---

## Bundle Format

*(Unchanged from v1.0 — see original spec for full details.)*

A `.a3ip.bundle` file embeds every package file with `=== FILE: <path> ===` / `=== END FILE ===` delimiters. It requires no special tooling — an AI reads it directly.

Frontmatter:
```
---
a3ip-bundle: "1.1"
package: <name>
version: <semver>
generated: <ISO-8601 timestamp>
files: <total file count>
---
```

---

## manifest.yaml

The manifest is the single source of truth for the package.

```yaml
# ─────────────────────────────────────────
# A3IP Manifest
# ─────────────────────────────────────────

a3ip: "1.1"                          # Spec version. Required. Use "1.0" for v1.0-only features.
name: "code-review-flow"
version: "1.2.0"                     # SemVer. Required. Bump on every distributed change.
description: "Complete code review workflow with inbox artifact, GitLab + Jira integration."
author: "Alex Morgan <alex.morgan@example.com>"
license: "MIT"
homepage: "https://..."

# ─── Spec compatibility ───────────────────
min_a3ip_spec: "1.1"                 # Minimum A3IP spec version required to install this package.
                                     # Omit for v1.0-only features. Set "1.1" to use CHANGELOG.md.

# ─── Latest change summary ───────────────
# One-line summary of the most recent version — lets the AI give a quick changelog preview
# without reading the full CHANGELOG.md. Update whenever version is bumped.
latest_change:
  version: "1.2.0"
  date: "2026-05-20"
  summary: "Added post-review recheck step; fixed Review Inbox Check Teams button."
  breaking: false                    # true = major version bump, config or MCP changes required

# ─── Components ───────────────────────────
components:
  skills:
    - path: components/skills/code-review
      description: "Guides the AI through the code review protocol step by step."

  artifacts:
    - path: components/artifacts/review-inbox
      description: "Persistent inbox view showing all open review requests."

  protocols:
    - path: components/protocols/move-to-review.md
      description: "The 'move to code review' command — initiates the review flow."

  prompts:
    - path: components/prompts/review-summary.md
      description: "Template for generating a review summary comment."

  scripts:
    - key: create_mr
      description: "Creates a GitLab MR via REST API and returns its URL."
      parameters: [ProjectPath, SourceBranch, TargetBranch, Title]
      implementations:
        - file: scripts/create_mr.py
          platform: any
        - file: adapters/windows/scripts/create_mr.ps1
          platform: windows

# ─── Dependencies ─────────────────────────
dependencies:
  mcp:
    - name: gitlab
      required: true
      purpose: "Read merge requests, post review comments."
      registry: "mcp-registry/gitlab"
      fallback: "Manual: paste MR diff into chat when GitLab MCP is unavailable."

  skills:
    - name: "git-basics"
      source: "skills.sh/git-basics@^2.0"
      required: false

# ─── Configuration schema ─────────────────
configuration:
  - key: api_token
    label: "Service API Token"
    description: "Personal Access Token for authenticating API calls."
    type: string
    required: true
    sensitive: true
    placeholder: "token-xxxxxxxxxxxx"
    when: before

  - key: sprint_start_date
    label: "Current Sprint Start Date"
    description: "ISO date of the current sprint start. Used as poll cutoff."
    type: string
    required: true
    placeholder: "2026-05-01"
    when: before
    refresh: periodic                  # This value goes stale and must be updated periodically.
    refresh_note: "Update at the start of each sprint."
                                       # No refresh_script — user updates this manually.

  - key: teams_access_token
    label: "Teams Access Token"
    description: "OAuth access token for posting to Teams. Written by auth_teams script."
    type: string
    required: true
    sensitive: true
    when: before
    refresh: on_expiry                 # Refresh when the token expires.
    refresh_note: "Tokens expire after ~1 hour of inactivity."
    refresh_script: auth_teams         # Script key to run to obtain a fresh token.

# ─── Platform compatibility ───────────────
platforms:
  tested:
    - cowork
    - claude-code
    - codex
```

### `refresh:` field on configuration keys

Some config values go stale without any package version change. The `refresh:` field signals this to the AI.

| Value | Meaning |
|---|---|
| `never` | Default. Set once at install, never needs updating. |
| `periodic` | Needs manual update on a recurring basis (e.g. sprint start date). The AI should remind the user when running protocols if the value looks stale. |
| `on_expiry` | Tied to a token or credential that expires. Pair with `refresh_script:` to automate renewal. |

`refresh_script:` names a script `key` in `components.scripts`. The AI runs it to obtain a fresh value and writes it back to `config.json`. This is how OAuth token renewal works: the auth script fetches a new token and overwrites the old one.

`refresh_note:` is a human-readable string the AI surfaces to the user when the value should be refreshed.

---

## CONFIGURE.md

*(Unchanged from v1.0.)*

`CONFIGURE.md` defines the installation wizard. It instructs the AI on how to collect configuration values from the user. See v1.0 spec for full details.

---

## INSTALL.md

`INSTALL.md` is written for an AI agent. It is the key innovation of A3IP. It provides the receiving AI with enough context to adapt and install the package on whatever platform it runs on.

### New in v1.1: `## Upgrading` section

Every `INSTALL.md` in a v1.1 package must include an `## Upgrading` section at the end. The AI checks for `installed.json` at the start of installation. If found, it goes directly to this section instead of running the full install steps.

```markdown
---
format: a3ip-install
spec: "1.1"
package: code-review-flow
---

# Installation Guide: Code Review Flow

## 1. Check for Existing Installation

Before proceeding, check whether this package is already installed:
Look for `installed.json` in the expected config directory
(typically `{{config.review_bot_dir}}/installed.json` or the platform's skills directory).

- **If `installed.json` is not found:** proceed with the full install steps below.
- **If `installed.json` is found:** go directly to [## Upgrading](#upgrading) at the end
  of this document. Do not re-run the full install.

## 2. Dependency Check

[... full install steps as before ...]

## N. Write installed.json

After completing all installation steps, write `installed.json` to the config directory:

{
  "package": "<name>",
  "version": "<version from manifest>",
  "installed_at": "<ISO-8601 timestamp>",
  "platform": "<platform name>",
  "a3ip_spec": "1.1",
  "config_dir": "<absolute path to config directory>"
}

This file is the record of the installed version. Do not delete it.

---

## Upgrading

When an `installed.json` is found, follow these steps instead of the full install:

### Step U1 — Read installed version

Read `installed.json`. Note the `version` field (e.g. "1.0.0").

### Step U2 — Read CHANGELOG.md

Open `CHANGELOG.md` from this bundle. Find all version entries newer than the installed version.
Apply them **in order from oldest to newest**.

For each version entry:
1. Check `### Breaking changes` — if any, tell the user before proceeding.
2. Check `### Config changes` — if new required keys, run the config wizard for those keys only.
3. Follow `### Upgrade steps` exactly.

### Step U3 — Update installed.json

After all upgrade steps complete, overwrite `installed.json` with the new version.

### Step U4 — Confirm

Tell the user:
- Upgraded from: <old version>
- Upgraded to: <new version>
- Changes applied: <summary from CHANGELOG.md>
- Config changes: <if any>
```

---

## CHANGELOG.md

`CHANGELOG.md` is the per-version upgrade guide. It is written by the package author each time a new version is released. The AI reads it during upgrades to determine exactly what changed and what steps to execute.

### Format

```markdown
---
format: a3ip-changelog
spec: "1.1"
package: <name>
---

# Changelog: <name>

All notable changes to this package are documented here.
Newest version first.

---

## [1.2.0] — 2026-05-20

### Breaking changes
None.

### Config changes
None.

### Files changed
- `components/artifacts/review-inbox/artifact.html` — replaced
- `components/protocols/check-review-requests.md` — replaced

### New dependencies
None.

### Upgrade steps (from 1.1.x)

1. Replace the Review Inbox artifact:
   - If your platform supports HTML artifacts: update the artifact with the new `artifact.html`.
   - If using the markdown fallback: no change needed.

2. Update the `check-review-requests` protocol:
   - Re-register the protocol from the updated file.
   - Trigger phrase is unchanged: "check review requests".

3. No config changes required. Your existing `config.json` remains valid.

### What changed (human summary)

The "Check Teams" button in the Review Inbox now triggers the actual scheduled poll.
A new post-review recheck step was added to the check-review-requests protocol.

---

## [1.1.0] — 2026-05-15

### Breaking changes
None.

### Config changes
- **Added** `teams_skip_author` (optional, default: "") — name to skip during Teams poll.
  The AI will ask the user for this value. Existing installations without it will work
  — the default is to skip nobody.

### Files changed
- `scripts/poll_teams.py` — replaced
- `adapters/windows/scripts/poll_teams.ps1` — replaced
- `CONFIGURE.md` — updated (new question for teams_skip_author)
- `manifest.yaml` — updated (new config key)

### New dependencies
None.

### Upgrade steps (from 1.0.x)

1. Ask the user for the new config value:
   > "There's a new optional setting: which person's Teams messages should I skip
   > during the review poll? This is usually yourself, to avoid generating reviews
   > for your own requests. Leave blank to skip nobody."
   - Key: `teams_skip_author` (string, optional)
   - Write to `config.json` as: `"teams_skip_author": "<value or empty string>"`

2. Replace `poll_teams.py` (and `.ps1` on Windows) with the versions from this bundle.

### What changed (human summary)

Added the ability to skip a specific author's messages during the Teams poll.
This prevents generating reviews for your own review requests.

---

## [1.0.0] — 2026-05-11

Initial release.
```

### Rules

- **Newest version first.** The AI reads from top to bottom but applies in chronological order.
- **Every `## [version]` section is self-contained.** The upgrade steps assume the reader is on the previous version. For larger jumps (e.g. 1.0.0 → 1.2.0), the AI applies 1.0→1.1 steps first, then 1.1→1.2 steps.
- **`### Breaking changes`** must be explicit. Never leave it implicit. If `None`, say `None`.
- **`### Config changes`** lists every key that was added, removed, or renamed. Removed or renamed keys are always breaking.
- **`### Files changed`** is the machine-readable list. Format: `path — action` where action is one of: `replaced`, `added`, `deleted`.
- **`### Upgrade steps`** are AI instructions — written the same way as INSTALL.md steps.
- **`### What changed`** is the human-readable summary — can be copy-pasted into a release note or shared with users.

### Breaking change taxonomy

A change is **breaking** (requires a major version bump and must be listed under `### Breaking changes`) if it requires any of the following from an existing user:

| Change | Breaking? | Why |
|---|---|---|
| New required config key (no default) | ✅ Yes | Existing config.json is incomplete |
| Config key removed or renamed | ✅ Yes | Scripts/protocols that read it will fail |
| Config type changed | ✅ Yes | Stored value may be incompatible |
| New required MCP dependency | ✅ Yes | Workflow will fail without it |
| Script interface changed (new required param) | ✅ Yes | Callers must be updated |
| New optional config key (has default) | ❌ No | Existing config.json still works |
| New optional MCP dependency | ❌ No | Graceful degradation applies |
| Script file replaced (same interface) | ❌ No | Drop-in replacement |
| Artifact HTML updated | ❌ No | Drop-in replacement |
| Protocol steps changed | ❌ No | AI re-registers updated protocol |
| INSTALL.md steps changed | ❌ No | Informational only |
| New script added | ❌ No | Additive |
| Bug fix with no interface change | ❌ No | Safe to apply |

---

## installed.json

`installed.json` is written by the AI to the package's config directory immediately after a successful installation or upgrade. It is the machine-readable record of what version is installed and where.

### Schema

```json
{
  "package": "acme-code-review-flow",
  "version": "1.1.0",
  "installed_at": "2026-05-15T14:32:00Z",
  "upgraded_from": "1.0.0",
  "platform": "cowork",
  "a3ip_spec": "1.1",
  "config_dir": "C:\\Users\\maksi\\.claude\\review_bot"
}
```

| Field | Required | Description |
|---|---|---|
| `package` | Yes | Package name from manifest |
| `version` | Yes | Installed version (semver) |
| `installed_at` | Yes | ISO-8601 timestamp of install/upgrade |
| `upgraded_from` | No | Previous version, if this was an upgrade |
| `platform` | Yes | AI platform name (cowork, claude-code, codex, etc.) |
| `a3ip_spec` | Yes | A3IP spec version used for this install |
| `config_dir` | Yes | Absolute path to the directory where config.json and scripts live |

### Location

`installed.json` lives in the **same directory as `config.json`** — i.e., the `review_bot_dir` or equivalent config directory for the package. It does not live inside the package directory itself.

This keeps the package directory (or bundle) a pure distributable artifact, while installation state lives with the user's config.

### Notes

- Do not include `installed.json` in the `.a3ip.bundle` or `.a3ip.zip`.
- If the user re-installs from scratch (not upgrading), overwrite `installed.json`.
- If installation fails partway through, do not write or update `installed.json` — a partial install should look like no install.

---

## Component Formats

*(Unchanged from v1.0 — Skill, Artifact, Protocol, Prompt Template formats are identical.)*

---

## Versioning

A3IP packages follow [SemVer](https://semver.org):

- **Major** (`2.0.0`): breaking changes — see Breaking change taxonomy above. Requires user to re-run config wizard for affected keys, or re-install from scratch.
- **Minor** (`1.1.0`): new features, new optional config keys, new optional dependencies. Existing installations upgrade cleanly.
- **Patch** (`1.0.1`): bug fixes, script replacements with no interface change, artifact updates, documentation clarifications.

The A3IP spec itself follows SemVer independently of package versions:
- **Major spec bump** (`2.0`): incompatible changes to manifest or INSTALL.md format.
- **Minor spec bump** (`1.1`): new fields and file types (backward compatible). v1.0 packages remain valid.

### Spec compatibility

Packages declare `min_a3ip_spec:` in their manifest to signal which spec features they rely on. An AI that only knows spec v1.0 should refuse to install a package requiring v1.1 and ask the user to use an updated AI.

| Spec version | Features added |
|---|---|
| `1.0` | Core: manifest, INSTALL.md, CONFIGURE.md, bundle format, `{{config.*}}` substitution |
| `1.1` | Versioning: CHANGELOG.md, installed.json, `## Upgrading` in INSTALL.md, `refresh:` on config keys, `min_a3ip_spec:`, `latest_change:` in manifest |

---

## Relationship to Existing Standards

| Concept | SKILL.md | APM | A3IP |
|---|---|---|---|
| Portable skills | ✅ Core format | ✅ Supports | ✅ Adopts SKILL.md exactly |
| Dependency declarations | ❌ | ✅ apm.yml | ✅ Extends APM model |
| MCP server configs | ❌ | ✅ | ✅ Inherited from APM |
| UI Artifacts | ❌ | ❌ | ✅ First-class component |
| Named protocols / commands | ❌ | ❌ | ✅ First-class component |
| AI-readable install guide | ❌ | ❌ | ✅ INSTALL.md |
| Installation wizard | ❌ | ❌ | ✅ CONFIGURE.md with typed schema |
| User config substitution | ❌ | ❌ | ✅ `{{config.*}}` syntax |
| Delta upgrades | ❌ | ❌ | ✅ CHANGELOG.md + installed.json |
| Stale config refresh | ❌ | ❌ | ✅ `refresh:` on config keys |
| Knowledge-worker platforms | ❌ | ❌ | ✅ Explicit design goal |
| CLI / developer platforms | ✅ | ✅ | ✅ |

---

## Design Principles

1. **Platform agnostic by default.** Components are described at intent level. Platform-specific implementations go in `adapters/<platform>/`.
2. **OS agnostic by default.** Scripts must provide a cross-platform Python implementation as the primary. OS-specific alternatives live in `adapters/<os>/scripts/`.
3. **AI-first installation.** The receiving AI reads `INSTALL.md` and performs setup. No human-operated CLI required.
4. **User-configurable.** `CONFIGURE.md` turns installation into a conversation.
5. **Two-variable model.** `{{config.*}}` values are set once at install time. `{{variable}}` values are filled at runtime each time a protocol runs.
6. **Graceful degradation.** Every dependency declares a fallback.
7. **Delta upgrades, not re-installs.** `CHANGELOG.md` gives the AI a precise, version-scoped upgrade path. Installing a new bundle does not mean wiping and redoing everything.
8. **Installation state is local.** `installed.json` lives with the user's config, not in the package. The package is a pure distributable — it carries no knowledge of where it's been installed.
9. **Composable.** A3IP packages can declare other A3IP packages as dependencies.
10. **Plain text end-to-end.** Every component file is plain text. The `.a3ip.bundle` format embeds the entire package as a single readable text file.
11. **Superset, not fork.** Any valid SKILL.md skill and any APM-compatible manifest block is valid inside A3IP.

---

*A3IP Specification v1.1*
*Supersedes v1.0. All v1.0 packages remain valid under v1.1.*
*Released: