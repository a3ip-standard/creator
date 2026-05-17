---
format: a3ip-install
spec: "1.2"
package: a3ip-creator
---

# Installation Guide: a3ip-creator

## 1. Check for Existing Installation

Look for `installed.json` at the platform-default install location:

- **Cowork (Windows):** `~/.claude/packages/a3ip-creator/installed.json`.
  **Use `mcp__filesystem__read_file`** for this read -- it expands `~` to the
  Windows user home (`C:/Users/USERNAME/`). Do NOT use bash (its `~` resolves
  to the ephemeral Linux sandbox home, not Windows) and do NOT use the Read
  tool with a raw `~` (it does not expand tildes). See
  `adapters/os/windows/file-ops.md` for the full tool-selection table.
- **Claude Code (macOS / Linux):** `~/.claude/packages/a3ip-creator/installed.json`.
  Use `os.path.expanduser('~')` or `$HOME` before reading.
- **Codex:** `~/.codex/packages/a3ip-creator/installed.json` (same tool
  guidance as Cowork for Windows).
- **Other platforms:** ask the user where they store package state.

**Result:**
- **Found:** read its `config_dir` field -- that is this user's actual
  `install_dir`. Go directly to the [## Upgrading](#upgrading) section at the
  end of this document. Apply only the changelog steps for versions after
  the installed version.
- **Not found:** proceed with the full install steps below.

(After Step 4 the configure wizard collects a NEW or confirmed `install_dir`
from the user. Step 5 then resolves it to an absolute path.)

## Plan

Before beginning installation, this package will take the following actions.
Please review and confirm before proceeding.

**Files written:**
- `<skills_dir>/a3ip-creator/SKILL.md` — the Creator skill (registered via platform's skill mechanism)
- `<skills_dir>/a3ip-creator/scripts/*.py` — 4 Python scripts (scaffold, sync, new_version, zip_package)
- `<skills_dir>/a3ip-creator/manifest.yaml` — package metadata (required by a3ip validate)
- `<skills_dir>/a3ip-creator/CHANGELOG.md` — version history (required by a3ip validate)
- `{{config.install_dir}}/installed.json` — install record (per spec template)

**Shell commands that will be available after install:**
- `a3ip validate <package_dir>` — validate a package before bundling
- `a3ip bundle <package_dir>` — build a distributable .a3ip.bundle

**Confirm to proceed.**

## 2. What This Package Installs

a3ip-creator is a skill that turns an AI assistant into an expert A3IP package author.
Once installed, say "create an A3IP package for my workflow" and the AI will conduct
an intake conversation, then generate a complete, validated, bundled package.

The Creator handles the parts that are easy to get wrong: config schema consistency,
cross-platform script requirements, auth flow scaffolding, and correct bundle generation.

## 3. Dependency Check

Verify the following before proceeding. Tell the user exactly what is missing and
do not continue until all required dependencies are satisfied.

**Required: Python 3.9+**
- [ ] Run: `python3 --version` (macOS / Linux) or `py -3 --version` (Windows)
- Minimum: Python 3.9. If not present, direct the user to https://python.org/downloads

**Required: a3ip CLI ≥1.2.1** (declared in `dependencies.tools` of manifest.yaml)

The AI installer SHOULD provision the CLI itself — do not put pip commands
on the user.

1. Run `a3ip --version` from the shell. Parse the output (format
   `a3ip X.Y.Z (spec X.Y)`). Three cases:

   - **Command not found:** the CLI is missing. Run:
     ```
     pip install --upgrade --user a3ip
     ```
     Then re-run `a3ip --version` to confirm.

   - **Version below 1.2.1:** the CLI is too old. Run:
     ```
     pip install --upgrade --user a3ip
     ```
     Then re-run `a3ip --version` to confirm ≥1.2.1.

   - **Version ≥1.2.1:** proceed.

2. Tell the user only the outcome — e.g. *"Installed a3ip CLI 1.2.1"* or
   *"a3ip CLI 1.2.1 already present — good"*. Do NOT make the user run pip.

3. **Fallback (ask the user):** if `pip` is missing, if `pip install` exits
   with an error you can't resolve, or if `~/.local/bin` isn't on PATH after
   install and you can't add it, surface the problem to the user with the
   exact command for them to run and stop the install until resolved.

**Why 1.2.1 specifically:** v1.2.1 introduces Check 10 (`install_dir spec`
compliance). Older CLIs silently skip it and produce non-spec-compliant
packages that fail at install time.

**Active gate:** the Creator's Phase 5 (`Cut a New Version`) repeats this
check before any sync/bundle work and auto-upgrades if needed.

## 4. Run Configuration Wizard

Read and follow CONFIGURE.md to collect all user-specific values.
Do not proceed until the user has confirmed the configuration summary.

All `{{config.*}}` references in subsequent steps are substituted with
the values collected here.

## 5. Install Scripts

Copy the `scripts/` directory into the skill folder.

**Cowork:** see `adapters/runtime/cowork/install-skill.md` for the full Cowork-specific
flow — Cowork registers skills through its UI, not via direct file copy.
Scripts are packaged inside the `.skill` zip in that flow.

**Claude Code:** copy to `~/.claude/skills/a3ip-creator/scripts/`

**Codex:** copy to `C:\Users\<user>\.codex\skills\a3ip-creator\scripts\`

**Cursor / Other platforms:** copy to the equivalent skills directory.

Scripts installed:
- **`scaffold.py`** — Generate a complete package directory from intake.json
- **`zip_package.py`** — Build a .a3ip.zip archive of a package directory
- **`sync.py`** — Detect files changed since the last bundle was produced
- **`new_version.py`** — Cut a new package version and create a CHANGELOG entry

Note: `validate.py` and `bundle.py` are **not** part of this package — those
functions are provided by the `a3ip` CLI (installed in Step 3).

## 6. Install Skill and Package Metadata

**Cowork:** follow `adapters/runtime/cowork/install-skill.md` — the skill, scripts, and
metadata are all packaged together as a `.skill` zip and installed via the
Cowork UI "Save skill" button. Skip the file-copy sub-steps below.

**Claude Code / Codex / Other platforms:** copy the following into the skill root:

- `components/skills/a3ip-creator/SKILL.md` → `<skills_dir>/a3ip-creator/SKILL.md`
- `manifest.yaml` → `<skills_dir>/a3ip-creator/manifest.yaml`
- `CHANGELOG.md` → `<skills_dir>/a3ip-creator/CHANGELOG.md`

`manifest.yaml` and `CHANGELOG.md` must be present alongside SKILL.md — they are
required by `a3ip validate` (Step 7). Without them the validator cannot check script
declarations or confirm the CHANGELOG exists for non-1.0.0 versions.

## 7. Verify Installation

First confirm the CLI is accessible:

```
a3ip --version
```

Expected output: `a3ip 1.1.0 (spec 1.6)` or later. If this fails, revisit Step 3.

Then run the validator against the installed skill directory:

- **Cowork / Claude Code**: `a3ip validate ~/.claude/skills/a3ip-creator/`
- **Codex**: `a3ip validate C:\Users\<user>\.codex\skills\a3ip-creator\`
- **Other platforms**: `a3ip validate <skills_dir>/a3ip-creator/`

Expected output: `✓ Validation passed — no errors or warnings.`

If validation fails, re-extract the affected files from the bundle and re-run until clean.

Summarize to the user:
- ✅ a3ip CLI confirmed at version `<version>`
- ✅ Scripts installed to `<skills_dir>/a3ip-creator/scripts/`
- ✅ Skill and metadata installed to `<skills_dir>/a3ip-creator/`
- ✅ `a3ip validate` passed with no errors or warnings

**How to use:** Say "create an A3IP package" to your AI assistant. It will begin the
intake conversation (package name, description, author, platforms, scripts, configuration).

## 8. Write installed.json

Write `{{config.install_dir}}/installed.json` with:

```json
{
  "package": "a3ip-creator",
  "version": "1.11.0",
  "installed_at": "<current ISO-8601 timestamp>",
  "platform": "<detected platform — cowork / claude-code / codex / etc.>",
  "a3ip_spec": "1.6",
  "config_dir": "{{config.install_dir}}",
  "install_method": "<cowork-skill or generic-copy>"
}
```

This file tracks the installed version and enables delta upgrades in future.
It lives outside the skill directory — it is local state, not part of the package.

---

## Platform-Specific Notes

### Cowork (primary platform)
Full support for artifacts, skills, and scheduled tasks.
Use `mcp__filesystem__write_file` and `mcp__windows-cli` (PowerShell `Copy-Item`) for
all file copy steps — do not use the bash sandbox for Windows file operations, as the
bash `~` is not the Windows user home and the mount may be stale.

### Claude Code (CLI)
Full protocol support. Artifacts degrade to markdown files.
Use cron or a system scheduler for automated tasks.

### Codex
Full support. Skills live in `C:\Users\<user>\.codex\skills\`.
Use `py -3` instead of `python3` if the system default Python is version 2.
The `a3ip` CLI must be on PATH — install with `py -3 -m pip install a3ip`.

### Cursor / Other platforms
Core skill works on any platform. Adapt the skill directory path as needed.

---

## Upgrading

When `installed.json` is found at `{{config.install_dir}}/installed.json`,
follow these steps instead of the full install.

### Step U1 — Read installed version
Read `{{config.install_dir}}/installed.json`. Note the `version` field. Note
also `install_method` if present — Cowork installs require the Cowork-specific
upgrade path (rebuild and re-save the `.skill` zip rather than patching files
in place).

### Step U2 — Apply CHANGELOG steps
Find all version entries in `CHANGELOG.md` newer than the installed version.
Apply them in order from oldest to newest. For each version entry:
1. Check `### Breaking changes` — if any, tell the user before proceeding.
2. Check `### Config changes` — if new required keys, run the configure wizard
   for those keys only.
3. Follow `### Upgrade steps` exactly.

**Clean old files** if the upgrade adds or removes scripts: remove files from
the skill directory that belong to the previous version before writing the new
ones (prevents stale files from confusing the validator). Back up the skill
directory first.

### Step U3 — Update installed.json
After all upgrade steps complete, overwrite
`{{config.install_dir}}/installed.json` with the new `version` and
`installed_at` timestamp. Preserve the existing `platform`, `a3ip_spec`,
`config_dir`, and (if present) `install_method` fields.

### Step U4 — Confirm
Tell the user the versions upgraded from and to, and the changes applied.

Do **not** run the full install sequence during an upgrade.
Apply only the delta steps listed in CHANGELOG.md.

If a version entry lists **Breaking changes**, re-run the configuration wizard
for any affected config keys before applying that version's upgrade steps.
