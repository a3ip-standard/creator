# Cowork runtime adapter — {{name}}

> **This file is a Creator template.** It was copied from
> `creator-repo/components/runtime-adapter-templates/cowork/install-skill.md`
> into `{{name}}/adapters/runtime/cowork/install-skill.md` during scaffold.
> Generic placeholders use `{{name}}` for the package name and italicised
> angle-bracket placeholders (e.g. *`<your-script>`*) for per-package
> component identifiers. Adapt the worked examples to this package's actual
> components and remove this banner before shipping a release.

This adapter is platform-knowledge for installing `{{name}}` on Cowork.
The installing AI reads this as context, then applies it to satisfy the
Tier 2 outcomes in INSTALL.md — specifically the "make skills
discoverable" step, the "make artifacts available" step (if this package
ships artifacts), and the "make protocols invocable" step. The rest of
INSTALL.md still applies — install detection, configure wizard, resolve
install_dir, write config.json, write installed.json, and the Upgrading
flow — all governed by INSTALL.md and the A3IP spec, not by this adapter.

Per A3IP spec v1.10 'Writing Adapter Documents', adapter content is
platform knowledge, not installation script. The code blocks below are
illustrative worked examples — adapt them to actual paths and user
choices rather than executing them verbatim.

## How Cowork discovers and registers skills

Cowork's **Personal Skills UI** is the registration mechanism. A skill
placed directly into Cowork's skills folder outside of this UI flow will
be ignored or overwritten when Cowork regenerates its internal skill
registry on restart. The right path is:

1. Build a `.skill` zip containing SKILL.md at the archive root plus any
   bundled runtime resources (scripts, artifact templates) in
   subdirectories.
2. Present the zip via `mcp__cowork__present_files` so the user gets a
   **"Save skill"** button in the chat UI.
3. After the user clicks Save skill and restarts Cowork, the skill
   appears in Personal Skills and is available in every session and
   project. The restart is required — Cowork's skill registry only
   refreshes on startup.

Cowork also discovers trigger phrases from the SKILL.md's `description:`
frontmatter automatically; no separate protocol registration is needed.
This is why the "make protocols invocable" step is a no-op on Cowork
once the skill installs.

Per-package state (config.json, installed.json, scripts) still lives at
`{{config.install_dir}}` per the spec — the `.skill` zip is the Cowork
mechanism for registering the skill globally, not a replacement for the
spec install directory.

## What a .skill file is

A `.skill` file is a zip archive containing SKILL.md at the root plus
any bundled resources (scripts, artifact templates) in subdirectories.

Valid SKILL.md frontmatter fields for Cowork:
`allowed-tools`, `compatibility`, `description`, `license`, `metadata`,
`name`.

Cowork rejects `version:` and `scripts_dir:`. Strip these from the
bundled SKILL.md before packaging — see Step C1 below.

## How Cowork handles artifacts

Cowork has a first-class artifact registry. The installing AI calls
`mcp__cowork__create_artifact` during install, and the artifact appears
in the user's sidebar immediately — not on first use. The runtime
updates it via `mcp__cowork__update_artifact` on its trigger event. This
is why other platform adapters (Codex, Claude Code) often degrade the
artifact to a markdown file the runtime rewrites in place: those
platforms lack this mechanism.

If `{{name}}` ships no artifacts, skip the artifact-related steps below
(C3, C5 of the upgrade flow).

## Worked example: the install flow on Cowork

The steps below are illustrative — they describe one way to achieve the
Tier 2 outcomes on Cowork. The install AI may adapt for variations
(non-default install_dir, alternative bundle extraction, an artifact
that already exists from a prior install, etc.).

### Step C1: Prepare SKILL.md — strip frontmatter and substitute install_dir

Two transformations on the bundled SKILL.md (typically at
`components/skills/<your-skill-name>/SKILL.md`) before packaging:

1. **Strip frontmatter fields Cowork rejects** (`version:`,
   `scripts_dir:`).
2. **Substitute the `{{install_dir}}` placeholder** with the absolute
   installation path the user chose (resolved in INSTALL.md Step 5).
   Substitution is appropriate here because `install_dir` is a path
   (non-secret, deterministic per install). Do NOT substitute secrets
   (tokens, api keys) or other config values — those stay in config.json
   so the skill remains portable across config changes.

