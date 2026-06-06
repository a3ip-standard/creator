# Claude Code runtime adapter — {{name}}

> **This file is a Creator template.** It was copied from
> `creator-repo/components/runtime-adapter-templates/claude-code/install-skill.md`
> into `{{name}}/adapters/runtime/claude-code/install-skill.md`
> during scaffold. Generic placeholders use `{{name}}` for the package
> name and italicised angle-bracket placeholders (e.g.
> *`<your-script>`*) for per-package component identifiers. Adapt the
> worked examples to this package's actual components and remove this
> banner before shipping a release.

This adapter is platform-knowledge for installing `{{name}}` on
**Claude Code** (Anthropic's CLI developer agent). The installing AI
reads this as context, then applies it to satisfy the Tier 2 outcomes
in INSTALL.md — specifically the "make skills discoverable" step, the
"make artifacts available" step (if this package ships artifacts), and
the "make protocols invocable" step. The rest of INSTALL.md still
applies — install detection, configure wizard, resolve install_dir,
write config.json, write installed.json, and the Upgrading flow — all
governed by INSTALL.md and the A3IP spec, not by this adapter.

Per A3IP spec v1.10 'Writing Adapter Documents', adapter content is
platform knowledge, not installation script. The code blocks below are
illustrative worked examples — adapt them to actual paths and user
choices rather than executing them verbatim.

## How Claude Code discovers skills

Claude Code **auto-discovers skills from `~/.claude/skills/`** on each
session start. Unlike Codex, no separate registration step is needed
— dropping a directory with a SKILL.md file into the skills folder is
sufficient for the runtime to surface it.

This makes the Claude Code install flow shorter than Codex's:

- **Skill files live at `~/.claude/skills/{{name}}/`** — one directory
  per skill. The directory must contain `SKILL.md` at its root (Claude
  Code looks for SKILL.md there, not under `components/`).
- **No AGENTS.md, no slash-command registration, no UI step.** The
  skill becomes available the next time Claude Code reads its skill
  index — typically on next session start, though `claude --refresh`
  or equivalent commands may force a re-scan in-session if the runtime
  supports it.
- **Triggers come from the SKILL.md frontmatter.** The `description:`
  field's trigger-phrase content is what Claude Code matches user
  utterances against. The package's protocol triggers transitively
  satisfy the "make protocols invocable" outcome once the skill is
  in place.

There is no UI registry, no marker file, no "Save skill" button. File
presence is the registration.

## Other Claude Code conventions

**Per-install state** lives at `{{config.install_dir}}` (typically
`~/.claude/packages/{{name}}/`). This is where `config.json`,
`installed.json`, and any package-managed runtime records live. These
paths are governed by INSTALL.md and the A3IP spec, not by this
adapter.

**No HTML artifact mechanism.** Claude Code has no equivalent of
Cowork's `mcp__cowork__create_artifact`. Artifacts degrade to markdown
files the runtime updates in-place at
`{{config.install_dir}}/<artifact-name>.md`. The SKILL.md still
treats each as a single named record — same purpose, different
medium. Seed each from
`components/artifacts/<artifact-name>/artifact.md` at install time.

**No "Save skill" UI.** Skills install as plain files; there's no
restart-required UI flow. The next session reads files fresh.

**`install_method: "generic-copy"`** in `installed.json` per A3IP
spec v1.10 Platform Conventions, distinguishing the Claude Code flow
from Cowork's `"cowork-skill"` UI flow. (Claude Code shares the
generic-copy method with Codex; the difference between them is the
registration mechanism — Claude Code auto-discovers, Codex needs the
AGENTS.md stanza.)

**Host OS default is POSIX.** Claude Code is typically deployed on
macOS or Linux developer machines. Windows is supported (via WSL or
native), but path operations and shell semantics default to POSIX
conventions in this adapter. On a Windows host, follow
`adapters/os/windows/file-ops.md` for OS-specific deviations.

**`~` expansion is well-defined.** Claude Code runs in the user's
native shell environment; `~` expands to `$HOME` (POSIX) or
`%USERPROFILE%` (Windows) without ambiguity. (Contrast with Cowork's
bash sandbox, where `~` resolves to an ephemeral Linux home.)

## What gets installed where

| Artifact | Claude Code location | Mechanism |
|---|---|---|
| Skill payload (SKILL.md + scripts/) | `~/.claude/skills/{{name}}/` | File copy; auto-discovered on next session |
| Per-install state | `{{config.install_dir}}` | config.json, installed.json, artifact markdown record(s) |
| Each artifact record (if any) | `{{config.install_dir}}/<artifact-name>.md` | Markdown the runtime rewrites after each trigger |

