# Codex runtime adapter — {{name}}

> **This file is a Creator template.** It was copied from
> `creator-repo/components/runtime-adapter-templates/codex/install-skill.md`
> into `{{name}}/adapters/runtime/codex/install-skill.md` during
> scaffold. Generic placeholders use `{{name}}` for the package name and
> italicised angle-bracket placeholders (e.g. *`<your-script>`*) for
> per-package component identifiers. Adapt the worked examples to this
> package's actual components and remove this banner before shipping a
> release.

This adapter is platform-knowledge for installing `{{name}}` on
**Codex** (OpenAI's coding agent). The installing AI reads this as
context, then applies it to satisfy the Tier 2 outcomes in INSTALL.md
— specifically the "make skills discoverable" step, the "make artifacts
available" step (if this package ships artifacts), and the "make
protocols invocable" step. The rest of INSTALL.md still applies —
install detection, configure wizard, resolve install_dir, write
config.json, write installed.json, and the Upgrading flow — all
governed by INSTALL.md and the A3IP spec, not by this adapter.

Per A3IP spec v1.10 'Writing Adapter Documents', adapter content is
platform knowledge, not installation script. The code blocks below are
illustrative worked examples — adapt them to actual paths, AGENTS.md
state, and user choices rather than executing them verbatim.

## How Codex discovers skills (critical convention)

This is the single most important thing to know about installing skills
on Codex: **Codex does NOT auto-discover files in `~/.codex/skills/`**.
Dropping files there is necessary but not sufficient. The host runtime
needs to be told about the skill through Codex's persistent-instructions
mechanism, which is **`~/.codex/AGENTS.md`**.

`~/.codex/AGENTS.md` is the global AGENTS.md file Codex loads at every
session start as a persistent system instruction. For Codex to
recognise the package's trigger phrases and follow the SKILL.md
protocol, that SKILL.md path must be referenced in AGENTS.md. Without
an AGENTS.md stanza, the user can say a trigger phrase and Codex will
improvise a generic response in the workspace instead of loading the
installed skill — a known failure mode discovered during early A3IP
testing.

The conventions are:

- **Skill files live at `~/.codex/skills/{{name}}/`** — one directory
  per skill. The directory must contain `SKILL.md` at its root (Codex
  looks for SKILL.md there, not under `components/`).
- **AGENTS.md at `~/.codex/AGENTS.md`** is where the skill gets
  registered. It is a plain markdown file; multiple skills can be
  registered side by side. The file may already have unrelated content
  from other installations or the user — preserve it.
- **Registration convention:** an A3IP stanza wrapped in marker
  comments so re-installs and uninstalls can replace or remove the
  block cleanly. The marker shape is:

      <!-- a3ip:{{name}}:start -->
      ## a3ip skill: {{name}}
      When the user says <trigger phrases>, read and follow
      <absolute path to SKILL.md>. That file is authoritative.
      <!-- a3ip:{{name}}:end -->

  An installing AI on a fresh machine (no existing AGENTS.md) creates
  the file. On a machine with existing AGENTS.md content, it appends
  the marker block at the end. On re-install, it locates the existing
  marker block by name and replaces its contents in place.

## Other Codex conventions

**Per-install state** lives at `{{config.install_dir}}` (typically
`~/.codex/packages/{{name}}/`). This is where `config.json`,
`installed.json`, and any package-managed runtime records live. These
paths are governed by INSTALL.md and the A3IP spec, not by this
adapter.

**No HTML artifact mechanism.** Codex has no equivalent of Cowork's
`mcp__cowork__create_artifact`. Artifacts degrade to markdown files the
runtime updates in-place at `{{config.install_dir}}/<artifact-name>.md`.
The SKILL.md still treats each as a single named record — same purpose,
different medium. Seed each from
`components/artifacts/<artifact-name>/artifact.md` at install time.

**No "Save skill" UI.** Skills install as plain files; there's no UI
button, no Personal Skills registry, no restart required for skill
changes to take effect. The next Codex session reads files fresh — but
only if AGENTS.md tells it to.

**`install_method: "generic-copy"`** in `installed.json` per A3IP spec
v1.10 Platform Conventions, distinguishing the Codex flow from
Cowork's `"cowork-skill"` UI flow.

**Direct PowerShell on Windows.** Codex on Windows talks to the native
filesystem directly; `$env:USERPROFILE` is the Windows user home with
no sandbox layer. `~`-expansion is unambiguous. (Contrast with
Cowork's bash sandbox, where `~` resolves to an ephemeral Linux home.)

## What gets installed where

| Artifact | Codex location | Mechanism |
|---|---|---|
| Skill payload (SKILL.md + scripts/) | `~/.codex/skills/{{name}}/` | File copy |
| Skill registration | `~/.codex/AGENTS.md` (stanza appended) | Marker-bounded block, points at the SKILL.md absolute path |
| Per-install state | `{{config.install_dir}}` | config.json, installed.json, artifact markdown record(s) |
| Each artifact record (if any) | `{{config.install_dir}}/<artifact-name>.md` | Markdown the runtime rewrites after each trigger |

## Worked example: the install flow on Codex

The steps below are illustrative — they describe one way to achieve the
Tier 2 outcomes on Codex. The install AI may adapt for variations
(e.g., the user's install_dir, an existing AGENTS.md with unrelated
content, an older a3ip CLI requiring
`$env:PYTHONIOENCODING = 'utf-8'`).

### Step C1: Detect prior install

Look at `{{config.install_dir}}/installed.json`. On Windows under Codex
use a tool that expands `~` to the Windows user home
(`$env:USERPROFILE` in PowerShell or `os.path.expanduser('~')` in
Python). See `adapters/os/windows/file-ops.md` for canonical
tool-selection guidance.

- **Found:** read the `version` field. Go to **Upgrading an existing
  Codex install** at the end of this document.
- **Not found:** continue with fresh install.

### Step C2: Extract bundle to a temp directory and validate

Before touching `~/.codex/skills/`, unpack the `.a3ip.bundle` into a
temp working directory and run `a3ip validate` against the unpacked
tree. This catches bundle-parsing issues before they affect the live
install.

```
$bundle = "<path to {{name}}-vX.Y.Z.a3ip.bundle>"
$work   = "$env:TEMP\{{name}}-vX.Y.Z-extracted"
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $work -Force
```

Parse the bundle (line-delimited `=== FILE: <path> ===` /
`=== END FILE ===` blocks) and write each file under `$work`. Then:

```
a3ip validate $work
```

If validation fails, do NOT proceed to overwriting the live skill
directory. Fix or escalate.

### Step C3: Back up existing skill (if upgrading)

If `~/.codex/skills/{{name}}/` exists, back it up before overwriting.
A timestamped folder under `~/.codex/backups/` is the convention; tell
the user the backup path so they can roll back.

### Step C4: Install the skill payload

Replace the live skill directory with the validated extraction. The
runtime payload is everything SKILL.md needs at runtime: SKILL.md
itself (lifted to the skill root), the scripts it invokes, and any
artifact templates it reads.

Lift `components/skills/<your-skill-name>/SKILL.md` to
`<skill>/SKILL.md` (the skill root) — Codex looks there, not in
`components/`. Then substitute the absolute `install_dir` into all
markdown files in the installed skill (SKILL.md plus any protocol
files that reference `{{install_dir}}`). Rationale: `install_dir` is a
non-secret deterministic path — substituting it at install time is the
only way the runtime AI knows where to read config.json. Other config
keys (tokens, secrets, identifiers) are NOT substituted; they stay in
config.json so the skill remains portable across config changes.

**Path-separator normalization (required).** The `install_dir` value
sourced from `CONFIGURE.md` or a prior `installed.json` may end with a
trailing path separator (`\` or `/`). SKILL.md templates reference
files as `{{install_dir}}/config.json` with a leading `/`. A naive
substitution of a trailing-separator value into a leading-slash
template produces a malformed mixed-slash path on Windows (e.g.
`C:\Users\me\.codex\packages\{{name}}\/config.json`), which Codex's
runtime file APIs reject. Strip trailing `/` and `\` from
`$installDir` before substituting so the join is well-formed.

Illustrative (adapt paths and install_dir literal):

```
$skill = "$env:USERPROFILE\.codex\skills\{{name}}"
$installDir = "<absolute install_dir from CONFIGURE.md>"
$installDir = $installDir.TrimEnd('/', '\')  # see normalization note above

Remove-Item -LiteralPath $skill -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $skill -Force
Copy-Item -Path (Join-Path $work '*') -Destination $skill -Recurse -Force
Copy-Item -LiteralPath (Join-Path $work 'components\skills\<your-skill-name>\SKILL.md') `
          -Destination (Join-Path $skill 'SKILL.md') -Force

Get-ChildItem -LiteralPath $skill -Recurse -Filter '*.md' | ForEach-Object {
    $text = Get-Content -LiteralPath $_.FullName -Raw
    if ($text -match '\{\{install_dir\}\}') {
        $text = $text -replace '\{\{install_dir\}\}', $installDir
        Set-Content -LiteralPath $_.FullName -Value $text -Encoding UTF8
    }
}
```

PowerShell quirk to be aware of: `-LiteralPath` does NOT expand
wildcards. Use `-Path` when copying with `*`, `-LiteralPath` only when
you have an exact filename. Mixing these incorrectly produces a silent
partial copy where only one file is moved.

### Step C5: Register the skill in AGENTS.md (THIS IS THE CRITICAL STEP)

Without this step, Step C4's files exist but are not discoverable.
Codex will not recognise the package's trigger phrases.

Append (or upsert) a marker-bounded stanza to `~/.codex/AGENTS.md`. If
the file does not exist, create it. If it exists with unrelated
content, preserve that content and append the stanza. If it already
contains a `{{name}}` marker block from a prior install, replace its
contents between the markers in place.

Illustrative (adapt the absolute SKILL.md path and trigger phrases to
match the package's actual protocols):

```
$agentsPath = "$env:USERPROFILE\.codex\AGENTS.md"
$skillMd    = "$env:USERPROFILE\.codex\skills\{{name}}\SKILL.md"

$stanza = @"
<!-- a3ip:{{name}}:start -->
## a3ip skill: {{name}}

When the user says any of <quoted trigger phrases from the package's
protocols, comma-separated>, read and follow $skillMd. That file is
authoritative; do not improvise a generic response.

Config for this skill lives at $installDir\config.json.
<!-- a3ip:{{name}}:end -->
"@

# Read existing AGENTS.md (or empty string if missing)
if (Test-Path -LiteralPath $agentsPath) {
    $current = Get-Content -LiteralPath $agentsPath -Raw
} else {
    $current = ""
    New-Item -ItemType Directory -Path (Split-Path $agentsPath) -Force | Out-Null
}

# Upsert: replace existing marker block if present, else append
$pattern = '(?ms)<!-- a3ip:{{name}}:start -->.*?<!-- a3ip:{{name}}:end -->'
if ($current -match $pattern) {
    $updated = [regex]::Replace($current, $pattern, [System.Text.RegularExpressions.Regex]::Escape($stanza) -replace '\\', '')
} else {
    $updated = if ($current.Trim()) { "$current`n`n$stanza`n" } else { "$stanza`n" }
}
Set-Content -LiteralPath $agentsPath -Value $updated -Encoding UTF8
```

**Verification (the install AI should self-check after C5):** open
AGENTS.md and confirm the marker block is present with the absolute
SKILL.md path filled in. If the path is still a literal placeholder,
substitution failed; re-run the step with the resolved install_dir.

### Step C6: Initialize artifact record(s) — if any

For each artifact declared in the package manifest, create a markdown
file the runtime will keep up to date. This is the Codex-side stand-in
for Cowork's artifact card: same purpose (one record, updated on
trigger), different medium.

```
$record = Join-Path $installDir '<artifact-name>.md'
if (-not (Test-Path -LiteralPath $record)) {
    Copy-Item -LiteralPath (Join-Path $work 'components\artifacts\<artifact-name>\artifact.md') `
              -Destination $record -Force
}
```

If the record already exists (from a previous install), leave it in
place — it carries the user's most recent state. The SKILL.md updates
the file in place on each trigger.

**TODO-template semantics (do not "fix" the placeholders).** The
bundled `components/artifacts/<artifact-name>/artifact.md` is a
template with intentional TODO / placeholder markers (e.g.
`<!-- TODO: yesterday's commits -->`, `## Pending first run`,
`{{config.author_login}}'s standup will appear here after the first
run`). Those markers are NOT bugs and the install AI MUST NOT
rewrite them at install time — they're the contract between the
template and the SKILL.md protocol: on each trigger, the runtime
fills in the placeholders with live data sourced from MCP calls,
config, or workspace state. Hand-edited content here would be
overwritten on the next run and would mask whether the protocol is
working. The install AI's job is to copy the template verbatim and
let the first protocol run write real content.

If `{{name}}` ships no artifacts, skip this step entirely.

### Step C7: Write installed.json

Per A3IP spec v1.10 Platform Conventions, Codex installs use
`install_method: "generic-copy"`:

```json
{
  "package": "{{name}}",
  "version": "<NEW>",
  "installed_at": "<ISO-8601 timestamp>",
  "upgraded_from": "<previous version, or omit if fresh install>",
  "platform": "codex",
  "a3ip_spec": "1.10",
  "config_dir": "{{config.install_dir}}",
  "install_method": "generic-copy",
  "source_bundle": "<absolute path to the .a3ip.bundle used>",
  "backup_dir": "<absolute path to backup from C3, or omit if fresh>"
}
```

Per spec: `upgraded_from`, `source_bundle`, and `backup_dir` are
optional; include them when applicable. Readers MUST tolerate their
absence.

### Step C8: Verify the install end-to-end

Two confirmations:

1. **Static:** `a3ip validate $skill` should report
   `[OK] Validation passed`.
2. **Runtime:** start a NEW Codex session (so AGENTS.md is freshly
   loaded) and say one of the package's trigger phrases. The AI should
   recognise the trigger, read config from
   `<install_dir>/config.json`, and behave per the SKILL.md. If it
   instead improvises a generic response, the AGENTS.md registration
   (Step C5) didn't take — re-check that file.

### Step C9: Clean up

```
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
```

## Upgrading an existing Codex install

Triggered when Step C1 found `{{install_dir}}/installed.json`.

1. Read the `version` field. Determine which CHANGELOG entries need to
   apply (everything between installed version and the bundle's
   version).
2. Apply each version's `### Upgrade steps` in order. For most packages
   on Codex this is "replace the skill files" — Steps C2 through C8
   above suffice for any minor/patch upgrade. Artifact records are
   preserved through Step C6's idempotency. The AGENTS.md stanza is
   upserted in place by Step C5.
3. For major bumps or breaking changes (per CHANGELOG `### Breaking
   changes`), follow the explicit instructions in that version's
   changelog entry before re-running C2–C8. If config keys changed,
   re-run the wizard for those keys and rewrite `config.json` before
   reinstalling the skill payload.
4. Update `installed.json` (Step C7) with the new version and
   `upgraded_from` = previous version. Preserve `config_dir`,
   `install_method`, optionally bump `a3ip_spec` and `backup_dir`.

## Troubleshooting

**`a3ip` command not on PATH after `pip install --user`:** find the
binary at `$env:APPDATA\Python\Python<XY>\Scripts\a3ip.exe` and invoke
explicitly, or add that directory to PATH. (Note: most packages do
not require `a3ip` at runtime — only the install AI uses it for
`a3ip validate`.)

**Skill files installed but trigger phrases still produce generic
responses:** the common failure mode. Step C5 (AGENTS.md registration)
was skipped or the marker block did not get the absolute SKILL.md
path substituted. Open `~/.codex/AGENTS.md` and confirm the
`{{name}}` marker block is present with the absolute path.

**PowerShell `-LiteralPath` + wildcard quietly skips most files:** use
`-Path` for wildcard copies; reserve `-LiteralPath` for exact
filenames. After any `Copy-Item -Recurse`, verify by listing the
destination.

**Skill triggers but a script can't find config:** SKILL.md still
contains a literal `{{install_dir}}` because Step C4's substitution
was skipped. Re-run Step C4, ensuring `$installDir` is the absolute
path the user chose during CONFIGURE.md.

**Artifact record never updates:** the skill writes via
`Set-Content -LiteralPath "$installDir\<artifact-name>.md"`. Confirm
the path is correct and the user account has write permission to
`{{config.install_dir}}`.

**Unicode crash when running validate:** upgrade to a3ip CLI 1.3.1 or
higher (`pip install --upgrade --user a3ip`). v1.3.1+ uses ASCII-safe
console output by default. Workaround for older versions:
`$env:PYTHONIOENCODING = 'utf-8'`.