**Path-separator normalization (required).** The `install_dir` value
sourced from `CONFIGURE.md` or a prior `installed.json` may end with a
trailing path separator (`/` or `\`) — this is a normal operator habit
on Windows in particular. SKILL.md templates use references like
`{{install_dir}}/config.json` with a leading `/`. A naive string-replace
of a trailing-separator value into a leading-slash template produces a
malformed path with a doubled or mixed separator (e.g.
`C:\Users\me\.claude\packages\{{name}}\/config.json`). POSIX hides the
symptom because the kernel collapses `//`; Windows path APIs (including
the Read tool used by the runtime AI) reject the mixed form. Always
strip trailing `/` and `\` from `install_dir` before substituting so the
resulting join is well-formed on every host OS.

Illustrative (adapt the install_dir literal and the SKILL.md path):

```python
import re

install_dir_abs = "<absolute path resolved in INSTALL.md Step 5>"
install_dir_norm = install_dir_abs.rstrip("/\\")  # see normalization note above

skill_md = open("components/skills/<your-skill-name>/SKILL.md", encoding="utf-8").read()
skill_md = re.sub(r'^(version|scripts_dir):.*\n', '', skill_md, flags=re.MULTILINE)
skill_md = skill_md.replace("{{install_dir}}", install_dir_norm)

assert "{{install_dir}}" not in skill_md, "install_dir placeholder still in SKILL.md"
open("/tmp/SKILL_clean.md", "w", encoding="utf-8").write(skill_md)
```

### Step C2: Package the runtime payload as a .skill zip

The `.skill` archive contains **everything the skill needs at runtime** —
nothing more, nothing less. The runtime payload is derived from reading
the cleaned SKILL.md: scripts it invokes, artifact templates it reads,
local docs it falls back to, prompts or templates it expands. Repository
scaffolding that exists only for source-tree maintenance (git metadata,
`.a3ip-source.json`, `__pycache__/`, top-level developer-facing README,
INSTALL.md / CONFIGURE.md consumed at install time) is NOT part of the
runtime payload.

Layout convention: SKILL.md sits at the archive root (where Cowork
loads it from); helper files referenced by relative path in SKILL.md
go in matching paths under the root. Typical mapping for a package with
one skill, one artifact (named *`<your-artifact-name>`*), and one
script (named *`<your-script>.py`*):

- `SKILL.md` (cleaned from Step C1) → archive root
- `scripts/<your-script>.py` → `scripts/` in the archive
- `components/artifacts/<your-artifact-name>/artifact.html` → `artifact.html` at root
- `components/artifacts/<your-artifact-name>/artifact.md` → `artifact.md` at root

Note that artifact files move to the archive root, not `components/...`
— that's where the runtime SKILL.md looks for them. This is a deliberate
re-layout: source tree organization (`components/artifacts/<name>/`)
differs from the runtime layout the skill expects. The install adapter
is the one place that knows about both.

Illustrative (adapt paths to actual bundle extraction and component
names):

```python
import zipfile, pathlib

pkg_dir = pathlib.Path(".")  # run from inside the {{name}}.a3ip/ directory
out_path = pathlib.Path("/tmp/{{name}}.skill")

