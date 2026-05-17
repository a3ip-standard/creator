# A3IP Specification v1.8

*Note: v1.8 is a superset of v1.7 for package authors — all v1.7 packages are valid v1.8. Changes: (a) `INSTALL.md` template language decoupled from any specific tool; (b) `installed.json` schema formalized with new optional fields; (c) `adapters/runtime/codex/` convention added alongside `cowork`, `claude-code`, `cursor`, `generic`. v1.8 also removes implementation-specific content that was previously included in error: the cross-product tool-selection table (which named specific Cowork tools by name) has been relocated from the spec to a separate `TOOL-AUTHORS.md` document in the spec repository. The spec describes package format, not tool implementations.*

## What's new in v1.8

v1.8 is a documentation + schema clarification release. No structural changes to manifests, bundles, or validation rules. Backward compatibility with v1.7 is preserved for package authors.

**(a) `INSTALL.md` template is tool-agnostic.** Earlier spec text referenced specific CLI commands by name in examples. v1.8 rewrites references to describe the *capability* required ("validate the package against the spec's 10 normative checks") without naming an implementation. The `a3ip` CLI remains the reference implementation, but the spec no longer anoints it as canonical — other validators and bundlers can claim spec compliance. Analogy: the HTML spec describes parsing rules, not Chrome.

**(b) `installed.json` schema formalized.** Earlier specs defined `package`, `version`, `installed_at`, `platform`, `a3ip_spec`, `config_dir`. v1.8 documents additional optional fields that emerged in real-world install adapters: `upgraded_from`, `install_method`, `registry_source`, `source_bundle`, `workspace_dir`, `backup_dir`. All optional. Readers MUST parse leniently (unknown fields are not errors), enabling future spec versions to extend the schema without breaking compatibility.

**(c) `adapters/runtime/codex/` recognized as a runtime adapter location.** v1.7 listed `cowork`, `claude-code`, `cursor`, and `generic` runtime adapters. v1.8 adds `codex`. Packages targeting Codex SHOULD ship `adapters/runtime/codex/install-skill.md` if their install flow differs meaningfully from the generic-copy path; MAY omit if generic-copy in INSTALL.md suffices.

**Removed from the spec (relocated to `TOOL-AUTHORS.md`):** the cross-product "tool selection" table that previously appeared in Platform Conventions was an implementation detail that should never have been in the spec — it named specific Cowork tools (`mcp__filesystem__read_file`) and prescribed exact handling of `~` expansion across runtimes. That content has been moved to a separate `TOOL-AUTHORS.md` document in the spec repo as non-normative implementation guidance for tool authors. The spec proper now only describes *what* (package format, manifest schema, adapter directory structure); the *how* (which tools to use, how to handle encoding edge cases) lives outside the spec.

---

## Table of Contents

