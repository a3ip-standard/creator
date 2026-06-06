---
name: a3ip-creator
description: >
  Guides the AI through authoring a new A3IP package. Conducts a structured
  intake conversation, then drives the `a3ip` CLI through scaffold, validate,
  and bundle to produce a distributable .a3ip.bundle. Platform-agnostic by
  design — outcomes are stated in this file; runtime-specific HOW lives in
  adjacent adapters/runtime/<platform>/skill-runtime.md files.
  Invoke when the user wants to create a new A3IP package or workflow package.
---

# A3IP Creator Skill

You are the A3IP Creator. Your job is to guide the user through the full A3IP
package lifecycle across eight phases:

0. **Read the Spec** — fetch and read the A3IP specification this package targets, before any other work
0.5. **Detect Platform Context** — call `a3ip platforms` to learn the host OS and AI runtime this Creator is on; use to anchor Intake and adapter scaffolds
1. **Intake** — conversation with the user to collect everything needed
2. **Scaffold** — generate the full package directory from the intake answers
3. **Validate** — run completeness checks; surface and fix all errors
4. **Build** — produce the `.a3ip.bundle` (and optionally `.a3ip.zip`)
5. **Version** — cut a new release: sync changes, bump version, fill CHANGELOG, rebundle
6. **Registry** — browse a registry, install from a bundle URL, check for updates

Read this file completely before beginning. Every rule here exists because of a
real pain point encountered while hand-authoring the first A3IP package.

---

## Runtime adapter consultation

This SKILL.md is platform-agnostic. It states the OUTCOMES each phase must
reach. The HOW for platform-specific operations is described in adjacent
runtime adapter files: `adapters/runtime/<your-platform>/skill-runtime.md`.

Platforms covered first-hand: `cowork`, `codex`, `claude-code`. Others
(`cursor`, future runtimes) are described by similarity or stubbed.

Operations the AI MUST consult the runtime adapter for:

| Operation in this skill | Consult adapter for HOW |
|---|---|
| Read/write a file on disk | Yes — file-tool choice varies by runtime |
| Ask the user a structured question | Yes — some runtimes have native question UIs, others use natural-language prompts |
| Present a file for the user to save (e.g., the .skill zip for Cowork install) | Yes — Cowork has present_files; other runtimes drop the path in chat |
| Build a .skill zip (Cowork-specific install artifact) | Yes — only applies on runtimes whose install path uses .skill |
| Run a `git` operation | Yes — shell choice varies by host OS and runtime sandbox |
| Run a CLI command (`a3ip ...`, `pip ...`, `py -3 ...`) | Yes — host shell selection varies, see adapter |

Operations the AI does NOT need adapter consultation for:

- Calling any `a3ip` CLI subcommand (`scaffold`, `validate`, `bundle`, `sync`,
  `new-version`, `zip`, `platforms`). These are runtime-agnostic by design.
- Reasoning, planning, content composition, intake conversations.

Step 0.5 (Detect Platform Context) tells the AI which adapter file to load.
On runtimes where the adapter is missing, the AI states the outcome each step
needs and asks the user to confirm tool choice when ambiguous.

---

## Phase 0 — Read the Spec

**Before doing anything else in this skill, read the A3IP specification.**

The spec defines all canonical structures: the INSTALL.md template, the
`installed.json` schema, the per-platform Config directory conventions, the
configuration block format, validation rules, and the Upgrading flow. Improvising
any of these — even slightly — produces non-compliant packages that pass the
existing validator but break at install time on real platforms. This has happened
multiple times. Phase 0 is the corrective.

### Step 0.1 — Determine which spec version applies

- **Creating a new package:** ask the user "Which A3IP spec version should this
  package target?" Default to the latest version available in this skill's
  `docs/` folder.
- **Versioning an existing package:** read `min_a3ip_spec:` from the package's
  `manifest.yaml`. That is the spec version the package was authored against.
- **Installing from a bundle:** read the `spec_url:` field in the bundle's
  frontmatter — the version is in the URL filename.

### Step 0.2 — Locate the spec text

In order of preference (web first since v2.1.0 — the canonical spec on GitHub
is always current; the bundled copy is an offline safety net that may lag
behind in-place patches to the same version number):

1. **Web fetch (preferred):** fetch the canonical spec from:
   ```
   https://raw.githubusercontent.com/a3ip-standard/spec/main/docs/A3IP-SPEC-v{version}.md
   ```
   Use whatever web fetch capability is available in your environment. This
   is the authoritative copy and gets any v1.10-style in-place patches.
2. **Local copy (offline fallback):** if web fetch is unavailable or blocked,
   look for `docs/A3IP-SPEC-v{version}.md` next to this SKILL.md file. The
   skill ships with the spec versions it targets. Note: this copy was current
   at the Creator's release time but may have been patched since on GitHub.
3. **Ask the user:** if neither works, ask the user to provide the spec text
   or point you at a local path.

If the version found in Step 0.1 is older than the latest available, tell the
user and offer to bump.

### Step 0.3 — Read the spec end to end

Pay special attention to:

- **INSTALL.md template** — the canonical structure for Step 1 (Check for
  Existing Installation), Step 3 (Create Installation Directory), Step 8 (Write
  installed.json), and the `## Upgrading` section. Every package's INSTALL.md
  MUST follow this template; do not improvise alternative install-detection
  schemes.
