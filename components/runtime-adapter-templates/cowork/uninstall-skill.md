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

Walk the package's config schema (the `configuration:` section in
`manifest.yaml`) one key at a time. Do NOT bulk-classify `config.json`
as a whole — the v1.10 `preserve_on_uninstall` annotation is set
per-key, and keys within the same file can have opposing policies.

For EACH config key, in declared order, perform this loop:

1. Read the key's `preserve_on_uninstall` value from the manifest.
2. If `preserve_on_uninstall: true`, add the key to the "will be
   PRESERVED" section of the uninstall plan. Do NOT ask the user.
   Do NOT destroy it in UC6.
3. If `preserve_on_uninstall: false`, add the key to the "will be
   PURGED" section. Do NOT ask the user.
4. If `preserve_on_uninstall: "ask"`, send the user ONE focused
   question that names this key explicitly: e.g. "Keep `api_token`?
   This stores the GitHub PAT used by the workflow. (y/N)".
   Capture the response, then route the key into the matching
   section of the plan.

After the loop, present the assembled Uninstall Plan as TWO explicit
lists — "Will be preserved" and "Will be purged" — with each key
named. Add a third short list naming the install_dir files outside
`config.json` that UC6 will delete. Get explicit user confirmation
before continuing to UC3.

Worked example (illustrative — adapt to this package's actual keys):

```text
Uninstall plan for {{name}} v1.2.3:

Will be PRESERVED:
  - api_token  (preserve_on_uninstall: true)

Will be PURGED:
  - workspace_dir   (preserve_on_uninstall: false)
  - default_branch  (preserve_on_uninstall: false, user said "purge")

Will be DELETED from install_dir:
  - artifact records, cached state, install scripts

Proceed? (y/N)
```

Common mistake (seen in the Sample B v1.1.0 dogfood, 2026-06-21):
the install AI read `config.json` once, asked one yes/no question for
the whole file, and silently destroyed everything in it. Sample A's
`api_token` (preserve_on_uninstall: true) would have been destroyed
that way. The per-key walk is load-bearing — don't shortcut it.

### Step UC3: Skill removal (UN3)

Send the user the message above asking them to remove the skill from
Personal Skills and restart Cowork. Wait for confirmation that they
have done so before moving on.

### Step UC4: Artifact removal (UN4)

If the package declares zero artifacts in its manifest, skip this
step entirely. Otherwise, for EACH artifact declared:

1. Call `mcp__cowork__list_artifacts()` to enumerate the user's
   current artifacts.
2. Filter for entries whose name (or title — whichever field the
   runtime exposes) matches the artifact name declared by this
   package. Multiple matches from prior installs are possible —
   collect ALL of them, don't stop at the first.
3. For each match, call `mcp__cowork__allow_cowork_file_delete(art["id"])`
   (or the runtime's artifact-deletion equivalent if the surface has
   evolved — consult the current Cowork MCP surface).
4. Call `mcp__cowork__list_artifacts()` a second time to verify the
   artifact is gone. If it still appears, fall back to asking the
   user to remove it manually via the Cowork artifact sidebar UI,
   then proceed.

Worked example (one artifact named *`<your-artifact-name>`*):

```python
# 1. Enumerate
artifacts = mcp__cowork__list_artifacts()

# 2. Filter all matches by name (not just the first)
matches = [a for a in artifacts if a["name"] == "<your-artifact-name>"]

# 3. Delete each match
for art in matches:
    mcp__cowork__allow_cowork_file_delete(art["id"])

# 4. Verify
remaining = [a for a in mcp__cowork__list_artifacts()
             if a["name"] == "<your-artifact-name>"]
if remaining:
    # Tell the user to remove manually via the Cowork sidebar.
    ...
```

Exception (preserve case): if the user chose to preserve at least
one configuration key in UC2 AND the artifact carries non-derivable
history (past standups, past reviews, etc.), the AI MAY skip
removal at its discretion. When skipping, name the artifact and its
location in the UC8 report so the user knows it survived.

Common mistake (seen in the Sample B v1.1.0 dogfood, 2026-06-21):
the install AI assumed the user could remove the artifact later via
the sidebar and skipped this step entirely — no
`mcp__cowork__list_artifacts` call, no
`mcp__cowork__allow_cowork_file_delete` call. Two artifacts
(`paper-inbox`, `experiment-log`) remained in the user's sidebar
after the uninstall "completed". The install side created the
artifact via `mcp__cowork__create_artifact`; the uninstall side
owns the symmetric removal.

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

Send the user a final report that explicitly enumerates each of the
five items below. This is the audit trail for the uninstall — do not
summarize, do not omit a section, do not collapse two sections into
one. Use the exact section labels from the worked example so the
user can read the report at a glance.

The report MUST contain:

1. **Version uninstalled.** Quote the `version` field from the
   `installed.json` you captured in UC1.

2. **Keys preserved.** List each preserved key by name, its absolute
   file path, and either its current value or `(value redacted)` if
   the key is sensitive (tokens, secrets). If no keys were
   preserved, write `none`.

3. **Keys purged.** List each purged key by name. If no keys were
   purged, write `none`.

4. **Skill registration.** State whether the user has confirmed the
   Personal Skills removal AND restarted Cowork (both required for
   UC3 to be complete). If the restart has not happened yet, name
   that as a follow-up so the user knows.

5. **Leftover state.** If any artifact was preserved per the UC4
   exception, name it and where it lives (sidebar location). If
   `config_dir` still exists because preserved keys survived, name
   the directory. Otherwise write `none`.

Worked example (illustrative — adapt to this package's actual state):

```text
Uninstall complete for {{name}} v1.2.3.

Version uninstalled: 1.2.3

Keys preserved:
  - api_token = (value redacted)
    at ~/.claude/packages/{{name}}/config.json

Keys purged:
  - workspace_dir
  - default_branch

Skill registration:
  Personal Skills entry removed; user confirms Cowork has been
  restarted. The package's triggers no longer fire.

Leftover state:
  - Artifact "Last Review" preserved (UC4 exception, contains review
    history). Visible in the Cowork artifact sidebar.
  - config_dir ~/.claude/packages/{{name}}/ survives because
    api_token was preserved.
```

Common mistake (seen in the Sample B v1.1.0 dogfood, 2026-06-21):
the uninstall AI wrote a vague "Uninstall complete, all done!"
message with no enumeration of preserved keys, purged keys, or
leftover state. The user had no way to audit what survived. The
five-section enumeration IS the contract.

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
