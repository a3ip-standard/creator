# Codex runtime adapter (uninstall) — {{name}}

> **This file is a Creator template.** It was copied from
> `creator-repo/components/runtime-adapter-templates/codex/uninstall-skill.md`
> into `{{name}}/adapters/runtime/codex/uninstall-skill.md` during
> scaffold. Generic placeholders use `{{name}}` for the package name and
> italicised angle-bracket placeholders for per-package component
> identifiers. Adapt the worked examples to this package's actual
> components and remove this banner before shipping a release.

This adapter is platform-knowledge for **uninstalling** `{{name}}` on
**Codex**. The installing AI reads this as context, then applies it to
satisfy the Tier 2 outcomes in INSTALL.md's `## Uninstalling` section
— specifically Step UN1 (locate the install), Step UN3 (make the skill
un-discoverable), Step UN4 (remove artifacts, if any), and Step UN5
(make protocols no longer invocable). The mechanical steps (UN2, UN6,
UN7, UN8) are governed by INSTALL.md and the A3IP spec, not by this
adapter.

Per A3IP spec v1.10 'Writing Adapter Documents', adapter content is
platform knowledge, not installation script. The code blocks below are
illustrative worked examples — adapt them to actual paths, AGENTS.md
state, and user choices rather than executing them verbatim.

This adapter is the symmetric counterpart of `install-skill.md` —
every mechanism that the install side put in place, the uninstall side
reverses.

## How Codex stores installed packages (UN1 discovery)

Codex itself does not maintain a global index of installed A3IP
packages. Discovery goes through two places:

1. **`installed.json` at the package's config directory.** For
   `{{name}}` on Codex, the default install location is
   `~/.codex/packages/{{name}}/` — but the user may have customised
   it during install. Read `~/.codex/packages/{{name}}/installed.json`
   first via the OS-appropriate file tool (on Windows where Codex CLI
   typically runs, that is the same path-expansion rules described in
   `adapters/os/windows/file-ops.md`).

2. **The AGENTS.md marker block.** Even if `installed.json` is absent
   or corrupted, the presence of a `<!-- a3ip:{{name}}:start -->` ...
   `<!-- a3ip:{{name}}:end -->` block in `~/.codex/AGENTS.md`
   indicates a prior install whose marker outlived the config
   directory. Treat that as evidence of a partial install needing
   cleanup: complete UN3 (marker removal) at minimum, even if the
   config directory is already gone.

If both `installed.json` and the AGENTS.md marker block are absent,
exit cleanly — there is genuinely nothing to uninstall.

Once located, read `installed.json` for `version`, `platform`,
`config_dir`, and `install_method`. The `install_method:
"generic-copy"` value (set during Codex install per spec v1.10) tells
you this was a Codex-flow install and confirms you're in the right
adapter.

## How Codex un-registers skills (UN3)

This is the critical inverse of install Step C5 (writing the AGENTS.md
marker block). **Removing the AGENTS.md marker block is what actually
makes the skill un-discoverable on Codex** — the SKILL.md file on disk
is inert without the AGENTS.md registration. Two operations:

1. **Remove the marker block from `~/.codex/AGENTS.md`.** Find the
   lines between (and including) `<!-- a3ip:{{name}}:start -->` and
   `<!-- a3ip:{{name}}:end -->` and delete them. Preserve every other
   line in the file unchanged — AGENTS.md may contain unrelated
   instructions from the user or other installations.

2. **Remove the skill files at `~/.codex/skills/{{name}}/`.** This is
   `rm -rf` semantics on the skill directory. After this, no files
   reference the skill on disk; combined with the AGENTS.md cleanup,
   the skill is fully gone.

Order matters: remove the AGENTS.md marker FIRST. If the file removal
fails mid-flow (e.g., permissions error), at least the registration
is gone — which is the actually-load-bearing piece. A stale skill
directory with no AGENTS.md reference is dormant; AGENTS.md reference
with no skill files is broken (next session, Codex tries to read a
missing path).

Illustrative (the marker-block removal pattern):

```python
import re
from pathlib import Path

agents_md = Path.home() / ".codex" / "AGENTS.md"
text = agents_md.read_text(encoding="utf-8")

# Match the entire block, including surrounding whitespace
pattern = re.compile(
    r"\n*<!-- a3ip:{{name}}:start -->.*?<!-- a3ip:{{name}}:end -->\n*",
    re.DOTALL,
)
new_text = pattern.sub("\n", text).rstrip() + "\n"

agents_md.write_text(new_text, encoding="utf-8")
```

If the marker block is not present in AGENTS.md (the install was
already partially uninstalled, or AGENTS.md was edited manually), do
not treat this as an error. The outcome — "the skill is not registered
with Codex" — is already satisfied. Continue to file removal.

## How Codex removes artifacts (UN4)

If `{{name}}` declared artifacts in its manifest, the install side
seeded `{{config.install_dir}}/<artifact-name>.md` from the bundled
`components/artifacts/<artifact-name>/artifact.md` template for each
one. Uninstall removes these files.