- **Required config keys** — the spec lists keys every package must include in
  its `configuration:` block (notably `install_dir`, which drives the entire
  install/upgrade flow). Missing required keys are a Rule 8 violation.
- **Platform Conventions table** — the canonical config directory, skills
  location, and installed.json location for each platform. Cowork's config
  directory is `~/.claude/packages/<package-name>/` per spec — do not invent
  alternatives.
- **`installed.json` schema** — what fields are required and what they mean.
- **Validation rules** — the spec lists the checks `a3ip validate` performs.
  When the validator reports an error, the auto-fix maps to a spec rule.

### Step 0.4 — Treat the spec as canonical for all subsequent phases

For every subsequent phase (Intake, Scaffold, Validate, Build, Version,
Registry), when in doubt about field names, file paths, install order, or
template wording, **return to the spec text you read in Step 0.3 — do not
improvise.** Phase 0 is not "read once and forget"; it is the reference you
hold open in the other tab while doing the work.

---

## Phase 0.5 — Detect Platform Context

After reading the spec, detect the platform context this Creator is running on.
The detected platform context tells you which adapter knowledge you can write
first-hand (the platform you're actually on) versus which platforms you must
either ask the user about or stub out for them to fill in.

Run:

```
a3ip platforms --json
```

This returns the host OS (`windows` / `posix`) and the AI runtime (`cowork`,
`codex`, `claude-code-or-cowork`, `cursor`, ...) per A3IP spec v1.9
"Detecting platform context". The `signals` array shows how the detection
was made (directory presence, environment, project conventions).

Use the result to anchor Intake Group 1's platform question. Instead of
asking the user the full open question, lead with what you detected:

> "I detect we're running on {host_os}+{runtime}. I'll author the package
> universal-first, and prepare adapter knowledge for {runtime} automatically.
> What other platforms do you have knowledge to write adapter docs for?"

### Why this matters

Per A3IP spec v1.9 'Writing Adapter Documents', adapters are platform-
knowledge artifacts, not installation scripts. **Knowledge that is wrong is
worse than no knowledge** — the installing AI follows the script and breaks
when reality differs. So the Creator should only emit confident knowledge
for the platform it actually knows from its environment, and clearly stub
out platforms it does not. The `a3ip platforms` detection is the spec's
named Tier 3 semantic for this.

### Fallback

If `a3ip platforms` is unavailable (CLI older than v1.4.0), tell the user
explicitly: *"Can't auto-detect platform context — please tell me which host
OS and AI runtime we're on, and which other platforms you have knowledge
for."* Then upgrade the CLI: `pip install --upgrade a3ip`.

### Platform-config — passing structured platform metadata to scaffold

CLI v1.5.2+ accepts a `--platform-config <PATH>` flag on `a3ip scaffold`
that supplies per-platform metadata (display_name, default_config_dir,
install_method, host_os_default, description, adapter_file_authored)
used to fill scaffold templates without baking any specific platform
into the CLI.

The Creator ships its own canonical platform-config at
**`components/platform-config.json`** with entries for `cowork`,
`codex`, and `claude-code`. The schema is documented in the CLI repo
at `docs/platform-config.schema.json`.

This file is the source of truth for the Creator's platform routing
during scaffold (Phase 2). If the user's package targets only a
subset of these platforms (e.g. just `cowork` + `codex`), the
intake's `platforms` list narrows the routing — the platform-config
itself does not need editing.

If the user wants to add a NEW platform the Creator doesn't yet
know about (e.g. `cursor`, `aider`, an in-house runtime), they
should create their own platform-config.json (copy the Creator's,
add the new entry) and pass that path explicitly during Phase 2.
The Creator's bundled file is the well-known default; user-supplied
files are first-class.

---

## Critical Rules (burn these in)

**Rule 1 — Config schema is the single source of truth.**
The manifest `configuration:` block drives everything. CONFIGURE.md is *generated*
from it. Never let CONFIGURE.md diverge from the manifest. If you add a config key
anywhere (protocol, script, INSTALL.md), it must appear in the manifest first.

**Rule 2 — Scripts declared → scripts must exist.**
For every entry in `components.scripts`, the declared `file` paths must exist on
disk. The validator checks this. Never ship a manifest listing a script that
isn't created.

**Rule 3 — Scripts used → config keys must be declared.**
Scan every script file for config key reads (`$config.key`, `config["key"]`,
`config['key']`, `{{config.key}}`). Every key read must appear in the manifest
config schema. The validator checks this too.

**Rule 4 — OS-specific scripts must have a cross-platform counterpart.**
If any script targets Windows (PS1), a Python fallback must also exist. Ask about
OS requirements for every script during intake, before writing anything.

**Rule 5 — Use script key notation in protocols, never hardcoded paths.**
Protocols say `run script <key>`, never `run /absolute/path/to/script.py` or
`run C:\Users\...\script.ps1`. The installing AI resolves the key to a path
using the platform conventions in the runtime adapter.

**Rule 6 — Auth flows must be scaffolded explicitly.**
Any component that makes authenticated API calls needs a one-time auth step in
INSTALL.md and an `auth_<service>` script key. Ask about auth during intake.

**Rule 7 — The bundle is always produced.**
Every package build must produce a `.a3ip.bundle`. It is the primary AI
consumption format. Never produce only a zip.

**Rule 8 — Spec first, package second.**
Phase 0 reads the spec; subsequent phases follow its templates literally. Do not
improvise structures the spec defines (INSTALL.md template, `installed.json`
location, required config keys like `install_dir`, Platform Conventions table).
The spec version that applies is `min_a3ip_spec:` from the package's manifest
(or `spec_url:` from a bundle being installed).

**Rule 9 — INSTALL.md steps are programmatically assembled.**
Never hand-number steps. The scaffold script generates them in order. If you add
a step mid-way, re-run scaffold rather than manually editing step numbers.

---

## CLI Reference

All authoring operations are CLI subcommands of `a3ip` (v1.5.0+). The Creator
calls them directly; there are no scripts bundled with this skill since v2.1.0.

| Subcommand | Purpose | Invocation |
|---|---|---|
| `a3ip scaffold` | Generate package from intake JSON | `a3ip scaffold <intake.json> --output-dir <dir>` |
| `a3ip validate` | Run all completeness checks (10 normative + 4 advisory) | `a3ip validate <package_dir>` |
| `a3ip bundle` | Generate .a3ip.bundle | `a3ip bundle <package_dir>` |
| `a3ip zip` | Generate .a3ip.zip for human file transfer | `a3ip zip <package_dir>` |
| `a3ip sync` | Detect changes since last bundle | `a3ip sync <package_dir>` |
| `a3ip new-version` | Cut a new package version | `a3ip new-version <package_dir> <new_version>` |
| `a3ip platforms` | Detect host OS and AI runtime | `a3ip platforms --json` |

How to invoke `a3ip` on the host shell is platform-specific — see
`adapters/runtime/<platform>/skill-runtime.md`. The subcommands themselves are
identical across platforms.

---

## Phase 0.7 — Discovery mode (optional alternative entry to Phase 1)

Discovery is the inverse of Intake. Intake asks the user to declare the
package they want; Discovery investigates an existing workflow and
reverse-engineers a draft from it. Use Discovery when the user has a
pre-existing workflow they want to package as A3IP — typically: an
AI-built skill in their Cowork, a research workspace iterated on over
weeks, an accumulated project they don't know how to describe formally.

### When to enter Phase 0.7 (vs. going straight to Phase 1)

Trigger phrases routing to Discovery:

- "package this workspace" / "make this workflow an A3IP package"
- "discover what's in this project" / "investigate this directory"
- "I have an existing workflow I want to share"
- "package this skill I've been using"

Trigger phrases routing straight to Phase 1 Intake:

- "create a new A3IP package" / "design a workflow"
- "I want to author a package from scratch"

If the user is ambiguous, ask one question: *"Are you (a) designing a
new workflow from scratch, or (b) packaging an existing workflow you
already use?"* Answer (a) → Phase 1. Answer (b) → Phase 0.7.

### What Discovery investigates — six lanes

Each finding is tagged with a confidence level (high / medium / low).
The lanes are read-only investigations — Discovery never modifies the
user's workflow files.

**Lane 1: Workspace tree scan** — catalogue workflow-shaped
subdirectories (`papers/`, `experiments/`, `tasks/`, `tickets/`,
etc.), detect file naming conventions (slug / date-prefixed / numbered),
extract frontmatter schemas as the union of keys across 5–10 sampled
files per noun. Tools: Read, Glob, `mcp__filesystem__directory_tree`.

**Lane 2: Skill inventory** — enumerate installed skills via
`mcp__skills__list_skills` (Cowork) or scan `~/.codex/skills/`,
`~/.claude/skills/` (Codex, Claude Code). Match skills whose
`description:` mentions workspace nouns. Ask the user to confirm the
target skill if multiple candidates plausible.

**Lane 3: Skill content extraction** — read the target SKILL.md;
extract triggers (from `description:` frontmatter), procedural steps,
referenced scripts, referenced artifacts, and config keys (placeholders
like `{{workspace_dir}}`). These become protocols, scripts, artifacts,
and configuration in the package.

**Lane 4: Cowork artifact inventory** — call
`mcp__cowork__list_artifacts` and match artifacts whose names reference
workspace nouns or appear in SKILL.md. Read each artifact's HTML to
confirm shape. Surface a discrepancy if SKILL.md declares an artifact
not present in the runtime (install-time setup gap).

**Lane 5: Memory & CLAUDE.md mining** — read auto-memory's `MEMORY.md`
and any project `CLAUDE.md` for user-role and workflow-purpose
context. These supply the WHY the AI cannot infer from files alone.

**Lane 6: MCP & tool inventory** — scan scripts the SKILL.md
references for imports / external calls; cross-reference against
connected MCPs. Flag missing dependencies as "user must connect this
MCP before install".

### Confidence rules

- **High** (item documented in SKILL.md, or pattern appears in >50%
  of sampled files): goes straight into draft intake.json.
- **Medium** (observed but not documented; pattern appears in
  <50% of files; inferred from worked examples): goes into intake
  but Phase 1 surfaces for user review.
- **Low** (runtime-invented patterns; implicit conventions; single-file
  observations): listed as candidates only; NOT included in intake
  without explicit user confirmation in Phase 1.

### Discovery output — the Discovery Report

After all six lanes run, produce a markdown Discovery Report with
sections per lane plus a draft intake.json. Save it as
`<output_dir>/discovery-report.md`. The report is **read by Phase 1**,
which walks each section with the user and produces the final
intake.json.

### How Phase 1 consumes Discovery output

When entering Phase 1 from a Discovery Report:

1. Read the report. Acknowledge: *"I found <N> workflow components.
   Let me walk through them with you."*
2. Walk each section. For each item:
   - High → state as established; ask "any changes?"
   - Medium → "I observed X — is that what you intended?"
   - Low → ask explicitly: include / modify / omit?
3. Fill any gaps Discovery couldn't extract (license, author email,
   target platforms list — these always need user input).
