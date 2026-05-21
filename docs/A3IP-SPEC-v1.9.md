# A3IP Specification v1.9

*Note: v1.9 is a re-alignment release for package authors — all v1.8 packages remain valid v1.9. Changes: (a) INSTALL.md Tier 2 install steps re-framed as outcomes (Steps 5/6/7); (b) tier markers added to step headers to disambiguate Tier 1 mechanical vs. Tier 2 outcome steps; (c) new normative section "Writing Adapter Documents" formalizes adapters as platform-knowledge artifacts (Tier 3 semantics) rather than installation scripts; (d) platform context detection promoted to a named Tier 3 semantic under Platform Conventions; (e) Validation reconciled to 10 checks (matching CLI 1.3.x) and three new warnings added (Checks 11/12/13). All warnings, not errors — existing v1.8 packages remain valid. v1.9 does NOT introduce uninstall (deferred to v1.10).*

## What's new in v1.9

v1.9 corrects implementation drift in the v1.8 INSTALL.md template and adapter contract. The three-tier specification model in [CONCEPT.md](../CONCEPT.md) (Tier 1 mechanical, Tier 2 outcomes, Tier 3 semantics) was always the design intent; this release brings the spec text into alignment with that model. No new concepts are introduced.

**(a) Tier 2 install steps re-framed as outcomes.** The v1.8 INSTALL.md template named Steps 5/6/7 after specific procedures ("Install Skills" / "Set Up Artifacts" / "Register Protocols"). Those names presupposed one platform's installation model — they read well on Cowork (where the Personal Skills UI handles registration as a side-effect of file placement) but mis-shaped author intent for runtimes where registration is a separate explicit act (Codex's AGENTS.md, for example). The names committed the spec to a procedure when the spec's job is to state outcomes and let the adapter describe the procedure. v1.9 renames:

| v1.8 | v1.9 |
|---|---|
| 5. Install Skills | 5. Make skills discoverable to the host runtime |
| 6. Set Up Artifacts | 6. Make artifacts available on the host runtime |
| 7. Register Protocols | 7. Make protocols invocable on the host runtime |

The mechanical Tier 1 steps (existing-install check, dependency check, create install dir, write config.json, write installed.json, confirm) keep their names — they were either already outcome-correct or are validator-checkable Tier 1 procedures by design.

**(b) Tier markers on step headers.** Every step in the INSTALL.md template now declares its tier on the line immediately after the heading:

    ## 5. Make skills discoverable to the host runtime
    *Tier: 2 (required outcome — adapter procedure)*

    After this step, the host runtime MUST be able to load each skill in
    `components/skills/` when its trigger phrases appear...

The marker disambiguates for both the installing AI and the validator. Tier 1 steps (e.g., "Write installed.json with these fields") get checked mechanically. Tier 2 steps get checked for outcome-shape (warning if they appear to leak into procedure language). The marker is also a reading-hint to the AI: this is a step to reason about (Tier 2), not to execute verbatim (Tier 1).

**(c) New section: "Writing Adapter Documents."** v1.8 had no formal guidance on how to write adapter content. In practice, this gap meant adapter authors wrote installation scripts (PowerShell, Bash) into adapter docs, which the installing AI treated as authoritative — losing the "AI as intelligent installer" property the spec depends on. v1.9 adds a normative section between Platform Conventions and Validation that names adapter content as Tier 3 platform-knowledge, with concrete before/after examples and five writing-discipline rules.

**(d) Platform context detection.** v1.8 mentions platform detection in passing. v1.9 promotes this to a sub-section under Platform Conventions, naming "platform context" as a Tier 3 semantic. The spec describes what platform context means (host OS + AI runtime, derived from env + tool surface + dir patterns) without prescribing how to derive it.

**(e) Validation reconciled to 10 checks; three new warnings.** v1.8 spec text said "nine checks" but CLI 1.3.x has added Check 10 (INSTALL.md spec compliance) — the spec text is reconciled. Three new validator warnings (not errors) are added:

- **Check 11 — Adapter outcome coverage** (Warning). Each platform listed in `platforms.tested` whose adapter exists at `adapters/runtime/<X>/install-skill.md` SHOULD reference each Tier 2 outcome it influences (Steps 5/6/7).
- **Check 12 — INSTALL.md tier shape** (Warning). Steps declared Tier 2 are scanned for procedure-language leakage (raw `bash`/`powershell` code blocks in step bodies, imperative "Run X" / "Execute Y" phrasing).
- **Check 13 — Adapter knowledge-shape** (Warning). Adapter `install-skill.md` files whose code-block line count exceeds their prose line count are flagged as "script-shaped rather than knowledge-shaped."