with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write("/tmp/SKILL_clean.md", "SKILL.md")

    for f in sorted((pkg_dir / "scripts").rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts:
            zf.write(f, f.relative_to(pkg_dir))

    artifact_dir = pkg_dir / "components" / "artifacts" / "<your-artifact-name>"
    if artifact_dir.is_dir():
        for f in sorted(artifact_dir.iterdir()):
            if f.is_file():
                zf.write(f, f.name)
```

The principle is *bundle what the skill uses at runtime*, derived from
reading SKILL.md, then place each piece where SKILL.md expects to find
it.

### Step C3: Create the package's artifact(s) — if any

Each artifact must exist in Cowork's artifact registry before the user
triggers a workflow that updates it. Create them now (during install)
in the current Cowork session so they appear immediately.

For each artifact declared in the package manifest:

1. Read `components/artifacts/<artifact-name>/artifact.html` from the
   bundle.
2. Call `mcp__cowork__list_artifacts` to check whether an artifact with
   this name already exists (idempotency for re-installs).
3. If it does not exist, call `mcp__cowork__create_artifact`:

```
mcp__cowork__create_artifact
  name: "<artifact-name>"
  content: <full HTML content of artifact.html>
```

If an artifact with this name already exists (from a previous install),
leave it in place — it may contain the user's recent state. The skill
updates it via `mcp__cowork__update_artifact` on each trigger.

If `{{name}}` ships no artifacts, skip this step entirely.

### Step C4: Present the .skill to the user

Copy the `.skill` file to the Cowork outputs directory (session
scratchpad), then call `mcp__cowork__present_files`. This renders an
interactive card with a **"Save skill"** button.

```
mcp__cowork__present_files  ->  file_path: <outputs_dir>/{{name}}.skill
```

Tell the user:
> "Click the **Save skill** button on the card to install {{name}} into
> Cowork. Once you've saved it, restart Cowork — the skill will appear
> in Personal Skills and will be available in every project."

If artifacts were created in Step C3, add:
> "Your *`<artifact-name>`* card is already in your artifacts list — it
> will update automatically when the workflow triggers it."

### Step C5: Verify after restart

After the user restarts Cowork, confirm the skill appears in Personal
Skills. Then verify end-to-end by saying one of the trigger phrases
declared in the package's protocols. The AI should recognise the
trigger, read config from `<install_dir>/config.json`, and behave per
the SKILL.md.

### Step C6: Write installed.json for Cowork installs

Cowork installs MUST set `install_method: "cowork-skill"` in
installed.json so future upgrades know to rebuild the `.skill` rather
than patch files in place:

```json
{
  "package": "{{name}}",
  "version": "<NEW>",
  "installed_at": "<ISO timestamp>",
  "platform": "cowork",
  "a3ip_spec": "1.10",
  "config_dir": "{{config.install_dir}}",
  "install_method": "cowork-skill"
}
```

Write this file at `{{config.install_dir}}/installed.json` per spec.

## Upgrading an existing Cowork install

Triggered by INSTALL.md Step 1 finding `installed.json` at
`{{config.install_dir}}/installed.json` with
`install_method: "cowork-skill"`.

1. **Read installed version** from `installed.json` (this is Step U1 of
   the spec Upgrading flow).
2. **Apply CHANGELOG steps** (Step U2). For each version between
   installed and current, follow `### Upgrade steps` exactly. Note any
   config changes — if a new required key is added, run the configure
   wizard for that key only and write back to `config.json`.
3. **Rebuild the `.skill` file** from the new bundle (Steps C1–C2
   above).
4. **(Idempotent)** check declared artifacts still exist via
   `mcp__cowork__list_artifacts`; create any missing ones (Step C3
   above).
5. **Present the new `.skill`** via `mcp__cowork__present_files`
   (Step C4).
6. **Tell the user:**
   > "An updated version is ready. Click **Save skill** to replace the
   > existing one, then restart Cowork. Cowork will use the new
   > version automatically. Your config.json at
   > `{{config.install_dir}}/config.json` is unchanged."
7. **After the user confirms restart,** overwrite `installed.json`
   (Step U3 of the spec) with the new `version` and `installed_at`
   timestamp, preserving `platform`, `a3ip_spec`, `config_dir`, and
   `install_method`.

## Troubleshooting

**Install AI reports "fresh install" but the user expected an upgrade**
— Step 1 of INSTALL.md checks `{{config.install_dir}}/installed.json`.
If that file is missing (e.g. a prior install didn't complete past the
installed.json write step), detection correctly returns fresh-install.
Confirm with the user whether a prior install attempt completed.

**"Save skill" button not visible** — the `.skill` file must be under
the outputs directory or a connected folder to be presentable via
`present_files`.

**Skill saves but doesn't trigger on its trigger phrases** — confirm
Cowork was restarted after saving. The skill registry only refreshes
on restart.

**Script fails with "config file not found"** — the skill expects
`<install_dir>/config.json`. Confirm INSTALL.md Step 5 (Resolve
install_dir) and the install-scripts step ran successfully. The user
can re-run the configure wizard at any time to rewrite the file.

**Artifact card doesn't appear after install** — Step C3 was skipped
or `mcp__cowork__create_artifact` failed. Re-run Step C3. The artifact
lives in Cowork's artifact registry, not in the skill zip, so it
persists independently of the skill itself.

**Skill disappears after Cowork restart** — it was not registered
through the UI flow. Repeat Steps C1–C4 and use **Save skill**, not a
manual file copy.