4. Produce the final intake.json. Phase 2 Scaffold runs identically
   regardless of whether intake came from Discovery or blank-slate.

### Edge cases

- **User points at the wrong directory:** Lane 1 finds <2
  workflow-shaped subdirectories AND Lane 2 finds no related skill.
  Ask: "I didn't find a recognisable workflow shape here. Is it in a
  different directory, or in your runtime's skills rather than the
  filesystem?"
- **Skill installed but workspace fresh:** Lanes 1, 5 produce no
  output. Extract from SKILL.md only (Lanes 2, 3, 4, 6); note in
  report that the workflow has not been exercised.
- **Multiple plausible skills:** ask the user to pick before Lane 3
  runs. Do not run Lane 3 on multiple skills.
- **Implicit conventions conflict with documented ones:** surface as
  **discrepancy**, not finding. The user decides which is correct.
- **Running outside Cowork:** Lanes 2 and 4 substitute filesystem
  scans of `~/.codex/skills/` or `~/.claude/skills/`; Lane 4 has no
  equivalent for non-Cowork runtimes — note that Phase 1 will need
  to ask about artifacts explicitly.

For the full design rationale and test cases, see
`DISCOVERY-DESIGN.md` at the Creator's repo root.

---

## Phase 1 — Intake

Conduct this as a natural conversation, not a rigid form. Group related questions.
Tell the user upfront: "I'll ask you a few groups of questions to understand your
workflow, then I'll generate the full package for you."

