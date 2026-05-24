---
format: a3ip-changelog
spec: "1.1"
package: a3ip-creator
---

# Changelog: a3ip-creator

This file documents changes between versions of this package.
Each version section contains:
- A human-readable **Summary** of what changed
- **Upgrade steps** — AI-readable instructions for applying this version's changes
  (written exactly like INSTALL.md steps; apply only what changed)
- **Breaking changes** — config keys renamed/removed, new required MCPs, etc.
  (an AI receiving an upgrade must re-run the wizard for any affected fields)

New version entries go at the **top** of this file (newest first).

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

## 2.1.0

*Released: 2026-05-24*

### Summary

Thin-wrapper migration: the Creator no longer ships its own copies of
`scaffold.py`, `sync.py`, `new_version.py`, or `zip_package.py`. Those four
authoring capabilities are now first-class subcommands of the `a3ip` CLI
(v1.5.0+) and the Creator's SKILL.md invokes them directly. This removes
roughly 75 KB of duplicate code from the Creator bundle and makes the CLI the
single source of truth for the package-authoring surface.

Two other changes ride along in this release:

1. **Spec target bump 1.9 -> 1.10.** Includes the v1.10 uninstall lifecycle
   (Steps UN1-UN8), the new `preserve_on_uninstall` per-key field, and the
   patched outcome-based discovery model. `docs/A3IP-SPEC-v1.10.md` is shipped
   as the offline fallback for Phase 0.
2. **Phase 0 spec-fetch order flipped.** The Creator now tries the canonical
   spec on GitHub first and falls back to the bundled `docs/` copy only when
   web fetch is unavailable. This ensures the AI always reads the current
   patched version of the spec, even when v1.10-style in-place patches land
   between Creator releases.

### Upgrade steps

For Cowork users (re-installing the .skill from the new bundle):

1. Open the Cowork UI, locate the installed `a3ip-creator` skill, and remove
   it (or keep it -- re-install will overwrite).
2. Drag the new `a3ip-creator.skill` into Cowork. Click **Save skill**.
3. Restart Cowork so the new SKILL.md takes effect.
4. Ensure `a3ip` CLI is at v1.5.0 or higher: `pip install --upgrade a3ip`.
   The Creator's Phase 5 Step 0 will refuse to run against older CLIs because
   the manifest's `dependencies.tools[a3ip].version` is now `>=1.5.0`.

For users invoking the bundle programmatically: the four `scripts/*.py` files
are gone. Update any external automation that called them to call the
equivalent `a3ip` subcommand:

| Old | New |
|---|---|
| `python3 scripts/scaffold.py <intake.json> <outdir>` | `a3ip scaffold <intake.json> --output-dir <outdir>` |
| `python3 scripts/sync.py <pkg_dir>` | `a3ip sync <pkg_dir>` |
| `python3 scripts/new_version.py <pkg_dir> <ver>` | `a3ip new-version <pkg_dir> <ver>` |
| `python3 scripts/zip_package.py <pkg_dir>` | `a3ip zip <pkg_dir>` |

### Breaking changes

- **`scripts/` directory is now empty.** Any external automation that imported
  the Creator's scripts as Python modules (rather than invoking via the CLI)
  must be updated. The functional equivalents live in `a3ip.scaffold_cmd`,
  `a3ip.sync_cmd`, `a3ip.new_version_cmd`, and `a3ip.zip_cmd` in the CLI
  package on PyPI.
- **`dependencies.tools[a3ip].version` raised to `>=1.5.0`.** Installs against
  older CLIs are refused at Phase 0 of any Creator workflow.

### Files changed

- `manifest.yaml` - bumped
- `CHANGELOG.md` - replaced
- `components/skills/a3ip-creator/SKILL.md` - replaced
- `manifest.yaml` - replaced
- `docs/A3IP-SPEC-v1.10.md` - added
- `scripts/new_version.py` - deleted
- `scripts/scaffold.py` - deleted
- `scripts/sync.py` - deleted
- `scripts/zip_package.py` - deleted

## 2.0.0

*Released: 2026-05-21*

### Summary

Major bump — re-aligns the Creator to A3IP spec v1.9 (outcome-shaped Tier 2
install steps, adapters as Tier 3 platform-knowledge). Four changes:

1. **`min_a3ip_spec` bumped 1.8 → 1.9.** The Creator now targets spec v1.9
   and ships `docs/A3IP-SPEC-v1.9.md` for Phase 0's local-fallback read.
   v1.9 is a re-alignment release of the existing spec, not a behavioral
   evolution — it codifies discipline that was always implicit in
   CONCEPT.md's three-tier model.

2. **`scaffold.py` INSTALL.md template re-shaped to outcomes.** Steps 5/6/7
   renamed from procedure language ("Install Skills" / "Set Up Artifacts" /
   "Register Protocols") to outcome language ("Make skills discoverable to
   the host runtime" / "Make artifacts available on the host runtime" /
   "Make protocols invocable on the host runtime"), each with a
   `*Tier: 2 (required outcome -- adapter procedure)*` marker and a short
   outcome description that points at `adapters/runtime/<your-platform>/`
   for the HOW. The `spec_ver` constant baked into scaffolded
   manifest/CONFIGURE/INSTALL frontmatter bumped from "1.7" to "1.9".

3. **SKILL.md gains Phase 0.5 — Detect Platform Context.** After Phase 0
   (read the spec), the Creator now calls `a3ip platforms --json` to
   determine its own host OS and AI runtime, and uses the result to anchor
   Intake Group 1's platform question. This addresses the question Max
   raised on 2026-05-21: the Creator already knows what platform it's
   running on, so the platform question is partially pre-answered. The
   rationale section explains why: knowledge written for the wrong
   platform is worse than no knowledge, so the Creator should only emit
   confident first-hand knowledge for its detected platform and stub the
   rest.