1. [Overview](#overview)
2. [Package Structure](#package-structure)
3. [Bundle Format](#bundle-format)
4. [Security Model](#security-model)
5. [Terminology](#terminology)
6. [Component Decision Table](#component-decision-table)
7. [Platform Conventions](#platform-conventions)
8. [Validation](#validation)
9. [Registry](#registry)
10. [manifest.yaml](#manifestyaml)
11. [CONFIGURE.md](#configuremd)
12. [INSTALL.md](#installmd)
13. [CHANGELOG.md](#changelogmd)
14. [installed.json](#installedjson)
15. [Component Formats](#component-formats)
16. [Versioning](#versioning)
17. [Design Principles](#design-principles)
18. [Relationship to Existing Standards](#relationship-to-existing-standards)
19. [Spec Version History](#spec-version-history)

---

## Overview

An A3IP package bundles everything needed to reproduce a working AI workflow into a single transferable unit: skills, protocols, UI artifacts, prompt templates, dependency declarations, and security declarations. Any AI agent on any platform can receive an A3IP package and install it into their workspace.

A3IP extends the existing ecosystem rather than replacing it:

| Layer | Existing standard adopted | A3IP addition |
|---|---|---|
| Skills | SKILL.md (Anthropic open standard) | — |
| Dependencies | APM `apm.yml` model | Artifact + protocol component types |
| Tooling | APM CLI compatible | AI-readable `INSTALL.md` |
| Configuration | — | Installation wizard via `CONFIGURE.md` |
| Versioning | — | `CHANGELOG.md` + `installed.json` delta upgrades |
| Security | — | `permissions:` block, `trust_level:`, install plan confirmation |
| Discovery | — | `registry.yaml` format + install-from-registry protocol |
| Audience | Developer / coding agents | + Knowledge worker / non-developer workspaces |

---

## Package Structure

An A3IP package exists in one of three distribution forms:

| Form | Extension | When to use |
|---|---|---|
| **Directory** | `my-workflow.a3ip/` | Local development and editing |
| **Zip archive** | `my-workflow.a3ip.zip` | Human-to-human file transfer (email, cloud drive) |
| **Bundle** | `my-workflow.a3ip.bundle` | AI-to-AI transfer — a single plain-text file any AI can read directly |

The bundle format is the **primary AI consumption format**. It embeds all package files inline with text delimiters, requiring no shell access, no unzip, and no filesystem writes. See [Bundle Format](#bundle-format) for details.

All three forms contain the same content and are interchangeable.

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
│   ├── skills/            # SKILL.md-compatible skill folders (one per skill)
│   │   └── <skill-name>/
│   │       └── SKILL.md
│   │
│   ├── artifacts/         # UI artifacts — persistent views the AI manages
│   │   └── <artifact-name>/
│   │       ├── artifact.md    # Required: artifact metadata and description
│   │       └── artifact.html  # Optional: HTML implementation
│   │
│   ├── protocols/         # Named command/workflow definitions
│   │   └── <protocol-name>.md
│   │
│   └── prompts/           # Reusable prompt templates
│       └── <prompt-name>.md
│
├── scripts/               # Cross-platform Python scripts (primary implementations)
│   └── <script-key>.py
│
└── adapters/              # Optional. OS and runtime-specific overrides.
    ├── os/                # Host operating system axis
    │   ├── windows/       # Windows: path conventions, tool selection, PS1 scripts
    │   │   ├── file-ops.md     # (v1.7+) Tool-selection guidance for filesystem ops
    │   │   └── scripts/        # PowerShell alternatives to scripts/<key>.py
    │   └── posix/         # macOS / Linux: expanduser conventions, $HOME usage
    │       ├── file-ops.md
    │       └── scripts/
    └── runtime/           # AI runtime axis (Cowork, Claude Code, Codex, etc.)
        ├── cowork/        # .skill UI flow, mcp__cowork__* tools, present_files
        │   ├── install-skill.md   # Cowork install adapter (replaces old adapters/claude/)
        │   └── SKILL.md           # Combined Cowork-loadable skill
        ├── claude-code/   # Direct file-copy to ~/.claude/skills/
        ├── codex/         # ~/.codex/skills/<name>/, code-exec sandbox, no UI flow
        │   └── install-skill.md   # Codex install adapter (file-copy + system instructions)
        ├── cursor/        # Editor-integrated
        └── generic/       # Generic fallback

Legacy flat layout (v1.6 and earlier) — DEPRECATED but still valid:

    ├── windows/           # OS-axis without `os/` parent
    ├── macos-linux/
    ├── claude/            # Runtime-axis without `runtime/` parent (renamed to cowork in v1.7)
    ├── codex/
    └── generic/
```

`CHANGELOG.md` is required once a package has been publicly distributed and then updated (any version after the initial `1.0.0` release).

---

## Bundle Format

A `.a3ip.bundle` file is a single plain-text document that embeds every file in the package using a simple delimiter syntax. It requires no special tooling — an AI reads it directly, extracts each embedded file's path and content, and installs from that in-memory representation.

### Why bundles exist

Zip archives are binary. An AI on a web interface, a mobile device, or a sandboxed environment cannot unzip a file without shell access. A bundle solves this: the user pastes it into chat or attaches it as a text file, and the receiving AI has the full package.

### Delimiter syntax

```
---
a3ip-bundle: "1.0"
package: <name>
version: <semver>
generated: <ISO-8601 timestamp>
files: <total file count>
spec_url: <URL to the A3IP spec version this package requires>
---

=== FILE: <relative/path/to/file> ===
<raw file content — preserves all whitespace and newlines exactly>
=== END FILE ===

=== FILE: <next/file> ===
...
=== END FILE ===
```

Rules:
- The opening frontmatter is mandatory and must come first.
- Each `=== FILE: <path> ===` line marks the start of an embedded file. The path is relative to the package root.
- Each `=== END FILE ===` line marks the end. Content between these delimiters is taken verbatim — no escaping.
- Files are embedded in any order; the receiver reconstructs the directory tree from paths.
- Binary files should be Base64-encoded with `# encoding: base64` on the line immediately after the `FILE:` marker.
- `config.json` and `installed.json` must never be included in a bundle.

### spec_url field

The `spec_url:` frontmatter field points a cold-start AI to the canonical published
spec for this bundle's required spec version. It is constructed from `min_a3ip_spec:`
in the package manifest:

```
spec_url: https://raw.githubusercontent.com/a3ip-standard/spec/main/docs/A3IP-SPEC-v{min_a3ip_spec}.md
```

**Behavior for the receiving AI:**
- If familiar with A3IP: ignore `spec_url:` and proceed normally.
- If unfamiliar with A3IP: fetch the spec from `spec_url:`, read it, then follow
  `INSTALL.md` to install the package.

**Distribution modes:**

| Mode | When to use | How |
|---|---|---|
| **Standard** | Default — spec is publicly available | Include `spec_url:` in frontmatter. No spec file embedded. |
| **Offline** | Airgapped or no internet access | Embed spec as a `FILE` block using `--spec`. Also include `spec_url:` for reference. |

If both `spec_url:` and an embedded spec file are present, the receiving AI should
prefer `spec_url:` — the live version is more current than a snapshot embedded at
bundle time.

`bundle.py` always emits `spec_url:` automatically. The `--spec` flag is retained
for offline/airgapped scenarios only.

### Generating a bundle

```
For each file in the package (recursively, sorted by path):
  Write: === FILE: <relative path> ===
  Write: <file contents verbatim>
  Write: === END FILE ===
```

### Consuming a bundle

When an AI receives a `.a3ip.bundle` file or its contents:

1. Parse the frontmatter to identify the package name and version.
2. Split on `=== FILE:` / `=== END FILE ===` delimiters to extract each embedded file.
3. Hold the files as an in-memory map of `{ path → content }`.
4. Follow `INSTALL.md` exactly as if the files were on disk.
5. Write files to disk only when installation explicitly requires it.

---

## Security Model

A3IP packages run code on the user's machine. Scripts can write files, call external APIs, run shell commands, and modify workspace configuration. The v1.2 security model gives package authors a way to declare what their package needs, and gives installers a structured basis to inform the user and get explicit consent before any side-effecting action is taken.

### Principles

1. **Declare before you act.** Every script must declare its highest privilege level (`trust_level:`). Every external resource must be listed in `permissions:`. The AI reads these before touching anything.
2. **Plan before you install.** For any package with scripts at `write-local` or above, `INSTALL.md` must include a `## Plan` section. The AI presents the plan to the user and waits for confirmation before proceeding.
3. **Secrets stay secret.** Config keys marked `sensitive: true` must never be logged, echoed, bundled, or displayed verbatim.
4. **Refuse clearly.** If the declared permissions or trust levels exceed what the user is comfortable with, the AI must refuse installation — not silently downgrade or skip steps.

### Trust Levels

`trust_level:` is declared on each script implementation:

| Value | What the script does |
|---|---|
| `read-only` | Reads from the workspace, config, or external APIs only. Makes no writes of any kind. |
| `network` | Makes outbound HTTP/API calls. May also read locally. Does not write files. |
| `write-local` | Writes files to the local filesystem. May also read and make network calls. |
| `shell-exec` | Runs arbitrary shell commands. Highest privilege — implies all lower levels. |

**Default:** if `trust_level:` is omitted, the AI must treat the script as `shell-exec` (most conservative assumption).

### Permissions Block

The `permissions:` block in `manifest.yaml` declares every external resource the package will touch during install or operation. It is presented to the user before any action begins.

```yaml
permissions:
  filesystem:
    - path: "{{config.install_dir}}"
      access: read-write
      reason: "Stores config, scripts, and installed.json."

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
      reason: "Runs all package scripts."
```

All fields are optional — include only what applies. `reason` is required on every entry.

### Sensitive Configuration

Config keys with `sensitive: true` carry strict rules for the AI installer:

1. **Never log or echo.** The value must not appear in any message shown to the user, in any log file, or in any tool call output.
2. **Never bundle.** `config.json` must never be included in an `.a3ip.bundle`.
3. **Never display verbatim.** When confirming a sensitive value was set, acknowledge receipt only — e.g., "API token saved."
4. **Store in the declared target.** Use the `storage:` hint to guide the AI to appropriate secure storage.

```yaml
configuration:
  - key: api_token
    label: "GitLab Personal Access Token"
    type: string
    required: true
    sensitive: true
    storage: keychain
    placeholder: "glpat-xxxx"
    when: before
```

**`storage:` values:**

| Value | Meaning |
|---|---|
| `config-file` | Default. Stored in `config.json`. |
| `env-var` | Stored as an environment variable. |
| `keychain` | Stored in the OS keychain (macOS Keychain, Windows Credential Manager, Linux Secret Service). |

---

## Terminology

Every A3IP package is built from five component types. This section defines each one precisely.

### Skill

**A persistent instruction set that changes how the AI behaves in all subsequent interactions.**

A Skill is loaded into the AI's context and remains active for the duration of a session (or permanently, depending on the platform). It does not respond to a specific trigger — it is always in effect once loaded.

**File:** `components/skills/<name>/SKILL.md`
**Format:** SKILL.md (Anthropic open standard)

**Use a Skill when:**
- You need to establish rules, preferences, or domain knowledge the AI must always apply.
- Example: "Always format code review comments as GitHub Flavored Markdown."

**Don't use a Skill when:**
- You need the AI to perform a specific workflow on demand → use a **Protocol**.
- You need to generate consistent text from a template → use a **Prompt**.

---

### Protocol

**A named, triggered workflow that the AI executes step by step when a specific phrase is spoken.**

A Protocol is dormant until its trigger phrase is matched. When triggered, the AI follows the protocol's steps exactly.

**File:** `components/protocols/<name>.md`
**Trigger:** A natural-language phrase registered as a slash command or remembered instruction.

**Use a Protocol when:**
- The user will say something specific and expect a defined sequence of actions.
- The workflow involves multiple steps, decisions, or tool calls.
- Example: "Move to code review" → creates a GitLab MR, posts to Teams, updates the inbox.

---

### Prompt

**A parameterized text template the AI fills in at runtime.**

A Prompt is a reusable text fragment with named `{{variable}}` placeholders. Typically called from within a Protocol.

**File:** `components/prompts/<name>.md`

**Use a Prompt when:**
- You need to generate consistent, structured text with varying inputs.
- Example: A review summary comment template that takes `{{mr_title}}` and `{{findings}}`.

---

### Artifact

**A persistent, interactive UI view the AI creates and the user can open and refresh.**

An Artifact is an HTML page (or its markdown equivalent) that the AI instantiates during installation. It does not run code on the host machine — it is a rendered view.

**Files:** `components/artifacts/<name>/artifact.html` (primary), `components/artifacts/<name>/artifact.md` (markdown fallback)

**Use an Artifact when:**
- The user needs a persistent view they can return to between sessions.
- Example: "Review Inbox" showing all open MRs assigned to the user, refreshed on demand.

**Always ship a markdown fallback.** Platforms that do not support HTML artifacts use `artifact.md`.

---

### Script

**Executable code that runs on the host machine.**

A Script is a file the AI copies to the user's machine and invokes using a shell command. Scripts can read and write the filesystem, call external APIs, and run shell commands.

**Files:** `scripts/<key>.py` (cross-platform), `adapters/windows/scripts/<key>.ps1` (Windows-preferred)
**Trust levels:** `read-only`, `network`, `write-local`, `shell-exec`

**Use a Script when:**
- You need to run code: call a REST API with complex auth, manipulate files, parse structured data.
- The logic is too complex or stateful for the AI to reason through reliably in plain text.

---

## Component Decision Table

| What I need | Component type |
|---|---|
| AI always behaves a certain way, no trigger required | **Skill** |
| User says a phrase → AI follows a defined sequence | **Protocol** |
| Reusable text template with runtime variables | **Prompt** |
| Persistent UI view the user can open and refresh | **Artifact** |
| Code that runs on the host machine | **Script** |
| Call a third-party API without complex auth or logic | MCP tool (in Protocol step, no Script needed) |
| Complex API call with auth, retries, or parsing | **Script** (called from Protocol) |
| One-time text output during a protocol run | Protocol step (no separate Prompt needed) |
| User-configurable values set once at install | Config key in manifest + `{{config.key}}` substitution |
| Values that change at runtime | `{{variable}}` in Prompt template |

**Common mistakes to avoid:**
- **Everything in a Skill.** If it requires a trigger, it's a Protocol. If it runs code, it's a Script.
- **Protocols that are too long.** If a protocol step says "run this 50-line Python logic," extract it into a Script. Protocols orchestrate; Scripts execute.
- **Scripts for simple MCP calls.** If an MCP tool covers the action cleanly, use it directly in the Protocol step.
- **Artifacts for one-time output.** If the user will only see it once during a protocol run, put it in the protocol output.

---

## Platform Conventions

Platform Conventions are split into two axes in v1.7: **OS conventions** (host filesystem) and **Runtime conventions** (AI host). Concrete deployments combine both — e.g. "Cowork on Windows" inherits OS conventions from Windows AND runtime conventions from Cowork.

### OS conventions

| Aspect | Windows | POSIX (macOS / Linux) |
|---|---|---|
| Path separator | `\` natively; use `/` in JSON / config files for portability | `/` |
| User home | `C:\Users\<user>\` | `/home/<user>/` (Linux) or `/Users/<user>/` (macOS) |
| `~` expansion | Native tools handle it; Linux-sandbox shells (e.g. Cowork's bash) do NOT — `~` there resolves to the ephemeral sandbox home | `os.path.expanduser('~')` or `$HOME` |
| Persistent config dir | `C:/Users/<user>/.claude/packages/<name>/` | `~/.claude/packages/<name>/` |
| Adapter directory | `adapters/os/windows/` | `adapters/os/posix/` |
| Path-specific scripts | `adapters/os/windows/scripts/<key>.ps1` (PowerShell) | `adapters/os/posix/scripts/<key>.sh` (optional bash scripts; the cross-platform Python in `scripts/<key>.py` is preferred) |

### Runtime conventions


A3IP is platform-agnostic by design. The same bundle can be installed on Cowork, Claude Code, Codex, or any other AI platform. This section defines what "installed" concretely means on each supported platform.

### Cowork

**Primary platform for knowledge workers. Full support for all A3IP component types.**

| Aspect | Convention |
|---|---|
| **Config directory** | `~/.claude/packages/<package-name>/` (or user-specified via `CONFIGURE.md`) |
| **Skills** | Copied to the workspace skills folder or registered as persistent instructions. |
| **Artifacts** | Created as Cowork artifacts (HTML). |
| **Protocols** | Registered as slash commands or remembered instructions. |
| **Scripts** | Copied to config directory. Invoked via Bash tool: `python3 <config_dir>/scripts/<key>.py` |
| **`installed.json`** | Written to `<config_dir>/installed.json` |
| **Scheduled tasks** | Use Cowork's built-in scheduler. |

### Claude Code

**Primary platform for developers. Full protocol support; artifacts degrade to markdown.**

| Aspect | Convention |
|---|---|
| **Config directory** | `~/.claude/packages/<package-name>/` |
| **Skills** | Copied to `~/.claude/skills/` or loaded as project-level CLAUDE.md content. |
| **Artifacts** | Use `artifact.md` fallback. HTML artifacts not natively supported. |
| **Protocols** | Registered as slash commands or CLAUDE.md instructions. |
| **Scripts** | Invoked via Bash: `python3 <config_dir>/scripts/<key>.py` |
| **`installed.json`** | Written to `<config_dir>/installed.json` |
| **Scheduled tasks** | Use system cron (`crontab -e`). The AI writes the cron entry during install. |

### Codex

**OpenAI's coding agent. Full protocol and script support; some artifact limitations. v1.8 adds an explicit runtime adapter location.**

| Aspect | Convention |
|---|---|
| **Config directory** | `~/.codex/packages/<package-name>/` |
| **Skills** | Loaded as persistent system instructions or project-level context files. Stored at `~/.codex/skills/<name>/`. No Cowork-style `.skill` UI — installation is file-copy + register-as-instruction. |
| **Artifacts** | Use `artifact.md` fallback. HTML artifacts not natively rendered. |
| **Protocols** | Registered as remembered instructions or project context. |
| **Scripts** | Invoked via code execution tool: `python3 <config_dir>/scripts/<key>.py` |
| **`installed.json`** | Written to `<config_dir>/installed.json` with `install_method: "generic-copy"`. |
| **Runtime adapter location** | `adapters/runtime/codex/install-skill.md` — packages SHOULD ship a Codex-specific install adapter when their install flow benefits from Codex-aware guidance (file paths, tool selection, PowerShell quirks on Windows). MAY omit if the generic-copy path in INSTALL.md suffices. |
| **OS host** | Most commonly Windows (Codex CLI runs natively). Filesystem ops MUST follow `adapters/os/windows/file-ops.md` (no bash sandbox here; `$env:USERPROFILE` is the Windows user home directly). |

### Generic

**Any AI platform not listed above. Minimal assumptions; maximum portability.**

| Aspect | Convention |
|---|---|
| **Config directory** | Ask the user. Default suggestion: `~/ai-packages/<package-name>/` |
| **Skills** | Load SKILL.md as a persistent instruction or paste into the system prompt. |
| **Artifacts** | Use `artifact.md` fallback. |
| **Protocols** | Register as remembered instructions. |
| **Scripts** | Ask the user to run manually and paste output back, or invoke via platform code execution. |
| **`installed.json`** | Write to the user-specified config directory. |
| **Scheduled tasks** | Document the schedule in INSTALL.md. Ask the user to set up the scheduler manually. |

### Implementation guidance for tool authors

The spec defines *where* OS-specific and runtime-specific conventions live (`adapters/os/{windows,posix}/` and `adapters/runtime/<name>/`) and that `INSTALL.md` MUST reference both for steps that cross dimensions. The spec does NOT prescribe *which tools* an install AI should use within each cross-product — that is implementation guidance and lives outside this document.

For concrete tool-selection patterns proven in real installs, see [`TOOL-AUTHORS.md`](../TOOL-AUTHORS.md) in the spec repository (non-normative).

### Detecting the platform

The AI installer detects the platform from context. If uncertain, ask the user:

> "Which platform are you installing this on? (e.g. Cowork, Claude Code, Codex, or something else)"

If the user's platform is not in `platforms.tested`, proceed with Generic conventions and note that the platform has not been tested by the author.

---

## Validation

A conformant A3IP validator must implement all nine checks defined in this section. Checks 1–7 apply to all packages; checks 8–9 apply only to packages using v1.2 security fields.

The reference implementation is `validate.py`, distributed with the A3IP Creator package.

**Error** — the package is incomplete or non-conformant. The AI installer must not install a package with errors.

**Warning** — not an error today, but indicates a likely oversight. The AI may proceed but should note warnings to the user.

---

### Check 1 — Config coverage

**Rule:** Every `{{config.key}}` reference in a non-script template file must correspond to a declared config key in `manifest.yaml`.

**Scope:** All `.md`, `.yaml`, `.yml`, `.json`, `.txt`, `.html`, `.js`, `.css` files. Excludes `docs/`, any file named `SKILL.md`, and script files (`.py`, `.ps1`, `.sh`).

**Outcome:** Error for each unique undeclared key found.

---

### Check 2 — Script existence

**Rule:** Every file declared in a script implementation must exist on disk at the specified path, relative to the package directory.

**Outcome:** Error for each missing file.

---

### Check 3 — Script config reads

**Rule:** Every config key accessed in a script file must be a declared config key in `manifest.yaml`.

**Patterns matched:** `config["key"]`, `config['key']`, `config.get("key")`, `$config.key_name` (PowerShell).

**Outcome:** Error for each undeclared key found in any script file.

---

### Check 4 — Cross-platform coverage

**Rule:** Every script that declares a Windows-specific implementation must also declare an `any`-platform (cross-platform) implementation.

**Outcome:** Error for each script with a Windows implementation but no `any` implementation.

---

### Check 5 — Auth flows

**Rule:** If the package includes authentication scripts, `INSTALL.md` must include an authentication step.

**Detection:** Any file matching `scripts/auth_*.py` or `adapters/windows/scripts/auth_*.ps1` is treated as an auth script. `INSTALL.md` must contain the filename stem or the word `authenticate`.

**Outcome:** Warning for each auth script whose name or `authenticate` keyword is absent from `INSTALL.md`.

---

### Check 6 — CHANGELOG present

**Rule:** Any package with a version higher than `1.0.0` must include a `CHANGELOG.md` file.

**Outcome:** Error if version is above `1.0.0` and `CHANGELOG.md` is absent. Warning if version is `1.0.0` and `CHANGELOG.md` is absent.

---

### Check 7 — Refresh scripts

**Rule:** Every `refresh_script:` value on a config key must be a declared script key.

**Outcome:** Error for each `refresh_script:` value that is not a declared script key.

---

### Check 8 — Trust level → permissions block (v1.2+)

**Rule:** Any package with at least one script implementation declaring `trust_level: network`, `write-local`, or `shell-exec` must include a `permissions:` block in `manifest.yaml`.

**Outcome:** Error if elevated-trust scripts are present and no `permissions:` block exists.

---

### Check 9 — Trust level → `## Plan` section (v1.2+)

**Rule:** Any package with at least one script implementation declaring `trust_level: write-local` or `shell-exec` must include a `## Plan` section in `INSTALL.md`.

**Outcome:** Error if write-trust scripts are present and `## Plan` is absent from `INSTALL.md`.

---

### Summary table

| # | Name | Severity | v1.2+ only |
|---|---|---|---|
| 1 | Config coverage | Error | No |
| 2 | Script existence | Error | No |
| 3 | Script config reads | Error | No |
| 4 | Cross-platform coverage | Error / Warning | No |
| 5 | Auth flows | Warning | No |
| 6 | CHANGELOG present | Error / Warning | No |
| 7 | Refresh scripts | Error | No |
| 8 | Trust → permissions | Error | Yes |
| 9 | Trust → plan section | Error | Yes |

**Exit behavior:** A conformant validator exits with code `0` when no errors are found and `1` when one or more errors are found.

---

## Registry

A registry is a `registry.yaml` file that makes A3IP packages discoverable. It can be local (a file on disk) or remote (a URL). Both are treated identically by the AI installer.

### registry.yaml format

```yaml
---
format: a3ip-registry
spec: "1.5"
name: "My Package Registry"
description: "What this registry covers."
maintained_by: "Author Name"
updated: "2026-05-12"
---

packages:

  - name: package-name              # must match manifest.yaml name exactly
    version: "1.0.0"
    description: "One-sentence description of what this package does."
    author: "Full Name <email>"
    license: Apache-2.0
    platforms:
      - cowork
      - claude-code
    tags:
      - code-review
      - gitlab
    bundle_url: "./packages/package-name.a3ip.bundle"
    min_a3ip_spec: "1.0"
    changelog_summary: "Initial release."
```

**`bundle_url` resolution rules:**
- `https://` or `http://`: retrieve via HTTP GET.
- `./` or `../`: resolve relative to the directory containing `registry.yaml`.
- Absolute path: use directly.
- The AI must not silently substitute a different URL if the bundle is not found at the declared location.

### Browsing a registry

1. **Locate the registry.** The user provides a path or URL to `registry.yaml`.
2. **Read and parse.** Load the `packages:` list.
3. **Filter by need.** If the user described what they need, filter by `tags`, `description`, and `platforms`.
4. **Present options.** Show each matching package as a brief entry with name, version, description, and latest changelog summary.
5. **Ask the user to choose.** Confirm before proceeding.
6. **Proceed to installation.** Retrieve the bundle and follow standard install procedure.

### Installing from a registry

1. **Retrieve the bundle.** Resolve `bundle_url` per the rules above.
2. **Proceed with normal installation.** Read `INSTALL.md`, run the `CONFIGURE.md` wizard, apply each install step.
3. **Version check.** If `installed.json` exists and its version matches or exceeds the registry entry's version, the package is already up to date.
4. **Record the registry source.** After successful install, add `registry_source` to `installed.json`.

### Checking for updates

If `installed.json` contains a `registry_source` field:
1. Load `registry.yaml` from the recorded source.
2. Find the entry matching the installed package name.
3. Compare versions.
4. If the registry has a newer version, inform the user and offer to upgrade.

---

## manifest.yaml

The manifest is the single source of truth for the package. It declares what the package contains and what it needs.

```yaml
$schema: "https://a3ip.dev/schema/v1.5/manifest.json"

# ─── Identity ─────────────────────────────
name: "ai-code-review-flow"          # Required. Unique package name.
version: "1.2.0"                     # Required. SemVer.
description: "Complete AI-powered code review workflow for GitHub and GitLab."
author: "Jane Smith <jane@example.com>"
license: "Apache-2.0"                # SPDX identifier or "proprietary"
homepage: "https://a3ip.dev/packages/ai-code-review-flow"

# ─── Spec compatibility ───────────────────
min_a3ip_spec: "1.2"                 # Minimum A3IP spec version to install this package.

# ─── Latest change summary ───────────────
latest_change:
  version: "1.2.0"
  date: "2026-05-20"
  summary: "Added post-review recheck step."
  breaking: false

# ─── Components ───────────────────────────
components:
  skills:
    - path: components/skills/code-review
      description: "Guides the AI through the code review protocol."

  artifacts:
    - path: components/artifacts/review-inbox
      description: "Persistent inbox showing all open review requests."

  protocols:
    - path: components/protocols/move-to-review.md
      description: "The 'move to code review' command."

  prompts:
    - path: components/prompts/review-summary.md
      description: "Template for review request comments."

  scripts:
    - key: create_mr
      description: "Creates a GitLab/GitHub MR via REST API."
      parameters: [ProjectPath, SourceBranch, TargetBranch, Title]
      implementations:
        - file: scripts/create_mr.py
          platform: any
          trust_level: network
        - file: adapters/windows/scripts/create_mr.ps1
          platform: windows
          trust_level: network

    - key: auth_teams
      description: "Authenticates with Microsoft Teams, saves the access token."
      implementations:
        - file: scripts/auth_teams.py
          platform: any
          trust_level: write-local   # Writes token to config.json

# ─── Permissions ──────────────────────────
permissions:
  filesystem:
    - path: "{{config.install_dir}}"
      access: read-write
      reason: "Stores config, scripts, and installed.json."

  network:
    - domain: "api.github.com"
      reason: "GitHub REST API — read PRs, post review comments."
    - domain: "gitlab.example.com"
      reason: "GitLab REST API — read MRs, post review comments."

  mcp:
    - name: github-mcp
      reason: "Read and comment on pull requests."
    - name: gitlab-mcp
      reason: "Read and comment on merge requests."

  shell:
    - command: python3
      reason: "Runs all package scripts."

# ─── Dependencies ─────────────────────────
dependencies:
  mcp:
    - name: github-mcp
      required: false
      purpose: "Read pull requests, post review comments."
      fallback: "Paste PR diff into chat when GitHub MCP is unavailable."

    - name: gitlab-mcp
      required: false
      purpose: "Read merge requests, post review comments."
      fallback: "Paste MR diff into chat when GitLab MCP is unavailable."

# ─── Configuration schema ─────────────────
configuration:
  - key: platform
    label: "Code review platform"
    description: "Which platform hosts your code repositories."
    type: select
    required: true
    options:
      - value: github
        label: "GitHub"
      - value: gitlab
        label: "GitLab"
    when: before

  - key: api_token
    label: "Personal Access Token"
    description: "Token for authenticating API calls to your code platform."
    type: string
    required: true
    sensitive: true
    storage: keychain
    placeholder: "ghp-xxxx or glpat-xxxx"
    when: before

  - key: install_dir
    label: "Installation directory"
    description: "Absolute path where the package will store its files."
    type: string
    required: true
    placeholder: "C:\\Users\\you\\.claude\\code-review"
    when: before

  - key: reviewers
    label: "Default reviewers"
    description: "Usernames to assign as reviewers on new review requests."
    type: list<string>
    required: true
    placeholder: "@username"
    when: before

  - key: teams_access_token
    label: "Teams Access Token"
    description: "OAuth token for posting to Teams. Written by auth_teams script."
    type: string
    required: false
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

### `refresh:` field on configuration keys

| Value | Meaning |
|---|---|
| `never` | Default. Set once at install, never needs updating. |
| `periodic` | Needs manual update on a recurring basis (e.g. sprint start date). |
| `on_expiry` | Tied to a credential that expires. Pair with `refresh_script:` to automate renewal. |

---

## CONFIGURE.md

`CONFIGURE.md` defines the installation wizard. It instructs the AI on how to collect configuration values from the user — what to ask, in what order, how to present options, and what to do with the answers.

```markdown
---
format: a3ip-configure
spec: "1.0"
package: ai-code-review-flow
---

# Configuration Wizard: AI Code Review Flow

You are setting up a code review workflow. Ask the user each question below
in order. Be conversational — you do not need to present this as a form, but
make sure you collect every required value before moving to installation.

## Required — ask before installation

### 1. Platform
Ask: "Which platform hosts your repositories — GitHub or GitLab?"

- Key: `platform`
- Type: select — `github` or `gitlab`

### 2. Personal Access Token (sensitive)
Ask: "I need a Personal Access Token to authenticate API calls. Please create
one in your account settings (needs repo read + write permissions) and paste
it here."

- Key: `api_token`
- Type: string
- Sensitive: true — do NOT echo the value back. Once received, confirm only:
  "✅ Token received and will be stored securely."

### 3. Installation Directory
Ask: "Where should I store the package files? I'll use this as the base
directory for config and scripts."

- Key: `install_dir`
- Type: string
- Default suggestion: "~/.claude/packages/ai-code-review-flow"

### 4. Default Reviewers
Ask: "Who should be assigned as reviewers by default? Please provide
usernames (e.g. @john.doe). You can list multiple."

- Key: `reviewers`
- Type: list of strings

## After collecting all values

Summarize what you collected and ask the user to confirm before proceeding:

"Here's what I'll set up:
- Platform: {{config.platform}}
- Installation directory: {{config.install_dir}}
- Default reviewers: {{config.reviewers}}
- API token: ✅ received

Shall I proceed with installation?"

Wait for confirmation before continuing to INSTALL.md.
```

### Configuration types

| Type | Description |
|---|---|
| `string` | Single text value |
| `list<string>` | Multiple text values |
| `boolean` | Yes / No |
| `number` | Numeric value |
| `select` | One choice from a fixed list |
| `multi-select` | Multiple choices from a fixed list |

### Timing (`when` field)

| Value | Meaning |
|---|---|
| `before` | Collected upfront before any install step begins (default) |
| `during` | Collected inline at the relevant install step |
| `after` | Collected at the end for optional fine-tuning |

---

## INSTALL.md

`INSTALL.md` is written **for an AI agent**, not a human. It provides the receiving AI with everything it needs to install the package on any supported platform, including graceful degradation when features are unavailable.

```markdown
---
format: a3ip-install
spec: "1.2"
package: ai-code-review-flow
---

# Installation Guide: AI Code Review Flow

## 1. Check for Existing Installation

Look for `installed.json` at the platform-default install location (see Platform Conventions for the install directory convention per AI runtime).

Follow the package's `adapters/os/<host>/` for OS-specific file-read guidance — different OS hosts have different conventions for resolving `~` in paths, and the OS adapter is where the package author records which approach to use. If the package omits an OS adapter, the install AI is expected to use whatever file-read mechanism is idiomatic on the host OS.

- **Not found:** proceed with the full install steps below.
- **Found:** read its `config_dir` field for the actual install location, then go directly to [## Upgrading](#upgrading).

## Plan

Before beginning installation, this package will take the following actions.
Please confirm before proceeding.

**Files written:**
- `{{config.install_dir}}/config.json` — your configuration
- `{{config.install_dir}}/installed.json` — installed version record
- `{{config.install_dir}}/scripts/` — package scripts

**Network calls:**
- `api.github.com` or `gitlab.example.com` — verifies your API token

**MCP tools used:**
- `github-mcp` or `gitlab-mcp` — reads repository data during verification

**Confirm to proceed.**

## 2. Dependency Check

**Required (at least one):**
- [ ] GitHub MCP — check if you can call a GitHub tool.
- [ ] GitLab MCP — check if you can call a GitLab tool.

If neither is available, tell the user and ask them to install the appropriate
MCP server before continuing.

## 3. Create Installation Directory

Create `{{config.install_dir}}` if it does not exist.
Copy all files from `scripts/` in this bundle to `{{config.install_dir}}/scripts/`.

## 4. Write config.json

Write `{{config.install_dir}}/config.json`:

```json
{
  "platform": "{{config.platform}}",
  "install_dir": "{{config.install_dir}}",
  "reviewers": {{config.reviewers}},
  "teams_access_token": ""
}
```

Do not write `api_token` to this file — store it in the OS keychain per the
`storage: keychain` declaration.

## 5. Install Skills

Copy `components/skills/code-review/` to your platform's skills directory.
(See Platform Conventions for the correct location per platform.)

## 6. Set Up Artifacts

**If your platform supports HTML artifacts (Cowork, Claude.ai):**
Create a new artifact from `components/artifacts/review-inbox/artifact.html`.

**If your platform does not support HTML artifacts (Claude Code, Codex):**
Create a file at `{{config.install_dir}}/review-inbox.md` with the content
from `components/artifacts/review-inbox/artifact.md` as your markdown fallback.

## 7. Register Protocols

Read `components/protocols/move-to-review.md`. Substitute all `{{config.*}}`
references. Register the trigger phrase "move to code review" as:
- A slash command (if supported)
- Or a remembered instruction ("when the user says 'move to code review', follow these steps")

## 8. Write installed.json

Write `{{config.install_dir}}/installed.json`:

```json
{
  "package": "ai-code-review-flow",
  "version": "1.2.0",
  "installed_at": "<current ISO-8601 timestamp>",
  "platform": "<detected platform>",
  "a3ip_spec": "1.2",
  "config_dir": "{{config.install_dir}}"
}
```

## 9. Confirm

Tell the user:
- What was installed successfully
- What MCP was connected (GitHub or GitLab)
- How to trigger the workflow ("say 'move to code review'")
- Any degraded features (e.g. markdown fallback instead of HTML artifact)

---

## Upgrading

When `installed.json` is found, follow these steps instead of the full install.

### Step U1 — Read installed version
Read `installed.json`. Note the `version` field.

### Step U2 — Read CHANGELOG.md
Find all version entries in `CHANGELOG.md` newer than the installed version.
Apply them in order from oldest to newest. For each version entry:
1. Check `### Breaking changes` — if any, tell the user before proceeding.
2. Check `### Config changes` — if new required keys, run the config wizard for those keys only.
3. Follow `### Upgrade steps` exactly.

### Step U3 — Update installed.json
After all upgrade steps complete, overwrite `installed.json` with the new version.

### Step U4 — Confirm
Tell the user the versions upgraded from and to, and the changes applied.
```

### `## Plan` section rules

- Must appear after the existing-installation check and before the first numbered action step.
- Must list every file written, every network domain contacted, every MCP tool invoked, and every shell command run.
- Must end with **Confirm to proceed.**
- The AI must not skip or summarize the Plan section.
- If the user declines, the AI aborts. No partial install state is written.

---

## CHANGELOG.md

`CHANGELOG.md` is the per-version upgrade guide. The AI reads it during upgrades to determine exactly what changed and what steps to execute.

```markdown
---
format: a3ip-changelog
spec: "1.1"
package: ai-code-review-flow
---

# Changelog: AI Code Review Flow

All notable changes to this package are documented here. Newest version first.

---

## [1.2.0] — 2026-05-20

### Breaking changes
None.

### Config changes
None.

### Files changed
- `components/protocols/move-to-review.md` — replaced
- `components/artifacts/review-inbox/artifact.html` — replaced

### New dependencies
None.

### Upgrade steps (from 1.1.x)

1. Re-register the `move-to-review` protocol from the updated file.
   Trigger phrase is unchanged: "move to code review".

2. If your platform supports HTML artifacts: update the Review Inbox artifact
   from the new `artifact.html`.

3. No config changes required. Your existing `config.json` remains valid.

### What changed (human summary)

Added a post-review recheck step to the move-to-review protocol.
The Review Inbox now shows reviewer response time.

---

## [1.0.0] — 2026-05-12

Initial release.
```

### CHANGELOG.md rules

- **Newest version first.** The AI reads top to bottom but applies in chronological order.
- **Every `## [version]` section is self-contained.** Upgrade steps assume the reader is on the previous version.
- **`### Breaking changes`** must be explicit. If `None`, say `None`.
- **`### Config changes`** lists every key added, removed, or renamed. Removed or renamed keys are always breaking.
- **`### Files changed`** format: `path — action` where action is one of: `replaced`, `added`, `deleted`.
- **`### Upgrade steps`** are AI instructions — written the same way as `INSTALL.md` steps.

### Breaking change taxonomy

| Change | Breaking? |
|---|---|
| New required config key (no default) | ✅ Yes |
| Config key removed or renamed | ✅ Yes |
| Config type changed | ✅ Yes |
| New required MCP dependency | ✅ Yes |
| Script interface changed (new required param) | ✅ Yes |
| New optional config key (has default) | ❌ No |
| New optional MCP dependency | ❌ No |
| Script file replaced (same interface) | ❌ No |
| Artifact HTML updated | ❌ No |
| Protocol steps changed | ❌ No |
| New script added | ❌ No |
| Bug fix with no interface change | ❌ No |

---

## installed.json

`installed.json` is written by the AI to the package's config directory immediately after a successful installation or upgrade. It is the machine-readable record of what version is installed and where.

```json
{
  "package": "ai-code-review-flow",
  "version": "1.2.0",
  "installed_at": "2026-05-20T14:32:00Z",
  "upgraded_from": "1.1.0",
  "platform": "cowork",
  "a3ip_spec": "1.8",
  "config_dir": "C:/Users/you/.claude/packages/ai-code-review-flow",
  "install_method": "cowork-skill",
  "registry_source": "https://raw.githubusercontent.com/a3ip-standard/packages/main/registry.yaml",
  "source_bundle": "C:/Users/you/Downloads/ai-code-review-flow-v1.2.0.a3ip.bundle",
  "workspace_dir": "C:/Users/you/projects/my-app",
  "backup_dir": "C:/Users/you/.claude/backups/ai-code-review-flow-20260520T143200Z"
}
```

**Required fields** (any install record):

| Field | Description |
|---|---|
| `package` | Package name from manifest |
| `version` | Installed version (semver) |
| `installed_at` | ISO-8601 timestamp of install/upgrade |
| `platform` | AI runtime name (`cowork`, `claude-code`, `codex`, `cursor`, ...) |
| `a3ip_spec` | A3IP spec version used for this install |
| `config_dir` | Absolute path to the config directory |

**Optional fields** (install adapters MAY write these; readers MUST tolerate their absence):

| Field | Description |
|---|---|
| `upgraded_from` | Previous version, if this was an upgrade. Omit on fresh installs. |
| `install_method` | Runtime-specific install path tag — e.g. `"cowork-skill"` (Cowork Personal Skills UI), `"generic-copy"` (file copy into a skills folder). Used by upgrade flows to choose the right re-install route. |
| `registry_source` | Path or URL of the registry this package was installed from. Used by `check-for-updates` flows. |
| `source_bundle` | Absolute path to the `.a3ip.bundle` file used for this install. Useful for audit trail and for re-installs without re-downloading. |
| `workspace_dir` | Absolute path to the user's project workspace at install time, if the package interacts with workspace-local files. |
| `backup_dir` | Absolute path to a backup the install adapter created before overwriting prior package state. Enables rollback. |

Readers (other install adapters, upgrade flows) MUST parse leniently — encountering an unknown field is not an error. This allows future spec versions to add more optional fields without breaking existing readers.

### Rules

- `installed.json` lives in the same directory as `config.json`.
- Never include it in an `.a3ip.bundle` or `.a3ip.zip`.
- If installation fails partway through, do not write or update `installed.json`.
- If the user re-installs from scratch, overwrite `installed.json`.

---

## Component Formats

### Skill (`components/skills/<name>/SKILL.md`)

Follows the [SKILL.md open standard](https://agentskills.io) exactly. Any valid SKILL.md is a valid A3IP skill component.

```markdown
---
name: code-review
description: "Step-by-step protocol for conducting and logging a code review."
version: "1.0.0"
---

## When to use this skill
Use when the user asks to start a code review, move an MR to review, or conduct a peer review.

## Steps
[full skill instructions here]
```

### Artifact (`components/artifacts/<name>/artifact.md`)

```markdown
---
name: review-inbox
description: "Persistent inbox listing all open code review requests with status and links."
type: ui-view
refresh: on-demand
---

## Purpose
Displays all open MRs awaiting review in a structured, scannable view.

## Fields
| Field | Source | Description |
|---|---|---|
| MR Title | GitLab/GitHub | Title of the merge request |
| Author | GitLab/GitHub | Who opened the MR |
| Waiting Since | GitLab/GitHub | Created date |
| Review Status | local | Pending / In Review / Approved / Changes Requested |

## Fallback (no HTML artifact support)
Maintain a markdown table in `review-inbox.md` with the same columns.
```

### Protocol (`components/protocols/<name>.md`)

```markdown
---
name: move-to-code-review
trigger: "move to code review"
aliases:
  - "start review"
  - "request review"
---

## What this protocol does
Moves a development task to "code review" state, notifying relevant parties
and updating all connected systems.

## Steps

1. **Identify the MR/PR** — Ask the user for the URL or number if not provided.
2. **Validate** — Check via MCP that the MR/PR is in a reviewable state.
3. **Assign reviewers** — Assign {{config.reviewers}} as reviewers.
4. **Post comment** — Post a structured review-request comment using the
   `review-summary` prompt template.
5. **Update inbox** — Add or update the entry in the Review Inbox artifact.
6. **Confirm** — Tell the user what was done and who was assigned.
```

### Prompt Template (`components/prompts/<name>.md`)

```markdown
---
name: review-summary
description: "Structured comment posted when a review is requested."
variables:
  - mr_title
  - author
  - ready_checklist
---

## Template

🔍 **Code Review Requested**

| | |
|---|---|
| MR/PR | {{mr_title}} |
| Author | {{author}} |
| Reviewers | {{config.reviewers}} |

**Ready checklist:**
{{ready_checklist}}
```

---

## Versioning

A3IP packages follow [SemVer](https://semver.org):

- **Major** (`2.0.0`): breaking changes. Requires user to re-run config wizard for affected keys, or re-install from scratch.
- **Minor** (`1.1.0`): new features, new optional config keys, new optional dependencies. Existing installations upgrade cleanly.
- **Patch** (`1.0.1`): bug fixes, script replacements with no interface change, documentation clarifications.

The A3IP spec itself follows SemVer independently of package versions:
- **Major spec bump** (`2.0`): incompatible changes to manifest or `INSTALL.md` format.
- **Minor spec bump** (`1.x`): new fields and features (backward compatible). All prior packages remain valid.

Packages declare `min_a3ip_spec:` in their manifest to signal which spec features they rely on. An AI that only knows an earlier spec should refuse to install a package requiring a later one and ask the user to use an updated AI.

---

## Design Principles

1. **Platform agnostic by default.** Components are described at intent level. Platform-specific implementations go in `adapters/<platform>/`.
2. **OS agnostic by default.** Scripts must provide a cross-platform Python implementation. OS-specific alternatives live in `adapters/<os>/scripts/`.
3. **AI-first installation.** The receiving AI reads `INSTALL.md` and performs setup. No human-operated CLI required.
4. **User-configurable.** `CONFIGURE.md` turns installation into a conversation.
5. **Two-variable model.** `{{config.*}}` values are set once at install time. `{{variable}}` values are filled at runtime each time a protocol runs.
6. **Graceful degradation.** Every dependency declares a fallback. Every artifact ships a markdown fallback.
7. **Delta upgrades, not re-installs.** `CHANGELOG.md` gives the AI a precise, version-scoped upgrade path.
8. **Installation state is local.** `installed.json` lives with the user's config, not in the package.
9. **Composable.** A3IP packages can declare other A3IP packages as dependencies.
10. **Plain text end-to-end.** Every component file is plain text. The `.a3ip.bundle` is a single readable text file.
11. **Superset, not fork.** Any valid SKILL.md skill and any APM-compatible manifest block is valid inside A3IP without modification.
12. **Declare before you act.** Scripts declare their trust level; packages declare their permissions; the AI presents a plan and gets user consent before any side-effecting step runs.
13. **One component, one job.** Each component type has a precise role. Mixing responsibilities makes packages harder to maintain and harder for the receiving AI to reason about.
14. **Validate before you ship.** A package that hasn't passed all nine validation checks is not ready to distribute. Validation is a gate, not a suggestion.
15. **Discoverable by default.** A package without a registry entry can only be installed by direct bundle transfer. Authors should publish to a registry so their packages can be found, updated, and composed into larger ecosystems.

---


## Relationship to Existing Standards

| Concept | SKILL.md | APM | A3IP |
|---|---|---|---|
| Portable skills | ✅ Core format | ✅ Supports | ✅ Adopts SKILL.md exactly |
| MCP dependency declarations | ❌ | ✅ | ✅ |
| AI-readable install guide | ❌ | ❌ | ✅ `INSTALL.md` |
| Installation wizard | ❌ | ❌ | ✅ `CONFIGURE.md` |
| Permission declarations | ❌ | ❌ | ✅ `permissions:` block |
| Script trust levels | ❌ | ❌ | ✅ `trust_level:` |
| Delta upgrades | ❌ | ❌ | ✅ `CHANGELOG.md` + `installed.json` |
| Sensitive config handling | ❌ | ❌ | ✅ `sensitive:` + `storage:` |
| Package registry format | ❌ | ❌ | ✅ `registry.yaml` |
| Plain-text bundle format | ❌ | ❌ | ✅ `.a3ip.bundle` |

---

## Spec Version History

| Version | Released | What it adds |
|---|---|---|
| `1.0` | 2026-05-12 | Core: manifest, INSTALL.md, CONFIGURE.md, bundle format, `{{config.*}}` substitution, component model |
| `1.1` | 2026-05-12 | Versioning: CHANGELOG.md, installed.json, `## Upgrading`, `refresh:` on config keys, `min_a3ip_spec:`, `latest_change:` |
| `1.2` | 2026-05-12 | Security: `trust_level:` on scripts, `permissions:` block, `## Plan` in INSTALL.md, `storage:` on sensitive config keys |
| `1.3` | 2026-05-12 | Terminology: formal component definitions, decision table, platform adapter conventions |
| `1.4` | 2026-05-12 | Validation: nine normative checks every conformant validator must implement |
| `1.5` | 2026-05-12 | Registry: `registry.yaml` format, browsing protocol, install-from-registry, update checks |
| `1.6` | 2026-05-15 | Bundle: `spec_url:` field — cold-start AIs fetch the spec by URL instead of requiring it embedded |

All packages authored under v1.0–v1.4 remain fully valid under v1.5.

---

*A3IP Specification v1.6 — Complete consolidated edition*
*© 2026 Maksym Prydorozhko · [a3ip.dev](https://a3ip.dev) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)*
