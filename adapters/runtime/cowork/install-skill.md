# Cowork Skill Installation — a3ip-creator

This adapter explains how to install a3ip-creator specifically on Cowork.
Follow these steps instead of the generic Steps 5–6 in INSTALL.md.

## Why Cowork is different

Cowork registers skills through its own UI and regenerates its internal skill
registry on restart. Any file written directly to the skills folder outside of
Cowork's install flow will be overwritten. The correct path is:

1. Package the skill as a `.skill` file (a zip archive containing SKILL.md plus
   the files the skill needs at runtime)
2. Present that file to the user via Cowork's `present_files` mechanism
3. User clicks "Save skill" in the Cowork UI — registers it persistently in Cowork
4. Restart Cowork — the skill appears in Personal Skills

## What a .skill file is

A `.skill` file is a zip archive containing SKILL.md at the root plus any
bundled resources (scripts, references, docs, assets) in subdirectories.

Valid SKILL.md frontmatter fields for Cowork:
`allowed-tools`, `compatibility`, `description`, `license`, `metadata`, `name`

Do NOT include `version:` or `scripts_dir:` — Cowork will reject the file.

## Steps

### Step C1: Prepare SKILL.md — strip invalid frontmatter fields

Run this Python snippet to produce a clean SKILL.md:

```python
import re
skill_md = open("components/skills/a3ip-creator/SKILL.md", encoding="utf-8").read()
skill_md = re.sub(r'^(version|scripts_dir):.*\n', '', skill_md, flags=re.MULTILINE)
open("/tmp/SKILL_clean.md", "w", encoding="utf-8").write(skill_md)
print("cleaned SKILL.md written to /tmp/SKILL_clean.md")
```

### Step C2: Package the runtime payload as a .skill zip

The `.skill` archive must contain **everything the skill needs at runtime** —
nothing more, nothing less. The runtime payload is whatever the skill's SKILL.md
references when an AI follows its instructions: scripts it invokes, docs it
reads (e.g. local spec fallbacks for offline use), reference files it points
to, prompts or templates it expands. Repository scaffolding that exists only
for source-tree maintenance — git metadata, build artifacts, sync state files
(`.a3ip-source.json`, `.a3ip-sync-report.json`), `__pycache__/`, `.gitignore`,
top-level `README.md` aimed at developers, etc. — is **not** part of the
runtime payload.

The implementing AI should:

1. Read the cleaned SKILL.md from Step C1.
2. Identify which directories and files it references during execution
   (look for `scripts/X.py`, `docs/Y.md`, `components/...`, etc.).
3. Include those — and only those — in the zip, preserving their paths
   relative to the package root.
4. Always include the cleaned SKILL.md at the archive root.

For a3ip-creator specifically (as of v1.14.x), the runtime payload is:

- `SKILL.md` (cleaned, at archive root)
- `scripts/` — sync.py, new_version.py, scaffold.py, zip_package.py
  (the SKILL invokes these directly)
- `docs/` — `A3IP-SPEC-v{min_a3ip_spec}.md` and any sibling spec versions
  (Phase 0 of the SKILL falls back to reading the local spec doc when
  fetching from GitHub is blocked)

A reasonable reference implementation:

```python
import zipfile, pathlib

pkg_dir = pathlib.Path(".")  # run from inside the package directory
out_path = pathlib.Path("/tmp/a3ip-creator.skill")

# Subdirectories to include verbatim (everything except dotfiles / pycache).
runtime_dirs = ["scripts", "docs"]

with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
    # SKILL.md at root (cleaned version from Step C1)
    zf.write("/tmp/SKILL_clean.md", "SKILL.md")
    for d in runtime_dirs:
        for f in sorted((pkg_dir / d).rglob("*")):
            if not f.is_file():
                continue
            if "__pycache__" in f.parts or any(p.startswith(".") for p in f.parts):
                continue
            zf.write(f, f.relative_to(pkg_dir))

print(f"Packaged: {out_path}  ({out_path.stat().st_size} bytes)")
```

This list is a guide, not a contract. If a future SKILL.md adds a new runtime
dependency (e.g. a `prompts/` directory it expands, or a `components/` it
reads), update the bundle accordingly — the principle is *bundle what the
skill uses at runtime*, derived from reading the skill's own instructions.

### Step C3: Copy to outputs directory and present to user

Copy the `.skill` file to the Cowork outputs directory (the session scratchpad),
then call `mcp__cowork__present_files` with the path. This renders an interactive
card with a **"Save skill"** button.

```
mcp__cowork__present_files  →  file_path: <outputs_dir>/a3ip-creator.skill
```

Tell the user:
> "Click the 'Save skill' button on the card to install a3ip-creator into Cowork.
> Once you've saved it, restart Cowork — the skill will appear in Personal Skills."

### Step C4: Verify after restart

After the user restarts Cowork, confirm the skill appears in Personal Skills.
Then verify end-to-end by starting a new conversation and saying:
> "Use the a3ip-creator skill to create a new package"

The AI should begin the intake conversation (Group 1 questions: name, author, platforms).

### Step C5: Write installed.json

Write `installed.json` to `~/.claude/packages/a3ip-creator/installed.json`
with the standard fields (package, version, installed_at, platform, workspace_dir).

## Troubleshooting

**"Save skill" button not visible** — the file must be under the outputs directory
or a connected folder to be presentable via `present_files`.

**Skill appears but scripts fail** — confirm `pip install a3ip` was run (Step 3
of INSTALL.md). The scripts depend on the `a3ip` CLI being on PATH.

**Skill disappears after Cowork restart** — it was not registered through the UI
flow. Repeat Steps C1–C3 and use "Save skill", not a manual file copy.

**Phase 0 of the skill can't read the spec** — the local spec doc fallback
expects `docs/A3IP-SPEC-v{min_a3ip_spec}.md` to be present inside the
installed skill. If absent, the runtime payload (Step C2) was packaged too
narrowly. Repackage including `docs/`.
