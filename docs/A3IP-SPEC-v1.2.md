# A3IP Specification v1.2
**AI Infrastructure Installation Package**

> A platform-agnostic format for packaging and sharing complete AI workspace workflows — a superset of the [SKILL.md](https://agentskills.io) open standard and [Microsoft APM](https://microsoft.github.io/apm/).

**What's new in v1.2:** Security and trust model — `trust_level:` on scripts, a `permissions:` block in the manifest, a required `## Plan` section in `INSTALL.md` for elevated-privilege packages, and tightened rules for sensitive configuration. Packages authored under spec v1.0 or v1.1 remain fully valid.

---

## Overview

*(Unchanged from v1.1.)*

An A3IP package bundles everything needed to reproduce a working AI workflow into a single transferable unit: skills, protocols, UI artifacts, prompt templates, and dependency declarations. Any AI agent on any platform can receive an A3IP package and install it into their workspace.

---

## Package Structure

*(Unchanged from v1.1 — see v1.1 spec for directory layout.)*

---

## Bundle Format

*(Unchanged from v1.0.)*

---

## Security Model

A3IP packages run code on the user's machine. Scripts can write files, call external APIs, run shell commands, and modify workspace configuration. Without a declared trust model, a receiving AI has no way to reason about the blast radius of an install before it begins.

The v1.2 security model gives package authors a way to declare what their package needs, and gives installers a structured basis to inform the user and get explicit consent before any side-effecting action is taken.

### Principles

1. **Declare before you act.** Every script must declare its highest privilege level (`trust_level:`). Every external resource must be listed in `permissions:`. The AI reads these before touching anything.
2. **Plan before you install.** For any package with scripts at `write-local` or above, `INSTALL.md` must include a `## Plan` section. The AI presents the plan to the user and waits for confirmation before proceeding.
3. **Secrets stay secret.** Config keys marked `sensitive: true` must never be logged, echoed, bundled, or displayed verbatim. Authors should also declare a `storage:` target so the AI knows the intended secure home for each secret.
4. **Refuse clearly.** If the declared permissions or trust levels exceed what the user is comfortable with, the AI must refuse installation — not silently downgrade or skip steps.

### Trust Levels

`trust_level:` is declared on each script implementation. Values are ordered from least to most privileged:

| Value | What the script does |
|---|---|
| `read-only` | Reads from the workspace, config, or external APIs only. Makes no writes of any kind. |
| `network` | Makes outbound HTTP/API calls. May also read locally. Does not write files. |
| `write-local` | Writes files to the local filesystem. May also read and make network calls. |
| `shell-exec` | Runs arbitrary shell commands. Highest privilege — implies all lower levels. |

**Default:** if `trust_level:` is omitted, the AI must treat the script as `shell-exec` (most conservative assumption).

**What the AI does with trust levels:**
- `read-only` / `network`: install without special confirmation beyond the normal plan.
- `write-local`: require a `## Plan` section in `INSTALL.md`; show plan and confirm before starting.
- `shell-exec`: additionally warn the user that arbitrary shell commands will be executed.

### Permissions Block

The `permissions:` block in `manifest.yaml` declares every external resource the package will touch during install or operation. It is a pre-declaration, not an enforcement mechanism — the AI uses it to inform the user before starting.

```yaml
permissions:
  filesystem:
    - path: "{{config.review_bot_dir}}"
      access: read-write
      reason: "Stores config, scripts, and installed.json."
    - path: "{{config.review_bot_dir}}/logs"
      access: write
      reason: "Script execution logs."

  network:
    - domain: "gitlab.example.com"
      reason: "GitLab REST API — read MRs, post review comments."
    - domain: "login.microsoftonline.com"
      reason: "Microsoft OAuth token endpoint."

  mcp:
    - name: gitlab
      reason: "Required: read merge requests, post review comments."
    - name: teams
      reason: "Optional: post notifications to Teams channels."

  shell:
    - command: python3
      reason: "Runs all Creator scripts."
```

All fields are optional — include only what applies. `path` values may use `{{config.*}}` substitutions. `reason` is required on every entry: it is shown to the user during the install plan confirmation.

**The AI checks `permissions:` before starting install.** If a permission entry references an `{{config.*}}` key that has not been collected yet, the config wizard runs first, then the plan is shown.

### Install Plan

Any package with `min_a3ip_spec: "1.2"` and at least one script at `write-local` or `shell-exec` trust level **must** include a `## Plan` section in `INSTALL.md`.

The plan section enumerates every side-effecting action the AI will take. It is written by the package author and is AI-readable, not auto-generated. The AI presents this section verbatim (or as a summary) to the user before executing any install step.

```markdown
## Plan

Before beginning installation, this package will take the following actions.
Please review and confirm before proceeding.

**Files written:**
- `{{config.review_bot_dir}}/config.json` — stores your configuration
- `{{config.review_bot_dir}}/installed.json` — records installed version
- `{{config.review_bot_dir}}/scripts/` — copies scripts from this bundle

**Network calls:**
- `gitlab.example.com` — verifies your API token
- `login.microsoftonline.com` — obtains a Teams OAuth token (auth step)

**MCP tools used:**
- `gitlab` — reads MR list during install verification

**Shell commands run:**
- `python3 scripts/auth_teams.py` — authenticates with Microsoft Teams

**Confirm to proceed.**
```

The AI must not begin any step in `INSTALL.md` until the user has confirmed the plan. If the user declines, the AI must abort cleanly — no partial state.

### Sensitive Configuration

Config keys with `sensitive: true` carry the following strict rules for the AI installer:

1. **Never log or echo.** The value must not appear in any message shown to the user, in any log file, or in any tool call output.
2. **Never bundle.** `config.json` must never be included in an `.a3ip.bundle` or `.a3ip.zip`. (This is already a v1.0 rule — stated here for completeness.)
3. **Never display verbatim.** When confirming a sensitive value was set, the AI acknowledges receipt only (e.g., "API token saved.") — it does not repeat the value back.
4. **Store in the declared target.** Authors may add a `storage:` hint to guide the AI to the appropriate secure storage.

```yaml
configuration:
  - key: api_token
    label: "GitLab Personal Access Token"
    description: "Used to authenticate API calls."
    type: string
    required: true
    sensitive: true
    storage: keychain          # Preferred: store in OS keychain
    placeholder: "glpat-xxxx"
    when: before

  - key: webhook_url
    label: "Slack Webhook URL"
    description: "Incoming webhook for posting notifications."
    type: string
    required: true
    sensitive: true
    storage: config-file       # Default: stored in config.json (access-controlled by OS)
    when: before
```

**`storage:` values:**

| Value | Meaning |
|---|---|
| `config-file` | Default. Stored in `config.json`. AI ensures the file is not world-readable where possible. |
| `env-var` | Stored as an environment variable. AI writes the value to the platform's env config (e.g., `.env`, `~/.profile`). Key name is the config `key` uppercased. |
| `keychain` | Stored in the OS keychain (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux). AI uses the platform's keychain API or asks the user to store it manually. |

If `storage:` is omitted on a `sensitive: true` key, the AI defaults to `config-file`.

---

## manifest.yaml

Changes from v1.1: `trust_level:` added to script implementations; `permissions:` block added as a top-level section; `min_a3ip_spec: "1.2"` used to signal use of v1.2 features.

```yaml
# ─────────────────────────────────────────
# A3IP Manifest
# ─────────────────────────────────────────

a3ip: "1.2"                          # Spec version. Required.
name: "code-review-flow"
version: "1.2.0"
description: "Complete code review workflow with inbox artifact, GitLab + Jira integration."
author: "Alex Morgan <alex.morgan@example.com>"
license: "MIT"

# ─── Spec compatibility ───────────────────
min_a3ip_spec: "1.2"                 # Set to "1.2" if using trust_level, permissions, or storage:.
                                     # Set to "1.1" for versioning features only.
                                     # Omit (or "1.0") for v1.0-only features.

# ─── Latest change summary ───────────────
latest_change: 2026-05-20            # ISO date of last change.

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
          trust_level: network       # Makes GitLab API call. Reads/writes no local files.
        - file: adapters/windows/scripts/create_mr.ps1
          platform: windows
          trust_level: network

    - key: auth_teams
      description: "Authenticates with Microsoft Teams and saves the access token."
      parameters: []
      implementations:
        - file: scripts/auth_teams.py
          platform: any
          trust_level: write-local   # Writes the token to config.json.

    - key: deploy_hook
      description: "Runs a post-deploy shell hook."
      parameters: [EnvName]
      implementations:
        - file: scripts/deploy_hook.sh
          platform: any
          trust_level: shell-exec    # Runs arbitrary shell commands.

# ─── Permissions ──────────────────────────
permissions:
  filesystem:
    - path: "{{config.review_bot_dir}}"
      access: read-write
      reason: "Stores config, scripts, and installed.json."

  network:
    - domain: "gitlab.example.com"
      reason: "GitLab REST API — read MRs, post review comments."
    - domain: "login.microsoftonline.com"
      reason: "Microsoft OAuth — Teams authentication."

  mcp:
    - name: gitlab
      reason: "Read merge requests, post review comments."

  shell:
    - command: python3
      reason: "Runs all package scripts."
    - command: bash
      reason: "Runs deploy_hook.sh."

# ─── Dependencies ─────────────────────────
dependencies:
  mcp:
    - name: gitlab
      required: true
      purpose: "Read merge requests, post review comments."
      fallback: "Manual: paste MR diff into chat when GitLab MCP is unavailable."

# ─── Configuration schema ─────────────────
configuration:
  - key: api_token
    label: "GitLab Personal Access Token"
    description: "Personal Access Token for authenticating API calls."
    type: string
    required: true
    sensitive: true
    storage: keychain
    placeholder: "glpat-xxxxxxxxxxxx"
    when: before

  - key: review_bot_dir
    label: "Installation Directory"
    description: "Absolute path where the package will store its files."
    type: string
    required: true
    placeholder: "C:\\Users\\you\\.claude\\review_bot"
    when: before

  - key: teams_access_token
    label: "Teams Access Token"
    description: "OAuth access token for posting to Teams. Written by auth_teams script."
    type: string
    required: true
    sensitive: true
    storage: config-file
    when: before
    refresh: on_expiry
    refresh_note: "Tokens expire after ~1 hour of inactivity."
    refresh_script: auth_teams

# ─── Platform compatibility ───────────────
platforms:
  tested:
    - cowork
    - claude-code
    - codex
```

---

## INSTALL.md

Changes from v1.1: packages using `min_a3ip_spec: "1.2"` with any `write-local` or `shell-exec` scripts must include a `## Plan` section. The `## Plan` section must appear **before** the first numbered install step so the AI presents it and waits for confirmation first.

```markdown
---
format: a3ip-install
spec: "1.2"
package: code-review-flow
---

# Installation Guide: Code Review Flow

## 1. Check for Existing Installation

Check whether `installed.json` exists in `{{config.review_bot_dir}}`.
- **Not found:** proceed with the full install steps below.
- **Found:** go directly to [## Upgrading](#upgrading).

## Plan

Before beginning installation, this package will take the following actions.
Please confirm before proceeding.

**Files written:**
- `{{config.review_bot_dir}}/config.json` — your configuration
- `{{config.review_bot_dir}}/installed.json` — installed version record
- `{{config.review_bot_dir}}/scripts/` — package scripts

**Network calls:**
- `gitlab.example.com` — verifies your API token during setup
- `login.microsoftonline.com` — Teams OAuth (auth step only)

**MCP tools used:**
- `gitlab` MCP — reads MR list during install verification

**Shell commands run:**
- `python3 scripts/auth_teams.py` — authenticates with Microsoft Teams

**Confirm to proceed.**

## 2. Dependency Check

[... install steps continue after confirmation ...]

## Upgrading

[... same as v1.1 ...]
```

### Plan section rules

- Must appear after `## 1. Check for Existing Installation` and before `## 2.` (or the first numbered action step).
- Must list every file written, every network domain contacted, every MCP tool invoked, and every shell command run — even if they are also listed in `permissions:`.
- Must end with **Confirm to proceed.** (or equivalent) so the AI knows to pause.
- The AI must not skip or summarize the Plan section — it must be shown in full (or as a structured summary of the same content).
- If the user declines, the AI aborts. No partial install state is written.

---

## CONFIGURE.md, CHANGELOG.md, installed.json

*(Unchanged from v1.1.)*

---

## Component Formats

*(Unchanged from v1.0.)*

---

## Versioning

*(Unchanged from v1.1. The spec compatibility table below is updated.)*

### Spec compatibility

| Spec version | Features added |
|---|---|
| `1.0` | Core: manifest, INSTALL.md, CONFIGURE.md, bundle format, `{{config.*}}` substitution |
| `1.1` | Versioning: CHANGELOG.md, installed.json, `## Upgrading` in INSTALL.md, `refresh:` on config keys, `min_a3ip_spec:`, `latest_change:` in manifest |
| `1.2` | Security: `trust_level:` on scripts, `permissions:` block in manifest, `## Plan` section in INSTALL.md, `storage:` on sensitive config keys |

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
| Script trust levels | ❌ | ❌ | ✅ `trust_level:` on implementations |
| Pre-install permission declaration | ❌ | ❌ | ✅ `permissions:` block |
| Sensitive config storage hints | ❌ | ❌ | ✅ `storage:` on config keys |
| Knowledge-worker platforms | ❌ | ❌ | ✅ Explicit design goal |
| CLI / developer platforms | ✅ | ✅ | ✅ |

---

## Design Principles

1. **Platform agnostic by default.** Components are described at intent level. Platform-specific implementations go in `adapters/<platform>/`.
2. **OS agnostic by default.** Scripts must provide a cross-platform Python implementation. OS-specific alternatives live in `adapters/<os>/scripts/`.
3. **AI-first installation.** The receiving AI reads `INSTALL.md` and performs setup. No human-operated CLI required.
4. **User-configurable.** `CONFIGURE.md` turns installation into a conversation.
5. **Two-variable model.** `{{config.*}}` values are set once at install time. `{{variable}}` values are filled at runtime.
6. **Graceful degradation.** Every dependency declares a fallback.
7. **Delta upgrades, not re-installs.** `CHANGELOG.md` gives the AI a precise, version-scoped upgrade path.
8. **Installation state is local.** `installed.json` lives with the user's config, not in the package.
9. **Composable.** A3IP packages can declare other A3IP packages as dependencies.
10. **Plain text end-to-end.** Every component file is plain text. The `.a3ip.bundle` is a single readable text file.
11. **Superset, not fork.** Any valid SKILL.md skill and any APM-compatible manifest block is valid inside A3IP.
12. **Declare before you act.** Scripts declare their trust level; packages declare their permissions; the AI presents a plan and gets user consent before any side-effecting step runs.

---

*A3IP Specification v1.2*
*Supersedes v1.1. All v1.0 and v1.1 packages remain valid under v1.2.*
*Released: 2026-05-12*