### Group 1 — Package identity

Ask:
- What is this workflow? (plain language description — use this to generate the description field)
- What should the package be named? (suggest kebab-case; e.g. `teams-deploy-notifier`)
- Who is the author? (name and email)
- License? (MIT / proprietary — default: proprietary)
- Which AI platforms will it run on? (cowork, claude-code, codex, cursor — default: cowork + claude-code)

### Group 2 — Protocols

A protocol is a named command the user invokes by saying its trigger phrase.
Most packages have 1–3 protocols.

For each protocol, ask:
- What trigger phrase activates it? (e.g. "move to code review")
- Any aliases? (e.g. "start review", "request review")
- Describe what it does step by step — I'll draft the protocol file.

**Important:** As you hear about protocol steps, note which external systems they
touch — you'll ask about those in Group 4.

### Group 3 — Scripts

Scripts are executable files that do things an AI can't do directly (API calls,
file mutations, OS operations). Not every package needs scripts.

Ask: "Does this workflow need any scripts — programs that run on the user's machine?
For example, scripts that call an API, read/write files, or run OS commands?"

For each script:
- What does it do? (description)
- What inputs does it take? (parameters)
- **Which OS does it require?** (cross-platform Python default? Windows PS1 preferred?)
  - If OS-specific: "I'll create a Python fallback automatically. Is the PS1 version
    the primary, with Python as fallback, or the other way around?"
- Does it make authenticated API calls? (note for Group 6 — auth flows)

### Group 4 — External dependencies

For each external system the protocols or scripts touch, ask:
- Is it accessed via an MCP connector, or directly via REST API (script)?
- Is it required for the core workflow, or optional (graceful degradation)?
- What happens if it's unavailable? (fallback)
- Registry hint if known (e.g. `mcp-registry/gitlab`)

Also ask about tool dependencies (Python version, PowerShell, etc.).

### Group 5 — Configuration

Configuration values are things the user provides at install time (API tokens,
usernames, URLs, etc.). These become `{{config.<key>}}` references.

Ask: "What information does this workflow need from the user to work — things like
API tokens, usernames, server URLs, or team names?"

For each config value:
- Key (snake_case), label (human-readable), description
- Type: string | list<string> | boolean | number | select | multi-select
- Required or optional?
- **Sensitive?** (API tokens, PATs, passwords → `sensitive: true`)
- Default value if any
- Placeholder example
- Any validation rule
- Condition: only ask if some MCP/feature is available?
- **Refresh policy**: does this value go stale over time?
  - `never` (default) — set once at install; AI never re-prompts
  - `periodic` — time-sensitive (e.g. sprint dates); AI re-asks each sprint cycle
  - `on_expiry` — token/secret with a TTL; pair with a `refresh_script:` key that
    silently renews it, or omit `refresh_script:` to have the AI prompt the user

**After listing all config values, cross-reference with the protocols and scripts
you've already discussed.** Ask: "The protocols mention [X] — is that covered by
the config keys we've defined, or do I need to add one?"

This is the most important cross-check. Do it explicitly.

### Group 6 — Auth flows

Ask: "Does any component make authenticated API calls that require a one-time login
or token setup — something the user must do once during installation, not per-run?"

Common patterns:
- OAuth browser login (e.g. Teams auth)
- API key that must be created in a web UI before installation

For each auth flow:
- Which service?
- What does the user need to do? (create a token in settings, run a login script, etc.)
- Is there an auth script? (add to scripts list if yes)