## Worked example: the install flow on Claude Code

The steps below are illustrative — they describe one way to achieve
the Tier 2 outcomes on Claude Code. The install AI may adapt for
variations (the user's install_dir, a Windows host where POSIX
shell idioms need PowerShell translation, an existing skill from a
prior install).

### Step C1: Detect prior install

Look at `{{config.install_dir}}/installed.json`. Use the file tool
that expands `~` correctly on this host (`os.path.expanduser('~')` in
Python or shell-native `~` substitution).

- **Found:** read the `version` field. Go to **Upgrading an existing
  Claude Code install** at the end of this document.
- **Not found:** continue with fresh install.

### Step C2: Extract bundle to a temp directory and validate

Before touching `~/.claude/skills/`, unpack the `.a3ip.bundle` into a
temp working directory and run `a3ip validate` against the unpacked
tree. This catches bundle-parsing issues before they affect the live
install.

```bash
BUNDLE="<path to {{name}}-vX.Y.Z.a3ip.bundle>"
WORK="$(mktemp -d)/{{name}}-vX.Y.Z-extracted"
mkdir -p "$WORK"
# Parse the bundle (line-delimited === FILE: <path> === blocks) and
# write each file under $WORK using your scripting tool of choice.

a3ip validate "$WORK"
```

If validation fails, do NOT proceed to overwriting the live skill
directory. Fix or escalate.

### Step C3: Back up existing skill (if upgrading)

If `~/.claude/skills/{{name}}/` exists, back it up before overwriting.
A timestamped folder under `~/.claude/backups/` is the convention;
tell the user the backup path so they can roll back.

```bash
SKILL="$HOME/.claude/skills/{{name}}"
BACKUP_ROOT="$HOME/.claude/backups"
if [ -d "$SKILL" ]; then
    mkdir -p "$BACKUP_ROOT"
    cp -r "$SKILL" "$BACKUP_ROOT/{{name}}-$(date +%Y%m%dT%H%M%S)"
fi
```

### Step C4: Install the skill payload

Replace the live skill directory with the validated extraction. The
runtime payload is everything SKILL.md needs at runtime: SKILL.md
itself (lifted to the skill root), the scripts it invokes, and any
artifact templates it reads.

Lift `components/skills/<your-skill-name>/SKILL.md` to `$SKILL/SKILL.md`
(the skill root) — Claude Code looks there, not in `components/`.
Then substitute the absolute `install_dir` into all markdown files
in the installed skill (SKILL.md plus any protocol files that
reference `{{install_dir}}`). Rationale: `install_dir` is a non-secret
deterministic path — substituting it at install time is the only way
the runtime AI knows where to read config.json. Other config keys
(tokens, secrets, identifiers) are NOT substituted; they stay in
config.json so the skill remains portable across config changes.

**Path-separator normalization (required).** The `install_dir` value
sourced from `CONFIGURE.md` or a prior `installed.json` may end with
a trailing path separator. SKILL.md templates reference files as
`{{install_dir}}/config.json` with a leading `/`. A naive substitution
of a trailing-separator value into a leading-slash template produces
a path with a doubled separator. On POSIX the kernel collapses `//`,
but on Windows hosts (Claude Code via WSL or native) mixed
separators may still cause issues. Strip trailing `/` and `\` from
the install_dir value before substituting.

Illustrative (POSIX shell; Windows hosts adapt to PowerShell per
`adapters/os/windows/file-ops.md`):

```bash
SKILL="$HOME/.claude/skills/{{name}}"
INSTALL_DIR="<absolute install_dir from CONFIGURE.md>"
INSTALL_DIR="${INSTALL_DIR%/}"      # strip trailing /
INSTALL_DIR="${INSTALL_DIR%\\}"     # strip trailing \

