# A3IP Specification v1.4
**AI Infrastructure Installation Package**

> A platform-agnostic format for packaging and sharing complete AI workspace workflows — a superset of the [SKILL.md](https://agentskills.io) open standard and [Microsoft APM](https://microsoft.github.io/apm/).

**What's new in v1.4:** Normative validation rules — a formal `## Validation` section that defines all nine checks any conformant A3IP validator must implement. The reference implementation (`validate.py`) ships with the A3IP Creator. Packages authored under v1.0, v1.1, v1.2, or v1.3 remain fully valid.

---

## Overview

*(Unchanged from v1.3.)*

---

## Package Structure

*(Unchanged from v1.2 — see v1.2 spec for directory layout and bundle format.)*

---

## Terminology

*(Unchanged from v1.3 — see v1.3 spec for component definitions and decision table.)*

---

## Platform Conventions

*(Unchanged from v1.3 — see v1.3 spec for platform adapter conventions.)*

---

## Validation

A conformant A3IP validator must implement all nine checks defined in this section. The checks are ordered: checks 1–7 apply to all packages; checks 8–9 apply only to packages that use v1.2 security fields.

The reference implementation is `validate.py`, distributed with the A3IP Creator package. Any validator on any platform must produce equivalent results for the same input package.

---

### Terminology

**Error** — a condition that means the package is incomplete or non-conformant. An AI installer must not install a package that has validation errors. The package author must fix the error before distributing.

**Warning** — a condition that is not an error today but may become one, or indicates a likely oversight. The author should review each warning; the AI installer may proceed but should note warnings to the user.

**Declared config key** — a key listed in `manifest.yaml` under the `configuration:` section, in a `- key: <name>` entry.

**Script key** — a key listed in `manifest.yaml` under `components: → scripts:`, in a `- key: <name>` entry.

**Implementation** — one entry in the `implementations:` list of a script definition. Each implementation has a `file:`, a `platform:`, and (from v1.2) optionally a `trust_level:`.

---

### Check 1 — Config coverage

**Rule:** Every `{{config.key}}` reference that appears in a non-script template file must correspond to a declared config key in `manifest.yaml`.

**Rationale:** Config substitution is the mechanism by which install-time values flow into package files. An undeclared reference will silently fail — the placeholder remains unresolved at install time.

**Scope of scan:** All files in the package directory whose extension is one of: `.md`, `.yaml`, `.yml`, `.json`, `.txt`, `.html`, `.js`, `.css`. Directories excluded from scan: `docs/`. Files excluded from scan: any file named `SKILL.md` (these are instructional documents that legitimately use `{{config.key}}` as example syntax). Script files (`.py`, `.ps1`, `.sh`) are excluded — config references in scripts are covered by Check 3.

**Pattern to match:** `{{config.<key_name>}}` where `key_name` consists of letters, digits, and underscores.

**Outcome:** Error for each unique undeclared key found. The error message names the key and the files that reference it.

---

### Check 2 — Script existence

**Rule:** Every file declared in a script implementation must exist on disk at the path specified, relative to the package directory.

**Rationale:** A package that declares a script but does not include the file will fail during installation when the receiving AI tries to copy or invoke the script.

**Scope:** Every implementation entry in `components: → scripts:`. For each entry: check that `<package_dir>/<implementation.file>` exists.

**Outcome:** Error for each missing file. The error message names the script key and the missing file path.

---

### Check 3 — Script config reads

**Rule:** Every config key accessed in a script file must be a declared config key in `manifest.yaml`.

**Rationale:** Scripts access config values at runtime. A key that is read but not declared will be absent from the config file and cause the script to fail.

**Scope of scan:** All files with extension `.py`, `.ps1`, or `.sh` in the package directory.

**Patterns to match (any of the following):**
- `config["key_name"]` or `config['key_name']`
- `config.get("key_name")` or `config.get('key_name')`
- `$config.key_name` (PowerShell)

**Outcome:** Error for each undeclared key found in any script file. The error message names the script file and the undeclared key.

---

### Check 4 — Cross-platform coverage

**Rule:** Every script that declares a Windows-specific implementation must also declare an `any`-platform (cross-platform) implementation.

**Rationale:** Windows-only scripts lock the package to a single OS. The A3IP standard requires that every script capability be available cross-platform. The Windows PS1 implementation is a preferred-platform optimisation, not a replacement.

**Scope:** Every script entry in `components: → scripts:`.

**Condition:** If the set of declared `platform:` values for a script includes `windows` but does not include `any`, the check fails.

**Outcome:** Error for each script that has a Windows implementation but no `any` implementation.

**Warnings (non-blocking):**
- A script declares `platform: windows` but `adapters/windows/scripts/<key>.ps1` does not exist on disk.
- A script declares `platform: any` but `scripts/<key>.py` does not exist on disk.

---

### Check 5 — Auth flows

**Rule:** If the package includes authentication scripts, INSTALL.md must include an authentication step.

**Rationale:** Auth scripts are useless unless the installer knows to run them. An auth script with no corresponding INSTALL.md step will be silently skipped during installation.

**Detection of auth scripts:** Any file matching `scripts/auth_*.py` or `adapters/windows/scripts/auth_*.ps1` in the package directory is treated as an auth script.

**Detection of auth step:** INSTALL.md (lowercased) contains either the filename stem of the auth script (e.g. `auth_gitlab`) or the word `authenticate`.

**Outcome:** Warning (not error) for each auth script whose name or authenticate keyword is absent from INSTALL.md. The warning names the script and suggests adding an Authenticate step.

---

### Check 6 — CHANGELOG present

**Rule:** Any package with a version higher than `1.0.0` must include a `CHANGELOG.md` file.

**Rationale:** Delta upgrades depend on CHANGELOG.md. An AI upgrading from a prior version reads CHANGELOG.md to determine which files to replace and what steps to apply. Without it, every upgrade requires a full reinstall.

**Version comparison:** Parse `version:` from manifest as a dot-separated integer tuple. Version `[1, 0, 0]` and `[1, 0]` are treated as initial releases; any higher version requires CHANGELOG.md.

**Outcome:** Error if the package version is above 1.0.0 and CHANGELOG.md is absent. Warning if version is 1.0.0 and CHANGELOG.md is absent (will be required on next release).

---

### Check 7 — Refresh scripts

**Rule:** Every `refresh_script:` value declared on a config key must be a declared script key.

**Rationale:** `refresh_script:` tells the AI which script to run to re-fetch or re-derive a config value. A reference to a non-existent script key means the refresh mechanism silently does nothing.

**Scope:** Every entry in `configuration:` that has a `refresh_script:` field.

**Outcome:** Error for each `refresh_script:` value that is not a declared script key in `components: → scripts:`. The error names the config key and the missing script key.

---

### Check 8 — Trust level → permissions block (v1.2+)

**Rule:** Any package in which at least one script implementation declares `trust_level: network`, `trust_level: write-local`, or `trust_level: shell-exec` must include a top-level `permissions:` block in `manifest.yaml`.

**Rationale:** Elevated-trust scripts have side effects outside the AI session — they touch the network, write files, or execute shell commands. The `permissions:` block is the formal declaration of what the package will access. Without it, the user and installer cannot make an informed consent decision before installation begins.

**Trust levels that trigger this check:** `network`, `write-local`, `shell-exec`. The level `read-only` does not trigger this check.

**Permissions block:** A top-level `permissions:` key in `manifest.yaml` containing any of: `filesystem:`, `network:`, `mcp_tools:`, `shell_commands:`.

**Outcome:** Error if elevated-trust scripts are present and no `permissions:` block exists. The error names each script and its trust level.

**Scope note:** This check only activates if at least one implementation has a `trust_level:` field. Packages that pre-date v1.2 and do not use `trust_level:` are unaffected.

---

### Check 9 — Trust level → `## Plan` section (v1.2+)

**Rule:** Any package in which at least one script implementation declares `trust_level: write-local` or `trust_level: shell-exec` must include a `## Plan` section in `INSTALL.md`.

**Rationale:** Scripts that write files or execute shell commands must obtain user consent before running. The `## Plan` section is the mechanism: the AI presents it to the user and waits for confirmation before executing any side-effecting step. Without it, the user has no opportunity to review and approve the installation's impact.

**Trust levels that trigger this check:** `write-local`, `shell-exec`. The levels `read-only` and `network` do not trigger this check.

**Plan section detection:** `INSTALL.md` contains a level-two heading matching `## Plan` (case-insensitive).

**Outcome:** Error if write-trust scripts are present and `## Plan` is absent from INSTALL.md. The error names each script and its trust level.

**Scope note:** Same as Check 8 — only activates when `trust_level:` fields are present.

---

### Summary table

| # | Name | Severity | v1.2+ only |
|---|---|---|---|
| 1 | Config coverage | Error | No |
| 2 | Script existence | Error | No |
| 3 | Script config reads | Error | No |
| 4 | Cross-platform coverage | Error / Warning | No |
| 5 | Auth flows | Warning | No |
| 6 | CHANGELOG present | Error / Warning | No |
| 7 | Refresh scripts | Error | No |
| 8 | Trust → permissions | Error | Yes |
| 9 | Trust → plan section | Error | Yes |

---

### Exit behavior

A conformant validator must exit with code `0` when no errors are found (warnings are acceptable) and exit with code `1` when one or more errors are found.

---

### Reference implementation

`validate.py` (distributed with the A3IP Creator, v1.1.0 and later) is the reference implementation of these nine checks. It is the normative reference: if this spec and the script diverge, the spec takes precedence.

The script uses `PyYAML` when installed and falls back to a minimal regex-based manifest parser when not. Authors of other validator implementations should aim for equivalent coverage of the checks above.

---

## manifest.yaml, CONFIGURE.md, INSTALL.md, CHANGELOG.md, installed.json

*(Unchanged from v1.2.)*

---

## Component Formats

*(Unchanged from v1.0 — Skill, Artifact, Protocol, Prompt Template, Script formats are identical.)*

---

## Versioning

*(Unchanged from v1.3. Updated spec compatibility table below.)*

### Spec compatibility

| Spec version | Features added |
|---|---|
| `1.0` | Core: manifest, INSTALL.md, CONFIGURE.md, bundle format, `{{config.*}}` substitution |
| `1.1` | Versioning: CHANGELOG.md, installed.json, `## Upgrading` in INSTALL.md, `refresh:` on config keys, `min_a3ip_spec:`, `latest_change:` |
| `1.2` | Security: `trust_level:` on scripts, `permissions:` block, `## Plan` in INSTALL.md, `storage:` on sensitive config keys |
| `1.3` | Terminology: formal component definitions, decision table, platform adapter conventions |
| `1.4` | Validation: nine normative checks every conformant validator must implement |

---

## Design Principles

*(Unchanged from v1.3.)*

1. **Platform agnostic by default.** Components are described at intent level. Platform-specific implementations go in `adapters/<platform>/`.
2. **OS agnostic by default.** Scripts must provide a cross-platform Python implementation. OS-specific alternatives live in `adapters/<os>/scripts/`.
3. **AI-first installation.** The receiving AI reads `INSTALL.md` and performs setup. No human-operated CLI required.
4. **User-configurable.** `CONFIGURE.md` turns installation into a conversation.
5. **Two-variable model.** `{{config.*}}` values are set once at install time. `{{variable}}` values are filled at runtime.
6. **Graceful degradation.** Every dependency declares a fallback. Every artifact ships a markdown fallback.
7. **Delta upgrades, not re-installs.** `CHANGELOG.md` gives the AI a precise, version-scoped upgrade path.
8. **Installation state is local.** `installed.json` lives with the user's config, not in the package.
9. **Composable.** A3IP packages can declare other A3IP packages as dependencies.
10. **Plain text end-to-end.** Every component file is plain text. The `.a3ip.bundle` is a single readable text file.
11. **Superset, not fork.** Any valid SKILL.md skill and any APM-compatible manifest block is valid inside A3IP.
12. **Declare before you act.** Scripts declare their trust level; packages declare their permissions; the AI presents a plan and gets user consent before any side-effecting step runs.
13. **One component, one job.** Each component type has a precise role. Mixing responsibilities (e.g. putting executable logic in a Skill) makes packages harder to maintain and harder for the receiving AI to reason about.
14. **Validate before you ship.** A package that hasn't passed all nine validation checks is not ready to distribute. Validation is a gate, not a suggestion.

---

*A3IP Specification v1.4*
*Supersedes v1.3. All v1.0, v1.1, v1.2, and v1.3 packages remain valid under v1.4.*
*Released: 2026-05-12*
