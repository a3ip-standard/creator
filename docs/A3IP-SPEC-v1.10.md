# A3IP Specification v1.10

*Note: v1.10 supersedes v1.9. All v1.9 packages remain valid v1.10 packages — uninstall is additive. v1.10 closes the package lifecycle by adding the uninstall flow that v1.9 deferred. Changes: (a) new normative `## Uninstalling` section in the INSTALL.md template, with Tier-marked steps UN1–UN8; (b) `adapters/runtime/<X>/uninstall-skill.md` as the canonical location for per-runtime uninstall knowledge, parallel to `install-skill.md`; (c) Writing Adapter Documents section extended to require both-direction coverage for any Tier 2 outcome the adapter addresses; (d) existing-install discovery promoted to a Tier 2 outcome — the spec no longer prescribes a platform-default detection path; runtime adapters describe HOW to locate prior installs on each platform; (e) new `preserve_on_uninstall` field on configuration schema keys, replacing a single uniform uninstall policy with per-key, author-declared policy; (f) Validation Check 14 (Warning) — INSTALL.md should contain an `## Uninstalling` section; (g) new normative `### Bundle preamble` subsection under Bundle Format — the prose between frontmatter and first FILE marker MUST direct the receiving AI to read INSTALL.md and the runtime adapter, and MUST name the "improvising from bundle structure" failure mode the preamble exists to prevent. All changes are additive; no installation behavior changes.*

## What's new in v1.10

v1.10 closes the install/upgrade/uninstall lifecycle. v1.9 deferred uninstall to its own design pass because doing it right required deciding several things the install model didn't pre-answer: the symmetry between install outcomes (Steps 5/6/7) and uninstall outcomes (Steps UN3/UN4/UN5), how the AI locates a prior install when the user comes back to remove it months later, and how to handle user-owned data (`config.json` — API tokens, project refs) that survives the workflow. v1.10 settles all of them.

**(a) New `## Uninstalling` section in INSTALL.md template.** The lifecycle from v1.0 through v1.9 covered install and upgrade — uninstall was absent. v1.10 closes the gap with eight steps (UN1–UN8), tier-marked the same way install steps are: UN3/UN4/UN5 are Tier 2 (outcome — adapter procedure), each the symmetric un-doing of install Steps 5/6/7; UN1 is Tier 2 (existing-install discovery, paired with INSTALL.md Step 1 — see (d) below); the remaining steps are Tier 1 (mechanical):

| Install (v1.9) | Uninstall (v1.10) |
|---|---|
| 1. Check for existing installation | UN1. Locate the existing install (paired with Step 1) |
| 5. Make skills discoverable to the host runtime | UN3. Make skills un-discoverable to the host runtime |
| 6. Make artifacts available on the host runtime | UN4. Remove artifacts from the host runtime |
| 7. Make protocols invocable on the host runtime | UN5. Make protocols no longer invocable |

The symmetry isn't decorative — it means an adapter that knows how to register a skill on Codex (write the AGENTS.md marker block) also knows the inverse (remove the marker block). The adapter knowledge is paired by construction; see (b).

**(b) New adapter file: `adapters/runtime/<X>/uninstall-skill.md`.** Parallel to `install-skill.md`, this file holds the per-runtime knowledge required to satisfy UN1/UN3/UN4/UN5 on platform `<X>`. The naming convention is normative — the installing AI and the validator both rely on the filename. Adapter authors maintain one install file and one uninstall file per platform; the Creator's scaffold generates both. Folding them into a single file was considered and rejected: the two procedures often span different code paths (e.g., Codex's install touches `~/.codex/skills/` and `~/.codex/AGENTS.md`; uninstall touches the same two locations but with different operations), and keeping the per-step adapter knowledge in adjacent files makes both easier to read and easier for a validator to assert coverage symmetry.