If the user chose to preserve at least one configuration key in
Step UN2, an artifact MAY be preserved at the AI's discretion — it
may carry non-derivable history. The default is to delete
unconditionally.

Illustrative (one artifact named *`<your-artifact-name>`*):

```python
from pathlib import Path

artifact_record = Path(config_dir) / "<your-artifact-name>.md"
if artifact_record.exists():
    artifact_record.unlink()
```

If `{{name}}` ships no artifacts, this step is a no-op.

## How Codex de-registers protocols (UN5)

Codex protocols are registered through the same AGENTS.md marker block
as the skill itself — the block lists trigger phrases that map to the
SKILL.md path. So **removing the AGENTS.md marker block in UN3
transitively un-registers the protocol triggers**, making UN5 a no-op
on Codex once UN3 completes.

If UN3 has not run yet (e.g., the user aborted between UN2 and UN3)
and UN5 is reached anyway, the outcome cannot be satisfied — return
to UN3.

## Worked example: the uninstall flow on Codex

The steps below describe one cohesive way to satisfy the Tier 2
outcomes on Codex. The uninstall AI may adapt for variations.

### Step UX1: Locate the install (UN1)

Read `~/.codex/packages/{{name}}/installed.json`. If absent, check
`~/.codex/AGENTS.md` for an `a3ip:{{name}}:start` marker. If both
absent, exit cleanly.

### Step UX2: Show the Uninstall Plan (UN2 — mechanical, handled by INSTALL.md)

Walk the config schema. Per the v1.10 `preserve_on_uninstall`
annotations, ask one focused question per `ask` key, silently purge
each `false` key, silently preserve each `true` key. Confirm.

### Step UX3: Remove AGENTS.md marker + skill files (UN3)

Apply the marker-block removal pattern shown above against
`~/.codex/AGENTS.md`. Then delete the directory tree at
`~/.codex/skills/{{name}}/` (typical pattern:
`shutil.rmtree(skill_dir, ignore_errors=False)`).

### Step UX4: Remove artifact records (UN4)

For each artifact declared in the package, delete
`{{config.install_dir}}/<artifact-name>.md` if present. Skip if the
user chose to preserve config and the artifact carries history the
user wanted to keep. If `{{name}}` ships no artifacts, skip.

### Step UX5: Protocols (UN5)

No-op once UX3 completes (the marker-block removal already cleaned
this up). Confirm to the user that the package's triggers no longer
fire.

### Step UX6: Trim config.json and remove install_dir contents (UN6 — mechanical)

Read `config.json` from `config_dir`. Construct a new object with
only the keys the user chose to preserve (plus any
`preserve_on_uninstall: true` keys). Write it back, or delete the
file if no keys survive.

Delete every other file and subdirectory in `config_dir` EXCEPT
`config.json` (if preserved) and `installed.json`. Artifact records
were handled in UX4.

### Step UX7: Remove installed.json (UN7 — mechanical)

Delete `config_dir/installed.json`. If `config_dir` is now empty,
remove the directory too.

### Step UX8: Confirm (UN8 — mechanical)

Tell the user the uninstall is complete. Name:
1. The version that was uninstalled.
2. Which configuration keys were preserved and where.
3. Which keys were purged.
4. That the AGENTS.md marker block was removed, and the rest of the
   file was preserved unchanged. Re-mention this so the user knows
   their other AGENTS.md content (if any) survived.
5. Any leftover state: e.g., if any artifact records were preserved,
   mention their locations.

## Edge cases

**AGENTS.md does not exist.** The user never had any A3IP package
installed on this Codex setup, or they deleted AGENTS.md manually.
UN3 becomes a partial no-op: there is no marker block to remove.
Skill file removal (UN3 second operation) still applies if
`~/.codex/skills/{{name}}/` exists. After UN3, confirm to the user
that the file's absence was noted.

**The AGENTS.md marker block is missing the closing marker.** Manual
editing or a botched re-install can leave only `:start` without
`:end`, or vice versa. The regex above will fail to match — offer
the user a human-edited cleanup, or remove from the start marker to
end-of-file as a fallback.

**The user customised AGENTS.md content INSIDE the marker block.**
The markers are a contract — their contents are owned by the
package. Any hand-edits the user made between `:start` and `:end`
will be lost when the block is removed. This is the expected
behaviour; the AI may warn the user but does not preserve such
edits.

**The user deleted `~/.codex/skills/{{name}}/` manually between
install and uninstall.** UN3 file-removal step is a no-op (directory
does not exist). Continue; only the AGENTS.md cleanup matters.

**Windows host with OneDrive-redirected user home.** `~/.codex/`
resolves through `$env:USERPROFILE`, which may point to
`C:\Users\<user>\OneDrive\` rather than `C:\Users\<user>\`. The
Windows file-ops adapter in `adapters/os/windows/file-ops.md` covers
this — use the YES-row tool to expand `~` properly. Bash's `~` will
NOT work on a Windows-hosted Codex.