4. **CLI dependency bumped `>=1.3.2` → `>=1.4.0`.** v1.4.0 ships the
   `a3ip platforms` command (used by Phase 0.5) and the v1.9 validator
   checks 11/12/13 (used by Phase 3). Phase 5 Step 0's CLI version gate
   auto-upgrades, so existing Creator installs pick this up on first
   "release a new version" invocation.

The Creator skill phase count goes from 7 to 8 (Phase 0.5 added). Phase 3's
"9 checks" wording in SKILL.md is updated to "10 normative checks plus 3
v1.9 advisory warnings (Checks 11-13)" to match CLI v1.4.0.

### Upgrade steps

For users with an existing Creator install (Cowork Personal Skill):

1. Save the new `a3ip-creator.skill` (presented at end of release).
2. Click **Save skill** in Cowork; confirm overwrite of the prior version.
3. Restart Cowork so the new SKILL.md loads.
4. The first time you say "release a new version" or similar, Phase 5
   Step 0 will auto-upgrade your `a3ip` CLI to >=1.4.0 if needed.

For users authoring new packages: nothing to do; `a3ip-creator` will
detect the v1.9 spec from `docs/A3IP-SPEC-v1.9.md`, run Phase 0.5 to
auto-detect platform context, and scaffold outcome-shaped INSTALL.md
templates by default.

### Breaking changes

None for **existing packages** the Creator has previously scaffolded —
spec v1.9 is backward-compatible with v1.8, so older packages remain
valid under v1.9. The renamed step titles only affect packages scaffolded
by Creator v2.0+ going forward.

The Creator's own CLI minimum version is bumped (`>=1.3.2` → `>=1.4.0`).
This is breaking for users who somehow can't update their CLI, but Phase
5 Step 0 auto-upgrades and Phase 0.5 falls back gracefully if `a3ip
platforms` is unavailable, so in practice this should not surface.

### Files changed

- `manifest.yaml` — bumped to 2.0.0; `min_a3ip_spec` 1.8 → 1.9; CLI dep `>=1.3.2` → `>=1.4.0`
- `CHANGELOG.md` — this entry prepended
- `components/skills/a3ip-creator/SKILL.md` — Phase 0.5 added; Phase 3 check list updated to 10 + 3 warnings; Phase 5 Step 0 CLI gate bumped to 1.4.0
- `scripts/scaffold.py` — INSTALL.md template Steps 5/6/7 renamed with Tier 2 markers; `spec_ver` 1.7 → 1.9 in three places
- `docs/A3IP-SPEC-v1.9.md` — added (copy of spec v1.9 for Phase 0 local fallback)

## 1.14.1

*Released: 2026-05-17*

### Summary

Housekeeping patch. Three changes, none of which alter scaffolded output or
runtime behavior:

1. **Apache-2.0 LICENSE added.** The creator-repo was created without a
   LICENSE file when it was split out of the workspace; this patch supplies
   the same Apache-2.0 license already used by `a3ip-standard/spec` and
   `a3ip-standard/cli`. `manifest.yaml` `license:` field updated from `MIT`
   to `Apache-2.0` to match.

2. **Cowork adapter Step C2 rewritten in Tier-3 language.** Previously the
   adapter enumerated the runtime payload as "SKILL.md + scripts/" — narrow
   and silently wrong (the SKILL's Phase 0 falls back to reading
   `docs/A3IP-SPEC-v{min_a3ip_spec}.md` when web fetch is blocked, so `docs/`
   must also ship). The new wording describes the *purpose* of the runtime
   payload — "everything the skill needs at runtime, derived from reading the
   skill's instructions" — and gives the current concrete answer for
   a3ip-creator (SKILL.md + scripts/ + docs/) as a worked example rather than
   a contract. This aligns the adapter with the three-tier framing in
   CONCEPT.md (mechanical / outcomes / semantics).

3. **CLI dependency minimum bumped from `>=1.3.1` to `>=1.3.2`.** v1.3.2
   reads the package name from `manifest.yaml` instead of the parent
   directory name. The Creator's own source lives at `creator-repo/` while
   the package name is `a3ip-creator`, so any installer using an older CLI
   to bundle Creator from source would produce a bundle with the wrong name
   in its frontmatter. Bumping the minimum guarantees correct bundle naming.

### Upgrade steps

No action required -- non-breaking update.

### Breaking changes

None.

### Files changed

- `manifest.yaml` — bumped version, license, a3ip dep minimum
- `adapters/runtime/cowork/install-skill.md` — Step C2 rewritten with
  Tier-3 framing; docs/ added to the worked-example runtime payload;
  troubleshooting entry added for the offline-spec fallback
- `LICENSE` — added (Apache-2.0)
- `CHANGELOG.md` — this entry

## 1.14.0

*Released: 2026-05-17*

### Summary

