# Claude Code runtime adapter (uninstall) — {{name}}

> **This file is a Creator template.** It was copied from
> `creator-repo/components/runtime-adapter-templates/claude-code/uninstall-skill.md`
> into `{{name}}/adapters/runtime/claude-code/uninstall-skill.md`
> during scaffold. Generic placeholders use `{{name}}` for the
> package name and italicised angle-bracket placeholders for
> per-package component identifiers. Adapt the worked examples to
> this package's actual components and remove this banner before
> shipping a release.

This adapter is platform-knowledge for **uninstalling** `{{name}}`
on **Claude Code**. The installing AI reads this as context, then
applies it to satisfy the Tier 2 outcomes in INSTALL.md's
`## Uninstalling` section — specifically Step UN1 (locate the
install), Step UN3 (make the skill un-discoverable), Step UN4
(remove artifacts, if any), and Step UN5 (make protocols no longer
invocable). The mechanical steps (UN2, UN6, UN7, UN8) are governed
by INSTALL.md and the A3IP spec, not by this adapter.

Per A3IP spec v1.10 'Writing Adapter Documents', adapter content is
platform knowledge, not installation script. The code blocks below
are illustrative worked examples — adapt them to actual paths and
user choices rather than executing them verbatim.

This adapter is the symmetric counterpart of `install-skill.md` —
every mechanism that the install side put in place, the uninstall
side reverses.

## How Claude Code stores installed packages (UN1 discovery)

Claude Code itself does not maintain a global index of installed
A3IP packages. Discovery is per-package and goes through the
package's own `installed.json` at the configured `install_dir`.

For `{{name}}` on Claude Code, the default install location is
typically `~/.claude/packages/{{name}}/` — but the user may have
customised it during install. The discovery procedure is:

1. **Default-path check first.** Read
   `~/.claude/packages/{{name}}/installed.json` via the file tool
   that expands `~` correctly on this host. If the file exists,
   parse its `config_dir` field — that is the authoritative install
   location for THIS install.

2. **Followed by the file's own `config_dir`.** Once you have the
   file's `config_dir`, that is where every subsequent uninstall
   step operates. Treat it as authoritative for the rest of the
   flow.

3. **If the default-path file is absent**, the user almost certainly
   did not customise `install_dir`. Exit cleanly: tell the user
   "{{name}} is not installed at the platform-default location;
   if you customised install_dir on install, please provide the
   path."

Read `installed.json` for `version`, `platform`, `config_dir`, and
`install_method`. The `install_method: "generic-copy"` value tells
you this was a Claude Code-flow install (or another generic-copy
platform). The `platform: "claude-code"` field confirms you're in
the right adapter.

## How Claude Code un-registers skills (UN3)

Because Claude Code **auto-discovers skills from
`~/.claude/skills/`**, un-discovery is the inverse: delete the skill
directory. There is no AGENTS.md stanza to remove (Codex), no UI
panel to click through (Cowork). One operation:

1. **Remove the skill directory at `~/.claude/skills/{{name}}/`.**
   This is `rm -rf` semantics on the skill directory. After this,
   Claude Code's next session scan will not find the skill, and its
   trigger phrases will no longer match user utterances.

Illustrative (POSIX shell):

```bash
SKILL="$HOME/.claude/skills/{{name}}"
if [ -d "$SKILL" ]; then
    rm -rf "$SKILL"
fi
```

On Windows hosts (Claude Code via WSL or native PowerShell), follow
`adapters/os/windows/file-ops.md` for the equivalent OS-appropriate
operation (`Remove-Item -LiteralPath $skill -Recurse -Force` in
PowerShell).