**(c) "Writing Adapter Documents" — both-direction coverage rule.** The v1.9 section that formalized adapters as Tier 3 platform-knowledge artifacts now adds one normative requirement: an adapter that addresses a Tier 2 install outcome (Steps 1/5/6/7) MUST have a paired uninstall adapter addressing the symmetric uninstall outcome (Steps UN1/UN3/UN4/UN5). This is the "knowledge that is wrong is worse than no knowledge" principle applied symmetrically — uninstall knowledge written without install context (or vice versa) drifts and breaks. Adapter authors satisfy the rule by maintaining `install-skill.md` and `uninstall-skill.md` as a pair.

**(d) Existing-install discovery is a Tier 2 outcome.** Earlier v1.10 drafts prescribed "look at the platform-default install location" in INSTALL.md Step 1 and Uninstall Step UN1. That language has been removed. The spec now states the outcome — "the AI MUST know whether this package is already installed on the host" — and delegates HOW to the runtime adapter, exactly as Steps 5/6/7 and UN3/UN4/UN5 do for their respective outcomes. The rationale is the same one that drove the v1.7 two-tier adapter model: a platform may reorganize its package conventions (move from `~/.claude/packages/` to a per-user index, register installs through a system service, etc.), but the spec's contract with the package author should not change. By making discovery a Tier 2 outcome, the spec is platform-neutral by construction; the platform's adapter carries whatever discovery mechanism is current on that platform. This also makes custom `install_dir` values cleanly supportable — the adapter's discovery routine determines how (and whether) custom locations are reachable, rather than the spec mandating a single lookup path that fails on non-default installs.

**(e) Per-key `preserve_on_uninstall` on configuration schema.** The first v1.10 drafts mandated a single binary choice at uninstall time — preserve `config.json` entirely or purge it entirely — and made the AI ask the user every time. That conflates the policy decision (which values are precious vs. throwaway) with the user's confirmation. The policy is properly the package author's domain: only the author knows that the API token is worth keeping while the install timestamp is not. v1.10 introduces a new field, `preserve_on_uninstall: true | false | "ask"`, that the author MAY set on each entry in the configuration schema. Default per key (if the field is omitted) is `"ask"`. Step UN2 walks the schema during the Uninstall Plan: keys marked `true` are silently preserved, keys marked `false` are silently purged, and only keys marked (or defaulting to) `"ask"` prompt the user for a per-key decision. This preserves user control where it matters and removes friction where it doesn't.

**(f) Validation Check 14 (Warning).** INSTALL.md SHOULD contain an `## Uninstalling` section. Warning if absent — gentle adoption now, hardened to error in v2.0 (the same trajectory as Checks 11/12/13 from v1.9). The check is structural: it looks for the section header. Step structure inside the section is the author's responsibility.

**(g) Normative bundle preamble.** The patch on 2026-05-25 added a new
`### Bundle preamble` subsection under `## Bundle Format`. Earlier v1.10 drafts
left the prose between bundle frontmatter and the first FILE marker entirely up
to the bundler. In practice this produced informational headers that AIs read
and then ignored — improvising install procedures from the raw `=== FILE: ===`
structure rather than reading INSTALL.md and the runtime adapter. The Codex
install of `ai-code-review-flow` v1.4.0 exhibited exactly this failure mode.
The fix makes the preamble normative: it MUST direct the receiving AI to read
INSTALL.md as the procedure outline, MUST name the runtime adapter as the
platform-knowledge source, MUST clarify that both are knowledge to reason about
rather than scripts to execute, and MUST name the "improvising from bundle
structure" failure mode the preamble exists to prevent. Exact wording is the
bundler's choice; the outcomes are the spec's. The `## Consuming a bundle`
checklist was also updated in lockstep so the install-time procedure surfaces
the preamble-reading step explicitly.

**Backward compatibility:** All v1.9 packages remain valid under v1.10. Uninstall is additive — a package without an `## Uninstalling` section still installs and upgrades correctly; the validator emits Check 14 as a warning, not an error. Packages without `uninstall-skill.md` adapter files have no install behavior change either; the warning surfaces in Check 11 (now extended to scan both install and uninstall coverage). Configuration schemas without `preserve_on_uninstall` fields are valid — every key defaults to `"ask"`, matching pre-v1.10 expectations. The new adapter file convention is normative for new authoring; packages predating v1.10 are not retroactively required to add uninstall coverage to ship. The normative bundle preamble applies to bundlers, not to packages — pre-v1.10.1 bundles in the wild remain readable; the new MUSTs constrain how `a3ip` CLI v1.5.1+ and other bundlers emit new bundles, not what already-issued bundles must contain.

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