All three are warnings in v1.9. They WILL become errors in v2.0 once authors have transitioned.

**Removed from this release:**

- **Uninstall protocol.** A genuine concept gap, but doing it well requires its own design conversation. Deferred to v1.10.

**Backward compatibility:** All v1.8 packages remain valid under v1.9. The renamed steps in INSTALL.md template are advisory for new authoring; v1.8-shaped step names still parse and install correctly. The new tier markers are advisory; INSTALL.md files without markers still validate (Check 12 falls back to a coarser heuristic). The new warnings (Checks 11–13) do not block installation.

---

## Table of Contents

1. [Overview](#overview)
2. [Package Structure](#package-structure)
3. [Bundle Format](#bundle-format)
4. [Security Model](#security-model)
5. [Terminology](#terminology)
6. [Component Decision Table](#component-decision-table)
7. [Platform Conventions](#platform-conventions)
8. [Writing Adapter Documents](#writing-adapter-documents)
9. [Validation](#validation)
10. [Registry](#registry)
11. [manifest.yaml](#manifestyaml)
12. [CONFIGURE.md](#configuremd)
13. [INSTALL.md](#installmd)
14. [CHANGELOG.md](#changelogmd)
15. [installed.json](#installedjson)
16. [Component Formats](#component-formats)
17. [Versioning](#versioning)
18. [Design Principles](#design-principles)
19. [Relationship to Existing Standards](#relationship-to-existing-standards)
20. [Spec Version History](#spec-version-history)

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
└── adapters/              # Optional. OS and runtime-specific platform knowledge.
    ├── os/                # Host operating system axis
    │   ├── windows/       # Windows: path conventions, tool selection, PS1 scripts
    │   │   ├── file-ops.md     # Tool-selection guidance for filesystem ops
    │   │   └── scripts/        # PowerShell alternatives to scripts/<key>.py
    │   └── posix/         # macOS / Linux: expanduser conventions, $HOME usage
    │       ├── file-ops.md
    │       └── scripts/
    └── runtime/           # AI runtime axis (Cowork, Claude Code, Codex, etc.)
        ├── cowork/        # .skill UI flow, mcp__cowork__* tools, present_files
        │   ├── install-skill.md   # Cowork platform-knowledge document
        │   └── SKILL.md           # Combined Cowork-loadable skill
        ├── claude-code/   # Direct file-copy to ~/.claude/skills/
        ├── codex/         # ~/.codex/skills/<name>/, AGENTS.md registration
        │   └── install-skill.md   # Codex platform-knowledge document
        ├── cursor/        # Editor-integrated
        └── generic/       # Generic fallback

Legacy flat layout (v1.6 and earlier) — DEPRECATED but still valid.
```

`CHANGELOG.md` is required once a package has been publicly distributed and then updated (any version after the initial `1.0.0` release).

**On the role of `adapters/`:** Adapter documents are platform-knowledge artifacts (Tier 3 semantics), not installation scripts. They teach the installing AI about a platform's conventions so the AI can reason about how to satisfy the Tier 2 outcomes in INSTALL.md on the specific install in front of it. See [Writing Adapter Documents](#writing-adapter-documents) for authoring guidance.

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

**Files:** `scripts/<key>.py` (cross-platform), `adapters/os/windows/scripts/<key>.ps1` (Windows-preferred)
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

Platform Conventions are split along two axes: **OS conventions** (host filesystem) and **Runtime conventions** (AI host). Concrete deployments combine both — e.g. "Cowork on Windows" inherits OS conventions from Windows AND runtime conventions from Cowork.

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
| **Skills** | Copied to the workspace skills folder or registered as persistent instructions. Cowork's Personal Skills UI auto-discovers skills in the configured location. |
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

**OpenAI's coding agent. Full protocol and script support; some artifact limitations.**

| Aspect | Convention |
|---|---|
| **Config directory** | `~/.codex/packages/<package-name>/` |
| **Skills** | Stored at `~/.codex/skills/<name>/`. Codex does NOT auto-discover this directory; the skill must be registered in `~/.codex/AGENTS.md` (which Codex loads as a persistent system instruction at session start) for the host runtime to find and load it. |
| **Artifacts** | Use `artifact.md` fallback. HTML artifacts not natively rendered. |
| **Protocols** | Registered as remembered instructions, AGENTS.md stanzas, or project context. |
| **Scripts** | Invoked via code execution tool: `python3 <config_dir>/scripts/<key>.py` |
| **`installed.json`** | Written to `<config_dir>/installed.json` with `install_method: "generic-copy"`. |
| **Runtime adapter location** | `adapters/runtime/codex/install-skill.md` — packages SHOULD ship a Codex-specific adapter document describing the platform's discovery mechanism. See [Writing Adapter Documents](#writing-adapter-documents). |
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

### Detecting platform context

The installing AI's **platform context** is the combination of host OS and AI runtime currently active. It is what the AI consults when choosing among adapter directories and applying their knowledge to the install in front of it.

Platform context is a Tier 3 semantic — the spec describes what it means and how the AI is expected to know it, without prescribing a mechanical detection procedure.

The AI is expected to derive its platform context from a combination of:

- **Environment variables** — `USERPROFILE` on Windows, `HOME` on POSIX hosts. `OS`, `OSTYPE`, and similar may also be present.
- **Tool surface** — presence of runtime-specific tools (e.g. `mcp__cowork__*` tools indicate Cowork; code-execution tooling with no MCP layer indicates Codex CLI). The runtime is identifiable from what the AI can do.
- **Directory presence** — `~/.codex/` vs `~/.claude/` vs `~/.cursor/` distinguish runtimes; the presence of one or more is observable.
- **Convention files** — `AGENTS.md` (Codex), `CLAUDE.md` (Claude Code / Cowork) indicate which runtime is reading instructions.
- **User confirmation** — when ambiguous, asking is correct.

Platform context is **not a manifest field**. Packages do not declare what platform context they're being installed into; the installing AI is responsible for knowing where it is. Manifest's `platforms.tested` declares which platforms the author has tested *authoring against*, which is a different concern.

When platform context cannot be determined unambiguously from environment + tool surface + directories, the AI MUST ask the user before proceeding with adapter-dependent steps.

### Implementation guidance for tool authors

The spec defines *where* OS-specific and runtime-specific conventions live (`adapters/os/{windows,posix}/` and `adapters/runtime/<name>/`) and that `INSTALL.md` MUST reference both for steps that cross dimensions. The spec does NOT prescribe *which tools* an install AI should use within each cross-product — that is implementation guidance and lives outside this document.

For concrete tool-selection patterns proven in real installs, see [`TOOL-AUTHORS.md`](../TOOL-AUTHORS.md) in the spec repository (non-normative).

For guidance on writing adapter documents themselves, see [Writing Adapter Documents](#writing-adapter-documents).

---

## Writing Adapter Documents

This section is normative guidance for **authors** writing adapter documents — the platform-specific content under `adapters/runtime/<X>/` and `adapters/os/<X>/`. The audience is humans (or authoring AIs) producing these files, not the installing AI consuming them.

### Adapter documents are platform-knowledge artifacts (Tier 3 semantics)

Per [CONCEPT.md's three-tier model](../CONCEPT.md), adapter documents sit at Tier 3 — semantic descriptions the installing AI reads as platform knowledge, not procedures it executes verbatim. They teach the AI *about* the platform: how skills are discovered, how triggers are registered, where files live, what the platform's quirks are. The AI then applies that knowledge to satisfy the Tier 2 outcomes in INSTALL.md on the specific install in front of it.

This distinction matters because a Tier 3 knowledge artifact and a Tier 1 procedure look similar on the page — both can contain code, commands, and step-by-step structure. But the AI's relationship to them is fundamentally different:

| | Tier 1 procedure | Tier 3 knowledge |
|---|---|---|
| Author's intent | "Execute this exactly." | "Here's how this platform works." |
| AI's interpretation | Run verbatim. | Apply to the situation. |
| Variation handling | Brittle — different paths, different versions break the script. | Robust — the AI reasons about what's different. |
| Right contents | Concrete commands, exact paths. | Conventions, locations, mechanisms; commands as illustration. |
| Right shape | Imperative ("Run X. Then Y.") | Descriptive ("Skills live at X. Registration happens via Y.") |

When adapter content drifts toward Tier 1 procedure-shape, the installing AI loses its "intelligent agent" property — it executes verbatim, breaks on variation, and the spec's platform-neutrality goal is silently violated.

### Knowledge-shaped vs. script-shaped: a concrete contrast

Both examples below describe the same install task (placing the skill payload on Codex such that the host runtime can load it). One is script-shaped. The other is knowledge-shaped.

**Script-shaped — DO NOT write adapters in this form:**

```powershell
$skill = "$env:USERPROFILE\.codex\skills\ai-code-review-flow"
Remove-Item -LiteralPath $skill -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $skill -Force
Copy-Item -Path (Join-Path $work '*') -Destination $skill -Recurse -Force
Copy-Item -LiteralPath (Join-Path $work 'components\skills\code-review\SKILL.md') `
          -Destination (Join-Path $skill 'SKILL.md') -Force
```

The AI reads this as procedure. If the user's `$env:USERPROFILE` is OneDrive-redirected, if the path separators don't match a quirk of the shell, if AGENTS.md already has content with a different stanza convention, the script fails. The AI has no room to reason because the adapter committed it to verbatim execution.

**Knowledge-shaped — DO write adapters in this form:**

> On Codex, skills live at `~/.codex/skills/<name>/` — one directory per skill.
> The directory must contain `SKILL.md` at its root (Codex looks for `SKILL.md`
> there, not in subdirectories). Codex does NOT auto-discover this directory;
> the skill must be registered in `~/.codex/AGENTS.md` by appending a stanza
> referencing the absolute path to `SKILL.md`. Codex loads `AGENTS.md` as a
> persistent system instruction at each session start.
>
> On Windows hosts, `~` resolves to `$env:USERPROFILE`. OneDrive-redirected home
> folders are normal; the resolved path may be under
> `C:\Users\<user>\OneDrive\...` rather than `C:\Users\<user>\`. The install AI
> should use whatever resolved path the OS gives it.
>
> AGENTS.md registration uses a marker-bounded stanza so re-installs and
> uninstalls can replace or remove the stanza cleanly. The marker convention is:
>
>     <!-- a3ip:<package-name>:start -->
>     ## a3ip skill: <package-name>
>     When the user says <trigger phrases>, read and follow
>     <absolute path to SKILL.md>. That file is authoritative.
>     <!-- a3ip:<package-name>:end -->
>
> Worked example (illustrative — adapt to actual user paths):
>
>     Copy-Item -Path "$work\*" `
>               -Destination "$env:USERPROFILE\.codex\skills\<name>" -Recurse
>
> After copy, lift SKILL.md from `components/skills/<name>/` to the skill root.

The AI reads this as knowledge. It learns the platform's conventions (where skills live, how registration happens, what OneDrive redirection means, how marker-bounded stanzas work) and then chooses how to satisfy the Tier 2 outcomes given the install in front of it. If a path is OneDrive-redirected, the AI knows that's normal. If the user's chosen install path differs, the AI knows the SKILL.md root constraint. The code is illustration, not commandment.

### Writing discipline

Authors writing adapter content should:

1. **Lead with conventions, not commands.** First sentence of any adapter section should describe what the platform does, not what the AI should do. "On Codex, skills live at `~/.codex/skills/<name>/`" is convention-shaped. "Copy the skill folder to `~/.codex/skills/<name>/`" is command-shaped.

2. **Name mechanisms.** When the platform has a non-obvious mechanism (auto-discovery vs. explicit registration; UI button vs. file edit; sandbox vs. native), name it. The AI's reasoning depends on knowing the mechanism, not just the destination path.

3. **Mark code as illustration.** Phrasings like "Example (illustrative):", "Worked example — adapt to actual paths:", "One way this can look:" signal to the installing AI that the code is a demonstration, not a script. Avoid framings like "Run this:", "Execute the following:", "The procedure is:".

4. **Avoid code as the section body.** If an adapter section is mostly code with a sentence of context, it's script-shaped. Rule of thumb: prose should outweigh code. [Check 13](#check-13--adapter-knowledge-shape-v19) enforces this coarsely.

5. **Describe variation, not error cases.** "On Windows hosts, paths use backslash" is convention. "If you see a 'path not found' error, try X" is troubleshooting — useful, but should go in a Troubleshooting section, not in the main convention prose.

### When script-shape is unavoidable

There are cases where a procedural code block legitimately belongs in an adapter: bootstrap scenarios where the platform has no established conventions yet, or operations where the exact sequence matters (e.g., creating a directory before substituting paths). In those cases:

- Wrap the script in clear illustrative framing: "Bootstrap example for first-time Cursor support — establishes the convention; subsequent installs should match this shape."
- Explain *why* the sequence matters, so the AI can preserve the invariant even if it varies the surface form.
- Place the script after the convention prose, not before.

Over time, as a platform's behavior stabilizes, adapter authors should shift such sections from script-shaped to knowledge-shaped — replacing "here's the script that worked" content with "here's the convention." That's the natural maturation path. Check 13 (warning) flags adapters that don't make this transition.

### Adapter coverage for Tier 2 outcomes

Each platform's runtime adapter SHOULD address each Tier 2 outcome in [INSTALL.md](#installmd) that its platform influences:

- Step 5 (skills discoverable) — every runtime adapter should describe how the platform discovers/loads skills.
- Step 6 (artifacts available) — every runtime adapter should describe its artifact mechanism (HTML support, markdown fallback, etc.).
- Step 7 (protocols invocable) — every runtime adapter should describe its trigger/registration mechanism.

[Check 11](#check-11--adapter-outcome-coverage-v19) (warning) flags missing coverage. The check is a cheap surface heuristic; the proper test is dogfood installation on the target platform.

---

## Validation

A conformant A3IP validator implements the 10 normative checks defined in this section, plus the 3 advisory warning checks added in v1.9. Checks 1–7 apply to all packages; Checks 8–9 apply only to packages using v1.2 security fields; Check 10 was added in v1.7 (INSTALL.md spec compliance); Checks 11–13 were added in v1.9 (re-alignment warnings).

The reference implementation is the `a3ip` CLI distributed via [PyPI](https://pypi.org/project/a3ip/).

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

**Detection:** Any file matching `scripts/auth_*.py` or `adapters/os/windows/scripts/auth_*.ps1` is treated as an auth script. `INSTALL.md` must contain the filename stem or the word `authenticate`.

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

### Check 10 — INSTALL.md spec compliance (v1.7+)

**Rule:** `INSTALL.md` MUST include:

- Frontmatter declaring `format: a3ip-install` and `spec: "<version>"` consistent with the package's `min_a3ip_spec`.
- An existing-installation check as the first numbered step (Step 1 in the canonical template).
- A `## Plan` section if any script implementation has `trust_level: write-local` or `shell-exec` (restates Check 9 from the INSTALL.md perspective).
- A reference to each platform listed in `platforms.tested` — either explicitly (named in a section) or implicitly (via a routing block delegating to `adapters/runtime/<platform>/`).

**Outcome:** Error for missing frontmatter, missing existing-install step, or missing per-platform reference. Warning for stylistic deviations.

---

### Check 11 — Adapter outcome coverage (v1.9+)

**Rule:** Each platform listed in `platforms.tested` whose adapter exists at `adapters/runtime/<X>/install-skill.md` SHOULD reference each Tier 2 outcome it influences (Steps 5/6/7 of the canonical INSTALL.md). Specifically: the adapter should contain content addressing skill discovery, artifact availability, and protocol invocability for any of those component categories the package declares.

**Detection:** The validator scans the adapter for references to each outcome step's keywords ("skills", "artifacts", "protocols") or to the outcome names ("discoverable", "available", "invocable").

**Outcome:** Warning for each (platform, outcome) pair where the platform's adapter doesn't reference the outcome.

**Rationale:** Adapters that don't address the outcomes they should are the v1.2.x → v1.2.2 Codex-bug class. The check is a cheap surface heuristic; the proper test is dogfood installation on the target platform.

---

### Check 12 — INSTALL.md tier shape (v1.9+)

**Rule:** Steps declared `*Tier: 2 (...)*` in their tier marker SHOULD NOT contain procedure-language leakage. Specifically:

- No raw `bash` or `powershell` code blocks in the step body (illustrative pseudocode marked as such is acceptable).
- No imperative verbs at sentence start: "Run X", "Execute Y", "Copy Z". Outcome verbs ("Make X", "Ensure Y is true") are preferred.

**Detection:** Pattern-match within each Tier 2 step body.

**Outcome:** Warning per occurrence. The warning includes the matched pattern and the step header so the author can locate it.

**Rationale:** Tier 2 steps are outcomes, not procedures. Authors who write Tier 2 steps in procedure language are reverting to the override model — adapters then have nothing to override against. The warning surfaces drift early.

**Fallback for INSTALL.md without tier markers:** Step headers starting with "Install", "Set Up", "Register", "Configure", "Write", "Run", "Execute" are treated as candidates for Tier 2 outcome re-framing. Warning is softer (suggestion only).

---

### Check 13 — Adapter knowledge-shape (v1.9+)

**Rule:** Adapter `install-skill.md` files SHOULD be more prose than code. Specifically: the ratio of non-code-block lines to code-block lines should be at least 2:1.

**Detection:** Count lines inside fenced code blocks vs. lines outside. Compute ratio.

**Outcome:** Warning if ratio falls below threshold. Message: `Adapter <path> appears more script-shaped than knowledge-shaped (code-to-prose ratio: X). Adapters are Tier 3 platform-knowledge artifacts; see "Writing Adapter Documents" in the spec.`

**Rationale:** Adapter authors trained on previous versions of the spec habitually write installation scripts. The ratio check is a coarse signal that the adapter is more script than knowledge. The check is intentionally lenient (1:2 prose:code threshold) — even well-written adapters can have substantial illustrative code.

---

### Summary table

| # | Name | Severity | Introduced |
|---|---|---|---|
| 1 | Config coverage | Error | v1.4 |
| 2 | Script existence | Error | v1.4 |
| 3 | Script config reads | Error | v1.4 |
| 4 | Cross-platform coverage | Error / Warning | v1.4 |
| 5 | Auth flows | Warning | v1.4 |
| 6 | CHANGELOG present | Error / Warning | v1.4 |
| 7 | Refresh scripts | Error | v1.4 |
| 8 | Trust → permissions | Error | v1.2 |
| 9 | Trust → plan section | Error | v1.2 |
| 10 | INSTALL.md spec compliance | Error / Warning | v1.7 |
| 11 | Adapter outcome coverage | Warning | **v1.9** |
| 12 | INSTALL.md tier shape | Warning | **v1.9** |
| 13 | Adapter knowledge-shape | Warning | **v1.9** |

**Exit behavior:** A conformant validator exits with code `0` when no errors are found (warnings present or absent) and `1` when one or more errors are found.

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
version: "1.3.0"                     # Required. SemVer.
description: "Complete AI-powered code review workflow for GitHub and GitLab."
author: "Jane Smith <jane@example.com>"
license: "Apache-2.0"                # SPDX identifier or "proprietary"
homepage: "https://a3ip.dev/packages/ai-code-review-flow"

# ─── Spec compatibility ───────────────────
min_a3ip_spec: "1.9"                 # Minimum A3IP spec version to install this package.

# ─── Latest change summary ───────────────
latest_change:
  version: "1.3.0"
  date: "2026-06-01"
  summary: "Re-aligned to spec v1.9 — adapters as knowledge artifacts."
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
        - file: adapters/os/windows/scripts/create_mr.ps1
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
  "Token received and will be stored securely."

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
- API token: received

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

Each numbered step declares its tier on the line immediately after the heading, so both the installing AI and the validator know how to interpret the step:

- `*Tier: 1 (mechanical)*` — the procedure is the outcome (e.g., "Write installed.json with these fields"). The validator can check it mechanically.
- `*Tier: 2 (required outcome — adapter procedure)*` — the spec states the outcome the runtime must reach; the adapter at `adapters/runtime/<X>/install-skill.md` describes the HOW for the host runtime.
- `*Tier: 2 (required outcome)*` — the spec states the outcome the AI must reach by its own reasoning; no adapter dependency.

```markdown
---
format: a3ip-install
spec: "1.9"
package: ai-code-review-flow
---

# Installation Guide: AI Code Review Flow

## 1. Check for Existing Installation
*Tier: 2 (required outcome — adapter procedure)*

After this step, the AI MUST know whether a prior installation of this package
exists on the host. The detection mechanism depends on the OS (path conventions
for the config directory) and the AI's tool surface (which file-reading tool is
idiomatic on the host).

The default detection target is `installed.json` at the platform-default
install location (see [Platform Conventions](#platform-conventions)).
Consult `adapters/os/<host>/file-ops.md` for OS-specific file-read conventions.

- **Not found:** proceed with the full install steps below.
- **Found:** read its `config_dir` field for the actual install location, then go directly to [## Upgrading](#upgrading).

## Plan
*Tier: 1 (mechanical — required for trust ≥ write-local)*

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
*Tier: 2 (required outcome — adapter procedure)*

After this step, the AI MUST have verified that all required MCP and runtime
dependencies are present. If any required dependency is missing, the install
is halted and the user is informed.

**Required (at least one):**
- [ ] GitHub MCP — check if you can call a GitHub tool.
- [ ] GitLab MCP — check if you can call a GitLab tool.

If neither is available, tell the user and ask them to install the appropriate
MCP server before continuing.

## 3. Create Installation Directory
*Tier: 1 (mechanical)*

Create `{{config.install_dir}}` if it does not exist. Copy all files from
`scripts/` in this bundle to `{{config.install_dir}}/scripts/`.

## 4. Write config.json
*Tier: 1 (mechanical)*

Write `{{config.install_dir}}/config.json` with the configured values:

```json
{
  "platform": "{{config.platform}}",
  "install_dir": "{{config.install_dir}}",
  "reviewers": {{config.reviewers}},
  "teams_access_token": ""
}
```

Do not write `api_token` to this file — store it per its `storage: keychain`
declaration.

## 5. Make skills discoverable to the host runtime
*Tier: 2 (required outcome — adapter procedure)*

After this step, the host runtime MUST be able to load each skill in
`components/skills/` when its trigger phrases appear. The procedure depends
on the runtime — consult `adapters/runtime/<your-platform>/install-skill.md`
for platform conventions and a worked example.

**Verification:** the AI installer should be able to articulate, in one
sentence, the runtime mechanism that will load the skill (e.g., "files in
`~/.codex/skills/` are loaded because `AGENTS.md` references them" or
"skills in the Personal Skills folder are auto-discovered by Cowork's UI").
If it can't, registration is incomplete.

## 6. Make artifacts available on the host runtime
*Tier: 2 (required outcome — adapter procedure)*

After this step, each artifact declared in the package MUST be in a form the
user can open and the runtime can update. On platforms supporting HTML
artifacts (Cowork), this typically means an artifact card; on platforms
without HTML support (Codex, Claude Code), it means the markdown fallback
file is in place at a known location.

Consult `adapters/runtime/<your-platform>/install-skill.md` for the platform's
artifact mechanism.

## 7. Make protocols invocable on the host runtime
*Tier: 2 (required outcome — adapter procedure)*

After this step, each protocol's trigger phrase MUST be recognized by the
host runtime. Registration mechanism depends on the runtime — slash
commands, remembered instructions, AGENTS.md stanzas, or skill-level
trigger declarations.

For each protocol: read `components/protocols/<protocol>.md`. Substitute
all `{{config.*}}` references. Apply registration per
`adapters/runtime/<your-platform>/install-skill.md`.

## 8. Write installed.json
*Tier: 1 (mechanical)*

Write `{{config.install_dir}}/installed.json` per the [installed.json schema](#installedjson):

```json
{
  "package": "ai-code-review-flow",
  "version": "1.3.0",
  "installed_at": "<current ISO-8601 timestamp>",
  "platform": "<detected platform context>",
  "a3ip_spec": "1.9",
  "config_dir": "{{config.install_dir}}",
  "install_method": "<runtime-appropriate value>"
}
```

## 9. Confirm
*Tier: 2 (required outcome)*

After this step, the user MUST know what was installed, what was degraded
(if anything), and how to invoke the workflow.

Tell the user:
- What was installed successfully
- What MCP was connected (GitHub or GitLab)
- How to trigger the workflow ("say 'move to code review'")
- Any degraded features (e.g., markdown fallback instead of HTML artifact)

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

### Tier marker conventions

Tier markers appear on the line immediately after the step heading, in italics. Three forms are valid:

- `*Tier: 1 (mechanical)*` — the procedure is the outcome.
- `*Tier: 2 (required outcome — adapter procedure)*` — outcome mandated by spec; procedure described by adapter.
- `*Tier: 2 (required outcome)*` — outcome mandated by spec; procedure is the AI's reasoning.

INSTALL.md files without tier markers remain valid (Check 12 falls back to a coarser heuristic). New authoring SHOULD include markers.

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

## [1.3.0] — 2026-06-01

### Breaking changes
None.

### Config changes
None.

### Files changed
- `INSTALL.md` — re-framed Tier 2 install steps as outcomes (per spec v1.9)
- `adapters/runtime/cowork/install-skill.md` — re-cast as knowledge artifact
- `adapters/runtime/codex/install-skill.md` — re-cast as knowledge artifact; adds AGENTS.md registration guidance
- `manifest.yaml` — `min_a3ip_spec` bumped to "1.9"

### New dependencies
None.

### Upgrade steps (from 1.2.x)

1. Re-read INSTALL.md fully; Steps 5/6/7 are now outcome-shaped.
   The procedures live in the runtime adapter.
2. On Codex: re-run skill registration per the updated adapter
   (AGENTS.md stanza must be present for the runtime to load the skill).
3. No config changes required. Your existing `config.json` remains valid.

### What changed (human summary)

INSTALL.md and adapters re-aligned to spec v1.9. The Codex install
sequence now correctly establishes runtime discoverability — previous
versions left the skill files in place but unregistered.

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
| New required config key (no default) | Yes |
| Config key removed or renamed | Yes |
| Config type changed | Yes |
| New required MCP dependency | Yes |
| Script interface changed (new required param) | Yes |
| New optional config key (has default) | No |
| New optional MCP dependency | No |
| Script file replaced (same interface) | No |
| Artifact HTML updated | No |
| Protocol steps changed | No |
| New script added | No |
| Bug fix with no interface change | No |

---

## installed.json

`installed.json` is written by the AI to the package's config directory immediately after a successful installation or upgrade. It is the machine-readable record of what version is installed and where.

```json
{
  "package": "ai-code-review-flow",
  "version": "1.3.0",
  "installed_at": "2026-06-01T14:32:00Z",
  "upgraded_from": "1.2.1",
  "platform": "cowork",
  "a3ip_spec": "1.9",
  "config_dir": "C:/Users/you/.claude/packages/ai-code-review-flow",
  "install_method": "cowork-skill",
  "registry_source": "https://raw.githubusercontent.com/a3ip-standard/packages/main/registry.yaml",
  "source_bundle": "C:/Users/you/Downloads/ai-code-review-flow-v1.3.0.a3ip.bundle",
  "workspace_dir": "C:/Users/you/projects/my-app",
  "backup_dir": "C:/Users/you/.claude/backups/ai-code-review-flow-20260601T143200Z"
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

**Code Review Requested**

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

1. **Platform agnostic by default.** Components are described at intent level. Platform-specific knowledge goes in `adapters/runtime/<platform>/` and `adapters/os/<host>/`.
2. **OS agnostic by default.** Scripts must provide a cross-platform Python implementation. OS-specific alternatives live in `adapters/os/<host>/scripts/`.
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
14. **Validate before you ship.** A package that hasn't passed all validation checks is not ready to distribute. Validation is a gate, not a suggestion.
15. **Discoverable by default.** A package without a registry entry can only be installed by direct bundle transfer. Authors should publish to a registry so their packages can be found, updated, and composed into larger ecosystems.
16. **Adapters are knowledge, not scripts.** Adapter documents at `adapters/runtime/<X>/` and `adapters/os/<X>/` describe platform conventions for the installing AI to reason about, not procedures for it to execute verbatim. The installing AI is trusted to apply the knowledge to the install in front of it. (v1.9+)
17. **Outcomes, not procedures, at Tier 2.** INSTALL.md steps state what must be true after each step, not what commands to run. The procedure to satisfy the outcome on a specific runtime lives in the runtime adapter. (v1.9+)

---

## Relationship to Existing Standards

| Concept | SKILL.md | APM | A3IP |
|---|---|---|---|
| Portable skills | Core format | Supports | Adopts SKILL.md exactly |
| MCP dependency declarations | — | Yes | Yes |
| AI-readable install guide | — | — | `INSTALL.md` |
| Installation wizard | — | — | `CONFIGURE.md` |
| Permission declarations | — | — | `permissions:` block |
| Script trust levels | — | — | `trust_level:` |
| Delta upgrades | — | — | `CHANGELOG.md` + `installed.json` |
| Sensitive config handling | — | — | `sensitive:` + `storage:` |
| Package registry format | — | — | `registry.yaml` |
| Plain-text bundle format | — | — | `.a3ip.bundle` |
| Outcome-shaped install contract | — | — | Tier 2 outcomes + runtime adapters (v1.9+) |

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
| `1.7` | 2026-05-16 | Two-tier adapter model (`adapters/os/{windows,posix}/` × `adapters/runtime/<name>/`); Check 10 (INSTALL.md spec compliance) |
| `1.8` | 2026-05-19 | INSTALL.md tool-agnostic language; `installed.json` schema formalized with optional fields; `adapters/runtime/codex/` recognized; cross-product tool-selection table relocated to `TOOL-AUTHORS.md` |
| `1.9` | 2026-05-21 | Re-alignment to three-tier concept: INSTALL.md Tier 2 steps re-framed as outcomes (Steps 5/6/7); tier markers on step headers; new "Writing Adapter Documents" section formalizes adapters as Tier 3 platform-knowledge; Platform Context Detection as Tier 3 semantic; Validation reconciled to 10 checks plus three new advisory warnings (Checks 11/12/13). All backward-compatible. Uninstall deferred to v1.10. |

All packages authored under v1.0–v1.8 remain fully valid under v1.9.

---

*A3IP Specification v1.9 — Complete consolidated edition*
*© 2026 Maksym Prydorozhko · [a3ip.dev](https://a3ip.dev) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)*
