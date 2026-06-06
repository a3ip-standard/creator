# Cowork runtime adapter (uninstall) — {{name}}

> **This file is a Creator template.** It was copied from
> `creator-repo/components/runtime-adapter-templates/cowork/uninstall-skill.md`
> into `{{name}}/adapters/runtime/cowork/uninstall-skill.md` during
> scaffold. Generic placeholders use `{{name}}` for the package name and
> italicised angle-bracket placeholders (e.g. *`<your-artifact-name>`*)
> for per-package component identifiers. Adapt the worked examples to
> this package's actual components and remove this banner before
> shipping a release.

This adapter is platform-knowledge for **uninstalling** `{{name}}` on
Cowork. The installing AI reads this as context, then applies it to
satisfy the Tier 2 outcomes in INSTALL.md's `## Uninstalling` section
— specifically Step UN1 (locate the install), Step UN3 (make the skill
un-discoverable), Step UN4 (remove the artifact, if any), and Step UN5
(make protocols no longer invocable). The mechanical steps (UN2, UN6,
UN7, UN8) are governed by INSTALL.md and the A3IP spec, not by this
adapter.

Per A3IP spec v1.10 'Writing Adapter Documents', adapter content is
platform knowledge, not installation script. The code blocks below are
illustrative worked examples — adapt them to actual paths and user
choices rather than executing them verbatim.

This adapter is the symmetric counterpart of `install-skill.md` —
every mechanism that the install side put in place, the uninstall side
reverses.

## How Cowork stores installed packages (UN1 discovery)

Cowork itself does not maintain a global index of which A3IP packages
are installed. Discovery is per-package and goes through the package's
own `installed.json` artifact at the configured `install_dir`.

For `{{name}}` on Cowork, the default install location is typically
`~/.claude/packages/{{name}}/` — but the user may have customised it
during the configure wizard. So the discovery procedure is:

1. **Default-path check first.** Read
   `~/.claude/packages/{{name}}/installed.json` via
   `mcp__filesystem__read_file`. On Cowork (Windows), `~` expands to
   the Windows user home through that tool. If the file exists, parse
   its `config_dir` field — that is the authoritative install location
   for THIS install. (The default-path lookup is just a starting
   point; the user may have customised.)

2. **Followed by the file's own `config_dir`.** Once you have the
   file's `config_dir`, that is where every subsequent uninstall step
   operates. Treat it as authoritative for the rest of the flow.

3. **If the default-path file is absent**, the user almost certainly
   did not customise `install_dir` (custom paths only happen if the
   user actively typed one in during install). Exit cleanly: tell the
   user "{{name}} is not installed at the platform-default location;
   if you customised install_dir on install, please provide the path."

Do NOT use the bash sandbox to read `installed.json` — bash's `~` is
the ephemeral Linux sandbox home, not the Windows user home. The
`mcp__filesystem__read_file` tool is the right path.

## How Cowork un-registers skills (UN3)

The install side registers the skill via the **Personal Skills UI** —
the user drags the `.skill` zip into Cowork and clicks "Save skill".
Uninstall inverts this:

1. **Tell the user to remove the skill from the Cowork UI.** Cowork
   does not expose a programmatic skill-removal API to the running
   session. The user removes `{{name}}` (named per the SKILL.md's
   `name:` field inside Cowork's Personal Skills panel) by selecting
   it and clicking the delete/remove action. Cowork will prompt for
   confirmation.

2. **Cowork's skill registry is in-process state**, refreshed at
   startup. After the user removes the skill, ask them to restart
   Cowork so the removal takes effect for new sessions. (The current
   session may still have the skill loaded; that's harmless — the
   file is gone, future sessions won't see it.)

3. **Do not try to delete skill files from disk yourself.** Cowork
   stores installed skills under an internal location managed by the
   UI; touching it from outside can corrupt the registry. The UI
   removal is the only supported deregistration path.

Once the skill is removed from Personal Skills, its `description:`
trigger phrases are no longer registered with Cowork — which
transitively satisfies Step UN5 (protocols no longer invocable) since
Cowork loads protocol triggers from the skill's frontmatter.

Illustrative (the message you send to the user during Step UN3 —
substitute the skill's Cowork display name):

```text
To complete the uninstall, open Cowork's Personal Skills panel
(usually in the sidebar or settings), find "<your-skill-name>", and
click Remove. Cowork will prompt for confirmation. After removal,
restart Cowork so the skill no longer appears in new sessions.
```

## How Cowork removes artifacts (UN4)

If `{{name}}` declared artifacts in its manifest, the install side
called `mcp__cowork__create_artifact` to surface each one in the
user's sidebar. Uninstall calls `mcp__cowork__list_artifacts` to find
them, then `mcp__cowork__allow_cowork_file_delete` (or the platform's
artifact deletion mechanism if available) to remove them.

Cowork's artifact registry is per-user, so artifacts are identified
by name rather than by absolute path. If `mcp__cowork__list_artifacts`
returns multiple artifacts with the same name from prior installs,
remove all of them.

Illustrative (the artifact removal pattern for one artifact named
*`<your-artifact-name>`*):

```python
# Find the artifact by name
artifacts = mcp__cowork__list_artifacts()
matching = [a for a in artifacts if a["name"] == "<your-artifact-name>"]

# Remove each match
for art in matching:
    mcp__cowork__allow_cowork_file_delete(art["id"])
```

If Cowork's environment does not provide a programmatic deletion
mechanism for the artifact, fall back to asking the user to remove it
through the Cowork artifact sidebar UI manually.

If at least one configuration key was preserved in Step UN2 (e.g., the
user keeps a token), the artifact MAY be preserved at the AI's
discretion — the card's content is often persisted history, which the
user may want to keep. The default is to remove unconditionally.

If `{{name}}` ships no artifacts, this step is a no-op.

## How Cowork de-registers protocols (UN5)

Cowork loads protocol trigger phrases from the SKILL.md `description:`
frontmatter at session start. Once Step UN3 removes the skill from
Personal Skills, the triggers are no longer loaded on the next session
start — so Step UN5 is a no-op once UN3 completes.

If you reach Step UN5 and the skill is still present in Personal Skills
(UN3 was skipped or failed), Step UN5 cannot succeed on Cowork —
return to UN3 and complete it first.

## Worked example: the uninstall flow on Cowork

The steps below describe one cohesive way to satisfy the Tier 2
outcomes on Cowork. The uninstall AI may adapt for variations (e.g.,
the artifact was already removed by a prior partial uninstall; the
user customised install_dir; the skill is no longer in Personal Skills
because Cowork was reinstalled).

### Step UC1: Locate the install (UN1)

Read `~/.claude/packages/{{name}}/installed.json` via
`mcp__filesystem__read_file`. If present, capture `config_dir`,
`version`, `platform`. If absent, exit cleanly.

### Step UC2: Show the Uninstall Plan (UN2 — mechanical, handled by INSTALL.md)

Walk the config schema. Per the v1.10 `preserve_on_uninstall`
annotations, ask one focused question per `ask` key, silently purge
each `false` key, silently preserve each `true` key. Confirm and
proceed.

### Step UC3: Skill removal (UN3)

Send the user the message above asking them to remove the skill from
Personal Skills and restart Cowork. Wait for confirmation that they
have done so before moving on.

### Step UC4: Artifact removal (UN4)

For each artifact declared in the package: call
`mcp__cowork__list_artifacts` to find matches by name. Remove each
one. If the user chose to preserve config and the artifact carries
non-derivable history, the AI MAY skip artifact removal at its
discretion (this is the exception noted in INSTALL.md Step UN4).

If `{{name}}` ships no artifacts, skip.

### Step UC5: Protocols (UN5)

No-op on Cowork once UC3 completes. Confirm to the user that triggers
are no longer registered.

### Step UC6: Trim config.json and remove install_dir contents (UN6 — mechanical)

Read `config.json` from `config_dir`. Construct a new object with
only the keys the user chose to preserve (and any
`preserve_on_uninstall: true` keys). Write it back (or delete the
file if no keys survive).

Delete every other file and subdirectory in `config_dir` except
`config.json` (if preserved) and `installed.json`. Use
`mcp__filesystem__list_directory` and `allow_cowork_file_delete` for
each item.

### Step UC7: Remove installed.json (UN7 — mechanical)

Delete `config_dir/installed.json`. If `config_dir` is now empty,
remove the directory too.

### Step UC8: Confirm (UN8 — mechanical)

Tell the user the uninstall is complete. Name:
1. The version that was uninstalled (from `installed.json`).
2. Which configuration keys were preserved and where.
3. Which keys were purged.
4. That the Personal Skills entry has been removed and Cowork was
   restarted — the package's triggers no longer fire.
5. Any leftover state: e.g., if the user previously had history in an
   artifact and the artifact was preserved, mention where it lives in
   the Cowork sidebar.

## Edge cases

**The skill was already removed from Personal Skills before uninstall
ran.** This is fine. Step UC3 becomes a no-op; the AI tells the user
"the skill is already absent from Personal Skills; continuing with
config and file cleanup."

**`installed.json` is missing but the install_dir has other files.**
This indicates a partial install (UN6/UN7 ran in a prior uninstall but
UN8 confirmation didn't reach the user). The AI MAY offer to clean up
the leftover files or leave them in place at the user's choice.

**The user changed the `install_dir` since install.** The `config_dir`
stored in `installed.json` is the authoritative source. If the user
moved the directory between install and uninstall, ask them where the
package's files actually live and use that path instead.