Skill removal takes effect on the next session start. If the user
has Claude Code running, ask them to start a fresh session so the
skill index is re-scanned without the removed entry. (The current
session may still have the skill loaded; that's harmless — the
files are gone, future sessions won't see them.)

## How Claude Code removes artifacts (UN4)

If `{{name}}` declared artifacts in its manifest, the install side
seeded `{{config.install_dir}}/<artifact-name>.md` from the bundled
`components/artifacts/<artifact-name>/artifact.md` template for
each one. Uninstall removes these files.

If the user chose to preserve at least one configuration key in
Step UN2, an artifact MAY be preserved at the AI's discretion — it
may carry non-derivable history. The default is to delete
unconditionally.

Illustrative (POSIX shell, one artifact named
*`<your-artifact-name>`*):

```bash
RECORD="$INSTALL_DIR/<your-artifact-name>.md"
if [ -f "$RECORD" ]; then
    rm "$RECORD"
fi
```

If `{{name}}` ships no artifacts, this step is a no-op.

## How Claude Code de-registers protocols (UN5)

Claude Code protocol triggers come from the SKILL.md `description:`
frontmatter. Once Step UN3 removes the skill directory, the
triggers are no longer discoverable — Claude Code's next session
will not match user utterances to the removed package. So
**UN5 is a no-op once UN3 completes**.

If UN3 has not run yet and UN5 is reached anyway, the outcome
cannot be satisfied — return to UN3.

## Worked example: the uninstall flow on Claude Code

The steps below describe one cohesive way to satisfy the Tier 2
outcomes on Claude Code. The uninstall AI may adapt for variations
(e.g., the skill was already removed manually; the user customised
install_dir).

### Step UCC1: Locate the install (UN1)

Read `~/.claude/packages/{{name}}/installed.json` via the
host-appropriate file tool. If present, capture `config_dir`,
`version`, `platform`. If absent, exit cleanly.

### Step UCC2: Show the Uninstall Plan (UN2 — mechanical, handled by INSTALL.md)

Walk the config schema. Per the v1.10 `preserve_on_uninstall`
annotations, ask one focused question per `ask` key, silently
purge each `false` key, silently preserve each `true` key. Confirm.

### Step UCC3: Remove skill directory (UN3)

Delete the directory tree at `~/.claude/skills/{{name}}/`. If the
directory does not exist (the user removed it manually, or a prior
uninstall already cleaned it), treat as success — the outcome is
satisfied.

Ask the user to start a fresh Claude Code session so the skill
index is re-scanned without the removed entry.

### Step UCC4: Remove artifact records (UN4)

For each artifact declared in the package, delete
`{{config.install_dir}}/<artifact-name>.md` if present. Skip if
the user chose to preserve config and the artifact carries history
the user wanted to keep. If `{{name}}` ships no artifacts, skip.

### Step UCC5: Protocols (UN5)

No-op once UCC3 completes. Confirm to the user that the package's
triggers no longer fire in fresh sessions.

### Step UCC6: Trim config.json and remove install_dir contents (UN6 — mechanical)

Read `config.json` from `config_dir`. Construct a new object with
only the keys the user chose to preserve (plus any
`preserve_on_uninstall: true` keys). Write it back, or delete the
file if no keys survive.

Delete every other file and subdirectory in `config_dir` EXCEPT
`config.json` (if preserved) and `installed.json`. Artifact records
were handled in UCC4.

### Step UCC7: Remove installed.json (UN7 — mechanical)

Delete `config_dir/installed.json`. If `config_dir` is now empty,
remove the directory too.

### Step UCC8: Confirm (UN8 — mechanical)

Tell the user the uninstall is complete. Name:
1. The version that was uninstalled.
2. Which configuration keys were preserved and where.
3. Which keys were purged.
4. That the skill directory at `~/.claude/skills/{{name}}/` has
   been removed — the package's triggers no longer fire in fresh
   Claude Code sessions.
5. Any leftover state: e.g., if any artifact records were
   preserved, mention their locations.

## Edge cases

**The skill directory was already removed before uninstall ran.**
UCC3 becomes a no-op. The AI tells the user "the skill directory is
already absent; continuing with config and file cleanup."

**`installed.json` is missing but the install_dir has other files.**
This indicates a partial install. The AI MAY offer to clean up the
leftover files or leave them in place at the user's choice.

**The user changed the `install_dir` since install.** The
`config_dir` stored in `installed.json` is the authoritative source.
If the user moved the directory between install and uninstall, ask
them where the package's files actually live and use that path
instead.

**Windows host (Claude Code via WSL or native).** All POSIX shell
idioms above need PowerShell or WSL-bash translation. See
`adapters/os/windows/file-ops.md` for the canonical tool-selection
guidance.

**OneDrive-redirected `$HOME` on Windows.** `~` resolves through
`%USERPROFILE%`, which may point to `C:\Users\<user>\OneDrive\`
rather than `C:\Users\<user>\`. The Windows file-ops adapter
covers this — use the YES-row tool to expand `~` properly.