Adopts A3IP spec v1.8, adds Codex runtime adapter, and bumps the a3ip CLI dependency to v1.3.1. Three concrete changes: (1) `min_a3ip_spec` bumped from `"1.7"` to `"1.8"` and a local copy of `docs/A3IP-SPEC-v1.8.md` is shipped so Phase 0 finds it without web access; (2) new `adapters/runtime/codex/install-skill.md` documents the Codex-specific install flow (no .skill UI; file-copy into `~/.codex/skills/<name>/`; `install_method: "generic-copy"`; PowerShell-direct on Windows without Cowork's bash sandbox); (3) `dependencies.tools[a3ip].version` bumped from `">=1.2.1"` to `">=1.3.1"` to require the Unicode-safe console output (Windows cp1252 no longer crashes) and the declared spec 1.8 compatibility. v1.8 spec is mostly documentation/schema clarifications; Creator behavior is unchanged except for the Codex adapter and the spec-doc shipped in docs/.

### Upgrade steps

**Step 1 — Upgrade the a3ip CLI to 1.3.1+:**
The new Creator manifest declares `a3ip >=1.3.1`. The install AI auto-runs
`pip install --upgrade --user a3ip` during INSTALL.md Step 3 and SKILL.md
Phase 5 Step 0; no manual operator action needed.

**Step 2 — Replace these files in the installed skill:**
- `manifest.yaml` (bumped `min_a3ip_spec`, bumped a3ip dep)
- `docs/A3IP-SPEC-v1.8.md` (newly shipped)
- `adapters/runtime/codex/install-skill.md` (newly shipped — only needed if
  Codex is in your install targets; harmless on other runtimes)

For Cowork installs, the `.skill` rebuild (Steps C1-C4 of
`adapters/runtime/cowork/install-skill.md`) covers all three automatically.
For Codex installs (or any other runtime), copy the files into your
`~/.codex/skills/a3ip-creator/` (or equivalent) directory.

**Step 3 — Update `installed.json`:**
- `version: "1.14.0"`
- `a3ip_spec: "1.8"`
- (`upgraded_from`: "1.13.1")

### Breaking changes

None. All changes are additive (new adapter file, new spec doc) or
backward-compatible dependency bumps (CLI minimum moved up but old packages
that still run with Creator continue to function). v1.7-targeted packages
remain valid as v1.8 per the v1.8 spec's backward-compatibility guarantee.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
TODO: List every other file that changed.
Format: `path/to/file.ext` — replaced | added | deleted
*(Run sync.py before new_version.py to auto-populate this section.)*

## 1.13.1

*Released: 2026-05-16*

### Summary

Dogfoods the Step 1 fix from v1.12.1 onto the Creator's own INSTALL.md. The Creator generates correct Step 1 wording for packages it scaffolds (per-OS tool selection that prevents bash-vs-Windows-`~` confusion), but its own INSTALL.md was hand-authored before that fix landed and still had the old, ambiguous wording. As a result, installing the Creator on Cowork × Windows kept being reported as fresh install even when v1.12.0 was correctly registered in installed.json -- the install AI used bash to check `~/.claude/packages/a3ip-creator/installed.json`, bash's `~` resolves to the ephemeral Linux sandbox home, no file found there, fresh install declared. v1.13.1 manually patches the Creator's Step 1 to match what scaffold.py now generates for everyone else.

### Upgrade steps

Replace `INSTALL.md` -- Step 1 now lists explicit Cowork / Claude Code / Codex
file paths with mandatory tool guidance (use `mcp__filesystem` on Cowork, NOT
bash). No other changes.

### Breaking changes

None. INSTALL.md wording only.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `INSTALL.md` — replaced

## 1.13.0

*Released: 2026-05-16*

### Summary

Adopts A3IP spec v1.7's two-tier adapter model. v1.6 conflated OS conventions (Windows vs POSIX) with AI runtime conventions (Cowork vs Claude Code vs Codex) into a single adapters/<name>/ axis -- in practice this produced a recurring class of cross-product bugs (notably 'Cowork on Windows', where the install AI's bash and Read tools handle `~` differently than mcp__filesystem). v1.7 separates the axes: adapters/os/{windows,posix}/ for filesystem conventions, adapters/runtime/{cowork,claude-code,codex,...}/ for AI-host conventions. This Creator release: (1) ships docs/A3IP-SPEC-v1.7.md; (2) bumps the Creator's own min_a3ip_spec to 1.7; (3) refactors its own adapter from adapters/claude/install-skill.md to adapters/runtime/cowork/install-skill.md; (4) adds adapters/os/{windows,posix}/file-ops.md with tool-selection guidance; (5) updates scaffold.py so generated packages emit the new layout by default. Future scaffolded packages get OS-axis adapters automatically; existing v1.6 packages remain valid (backward-compatible).

### Upgrade steps

1. **Replace `scripts/scaffold.py`** with the new file. Restart the skill so
   the new scaffold is loaded.
2. **Add `docs/A3IP-SPEC-v1.7.md`** to the skill's docs directory so Phase 0
   can find the new spec locally.
3. **Migrate the Creator's own adapter:** rename `adapters/claude/` to
   `adapters/runtime/cowork/` and add `adapters/os/{windows,posix}/file-ops.md`.
   For most users this is handled by the .skill re-save in the install flow
   -- the new .skill zip has the new layout.
4. **Update `installed.json`** to `version: "1.13.0"` and `a3ip_spec: "1.7"`.

No config changes. INSTALL.md adapter references updated automatically.

**Existing scaffolded packages (e.g. ai-code-review-flow):** continue to work
as v1.6 packages (the spec v1.7 is backward-compatible). Re-scaffolding is
optional; to adopt the two-tier layout, re-run scaffold or manually migrate
adapter files.

### Breaking changes

