# Codex Skill Installation — a3ip-creator

This adapter explains how to install a3ip-creator on **Codex** (OpenAI's coding agent). Codex differs from Cowork enough that the runtime-axis install flow gets its own document, in addition to the OS-axis file-ops adapter under `adapters/os/<host>/file-ops.md`.

## Why Codex is different from Cowork

Codex has no Cowork-style **Save skill** UI for `.skill` zips. Skills on Codex are installed as plain files in `~/.codex/skills/<name>/` and registered as persistent system instructions. There's no Personal Skills registry to refresh, no UI button, no restart required for skill changes to take effect (the next session reads files fresh).

Codex also has direct access to PowerShell on Windows (no Linux sandbox layered on top), so `$env:USERPROFILE` is the Windows user home directly — no `~`-expansion ambiguity between bash and Windows-native tools.

Per the spec v1.8 Platform Conventions, Codex installs use `install_method: "generic-copy"` in `installed.json` to distinguish from Cowork's `"cowork-skill"` UI flow.

## What gets installed

| Artifact | Codex location |
|---|---|
| **Skill files** | `~/.codex/skills/a3ip-creator/` — contains SKILL.md + scripts/ + docs/ |
| **Package state** | `~/.codex/packages/a3ip-creator/` — contains installed.json |
| **CLI binary** | Provisioned via `pip install --user a3ip` — entry point at `%APPDATA%/Python/Python<XY>/Scripts/a3ip.exe` |

## Steps

### Step C1: Detect prior install

Look at `~/.codex/packages/a3ip-creator/installed.json`. On Windows under Codex use a tool that expands `~` to the Windows user home (typically `os.path.expanduser('~')` in Python, or `$env:USERPROFILE` in PowerShell). See `adapters/os/windows/file-ops.md` for the canonical tool-selection guidance.

- **Found:** read the `version` field. Go to **Upgrading an existing Codex install** at the end of this document.
- **Not found:** continue with fresh install.

### Step C2: Provision the a3ip CLI

```
py -3 -m pip install --upgrade --user a3ip
```

Verify with `a3ip --version`. If the command is not found, the pip user-scripts directory likely isn't on PATH — try the explicit path (Python 3.10 example):

```
& "$env:APPDATA\Python\Python310\Scripts\a3ip.exe" --version
```

Adjust the Python version segment as needed. If `a3ip --version` reports a version below the Creator manifest's `dependencies.tools[a3ip].version` minimum, the pip install needs to have succeeded — surface to the operator with the exact path it landed at.

### Step C3: Extract bundle to a temp directory + validate

Before touching `~/.codex/skills/`, unpack the `.a3ip.bundle` into a temp working directory and run `a3ip validate` against the unpacked tree. This catches bundle-parsing issues before they affect the live install.

```
$bundle = "<path to a3ip-creator-vX.Y.Z.a3ip.bundle>"
$work   = "$env:TEMP\a3ip-creator-vX.Y.Z-extracted"
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $work -Force
```

Parse the bundle (line-delimited `=== FILE: <path> ===` / `=== END FILE ===` blocks) and write each file under `$work`. Then:

```
a3ip validate $work
```

If validation fails, do NOT proceed to overwriting the live skill directory. Fix or escalate. Note: on cp1252 Windows consoles, set `$env:PYTHONIOENCODING = 'utf-8'` first if running an older CLI — a3ip 1.3.1+ uses ASCII-safe output by default.

### Step C4: Back up existing skill (if upgrading)

If `~/.codex/skills/a3ip-creator/` exists, back it up before overwriting. A timestamped folder under `~/.codex/backups/` is the convention:

```
$skill   = "$env:USERPROFILE\.codex\skills\a3ip-creator"
$stamp   = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$backup  = "$env:USERPROFILE\.codex\backups\a3ip-creator-$stamp"
if (Test-Path -LiteralPath $skill) {
    New-Item -ItemType Directory -Path (Split-Path $backup) -Force
    Copy-Item -LiteralPath $skill -Destination $backup -Recurse -Force
}
```

Tell the operator the backup path so they can roll back if anything misbehaves.

### Step C5: Install the skill files

Replace the live skill directory with the validated extraction. The skill's `SKILL.md` lives at the root of the skill directory; the bundle layout has it under `components/skills/a3ip-creator/SKILL.md`, so the install adapter needs to lift it to the right level.

```
# Remove the old skill (after backing up in C4)
Remove-Item -LiteralPath $skill -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $skill -Force

# Copy the extracted package contents into the skill root
Copy-Item -Path (Join-Path $work '*') -Destination $skill -Recurse -Force

# Lift SKILL.md to the skill root (Codex loads SKILL.md from there, not from components/)
Copy-Item -LiteralPath (Join-Path $work 'components\skills\a3ip-creator\SKILL.md') `
          -Destination (Join-Path $skill 'SKILL.md') -Force
```

**PowerShell gotcha:** `-LiteralPath` does NOT expand wildcards. Use `-Path` when copying with `*`, `-LiteralPath` only when you have an exact filename and want to avoid wildcard interpretation. Mixing these incorrectly was a real issue seen during Phase 1 dogfooding: a `-LiteralPath ... \*` copy only moved the literally-named file and silently skipped the rest.

### Step C6: Write installed.json

```
$pkg = "$env:USERPROFILE\.codex\packages\a3ip-creator"
New-Item -ItemType Directory -Path $pkg -Force

# Build the record. Use install_method: "generic-copy" per spec v1.8.
$record = [ordered]@{
    package        = 'a3ip-creator'
    version        = '<NEW>'
    installed_at   = (Get-Date).ToUniversalTime().ToString('o')
    upgraded_from  = '<previous version, or omit if fresh install>'
    platform       = 'codex'
    a3ip_spec      = '1.8'
    config_dir     = $pkg
    install_method = 'generic-copy'
    source_bundle  = '<absolute path to the .a3ip.bundle used>'
    backup_dir     = '<absolute path to backup from C4, or omit if fresh>'
}
($record | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath "$pkg\installed.json" -Encoding UTF8
```

Per spec v1.8: `upgraded_from`, `source_bundle`, and `backup_dir` are optional. Include them if applicable; readers MUST tolerate their absence.

### Step C7: Verify the install

```
a3ip validate $skill
```

Should report `[OK] Validation passed - no errors or warnings.` (a3ip 1.3.1+ uses ASCII-safe output; older versions printed the Unicode `✓` which crashed on cp1252).

Then prompt the operator to start a new Codex session and try the Creator's trigger phrase:

> "create an A3IP package"

Codex should respond by loading the Creator SKILL.md and beginning the intake conversation (Phase 0 → Phase 1).

### Step C8: Clean up

```
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
```

## Upgrading an existing Codex install

Triggered when Step C1 found `~/.codex/packages/a3ip-creator/installed.json`.

1. Read the `version` field. Determine which CHANGELOG entries need to apply (everything between installed version and the bundle's version).
2. Apply each version's `### Upgrade steps` in order. For Creator-on-Codex this is usually just "replace the files" — Steps C3 through C7 above suffice for any minor/patch upgrade.
3. For major bumps or breaking changes (per CHANGELOG `### Breaking changes`), follow the explicit instructions in that version's changelog entry before re-running C3-C7.
4. Update `installed.json` (Step C6) with the new version and `upgraded_from` = previous version. Preserve `config_dir`, `install_method`, optionally bump `a3ip_spec` and `backup_dir`.

## Troubleshooting

**`a3ip` command not on PATH after `pip install --user`:** find the binary at `$env:APPDATA\Python\Python<XY>\Scripts\a3ip.exe` and invoke explicitly, or add that directory to PATH.

**Unicode crash when running validate or bundle:** upgrade to a3ip CLI 1.3.1 or higher (`pip install --upgrade --user a3ip`). v1.3.1 uses ASCII-safe console output by default. Workaround for older versions: `$env:PYTHONIOENCODING = 'utf-8'`.

**PowerShell `-LiteralPath` + wildcard quietly skips most files:** use `-Path` for wildcard copies; reserve `-LiteralPath` for exact filenames. After any `Copy-Item -Recurse`, verify by listing the destination.

**Skill doesn't trigger on "create an A3IP package":** confirm `~/.codex/skills/a3ip-creator/SKILL.md` exists at the skill root (not buried under `components/`). Codex reads SKILL.md from the directory root.