rm -rf "$SKILL"
mkdir -p "$SKILL"
cp -r "$WORK"/* "$SKILL"/
cp "$WORK/components/skills/<your-skill-name>/SKILL.md" "$SKILL/SKILL.md"

# Substitute {{install_dir}} in every .md file in the installed skill
find "$SKILL" -name '*.md' -type f | while read -r f; do
    if grep -q '{{install_dir}}' "$f"; then
        sed -i.bak "s|{{install_dir}}|$INSTALL_DIR|g" "$f"
        rm "$f.bak"
    fi
done
```

(macOS uses `sed -i ''` instead of `sed -i.bak` + `rm`; adapt as
needed. Or use Python for portable substitution.)

### Step C5: Initialize artifact record(s) — if any

For each artifact declared in the package manifest, create a markdown
file the runtime will keep up to date. This is the Claude Code-side
stand-in for Cowork's artifact card: same purpose (one record,
updated on trigger), different medium.

```bash
RECORD="$INSTALL_DIR/<artifact-name>.md"
if [ ! -f "$RECORD" ]; then
    cp "$WORK/components/artifacts/<artifact-name>/artifact.md" "$RECORD"
fi
```

If the record already exists (from a previous install), leave it in
place — it carries the user's most recent state. The SKILL.md
updates the file in place on each trigger.

If `{{name}}` ships no artifacts, skip this step entirely.

### Step C6: Write installed.json

Per A3IP spec v1.10 Platform Conventions, Claude Code installs use
`install_method: "generic-copy"`:

```json
{
  "package": "{{name}}",
  "version": "<NEW>",
  "installed_at": "<ISO-8601 timestamp>",
  "upgraded_from": "<previous version, or omit if fresh install>",
  "platform": "claude-code",
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

### Step C7: Verify the install end-to-end

Two confirmations:

1. **Static:** `a3ip validate $SKILL` should report
   `[OK] Validation passed`.
2. **Runtime:** start a NEW Claude Code session (so the skill index is
   freshly scanned) and say one of the package's trigger phrases. The
   AI should recognise the trigger, read config from
   `<install_dir>/config.json`, and behave per the SKILL.md. If
   Claude Code does not recognise the trigger, check that the skill
   directory exists at `~/.claude/skills/{{name}}/` and contains a
   valid SKILL.md with the expected `description:` frontmatter.

### Step C8: Clean up

```bash
rm -rf "$WORK"
```

## Upgrading an existing Claude Code install

Triggered when Step C1 found `{{install_dir}}/installed.json`.

1. Read the `version` field. Determine which CHANGELOG entries need
   to apply (everything between installed version and the bundle's
   version).
2. Apply each version's `### Upgrade steps` in order. For most
   packages on Claude Code this is "replace the skill files" —
   Steps C2 through C7 above suffice for any minor/patch upgrade.
   Artifact records are preserved through Step C5's idempotency.
3. For major bumps or breaking changes (per CHANGELOG
   `### Breaking changes`), follow the explicit instructions in
   that version's changelog entry before re-running C2–C7. If config
   keys changed, re-run the wizard for those keys and rewrite
   `config.json` before reinstalling the skill payload.
4. Update `installed.json` (Step C6) with the new version and
   `upgraded_from` = previous version. Preserve `config_dir`,
   `install_method`, optionally bump `a3ip_spec` and `backup_dir`.

## Troubleshooting

**`a3ip` command not on PATH after `pip install --user`:** find the
binary at `~/.local/bin/a3ip` (POSIX) or
`$env:APPDATA\Python\Python<XY>\Scripts\a3ip.exe` (Windows) and
invoke explicitly, or add that directory to PATH. (Note: most
packages do not require `a3ip` at runtime — only the install AI
uses it for `a3ip validate`.)

**Skill files installed but Claude Code doesn't recognise the
trigger:** confirm the SKILL.md is at the **root** of
`~/.claude/skills/{{name}}/` (not under a `components/` subdirectory)
and has the expected `description:` frontmatter. Then start a NEW
session — Claude Code's skill index is read at startup and may not
pick up a newly-added skill until the next session.

**Script fails with "config file not found":** SKILL.md still
contains a literal `{{install_dir}}` because Step C4's substitution
was skipped. Re-run Step C4, ensuring the substitution variable is
the absolute path the user chose during CONFIGURE.md.

**Artifact record never updates:** the skill writes via the runtime's
file tool. Confirm the path is correct and the user account has write
permission to `{{config.install_dir}}`.

**Unicode crash when running validate:** upgrade to a3ip CLI 1.3.1 or
higher (`pip install --upgrade --user a3ip`). v1.3.1+ uses ASCII-safe
console output by default.

**OneDrive-redirected `$HOME` on Windows.** If `~` resolves through
`%USERPROFILE%` to a OneDrive-redirected path, file operations work
but may be slower on first access. The Windows file-ops adapter at
`adapters/os/windows/file-ops.md` covers this case.