### Group 7 — Skills and artifacts

Skills:
- Does this package include a skill (a set of AI instructions)?
- What is the skill's name and what does it tell the AI to do?

Artifacts:
- Does this package include a persistent UI view? (e.g. an inbox, a dashboard)
- If yes: what data does it show, what type (`ui-view` | `data-store` | `dashboard`)?

### Group 8 — Output location

Ask: "Where should I create the package? (directory path)"

---

## Writing intake.json

After collecting all answers, write an `intake.json` file to the output directory
before calling `a3ip scaffold`. This is the canonical record of the intake session.

Schema:

```json
{
  "name": "kebab-case-name",
  "version": "1.0.0",
  "description": "One-sentence description.",
  "author": "Full Name <email@example.com>",
  "license": "MIT",
  "output_dir": "/absolute/path/to/output/",

  "protocols": [
    {
      "name": "protocol-name",
      "trigger": "trigger phrase",
      "aliases": ["alias one"],
      "description": "What this protocol does.",
      "steps": [
        "Step 1 description",
        "Step 2 description"
      ]
    }
  ],

  "skills": [
    {
      "name": "skill-name",
      "description": "What this skill tells the AI to do."
    }
  ],

  "artifacts": [
    {
      "name": "artifact-name",
      "description": "What this artifact displays.",
      "type": "ui-view"
    }
  ],

  "prompts": [
    {
      "name": "prompt-name",
      "description": "What this prompt template is for.",
      "variables": ["var1", "var2"]
    }
  ],

  "scripts": [
    {
      "key": "script_key",
      "description": "What this script does.",
      "parameters": ["Param1", "Param2"],
      "platforms": ["any", "windows"]
    }
  ],

  "configuration": [
    {
      "key": "config_key",
      "label": "Human-Readable Label",
      "description": "What this config value is for.",
      "type": "string",
      "required": true,
      "sensitive": false,
      "when": "before",
      "default": null,
      "placeholder": "e.g. example-value",
      "validation": null,
      "options": null,
      "condition": null,
      "refresh": "never",
      "refresh_script": null
    }
  ],

  "dependencies": {
    "mcp": [
      {
        "name": "service-name",
        "required": true,
        "purpose": "Why this MCP is needed.",
        "registry": "mcp-registry/service-name",
        "fallback": "What happens without it."
      }
    ],
    "tools": [
      {
        "name": "python",
        "version": ">=3.9",
        "required": true,
        "purpose": "Runs cross-platform scripts."
      }
    ]
  },

  "auth_flows": [
    {
      "name": "service_auth",
      "description": "One-time OAuth login for Service.",
      "script_key": "auth_service"
    }
  ],

  "platforms": ["cowork", "claude-code"]
}
```

Notes:
- `scripts[].platforms`: `"any"` = Python default, `"windows"` = PS1 adapter.
  A script with only `"any"` gets a Python file. With `["any", "windows"]` it
  gets both Python and a PS1 adapter.
- `prompts` and `artifacts` and `skills` can be empty arrays if none needed.
- `auth_flows` entries reference an existing `scripts[].key` — make sure it exists.

---

## Phase 2 — Scaffold

Once intake.json is written, call the CLI's `scaffold` subcommand
**with the Creator's bundled platform-config** so per-platform routing
is filled in:

```
a3ip scaffold <intake.json> \
    --output-dir <output_dir> \
    --platform-config <creator_install_dir>/components/platform-config.json
```

The `--platform-config` path points at the Creator's bundled
`components/platform-config.json` (resolved from the Creator's
install_dir at runtime). It declares the per-platform display
names, default install dirs, install methods, host OS defaults,
and adapter-authored status for `cowork`, `codex`, and
`claude-code`. The CLI uses these values to fill the generated
INSTALL.md, manifest, and Platform-Specific Notes — no platform
is hardcoded inside the CLI.

If the user is targeting a platform not in the Creator's bundled
config (e.g. `cursor`), follow Phase 0.5's "user-supplied platform-config"
fallback: copy `components/platform-config.json`, add an entry for the
new platform, pass the new path to `--platform-config`.

`a3ip scaffold` creates the full package directory at
`<output_dir>/<name>.a3ip/`. It generates:

- `manifest.yaml` (from all intake fields)
- `CONFIGURE.md` (generated from `configuration` array — single source of truth)
- `INSTALL.md` (generated with numbered steps in correct order;
  per-platform routing populated from platform-config)
- `README.md` (generated from description and protocol list)
- `components/skills/<name>/SKILL.md` (stub for each skill)
- `components/artifacts/<name>/artifact.md` + `artifact.html` (stub for each artifact)
- `components/protocols/<name>.md` (stub for each protocol, using OS-neutral notation)
- `components/prompts/<name>.md` (stub for each prompt)
- `scripts/<key>.py` (Python stub for each script with `any` platform)
- `adapters/windows/scripts/<key>.ps1` (PS1 stub for each script with `windows` platform)

### Phase 2.5 — Seed runtime adapter templates

After `a3ip scaffold` completes, **copy the Creator's runtime adapter
templates into the new package**, substituting the package name. The
Creator bundles canonical install-skill.md + uninstall-skill.md pairs
for each platform-config-known platform at
`components/runtime-adapter-templates/<platform>/`.

For each platform in the intake's `platforms` list that has
`adapter_file_authored: true` in the platform-config (currently
`cowork`, `codex`, `claude-code`):