None at the spec or package-schema level -- v1.7 is a strict superset of
v1.6. The Creator's own adapter directory moved from adapters/claude/ to
adapters/runtime/cowork/, which is technically a path change, but the install
adapter is the only file inside and the migration is mechanical.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `INSTALL.md` — replaced
- `manifest.yaml` — replaced
- `scripts/scaffold.py` — replaced
- `adapters/os/posix/file-ops.md` — added
- `adapters/os/windows/file-ops.md` — added
- `adapters/runtime/cowork/install-skill.md` — added
- `docs/A3IP-SPEC-v1.7.md` — added
- `adapters/claude/install-skill.md` — deleted

## 1.12.1

*Released: 2026-05-16*

### Summary

Fixes a recurring class of bug where the install AI uses bash to check filesystem paths containing `~`, finds nothing (bash's `~` is the ephemeral Linux sandbox home, not the persistent Windows user home), and treats an existing install as fresh. Generated INSTALL.md Step 1 now explicitly tells the install AI to use `mcp__filesystem__read_file` on Cowork (which expands `~` to the Windows user home) and NOT to use bash or the raw Read tool for tilde-prefixed paths. Same guidance applied to Codex (Windows) and Claude Code (macOS/Linux, where `os.path.expanduser` works). This is the third incarnation of the same fundamental issue (after the v1.11.1 CLI-install path bug and the v1.12.0 runtime config-read path bug) -- now closed everywhere INSTALL.md reads a path with a tilde.

### Upgrade steps

Replace `scripts/scaffold.py` and restart the skill. Existing scaffolded
packages with the old Step 1 wording will continue to misbehave -- they need
to be re-scaffolded (or have their INSTALL.md Step 1 manually patched). For
ai-code-review-flow specifically, v1.0.4 ships the corrected Step 1 directly.

### Breaking changes

None. scaffold.py change is purely in the generated INSTALL.md wording.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `scripts/scaffold.py` — replaced

## 1.12.0

*Released: 2026-05-16*

### Summary

Teaches `scaffold.py` to generate spec-compliant Cowork-aware INSTALL.md without manual post-scaffold edits. Three improvements: (1) the auto-injected `install_dir` config key's description now tells the install AI to expand `~` to an absolute path before persisting (file-reading tools at runtime do not expand tildes, so a literal `~/...` in config.json breaks the runtime lookup). (2) Generated INSTALL.md gains a new "Resolve install_dir to an absolute path" step right after the configure wizard, making the expansion a first-class step rather than buried guidance. (3) When `cowork` appears in `platforms.tested` in intake.json, generated INSTALL.md emits Cowork-adapter routing in the Install Skills / Set Up Artifacts / Register Protocols steps (referring to `adapters/claude/install-skill.md`), instead of generic file-copy lines that overlap with adapter behavior and produce duplicate Save-skill prompts. Discovered during a real install test of ai-code-review-flow v1.0.0 — the install AI ran both the adapter and the generic steps, presenting the .skill twice. Future packages scaffolded from this Creator avoid both bugs by default.

### Upgrade steps

1. Replace `scripts/scaffold.py` with the new file. (No SKILL.md changes,
   no manifest changes.) Restart the skill after replacing so the new
   scaffold.py is picked up.
2. Existing scaffolded packages are unaffected by this change. To regenerate
   a package's INSTALL.md with the new template, re-run scaffold against the
   package's intake.json -- be aware this overwrites manifest.yaml,
   INSTALL.md, CONFIGURE.md, README.md, CHANGELOG.md, and any stub component
   files. Filled-in content (real skills, protocols, scripts) is preserved
   only if not yet stubbed -- safer to scaffold to a temp dir, diff, then
   merge.

### Breaking changes

None. scaffold.py changes are purely additive -- the new generated INSTALL.md
template is a superset of the old one (extra step + Cowork branches). No
config keys changed, no API changes to ensure_spec_required_keys, no
manifest schema changes.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `scripts/scaffold.py` — replaced

## 1.11.1

*Released: 2026-05-16*

### Summary

Shifts CLI provisioning from user-side to installer-side. v1.11.0's INSTALL.md Step 3 and SKILL.md Phase 5 Step 0 both told the user to run `pip install --upgrade a3ip` themselves and refused to proceed if the CLI was missing/old. Real users installing an A3IP package shouldn't be expected to know about pip, PATH, or Python tooling — that's the AI installer's job. v1.11.1 rewrites both checkpoints so the install AI runs `pip install --upgrade --user a3ip` itself when the CLI is missing or below 1.2.1, and only falls back to asking the user if pip itself is unavailable or the install fails. No new config keys, no manifest changes, no breaking changes — purely a UX/behavior fix in INSTALL.md and SKILL.md.

### Upgrade steps

1. Replace `INSTALL.md` — Step 3 (Dependency Check) now instructs the
   install AI to auto-install/upgrade the a3ip CLI via
   `pip install --upgrade --user a3ip`. The user is no longer prompted to run
   pip themselves; they only see the outcome.
2. Replace `components/skills/a3ip-creator/SKILL.md` — Phase 5 Step 0 now
   auto-upgrades the CLI when below minimum, instead of refusing. Restart the
   skill after replacing.

No config changes. No manifest changes. The behavior change is install/upgrade
UX only.

### Breaking changes

None. The minimum CLI version is still 1.2.1, declared the same way in
manifest.yaml. Only the way INSTALL.md / Phase 5 Step 0 respond to a missing
or stale CLI has changed (auto-install instead of asking the user to run
pip).

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `INSTALL.md` — replaced
- `components/skills/a3ip-creator/SKILL.md` — replaced

## 1.11.0

*Released: 2026-05-16*

### Summary

Brings the Creator package itself into A3IP spec v1.6 compliance and tightens the dependency chain on the `a3ip` CLI. Concretely: (1) declares `install_dir` as a required config key in the Creator's own manifest — closing the meta-bug where the Creator scaffolded spec-compliant packages but wasn't itself spec-compliant (Check 10 was flagging it); (2) rewrites INSTALL.md Step 1, Step 8, and Upgrading section to use `{{config.install_dir}}` per the spec INSTALL.md template; (3) adds a new CONFIGURE.md asking for `install_dir`; (4) declares `a3ip >=1.2.1` in `dependencies.tools` of manifest.yaml so the spec's Step 2 Dependency Check covers it formally; (5) rewrites INSTALL.md's Dependency Check to enforce the new minimum CLI version (with rationale: older CLIs silently skip Check 10); (6) inserts a Phase 5 Step 0 in SKILL.md that runs `a3ip --version` at the start of every release cut and refuses to proceed below the manifest's declared minimum. The dependency on the CLI is now declared in three layers — manifest, INSTALL.md install-time check, and SKILL.md runtime gate.

### Upgrade steps

1. **Upgrade the `a3ip` CLI first.**
   - Run: `pip install --upgrade a3ip`
   - Verify: `a3ip --version` reports `1.2.1` or higher.
   - This is mandatory — Phase 5 of the new Creator gates on this version
     (Step 0 of Phase 5 actively checks).

2. **Run the configure wizard for the new `install_dir` key.**
   - Read the new `CONFIGURE.md` (it asks one question).
   - Default `~/.claude/packages/a3ip-creator/` on Cowork / Claude Code.
   - The value persists into `installed.json`.

3. **Replace four package files with the new versions:**
   - `manifest.yaml` — adds `install_dir` config key and `a3ip` tool dep.
   - `INSTALL.md` — Step 1, Step 8, Dependency Check, and Upgrading rewritten
     for spec compliance.
   - `CONFIGURE.md` — new file (didn't exist in v1.10.0).
   - `components/skills/a3ip-creator/SKILL.md` — Phase 5 now has Step 0
     (active CLI version gate) before Step 1 (sync).

4. **Migrate `installed.json`.**
   - Move it from the previous location (`~/.claude/packages/a3ip-creator/installed.json`)
     to `{{config.install_dir}}/installed.json` if the user picked a different
     `install_dir`. Most users will pick the default, which matches the old
     location — in that case it's already in the right place.
   - Add the new fields per spec: `a3ip_spec: "1.6"`,
     `config_dir: <install_dir>`, `install_method: "cowork-skill"` (Cowork)
     or `"generic-copy"` (other platforms).
   - Bump `version` to `"1.11.0"` and refresh `installed_at`.

5. **Restart the skill** so the new SKILL.md (with Phase 5 Step 0) is loaded.

After these steps, the next time Phase 5 runs, Step 0 will verify `a3ip
--version` ≥ 1.2.1 before doing anything. If you haven't upgraded the CLI,
Phase 5 refuses to proceed.

### Breaking changes

**New required config key:** `install_dir`. v1.10.0 and earlier had no
config keys at all. v1.11.0 introduces one — the configure wizard must
collect it before install proceeds. Existing installs need a one-time
configure-wizard run for this key (see Upgrade steps above).

**Tool dependency bumped:** `a3ip` CLI minimum is now 1.2.1 (was effectively
unenforced before — INSTALL.md said 1.1.0+ but the dependency wasn't in the
manifest). Users on CLI 1.1.0 must `pip install --upgrade a3ip` before this
version of the Creator's Phase 5 will run — Phase 5 Step 0 actively gates on
this.

**installed.json location moved (conditionally):** for users keeping the
default `install_dir` of `~/.claude/packages/a3ip-creator/`, the location is
unchanged. For users who customize `install_dir`, `installed.json` now lives
under their chosen directory per spec. The schema also gained
`a3ip_spec`, `config_dir`, and `install_method` fields per spec INSTALL.md
template.

### Files changed

- `manifest.yaml` — replaced (added install_dir config key, added a3ip tool dependency)
- `CHANGELOG.md` — replaced (this entry)
- `INSTALL.md` — replaced (Step 1, Step 8, Dependency Check, Upgrading sections all rewritten)
- `CONFIGURE.md` — added (new file — Creator now has a wizard)
- `components/skills/a3ip-creator/SKILL.md` — replaced (Phase 5 Step 0 — active CLI version gate)

## 1.10.0

*Released: 2026-05-16*

### Summary

Adds Phase 0 (Read the Spec) to the Creator's SKILL.md workflow, and updates scaffold.py to auto-inject the spec-required `install_dir` config key into every newly scaffolded package. Both changes close a gap that produced multiple non-compliant packages (ai-code-review-flow v1.0.x through v1.1.x): Rule 8 used to be aspirational ("Use the spec definitions") but never operationalised — the AI never actually opened the spec. Phase 0 now requires fetching and reading `docs/A3IP-SPEC-v{version}.md` (shipped with this skill — v1.1 through v1.6) before any other phase, and the scaffold automatically populates `install_dir` so generated INSTALL.md files use `install_dir` (the config key) consistently for Step 1 install detection, Step "Install Scripts", and Step "Write installed.json" per the spec's INSTALL.md template. Also tightens the generated `## Upgrading` section to match the spec's Step U1–U4 template.

### Upgrade steps

1. Replace `components/skills/a3ip-creator/SKILL.md` with the new file —
   it adds the **Phase 0** section before Critical Rules, and updates Rule 8
   to reference Phase 0 instead of restating its content.
2. Replace `scripts/scaffold.py` with the new file. The new scaffold:
   - Defines `ensure_spec_required_keys(pkg)` that injects `install_dir`
     into a package's `configuration:` block if absent (idempotent).
   - Calls that helper at the top of `scaffold()` so every builder
     (manifest, configure, install) sees `install_dir`.
   - Bumps the generated `min_a3ip_spec:` value and INSTALL.md `spec:`
     frontmatter from `1.5` to `1.6`.
   - Rewrites Step 1 of generated INSTALL.md to use
     `Look for installed.json in <install_dir>` per spec.
   - Rewrites the "Write installed.json" step to write to
     `<install_dir>/installed.json` with `a3ip_spec` and `config_dir`
     fields per spec.
   - Tightens the `## Upgrading` section to use Step U1–U4 per spec template.
3. Add `docs/A3IP-SPEC-v1.6.md` so Phase 0's local-copy lookup finds it
   without needing web access.

After replacing these files, restart the skill so the new SKILL.md is loaded.

### Breaking changes

**For users of the Creator skill itself:** none. Phase 0 is an additional
phase; existing intake/scaffold/validate/build/version/registry flows are
unchanged in shape. Rule 8's wording changed but the underlying rule
("follow the spec") is the same.

**For packages scaffolded with the new scaffold.py:** the generated
`manifest.yaml` now includes an `install_dir` config key by default. Existing
hand-edited packages are unaffected. Packages that intend to follow the spec
should add `install_dir` to their `configuration:` block; the next
`a3ip validate` (after Check 10 ships in the a3ip CLI) will flag its absence.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `components/skills/a3ip-creator/SKILL.md` — replaced
- `scripts/scaffold.py` — replaced
- `docs/A3IP-SPEC-v1.6.md` — added

## 1.9.5

*Released: 2026-05-15*

### Summary

Corrected INSTALL.md: removed `validate.py` and `bundle.py` from the scripts
list (they are part of the `a3ip` CLI, not this package), updated script count
from 6 to 4, updated expected CLI version to `a3ip 1.1.0 (spec 1.6)` in Step 7,
and updated the `installed.json` template version to 1.9.5.

### Upgrade steps

No action required — non-breaking update.

### Breaking changes

None.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `INSTALL.md` — replaced

## 1.9.4

*Released: 2026-05-15*

### Summary

Updated INSTALL.md to reference CLI v1.1.0 (spec 1.6) and added a GitHub
install fallback (`pip install git+https://github.com/a3ip-standard/cli.git`)
for use while CLI v1.1.0 is pending PyPI publication.

### Upgrade steps

No action required — non-breaking update.

### Breaking changes

None.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `INSTALL.md` — replaced

## 1.9.3

*Released: 2026-05-15*

### Summary

Removed `scripts/validate.py` and `scripts/bundle.py` from the Creator package.
These are now provided by the `a3ip` CLI (`a3ip validate`, `a3ip bundle`) and
should never have been shipped as Creator scripts. The Creator's SKILL.md and
manifest have been updated to reflect this — all validate and bundle operations
now call the CLI directly. The Creator-specific scripts (`scaffold.py`, `sync.py`,
`new_version.py`, `zip_package.py`) are unchanged and remain in the package.

### Upgrade steps

- Delete `scripts/validate.py` and `scripts/bundle.py` from your Creator install
  directory — they are no longer part of the package.
- Replace `components/skills/a3ip-creator/SKILL.md` with the updated version.
- Ensure `a3ip` CLI is installed: `pip install a3ip` (or `pip install --upgrade a3ip`).

### Breaking changes

`scripts/validate.py` and `scripts/bundle.py` removed from the package.
Use `a3ip validate <pkg>` and `a3ip bundle <pkg>` instead (CLI must be on PATH).

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `components/skills/a3ip-creator/SKILL.md` — replaced
- `scripts/bundle.py` — deleted
- `scripts/validate.py` — deleted

## 1.9.2

*Released: 2026-05-15*

### Summary

Bumped `min_a3ip_spec` from `"1.5"` to `"1.6"` in `manifest.yaml`. The Creator
now declares that it requires spec v1.6, which is the version that formally defines
the `spec_url:` bundle field. Bundles produced by this Creator will include a
`spec_url:` pointing to the canonical v1.6 spec on GitHub instead of v1.5.

### Upgrade steps

No action required — non-breaking update. Re-bundle the Creator to get a bundle
whose `spec_url:` references v1.6.

### Breaking changes

None.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced

## 1.9.1

*Released: 2026-05-15*

### Summary

Updated `bundle.py` to implement spec v1.6 distribution model: bundles now always
include `spec_url:` in their frontmatter pointing to the canonical published spec on
GitHub, instead of embedding the full spec document. This eliminates the delimiter
collision problem (the spec's own bundle format examples were confusing parsers) and
reduces bundle size significantly. The `--spec` flag is retained for offline/airgapped
scenarios only. The spec URL is derived automatically from `min_a3ip_spec:` in the
package manifest.

### Upgrade steps

- Replace `scripts/bundle.py` with the new version from this bundle.
- No config changes required.

### Breaking changes

None. Bundles produced by the new `bundle.py` are backward compatible — receivers
that do not recognise `spec_url:` simply ignore the field.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `scripts/bundle.py` — replaced

## 1.9.0

*Released: 2026-05-15*

### Summary

Added Cowork-specific skill installation documentation. The SKILL.md preamble
now correctly lists all six phases (Phases 5 and 6 were missing). INSTALL.md
Steps 5 and 6 now route Cowork users to `adapters/claude/install-skill.md`
rather than incorrectly pointing them to `~/.claude/skills/` (a path that
works for Claude Code but is silently overwritten by Cowork on restart). The
new adapter explains the correct flow: package as `.skill` zip, present via
`mcp__cowork__present_files`, install via the Cowork UI "Save skill" button.

### Upgrade steps

- Replace `components/skills/a3ip-creator/SKILL.md` with the updated version.
- Replace `INSTALL.md` with the updated version.
- Add the new `adapters/claude/` directory to your installed copy.
- No config changes required. No re-run of the configuration wizard needed.

### Breaking changes

None.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `CHANGELOG.md` — replaced
- `INSTALL.md` — replaced
- `components/skills/a3ip-creator/SKILL.md` — replaced
- `adapters/claude/install-skill.md` — added

## 1.8.3

*Released: 2026-05-15*

### Summary

Fixed a gap in INSTALL.md where `manifest.yaml` and `CHANGELOG.md` were not listed
as files to copy into the skills directory. Without these files, `a3ip validate
<skills_dir>/a3ip-creator/` fails (Check 2 — missing manifest, Check 6 — missing
CHANGELOG). Step 6 now explicitly copies both files alongside SKILL.md and explains
why they are required. Also added a Cowork platform note warning against using the
bash sandbox for file copy operations on Windows (bash `~` ≠ Windows user home).

### Upgrade steps

- Replace `INSTALL.md` with the new version.
- Copy `manifest.yaml` and `CHANGELOG.md` from the bundle root into your
  `<skills_dir>/a3ip-creator/` directory if not already present.

### Breaking changes

None.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `INSTALL.md` — replaced

## 1.7.4

*Released: 2026-05-13*

### Summary

Fixes `### Files changed` audit accuracy. `new_version.py` always bumps
`manifest.yaml` and prepends a new entry to `CHANGELOG.md` on every release,
but those two files were never included in the auto-populated `### Files changed`
block — making the audit trail for every previous version technically incomplete.
`new_version.py` now unconditionally prepends `manifest.yaml — bumped` and
`CHANGELOG.md — replaced` to the files-changed block before appending sync.py's
detected file list.

This also retroactively validates the 1.7.3 `### Files changed` finding from
Codex: that section only listed `INSTALL.md` but the upgrade also touched
`manifest.yaml` and `CHANGELOG.md`. From 1.7.4 onwards every entry is accurate
by default.

### Upgrade steps

1. Replace `scripts/new_version.py` with the new version from this bundle.

### Breaking changes

None.

### Files changed

- `manifest.yaml` — bumped
- `CHANGELOG.md` — replaced
- `scripts/new_version.py` — replaced

## 1.7.3

*Released: 2026-05-13*

### Summary

Fixes three upgrade-completeness gaps discovered during Codex upgrade testing (1.7.0 → 1.7.2):

1. **manifest.yaml and CHANGELOG.md missing from upgrade steps** — When an installer
   persists the full package directory (as Codex does), these files go stale after each
   upgrade because they were never mentioned in delta steps. A new standing rule in the
   `## Upgrading` section requires always replacing `manifest.yaml` and `CHANGELOG.md`
   from the bundle root on every upgrade, regardless of what the version-specific steps say.

2. **manifest.yaml and CHANGELOG.md missing from fresh install** — A new Step 9 now
   explicitly installs `manifest.yaml`, `CHANGELOG.md`, and `README.md` into
   `<install_dir>/`. The confirmation summary (Step 12) is updated to include these.

3. **Codex install path too vague** — Step 4 and the Codex platform note now list
   `~/.codex/skills/a3ip-creator/` as the primary default install directory instead of
   "a project-level context directory, or paste SKILL.md as a persistent instruction."

Steps renumbered: old 9–11 → new 11–13 to accommodate the new Step 9.

### Upgrade steps

1. Replace `INSTALL.md` with the new version from this bundle.
2. Copy `manifest.yaml` from the bundle root into `<install_dir>/manifest.yaml`.
3. Copy `CHANGELOG.md` from the bundle root into `<install_dir>/CHANGELOG.md`.

### Breaking changes

None.

### Files changed

- `INSTALL.md` — replaced

## 1.7.2

*Released: 2026-05-13*

### Summary

Fixes two install gaps discovered during Codex upgrade testing (1.0.0 → 1.7.0):

1. **Missing protocols install step** — INSTALL.md had no step for
   `components/protocols/`. The protocol files (`create-package.md`,
   `cut-version.md`) were silently omitted from Codex installs. A new Step 7
   now explicitly installs both files into `<install_dir>/protocols/` with
   individual copy commands (no glob expansion).

2. **Spec docs wildcard copy** — Step 8 (was Step 7) previously said "copy
   all spec versions" without listing files individually. Glob/wildcard
   expansion failed on some platforms, leaving spec docs incomplete. The step
   now lists all five spec files explicitly with individual copy commands.

Step numbers 7–11 are renumbered to accommodate the new protocols step.
Confirmation summary (Step 10) updated to include protocols. The
`installed.json` template version is corrected to `1.7.2`.

### Upgrade steps

1. Copy `components/protocols/create-package.md` into `<install_dir>/protocols/create-package.md` — new file (create the `protocols/` directory if it does not exist).
2. Copy `components/protocols/cut-version.md` into `<install_dir>/protocols/cut-version.md` — new file.
3. Replace `INSTALL.md` with the new version from this bundle. No other changes.

### Breaking changes

None.

*(If none, write: "None.")*

### Files changed

- `CHANGELOG.md` — replaced
- `INSTALL.md` — replaced

## 1.7.1

*Released: 2026-05-12*

### Summary

Fixes INSTALL.md drift identified during Codex upgrade testing. The previous INSTALL.md was
written at v1.0.0 and never updated as the package grew. Specific fixes: Step 6 now lists all
seven script files (was "five"), Step 7 now references `A3IP-SPEC-v1.5.md` (was v1.1), Step 8
now includes the Phase 6 "browse the registry" trigger phrase, Step 9 now shows "7 files" in
the install summary, Step 10 now shows `version: "1.7.1"` and includes the `registry_source`
field with guidance on when to set it. Codex platform added to Step 1 and Step 4 location lists.

### Upgrade steps

1. Replace `INSTALL.md` with the new version from this bundle. No other changes.

### Breaking changes

None.

### Files changed

- `INSTALL.md` — replaced

## 1.7.0

*Released: 2026-05-12*

### Summary

Adds A3IP spec v1.5 — Registry & Ecosystem. The spec defines the `registry.yaml` index
format, browsing protocol, install-from-registry flow, update checking, and authoring
guidance. `installed.json` gains a `registry_source` field so future update checks know
where to look. The Creator SKILL.md gains a new `## Phase 6 -- Registry` section covering
how to browse a registry, resolve bundle URLs, install from a registry entry, and check for
updates. Also adds Design Principle 15: "Discoverable by default."

### Upgrade steps

1. Replace `components/skills/a3ip-creator/SKILL.md` with the new version from this bundle.
2. No script, config, or MCP changes.

No action required for the spec — replace the docs directory to get `docs/A3IP-SPEC-v1.5.md`.

### Breaking changes

None.

### Files changed

- `components/skills/a3ip-creator/SKILL.md` — replaced
- `docs/A3IP-SPEC-v1.5.md` — added

## 1.6.0

*Released: 2026-05-12*

### Summary

Creator improvements (Phase 5). `scaffold.py` now auto-generates natural-language question
text for every config key in CONFIGURE.md — no more `TODO: write the question text` markers.
Questions are derived from `label` and `description` with type-aware phrasing (boolean →
"Should X be enabled?", select → "Which X should be used?", sensitive → privacy note appended,
optional → default or skip note appended). `scripts/requirements.txt` is added to make the
PyYAML dependency explicit (`pip install -r requirements.txt`).

### Upgrade steps

1. Replace `scripts/scaffold.py` with the new version from this bundle.
2. Copy `scripts/requirements.txt` into the Creator's scripts directory — new file.

No config changes, no MCP changes, no breaking interface changes.

### Breaking changes

None.

### Files changed

- `scripts/scaffold.py` — replaced
- `scripts/requirements.txt` — added

## 1.5.0

*Released: 2026-05-12*

### Summary

Adds the interactive fix loop to the Creator skill (Phase 3 — Validate). The `## Phase 3`
section now lists all nine normative validator checks (updated from the previous four),
and includes an Auto-Fix Playbook: for each error type the Creator AI receives prescriptive
instructions on how to fix it autonomously without waiting for the user to interpret the
error. Also fixes a truncation bug in Phase 4 (incomplete `bundle.py` command) and updates
the spec version reference from v1.1 to v1.4.

### Upgrade steps

1. Replace `components/skills/a3ip-creator/SKILL.md` with the new version from this bundle.
   No scripts, config, or MCP changes.

### Breaking changes

None.

### Files changed

- `components/skills/a3ip-creator/SKILL.md` — replaced

## 1.4.0

*Released: 2026-05-12*

### Summary

Adds A3IP spec v1.4 — normative validation rules. The `## Validation` section defines all
nine checks any conformant A3IP validator must implement, with precise scope rules, pattern
definitions, error vs. warning severity, and exit-code requirements. The reference
implementation (`validate.py`) ships with the Creator. Also adds Design Principle 14:
"Validate before you ship." No changes to Creator scripts or tooling — documentation only.

### Upgrade steps

No action required — non-breaking update. Replace the docs directory contents with the updated
bundle to get `docs/A3IP-SPEC-v1.4.md`.

### Breaking changes

None.

### Files changed

- `docs/A3IP-SPEC-v1.4.md` — added

## 1.3.0

*Released: 2026-05-12*

### Summary

Adds A3IP spec v1.3 — formal terminology (Skill, Protocol, Prompt, Artifact, Script definitions,
component decision table) and canonical platform adapter conventions (Cowork, Claude Code, Codex,
Generic). No changes to Creator scripts or tooling — this is a documentation-only release.

### Upgrade steps

No action required — non-breaking update. Replace the docs directory contents with the updated
bundle to get `docs/A3IP-SPEC-v1.3.md`.

### Breaking changes

None.

### Files changed

- `CHANGELOG.md` — replaced
- `components/protocols/cut-version.md` — replaced
- `docs/A3IP-SPEC-v1.3.md` — added

## 1.2.0

*Released: 2026-05-12*

### Summary

Adds A3IP spec v1.2 security model support. `scaffold.py` now generates `trust_level:` on
script implementations, a `permissions:` block in the manifest, a `## Plan` section in
`INSTALL.md` for elevated-privilege packages, and `storage:` hints on sensitive config keys.
`validate.py` gains two new checks: Check 8 verifies that scripts with `network` or higher
trust level have a `permissions:` block declared, and Check 9 verifies that scripts with
`write-local` or `shell-exec` trust level have a `## Plan` section in `INSTALL.md`. The
A3IP-SPEC-v1.2.md document is included in the docs directory.

### Upgrade steps

1. Replace `scripts/scaffold.py` with the new version from this bundle.
2. Replace `scripts/validate.py` with the n