### Bundle preamble

The bundle preamble is the prose block that appears between the closing
frontmatter `---` and the first `=== FILE: ===` marker. It is the first
content a receiving AI reads, and its job is to anchor that AI to the
package's install knowledge.

**A bundle MUST include a preamble** between the frontmatter and the
first FILE marker, and the preamble MUST point the receiving AI at the
in-bundle install knowledge: `INSTALL.md` and the runtime adapter at
`adapters/runtime/<platform>/install-skill.md`. Without that pointer, an
AI lacking prior A3IP familiarity has no signal anchoring it to the
install contract.

How the preamble is phrased is the bundler's choice. The spec mandates
the outcome (the AI reaches INSTALL.md and the runtime adapter), not
specific prose, framing, or enumeration. Bundlers may include additional
context as fits their project: scope notes about the CLI vs. installer
role, fallback guidance if knowledge artifacts are missing, project- or
language-specific commentary.

**Format convention.** Preambles are commonly formatted as a comment
block (lines beginning with `#`) to visually separate them from the FILE
markers, but the spec does not require this — a bundler may use any
plain-text format that is unambiguous to identify as a preamble (i.e.
not parseable as a `=== FILE: ===` marker).

**Reference implementation:** the `a3ip` CLI's `bundle.py` emits a
preamble that satisfies the above. Authors implementing a new bundler
may use its preamble as a starting point and adapt to their project.

### Generating a bundle

```
For each file in the package (recursively, sorted by path):
  Write: === FILE: <relative path> ===
  Write: <file contents verbatim>
  Write: === END FILE ===
```

### Consuming a bundle

When an AI receives a `.a3ip.bundle` file or its contents, a conformant
install reaches these outcomes:

- The package's frontmatter, preamble, and embedded files are parsed.
- The install knowledge inside the bundle — `INSTALL.md` and the relevant
  `adapters/runtime/<platform>/install-skill.md` — is read and applied
  before any side-effecting action.
- Files are written to disk only as INSTALL.md and the adapter direct.

How the AI sequences the parse, what tools it uses, and how it recovers
from a malformed delimiter or a missing knowledge artifact are
implementation. The contract is that the AI installs from the bundle's
install knowledge, not by inferring layout from the file structure
alone.

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

6. **Make the mechanism articulable.** A reader of the adapter section should be able to summarize the platform mechanism in one sentence after reading it — "files in `~/.codex/skills/` are loaded because `AGENTS.md` references them," "skills in the Personal Skills folder are auto-discovered by Cowork's UI." If the section reads as instructions without surfacing the underlying mechanism, the AI gets a procedure but loses the model — and cannot recover when the procedure fails for reasons outside the documented path. Articulability is the test of whether the adapter is teaching, not just dictating.

### When script-shape is unavoidable

There are cases where a procedural code block legitimately belongs in an adapter: bootstrap scenarios where the platform has no established conventions yet, or operations where the exact sequence matters (e.g., creating a directory before substituting paths). In those cases:

- Wrap the script in clear illustrative framing: "Bootstrap example for first-time Cursor support — establishes the convention; subsequent installs should match this shape."
- Explain *why* the sequence matters, so the AI can preserve the invariant even if it varies the surface form.
- Place the script after the convention prose, not before.

Over time, as a platform's behavior stabilizes, adapter authors should shift such sections from script-shaped to knowledge-shaped — replacing "here's the script that worked" content with "here's the convention." That's the natural maturation path. Check 13 (warning) flags adapters that don't make this transition.

### Adapter coverage for Tier 2 outcomes

Each platform's runtime adapter SHOULD address each Tier 2 outcome in [INSTALL.md](#installmd) that its platform influences:

- Step 1 (existing-install discovery, v1.10+) — every runtime adapter should describe how to determine whether a prior install of a package exists on the platform, and how to locate its `config_dir`. The same discovery mechanism is reused by Uninstall Step UN1, so `install-skill.md` and `uninstall-skill.md` MAY cross-reference rather than duplicate.
- Step 5 (skills discoverable) — every runtime adapter should describe how the platform discovers/loads skills.
- Step 6 (artifacts available) — every runtime adapter should describe its artifact mechanism (HTML support, markdown fallback, etc.).
- Step 7 (protocols invocable) — every runtime adapter should describe its trigger/registration mechanism.

[Check 11](#check-11--adapter-outcome-coverage-v19) (warning) flags missing coverage. The check is a cheap surface heuristic; the proper test is dogfood installation on the target platform.

### Paired install / uninstall adapter files (v1.10)

Each platform's runtime adapter is a pair of files, not a single file:

- `adapters/runtime/<X>/install-skill.md` — knowledge for satisfying install Steps 5/6/7 on platform `<X>`.
- `adapters/runtime/<X>/uninstall-skill.md` — knowledge for satisfying uninstall Steps UN3/UN4/UN5 on platform `<X>`.

The filenames are normative — the installing AI looks for them by exact name when entering the install or uninstall flow, and the validator's coverage checks scan them separately. Authors maintain both as a pair.

**Both-direction coverage rule.** An adapter that documents how to satisfy an install outcome (Step 1, 5, 6, or 7) MUST also document how to satisfy the symmetric uninstall outcome (Step UN1, UN3, UN4, or UN5 respectively) on the same platform. Asymmetric coverage — install knowledge with no uninstall counterpart — is the v1.10 equivalent of the "knowledge that is wrong is worse than no knowledge" problem: an installing AI that can register a Codex skill but can't deregister it leaves users unable to cleanly remove what they installed; an adapter that knows how to find an existing install but doesn't describe the inverse for uninstall is equally broken.

The rule is satisfied by writing both files. The symmetry is at the file-presence level, not line-by-line — `uninstall-skill.md` does not need to mirror `install-skill.md` structurally, only to address the corresponding outcomes.

[Check 11](#check-11--adapter-outcome-coverage-v19) was extended in v1.10 to enforce this: the coverage matrix now includes both install and uninstall adapter files per platform.

**Knowledge shape applies equally.** All five writing-discipline rules above apply to `uninstall-skill.md` exactly as they do to `install-skill.md`. Uninstall code is illustration; uninstall conventions are knowledge. Adapter authors who lapse into procedure-shape for uninstall (the equivalent of "Run this PowerShell to delete the skill") trigger [Check 13](#check-13--adapter-knowledge-shape-v19), which v1.10 extends to scan uninstall files too.

**Worked example pairing (illustrative, Codex):**

Install adapter (excerpt):

> On Codex, skill registration happens by appending a marker-bounded stanza to `~/.codex/AGENTS.md`. The stanza references the absolute path to `SKILL.md` in `~/.codex/skills/<name>/`. AGENTS.md is loaded as a persistent system instruction at session start; the registration is what makes the trigger phrases discoverable.

Uninstall adapter (excerpt):

> Uninstall on Codex reverses the AGENTS.md registration before touching the skill files. Locate the `<!-- a3ip:<package>:start --> ... <!-- a3ip:<package>:end -->` block in `~/.codex/AGENTS.md` and remove the entire block, preserving the rest of the file. Once the block is gone, the trigger phrases are no longer registered — even if the skill files remain, Codex will not load them on the next session start.

The two together form the platform's knowledge for skill discoverability — install and uninstall described as inverses of the same mechanism (AGENTS.md registration), not as two unrelated procedures.

---

## Validation

A conformant A3IP validator implements the 10 normative checks defined in this section, plus 4 advisory warning checks (3 added in v1.9, 1 added in v1.10). Checks 1–7 apply to all packages; Checks 8–9 apply only to packages using v1.2 security fields; Check 10 was added in v1.7 (INSTALL.md spec compliance); Checks 11–13 were added in v1.9 (re-alignment warnings); Check 14 was added in v1.10 (uninstall coverage). Checks 11 and 13 were extended in v1.10 to scan both `install-skill.md` and `uninstall-skill.md` adapter files.

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

**Rule:** Each platform listed in `platforms.tested` whose adapter exists at `adapters/runtime/<X>/install-skill.md` SHOULD reference each Tier 2 outcome it influences (Steps 1, 5, 6, 7 of the canonical INSTALL.md). Specifically: the adapter should contain content addressing existing-install discovery, skill discovery, artifact availability, and protocol invocability for any of those component categories the package declares.

**Detection:** The validator scans the adapter for references to each outcome step's keywords ("existing install", "installed.json", "discovery", "locate", "skills", "artifacts", "protocols") or to the outcome names ("discoverable", "available", "invocable").

**Outcome:** Warning for each (platform, outcome) pair where the platform's adapter doesn't reference the outcome.

**Rationale:** Adapters that don't address the outcomes they should are the v1.2.x → v1.2.2 Codex-bug class. The check is a cheap surface heuristic; the proper test is dogfood installation on the target platform.

**v1.10 amendment:** Step 1 (existing-install discovery) was promoted from a spec-prescribed mechanism to a Tier 2 outcome in v1.10; adapters MUST now describe their platform's discovery mechanism. The check scans for the discovery outcome alongside Steps 5/6/7.

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

**v1.10 amendment:** the check now scans both `install-skill.md` AND `uninstall-skill.md` adapter files (added in v1.10). Threshold and outcome are identical for both filenames.

---

### Check 14 — INSTALL.md uninstall coverage (v1.10+)

**Rule:** `INSTALL.md` SHOULD contain a top-level `## Uninstalling` section. The section is the documented entry point for the uninstall flow (Steps UN1–UN8 in the canonical template).

**Detection:** Pattern-match the file for an `^## Uninstalling` heading.

**Outcome:** Warning if absent. The warning includes the suggested template reference: `INSTALL.md is missing the '## Uninstalling' section. See A3IP spec v1.10 INSTALL.md template for the canonical Steps UN1–UN8.`

**Rationale:** The install/upgrade/uninstall lifecycle is incomplete without uninstall. Packages predating v1.10 SHOULD add the section on their next version bump; new packages MUST add it. The check is a warning in v1.10 (gentle adoption) and is planned to become an error in v2.0, the same trajectory as Checks 11/12/13.

**Companion check on adapters:** Check 11 (Adapter outcome coverage) is extended in v1.10 to scan both `install-skill.md` and `uninstall-skill.md` per platform. The (platform, outcome) coverage matrix is checked against the install outcomes (Steps 1, 5, 6, 7) for the install adapter and the uninstall outcomes (Steps UN1, UN3, UN4, UN5) for the uninstall adapter.

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
| 11 | Adapter outcome coverage (install + uninstall) | Warning | v1.9 (extended v1.10) |
| 12 | INSTALL.md tier shape | Warning | v1.9 |
| 13 | Adapter knowledge-shape (install + uninstall) | Warning | v1.9 (extended v1.10) |
| 14 | INSTALL.md uninstall coverage | Warning | **v1.10** |

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
    preserve_on_uninstall: true        # credential — keep across uninstall to avoid re-issuing

  - key: install_dir
    label: "Installation directory"
    description: "Absolute path where the package will store its files."
    type: string
    required: true
    placeholder: "C:\\Users\\you\\.claude\\code-review"
    when: before
    preserve_on_uninstall: false       # meaningless after uninstall — purge silently

  - key: reviewers
    label: "Default reviewers"
    description: "Usernames to assign as reviewers on new review requests."
    type: list<string>
    required: true
    placeholder: "@username"
    when: before
    preserve_on_uninstall: ask         # user-curated list — confirm at uninstall time

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
    preserve_on_uninstall: true        # OAuth token — keep so re-install does not re-prompt

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

### `preserve_on_uninstall:` field on configuration keys (v1.10+)

Declares the package author's policy for what should happen to this config key's value when the user uninstalls the package. The installing AI consults this field during Step UN2 (the Uninstall Plan) and acts accordingly in Step UN6.

| Value | Meaning |
|---|---|
| `ask` | Default. The AI asks the user at uninstall time whether to keep or remove this key's value. Use when the right answer depends on the user's situation (a list of project members might or might not be worth keeping). |
| `true` | The key's value is silently preserved across uninstall. Use for hard-earned credentials and tokens that would be friction to re-issue (API tokens, OAuth refresh tokens). A future re-install reuses the preserved value without re-prompting. |
| `false` | The key's value is silently purged at uninstall. Use for values that are meaningless after the package is gone (the install directory path itself, install timestamps, transient state). |

If the field is omitted, the AI MUST treat the key as `ask`. This preserves pre-v1.10 behavior — older packages without per-key annotations still uninstall correctly; the AI simply prompts for every key.

The field applies regardless of the `storage:` location. A key stored in the OS keychain with `preserve_on_uninstall: false` is removed from the keychain at uninstall; a key stored in `config.json` with `preserve_on_uninstall: true` survives even when the rest of `config.json` is purged (the AI rewrites `config.json` containing only the preserved keys).

**Worked example — a single `config.json` after the user uninstalls a package whose `api_token` is `preserve_on_uninstall: true`, `reviewers` was answered "preserve" at the prompt, and `install_dir` was `preserve_on_uninstall: false`:**

```json
{
  "api_token": "ghp-...",
  "reviewers": ["@alice", "@bob"]
}
```

The `install_dir` key is gone; everything else the user wanted kept survives.

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
exists on the host, and if so where its `config_dir` lives.

The discovery mechanism is host-runtime-specific — read
`adapters/runtime/<platform>/install-skill.md` for how to locate prior installs
on the current platform. The adapter is responsible for whatever lookup is
idiomatic on its platform (scanning a conventional package home, reading a
per-runtime index, consulting a system service, following pointer files for
custom install locations, etc.). The spec does not prescribe a single
detection path.

- **Not found:** proceed with the full install steps below.
- **Found:** the adapter returns the `config_dir` of the existing install. Read
  `installed.json` at that path for the installed version and any other fields
  needed downstream, then go directly to [## Upgrading](#upgrading).

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

---

## Uninstalling

Triggered when the user says "uninstall <package>", "remove <package>", "get rid of <package>", or equivalent. Uninstall is idempotent — running it on a package whose `installed.json` is already absent is a no-op, not an error.

### Step UN1 — Locate the existing install
*Tier: 2 (required outcome — adapter procedure)*

After this step, the AI MUST know whether this package is installed on the host, and if so where its `config_dir` lives.

The discovery mechanism is host-runtime-specific — read `adapters/runtime/<platform>/uninstall-skill.md` for how to locate prior installs on the current platform. This is the symmetric counterpart of INSTALL.md Step 1's discovery; the same adapter knowledge applies (the install adapter and uninstall adapter SHOULD describe the same lookup mechanism, since they are answering the same question from opposite ends of the lifecycle).

- **Not found:** tell the user there is nothing to uninstall and exit cleanly. Steps UN2 onward are skipped.
- **Found:** the adapter returns the `config_dir` of the existing install. Read `installed.json` at that path and capture `version`, `platform`, `config_dir`, and `install_method` — they drive every subsequent uninstall step.

### Step UN2 — Show the Uninstall Plan and resolve per-key config policy
*Tier: 1 (mechanical)*

Present an Uninstall Plan that lists, item by item:

- The skill files that will be removed (paths derived per the platform's adapter).
- The artifacts that will be removed (artifact names and their host-runtime mechanism).
- Any host-runtime registrations that will be reverted (e.g., on Codex: removal of the `<!-- a3ip:<package>:start --> ... <!-- a3ip:<package>:end -->` block from `~/.codex/AGENTS.md`).
- The per-key disposition of every configuration value (see below).
- The `installed.json` file that will be removed.

**Resolving the config-key policy.** Walk every entry in the `configuration:` block of `manifest.yaml` and consult its [`preserve_on_uninstall:` field](#preserve_on_uninstall-field-on-configuration-keys-v110):

- `true` — silently classified as *preserve*. The user is NOT asked. The plan SHOULD list the key under "values that will be kept" so the user can see what survives.
- `false` — silently classified as *purge*. The user is NOT asked. The plan SHOULD list the key under "values that will be removed".
- `ask` (or field omitted) — the AI MUST ask the user, per key, whether to preserve or remove that value. Present each `ask` key as a separate inline question with enough context for the user to answer (the key's `label:` and `description:` from the schema, plus a brief reminder of what's stored). Capture each answer and add it to the plan under preserve or remove accordingly.

After all `ask` keys have been resolved, the plan ends with **Confirm to proceed.**

If the user declines confirmation, the AI aborts. No files are removed, no registrations are reverted, the original install remains intact.

The resolved per-key decisions (preserve vs. purge for every key) carry forward to Step UN6, which applies them.

### Step UN3 — Make skills un-discoverable to the host runtime
*Tier: 2 (required outcome — adapter procedure)*

After this step, the host runtime MUST NOT load any skill from `components/skills/` in response to its trigger phrases. The procedure depends on how skills were made discoverable in install Step 5 — read `adapters/runtime/<platform>/uninstall-skill.md` for the platform-specific procedure.

The exact mechanism varies: removing files from a skills directory, removing a marker-bounded stanza from a persistent-instructions file, calling a runtime-specific deregistration tool, or some combination. The outcome is the same: trigger phrases that previously loaded this package's skill must now have no effect related to this package.

### Step UN4 — Remove artifacts from the host runtime
*Tier: 2 (required outcome — adapter procedure)*

After this step, the host runtime MUST NOT surface any artifact this package created in install Step 6. On a runtime with a first-class artifact registry (e.g., Cowork's `mcp__cowork__list_artifacts` / `delete_artifact`), this means calling the platform's deletion mechanism. On a runtime without an artifact registry (e.g., Codex, where artifacts degrade to markdown files), this means removing the markdown file(s).

Artifacts that contain ONLY persisted state (no fresh runtime-generated content) MAY be preserved at the AI's discretion when at least one configuration key was resolved to *preserve* in Step UN2 — the package's user-facing state was clearly meant to survive, and an artifact that just reflects that state can survive with it. The default is to remove artifacts unconditionally; the adapter MAY override if the artifact represents user data the user would want to keep.

### Step UN5 — Make protocols no longer invocable
*Tier: 2 (required outcome — adapter procedure)*

After this step, the host runtime MUST NOT recognize this package's protocol trigger phrases. On runtimes where protocol discovery is a side-effect of skill discovery (Cowork's `description:` frontmatter loaded with the skill), this is a no-op once UN3 completes. On runtimes that register protocols separately, the adapter describes the deregistration procedure.

### Step UN6 — Remove install_dir contents
*Tier: 1 (mechanical)*

After UN6, the following end-state holds:

- `{{config.install_dir}}/config.json` (if present) contains only the
  configuration keys whose disposition from UN2 is *preserve*. If the set
  of preserved keys is empty, the file is gone.
- For any preserved key whose `storage:` field is something other than
  `config-file` (e.g., `keychain`), the value remains in that storage.
  For any purged key with non-`config-file` storage, the value has been
  removed from that storage. The runtime adapter is the authority on the
  per-storage mechanism.
- No other files from the package install remain in
  `{{config.install_dir}}`. Subdirectories the install side created
  (`scripts/`, generated state, etc.) are gone.
- `installed.json` is untouched in this step. It survives to UN7 so that
  the uninstall stays observable until the last step lands; if UN6 fails
  partway, the next run sees `installed.json` and resumes.

### Step UN7 — Remove installed.json
*Tier: 1 (mechanical)*

Remove `{{config.install_dir}}/installed.json`. After this step, INSTALL.md Step 1 / Step UN1 (existing-installation discovery) returns "no install" on subsequent runs, making the uninstall idempotent.

If, after `installed.json` is removed, the install directory is empty (no preserved `config.json`, no other preserved files), the AI SHOULD remove the empty install directory as well. If preserved values remain (a trimmed `config.json`, for example), the install directory survives so the user can find them.

### Step UN8 — Confirm to the user
*Tier: 1 (mechanical)*

Tell the user the uninstall completed. Name (1) the version that was uninstalled, (2) which configuration keys were preserved (by name) and where the preserved values live (typically a trimmed `config.json` at the original config directory, plus any keychain entries that survived), (3) which keys were purged, and (4) any leftover state the user may want to know about (e.g., on Codex, mention that the AGENTS.md stanza was removed and the file's other content is unchanged).
```

### `## Plan` section rules

- Must appear after the existing-installation check and before the first numbered action step.
- Must list every file written, every network domain contacted, every MCP tool invoked, and every shell command run.
- Must end with **Confirm to proceed.**
- The AI must not skip or summarize the Plan section.
- If the user declines, the AI aborts. No partial install state is written.

### `## Uninstalling` section rules

- Step UN1 is Tier 2 (required outcome — adapter procedure). It is the symmetric counterpart of INSTALL.md Step 1; both use the runtime adapter to locate prior installs on the host. The spec does NOT prescribe a fixed lookup path (e.g., a platform-default directory) — that knowledge lives in `adapters/runtime/<platform>/uninstall-skill.md`.
- Step UN2 is Tier 1. The Uninstall Plan MUST walk the `configuration:` block of `manifest.yaml` and resolve a preserve-or-purge disposition for every key, using each key's `preserve_on_uninstall` field. Keys with `preserve_on_uninstall: true` are silently preserved; keys with `false` are silently purged; keys with `ask` (or no annotation) trigger a per-key prompt to the user. The plan ends with **Confirm to proceed.**
- Steps UN3, UN4, UN5 are always Tier 2 (required outcome — adapter procedure). Each is the symmetric un-doing of its install counterpart (Steps 5/6/7).
- Steps UN6, UN7, UN8 are always Tier 1. Order matters: `install_dir` contents are reconciled first (UN6 — rewrite `config.json` keeping only preserved keys, remove non-config files), then `installed.json` (UN7), then user-facing confirmation (UN8). Uninstalls that fail mid-flow leave `installed.json` in place, so the next run can resume.
- Uninstall is idempotent: running it on a package whose `installed.json` cannot be located by the adapter is a no-op (Step UN1 exits cleanly), not an error.
- The uninstall flow does NOT have a `## Plan` block of its own — Step UN2 serves the same confirmation role and replaces it.

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
| `1.10` | 2026-05-24 | Uninstall lifecycle: new `## Uninstalling` section in the INSTALL.md template with Tier-marked Steps UN1–UN8; `adapters/runtime/<X>/uninstall-skill.md` as a normative companion to `install-skill.md`; "Writing Adapter Documents" extended with the both-direction coverage rule; existing-install discovery (INSTALL.md Step 1 / Uninstall Step UN1) promoted to Tier 2 outcome — runtime adapters describe HOW; new `preserve_on_uninstall: true \| false \| "ask"` field on configuration schema keys (default `"ask"`) for author-declared per-key uninstall policy; new Check 14 (warning) for INSTALL.md uninstall coverage; Checks 11 and 13 extended to scan both install and uninstall adapter files. Amended 2026-05-25 with normative `### Bundle preamble` subsection — the prose between bundle frontmatter and first FILE marker MUST direct the receiving AI to INSTALL.md + runtime adapter, with knowledge-not-script framing. All backward-compatible. |

All packages authored under v1.0–v1.9 remain fully valid under v1.10.

---

*A3IP Specification v1.10 — Complete consolidated edition*
*© 2026 Maksym Prydorozhko · [a3ip.dev](https://a3ip.dev) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)*