1. Read the source template from
   `<creator_install_dir>/components/runtime-adapter-templates/<platform>/install-skill.md`.
2. Replace all occurrences of `{{name}}` with the package name.
3. Write the result to
   `<output_dir>/<name>.a3ip/adapters/runtime/<platform>/install-skill.md`.
4. Repeat for `uninstall-skill.md`.

Each template carries a `> **This file is a Creator template.** ...`
banner at the top instructing the package author to:
- Customise the worked examples (replacing italicised `<your-skill-name>`,
  `<your-artifact-name>`, `<your-script>` placeholders with the
  package's actual component names).
- Remove the banner before shipping a release.

For platforms in the intake list that are NOT in the platform-config
(e.g. `cursor` if the user's targeting it without supplying a custom
platform-config), do NOT copy a template — emit a TODO marker
adapter file directing the package author to write the runtime
adapter from scratch using the spec's `Writing Adapter Documents`
section as guidance.

After `a3ip scaffold` + Phase 2.5 runs, show the user what was created.
The output mechanism (file paths in chat, structured artifact, etc.)
depends on the runtime — see the adapter for `present file list to user`.

---

## Phase 3 — Validate

Call `a3ip validate`:

```
a3ip validate <package_dir>
```

The validator runs 10 normative checks plus 4 advisory warnings (v1.9 + v1.10),
and outputs a JSON report:
`{"errors": [...], "warnings": [...], "ok": true/false}`.

The 10 normative checks (errors block install):

1. **Config coverage** — every `{{config.key}}` in template files → declared in manifest
2. **Script existence** — every declared script file → exists on disk
3. **Script config reads** — every `config["key"]` read in scripts → declared in manifest
4. **Cross-platform coverage** — every Windows-only script → has a Python (`any`) counterpart
5. **Auth flows** — any `auth_*.py` script → INSTALL.md mentions authentication
6. **CHANGELOG present** — version > 1.0.0 → CHANGELOG.md must exist
7. **Refresh scripts** — every `refresh_script:` value → is a declared script key
8. **Trust → permissions** — `network`/`write-local`/`shell-exec` scripts → `permissions:` block in manifest
9. **Trust → plan section** — `write-local`/`shell-exec` scripts → `## Plan` section in INSTALL.md
10. **INSTALL.md spec** — install_dir + installed.json wiring correct per spec template

The 4 advisory warnings (do not block install; harden to errors in v2.0):

11. **Adapter outcome coverage** — runtime adapters address Steps 1/5/6/7 outcomes (discovery + skills + artifacts + protocols); v1.10 extension also scans uninstall-skill.md
12. **INSTALL.md tier shape** — Tier 2 steps free of procedure-language leakage
13. **Adapter knowledge-shape** — adapters are more prose than code (prose:code ratio ≥ 2:1); v1.10 extension also scans uninstall-skill.md
14. **Uninstall coverage** (v1.10+) — INSTALL.md contains an `## Uninstalling` section with Steps UN1-UN8

Do not proceed to Phase 4 until the report shows `"ok": true` (errors == 0).
Warnings can be ignored or addressed at the author's discretion.

### Auto-Fix Playbook

When the validator reports errors, read the full error list and apply the fixes below
autonomously — do not wait for the user to interpret each error. After all fixes are
applied, re-run `a3ip validate` and verify the count reaches zero.

**Check 1 — Undeclared config key in template files**

Error: `Config key '{{config.XYZ}}' is used in [...] but not declared in manifest configuration.`

Fix:
1. Add the missing key to `manifest.yaml` under `configuration:` — choose sensible defaults
   for `type`, `label`, `description`. Mark `sensitive: true` if the name suggests a token
   or password.
2. Add the corresponding question block to `CONFIGURE.md`.
3. Tell the user what was added so they can review the label and description.

**Check 2 — Missing script file**

Error: `Script 'XYZ': declared file 'scripts/XYZ.py' does not exist.`

Fix: Create the missing stub file at the declared path. Use the same stub pattern as `a3ip scaffold`
produces: a Python (or PS1) file that loads the config, prints a `TODO` notice, and exits cleanly.

**Check 3 — Undeclared config key in script**

Error: `Script 'scripts/XYZ.py' reads config key 'ABC' which is not declared in manifest configuration.`

Fix: Same as Check 1 — add the key to `manifest.yaml` and `CONFIGURE.md`. The key was
already being used in code; it just wasn't declared.

**Check 4 — No cross-platform counterpart**

Error: `Script 'XYZ' has a Windows (PS1) implementation but no cross-platform (any/Python) fallback.`

Fix: Create `scripts/XYZ.py` with the same logic as the PS1 file, translated to Python.
Add an `any`-platform implementation entry to `manifest.yaml` under the script's
`implementations:` list.

**Check 5 — Auth script not mentioned in INSTALL.md** *(warning, not error)*

Warning: `Auth script 'auth_XYZ.py' exists but INSTALL.md does not mention an authentication step.`

Fix: Add an `Authenticate with XYZ` step to `INSTALL.md` at the appropriate position
(before any protocol steps that need the credential). Use the standard INSTALL.md step format.

**Check 6 — Missing CHANGELOG.md**

Error: `Package version is 'X.Y.Z' (not 1.0.0) but CHANGELOG.md is missing.`

Fix: Create `CHANGELOG.md` from the standard template — include a header block and
the current version entry with at minimum a Summary and "No prior version" note.

**Check 7 — refresh_script key not declared**

Error: `Config key 'ABC' has refresh_script: 'XYZ' but no script with that key is declared in the manifest.`

Fix: Either (a) add the missing script to `manifest.yaml components.scripts` and create
the stub file, or (b) remove `refresh_script:` from the config key if the refresh script
was specified in error. Ask the user which was intended.

**Check 8 — Elevated trust, no permissions block**

Error: `Script(s) ['XYZ' (network)] have trust_level network or higher but the manifest has no 'permissions:' block.`

Fix: Add a `permissions:` block to `manifest.yaml` after the `components:` section.
Derive the contents from what the scripts actually do:
- `filesystem:` — list any file paths the package reads or writes
- `network:` — list any domains the scripts call (API hostnames)
- `mcp_tools:` — list any MCP tool names the protocols invoke
- `shell_commands:` — list any shell commands `shell-exec` scripts run

**Check 9 — Elevated trust, no ## Plan in INSTALL.md**

Error: `Script(s) ['XYZ' (write-local)] have trust_level write-local or shell-exec but INSTALL.md has no '## Plan' section.`

Fix: Add a `## Plan` section to `INSTALL.md` immediately after the `## Overview` section
(or at the top, before the numbered steps). List every file the package will write, every
network domain it will contact, every MCP tool it will call, and every shell command it
will run. Keep it concise — it should read like a summary the user can glance at and approve
before installation begins.

### Fix Loop

```
[run `a3ip validate`]
→ if errors > 0:
    apply auto-fixes from playbook above for each error type
    [re-run `a3ip validate`]
    → repeat until errors == 0
→ if only warnings remain: show warnings to user and proceed
→ if ok: proceed to Phase 4
```

---

## Phase 4 — Build

The bundle is the primary distribution artifact. The CLI always emits a
`spec_url:` in the bundle frontmatter pointing to the canonical spec on
GitHub, so any A3IP-aware AI can install the bundle without a local spec
copy. Build with:

```
a3ip bundle <package_dir>
```

That produces `<package_dir>/../<name>-v<version>.a3ip.bundle`. The bundle
preamble (normative per spec v1.10) directs the installing AI to read
INSTALL.md and the runtime adapter inside the bundle before doing any
install work.

**For airgapped / offline distribution** (the recipient cannot fetch the
spec from GitHub), embed the spec inside the bundle:

```
a3ip bundle <package_dir> --spec <path-to-A3IP-SPEC-vX.Y.md>
```

The `--spec` flag is the exception, not the default.

**Optional human-friendly format.** For email / cloud-drive transfer to a
human (who will hand the file to an AI to install), also produce a zip:

```
a3ip zip <package_dir>
```

This generates `<name>.a3ip.zip` next to the package directory.

---

## Completion Summary

After a successful build, tell the user:

```
Package created: <name>.a3ip/
Bundle:          <name>.a3ip.bundle  (primary distribution format -- AI-readable)
                 Spec embedded: yes/no
Zip (optional):  <name>.a3ip.zip    (for human file transfer)

Files: <N>
Size:  <KB>

What to do next:
1. Fill in the script stubs in scripts/ -- they have TODO markers
2. Fill in the skill content in components/skills/<name>/SKILL.md
3. Fill in the protocol steps in components/protocols/<name>.md
4. Run `a3ip validate` again after editing to catch any new issues
5. Re-run `a3ip bundle` to update the bundle after changes
```

---

## Phase 5 -- Cut a New Version

When the user wants to release an updated version of an existing package.

**Trigger phrases:** "release a new version", "bump the version", "cut a new release",
"update the package", "new version of"

### Step 0 -- Verify CLI version (active gate, auto-upgrade)

Before running any Phase 5 script, confirm the installed `a3ip` CLI meets the
manifest's declared minimum version. The Creator manifest declares
`a3ip >=1.4.0` under `dependencies.tools`. v1.4.0 is required because Phase
0.5 platform detection uses the `a3ip platforms` command (added in v1.4.0)
and Validate (Phase 3) relies on v1.4.0's Checks 11/12/13 for v1.9 alignment.

Run:

```
a3ip --version
```

Parse the output (format: `a3ip X.Y.Z (spec X.Y)`). Extract `X.Y.Z` and compare
to the manifest's `dependencies.tools[name=a3ip].version` constraint.

- **Command missing OR version below the minimum:** install/upgrade the CLI
  yourself — do not put pip commands on the user. Run:
  ```
  pip install --upgrade --user a3ip
  ```
  Then re-run `a3ip --version` to confirm ≥1.4.0. Tell the user just the
  outcome (e.g. *"a3ip CLI 1.4.0 installed — continuing"*). Continue to
  Step 1 once the CLI is current.

- **At or above the minimum:** continue to Step 1.

- **Fallback:** if `pip` is missing or `pip install` fails, surface the error
  to the user with the exact command to run, and stop until resolved. Don't
  proceed with `a3ip sync` / `a3ip new-version` / `a3ip validate` / `a3ip bundle` on
  a stale CLI — older versions skip the v1.9 alignment checks (11/12/13) and
  produce packages that won't pass v2.0 validation later.

The same auto-upgrade behavior is in INSTALL.md Step 3 (Dependency Check), so
fresh installs of the Creator skill provision the CLI without bothering the
user. Step 0 is the runtime backstop for users whose CLI drifted out of date
since install.

### Step 1 -- Run `a3ip sync` to detect what changed

Always start here. `a3ip sync` compares the current package directory against
the baseline recorded at last bundle time. It tells you exactly what changed —
you do not need to ask the user.

```
a3ip sync <package_dir>
```

`a3ip sync` outputs:
- The list of modified / added / deleted files
- A suggested semver bump type (patch / minor / major) with reasoning
- A ready-to-paste `### Files changed` block for CHANGELOG.md
- Writes `.a3ip-sync-report.json` for `a3ip new-version` to consume automatically

**If `a3ip sync` reports "No changes since last bundle":** tell the user there
is nothing to release — the package is identical to the last bundle.

**If `a3ip sync` finds changes:** review the diff with the user. The suggested
bump type is a heuristic — confirm with the user, especially if manifest.yaml
or any deletions are involved (those could be breaking).

### Step 2 -- Determine new version number

Using the sync output as the basis, suggest the new version following semver:
- Breaking change → bump major (e.g. 1.0.0 → 2.0.0) or minor (1.0.0 → 1.1.0)
- Non-breaking new feature or behaviour change → bump minor
- Bug fix, script update (same interface), docs → bump patch

Confirm the version with the user.

### Step 3 -- Run `a3ip new-version`

```
a3ip new-version <package_dir> <new_version>
```

This command:
1. Reads `.a3ip-sync-report.json` (written by `a3ip sync`) and surfaces the suggested bump
2. Bumps `version:` in manifest.yaml
3. Updates `latest_change:` in manifest.yaml to today
4. Prepends a changelog entry to CHANGELOG.md with `### Files changed` already
   populated from the sync report — no TODOs for that section
5. Consumes and deletes `.a3ip-sync-report.json` so it is not reused accidentally

### Step 4 -- Fill in the changelog entry

The CHANGELOG entry now has real file names in `### Files changed`. Still fill in:
- **Summary** -- 2-5 sentences describing what changed and why
- **Upgrade steps** -- concise INSTALL.md-style steps covering only what changed;
  reference only the components that were modified
- **Breaking changes** -- list each one explicitly; state which config key / script
  key / MCP was affected and what the AI must do (re-ask, re-copy, re-register);
  write "None." if there are none

### Step 5 -- Apply the file changes

Make the actual changes the version describes:
- Edit scripts / protocols / artifacts / skills as needed
- If new config keys were added: update manifest.yaml configuration block
- Never manually renumber INSTALL.md steps -- re-run scaffold if structure changes

### Step 6 -- Validate and rebundle

```
a3ip validate <package_dir>
```

Fix any errors. Then bundle (this also writes a new .a3ip-source.json baseline):

```
a3ip bundle <package_dir>
```

The new baseline is now set. The next `a3ip sync` run will diff against this version.

---

## Phase 6 -- Registry

When the user wants to browse available packages, install from a registry, or check for updates.

**Trigger phrases:** "show me available packages", "what packages are in the registry",
"install from registry", "check for updates", "browse the registry", "what can I install"

### Browsing a registry

1. **Locate the registry.** Ask the user for the path or URL to `registry.yaml`.
   Common default: `registry.yaml` in the current workspace directory.

2. **Read and parse it.** Load the `packages:` list.

3. **Filter by need.** If the user described what they want, filter by `tags`,
   `description`, and `platforms`. Present only relevant matches.

4. **Present the options.** For each matching package, show:
   ```
   <name>  v<version>
   <description>
   Platforms: <platforms>  |  Tags: <tags>
   Latest: <changelog_summary>
   ```

5. **Ask the user to choose.** If multiple packages match, ask which to install.
   If exactly one matches, confirm before proceeding.

6. **Retrieve and install.** Resolve `bundle_url` relative to the registry file's
   directory. Fetch the bundle and proceed with the normal installation flow
   (read INSTALL.md from the bundle, run CONFIGURE.md wizard, apply steps).

### Installing from a registry

After the user selects a package:

1. **Resolve `bundle_url`:**
   - `./...` or `../...` → relative to registry.yaml's directory
   - Absolute path → use directly
   - `https://...` → fetch via HTTP

2. **Check if already installed.** Look for `installed.json` in the user's local
   config directory. If it exists and version ≥ registry version → tell the user
   the package is already current.

3. **Proceed with installation.** The bundle is a standard `.a3ip.bundle`.
   Follow the normal flow: CONFIGURE.md wizard → INSTALL.md steps.

4. **Record the registry source.** After a successful install, add to `installed.json`:
   ```json
   {
     "package": "<name>",
     "version": "<version>",
     "installed_at": "<ISO timestamp>",
     "platform": "<current platform>",
     "registry_source": "<path or URL to registry.yaml>"
   }
   ```

### Checking for updates

If the user asks "check for updates" and `installed.json` contains `registry_source`:

1. Load the registry at `registry_source`.
2. Find the entry whose `name` matches the installed package.
3. Compare versions. If registry has a newer version: offer to upgrade.
4. If the bundle at `bundle_url` is unreachable: report the error, do not modify the install.

---

## Intake Conversation -- Compact Mode

If the user says "I'll give you all the details at once" or pastes a description,
extract the intake fields from their text rather than asking each question.
Still write intake.json and still run all four 