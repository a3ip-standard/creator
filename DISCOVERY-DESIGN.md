# Phase 0.7 — Discovery mode (design doc for Creator v3.0)

*Status: design, ready for #118 SKILL.md integration. Authored 2026-06-06
based on the ai-research-workspace dogfood findings.*

## Why Discovery exists

Today's Creator workflow assumes the user knows what their package
should contain and can answer ~30 intake questions describing it
(triggers, components, configuration keys, scripts, MCPs, platforms).
This is the right shape when the user is **designing** a package from
scratch.

But increasingly the user has a **pre-existing workflow** they want to
package: an AI-built skill in their Cowork, a research workspace they've
been iterating on with Claude over weeks, a project's accumulated
conventions in CLAUDE.md and memory. They cannot answer intake
questions for that workflow because they don't know what its
components are — the AI built most of it; the user only knows the
outcomes ("I review papers and synthesize findings").

Discovery is the inverse: instead of asking the user to declare the
package, **the Creator AI investigates the existing workflow and
reverse-engineers a draft package from it**. The user reviews and
corrects the draft, then proceeds to scaffold from a finished
intake.

This was articulated in the dogfood findings for `ai-research-workspace`
(2026-06-06): a real research workspace had file conventions,
trigger phrases, frontmatter schemas, and Cowork artifacts that the
Creator could have detected automatically. Discovery is the design
that captures this.

## Where Phase 0.7 sits in the Creator flow

```
Phase 0   Pre-flight (read spec, check tooling)
Phase 0.5 Platform parameterisation  (gather platform-config)
Phase 0.7 Discovery  (NEW — optional, alternative to Phase 1)
Phase 1   Intake     (now: blank-slate authoring OR Discovery refinement)
Phase 2   Scaffold
Phase 3   Validate
Phase 4   Build
Phase 5   Version
```

Phase 0.7 is **optional** and **alternative**:

- If the user is authoring from scratch, skip 0.7 → go to Phase 1.
- If the user wants to package an existing workflow, run 0.7 → the
  output of Discovery becomes the starting draft for Phase 1.

Discovery never replaces Phase 1 — it only populates it. The user
still reviews and confirms before Scaffold runs.

## Entry signals — when Discovery triggers

The Creator's SKILL.md should route to Phase 0.7 when the user says any
of:

- "Package this workspace" / "make this workflow an A3IP package"
- "Discover what's in this project" / "investigate this directory"
- "I have an existing workflow I want to share" / "turn this into a
  package"
- "Package this skill I've been using" / "wrap up this skill"

If the user instead says "create a new A3IP package" or "I want to
design a workflow", route to Phase 1 Intake directly — that's the
blank-slate path.

If the user is ambiguous, ask one question: "Are you (a) designing a
new workflow from scratch, or (b) packaging an existing workflow you
already use?" Answer (a) → Phase 1; answer (b) → Phase 0.7.

## What Discovery investigates

Six investigation lanes, each producing items tagged with confidence:

### Lane 1: Workspace tree scan

Look at the user-pointed-to workspace directory (or the Cowork
working directory). Catalogue:

- Top-level subdirectories that look like workflow concerns
  (`papers/`, `experiments/`, `syntheses/`, `tasks/`, `notes/`,
  `tickets/`, `releases/`). These often map to the workflow's nouns.
- File naming patterns: are files slug-named (`why-rope-matters.md`),
  date-prefixed (`2026-06-04-rope.md`), numbered (`001-intro.md`)?
- File extensions and counts: 30 `.md` files in one folder is a
  workflow shape signal; 1 `.json` config file is a setup signal.
- Frontmatter schema: for the first 5–10 markdown files per
  workflow-shaped subdirectory, extract the frontmatter keys and
  take the union — that's the workflow's data schema.

**Tool:** Read tool, Glob, mcp__filesystem__directory_tree.

**Output:** a "Workspace structure" section listing each
workflow-shaped subdirectory, its file count, naming convention, and
detected frontmatter schema.

**Confidence rules:**

- Subdirectory exists with >3 same-shape files → **high**.
- Frontmatter key appears in >50% of sampled files → **high**.
- Frontmatter key appears in only 1 file → **medium** (might be
  one-off, might be the user adding a new field they haven't
  back-filled).

### Lane 2: Skill inventory

If running on Cowork, call `mcp__skills__list_skills` to enumerate
the user's installed skills. Look for:

- Skills whose `description:` mentions concepts that overlap with
  the workspace's nouns ("research", "papers", "review" → likely
  related to a `papers/`-shaped workspace).
- Skills the user explicitly says "this is the one I want to
  package".

**Tool:** mcp__skills__list_skills (Cowork-only).

**Output:** a "Skills found" section listing each matching skill, its
description excerpt, and a marker for "user confirmed this is the
target skill" vs "candidate match, needs confirmation".

**Confidence rules:**

- User explicitly named the skill → **high**.
- Skill `description:` overlaps with workspace nouns and no other
  candidate matches better → **medium**.
- Multiple plausible candidates → **low** (ask the user which one).

### Lane 3: Skill content extraction

For the target skill (chosen from Lane 2 with user confirmation), read
its SKILL.md and extract:

- **Trigger phrases** from the `description:` frontmatter — these
  become the package's protocols.
- **Procedural steps** the SKILL.md describes — these become protocol
  step lists.
- **Referenced scripts** (paths like `scripts/<name>.py`,
  `mcp__cowork__update_artifact`, etc.) — these become declared
  scripts or MCP dependencies.
- **Referenced artifacts** (named patterns like "the kanban", "the
  log") — these become declared artifacts.
- **Referenced config keys** (placeholders like `{{workspace_dir}}`,
  `{{author_name}}`) — these become configuration entries.

**Tool:** Read tool on the skill's SKILL.md file.

**Output:** a "Skill content" section with extracted triggers,
procedural steps, scripts, artifacts, and config keys.

**Confidence rules:**

- Item is explicitly documented in SKILL.md → **high**.
- Item is inferred from a worked example in SKILL.md but not in the
  main text → **medium**.

### Lane 4: Cowork artifact inventory

If running on Cowork, call `mcp__cowork__list_artifacts` and identify
which artifacts the target workflow uses. A workflow's artifacts are
usually:

- Named after the workflow's persistent state ("paper-inbox",
  "experiment-log", "last-review").
- Updated by the workflow's protocols (the artifact's content shape
  matches the workflow's output).

Read each candidate artifact's HTML content to confirm the shape.

**Tool:** mcp__cowork__list_artifacts, mcp__cowork__read_widget_context.

**Output:** an "Artifacts found" section listing each matched
artifact, its name, and a one-line description derived from its
content.

**Confidence rules:**

- Artifact name matches a name referenced in SKILL.md → **high**.
- Artifact name plausibly relates to workspace nouns but is not
  referenced in SKILL.md → **medium**.

### Lane 5: Memory & CLAUDE.md mining

Read the user's persistent context for signals about the workflow:

- The auto-memory file at `<memory-dir>/MEMORY.md` and its referenced
  files: look for entries about the workflow's purpose, user's role,
  conventions used.
- The workspace's `CLAUDE.md` (if present): look for project-specific
  instructions about the workflow.

These often contain the **user's WHY**, which the AI cannot infer from
files alone: "papers are tracked because Max is preparing for his
thesis defence and needs to cite the lit review systematically."

**Tool:** Read tool, Glob.

**Output:** a "Context found" section listing each extracted statement
about the workflow's purpose, the user's role, conventions, and
constraints.

**Confidence rules:**

- Memory entry directly references the workflow by name → **high**.
- Memory entry describes the user's role and that role plausibly uses
  this workflow → **medium**.
- CLAUDE.md mentions a related convention → **medium**.

### Lane 6: MCP & tool inventory

Identify which connected MCPs and command-line tools the workflow
depends on:

- For each script the SKILL.md references, look at the script's
  imports/requires to detect external tool dependencies (Python
  packages, CLIs invoked, MCPs called).
- Cross-reference against the host runtime's connected MCPs (Cowork:
  the MCP toolbar; Codex: `~/.codex/mcp-config.json`; Claude Code:
  the MCP server registry).

**Tool:** Read tool on script files, mcp__mcp-registry__list_connectors
(if available).

**Output:** an "MCPs & tools" section listing each detected dependency
with required/optional status.

**Confidence rules:**

- Script imports `requests` and SKILL.md says "calls the GitLab API"
  → tool dependency, **high**.
- Script imports an MCP tool that's in the user's connected MCPs →
  MCP dependency, **high**.
- Script imports a tool not in the user's MCPs → MCP dependency,
  **medium** with a note that the user may need to install it before
  the package's first install.

## The Discovery Report

After all six lanes run, Discovery produces a **Discovery Report** in
markdown. This is the primary user-facing output. It is also the
input to Phase 1 (which transforms the report into intake.json with
the user's corrections).

The report layout:

```markdown
# Discovery Report: <workflow name>

*Generated 2026-MM-DD by A3IP Creator v3.0 Discovery mode.*

## Summary

<one-paragraph summary of what was found and the candidate package
shape it suggests.>

## Workspace structure  (Lane 1)

<list of workflow-shaped subdirectories, file counts, naming
conventions, frontmatter schemas, each item tagged with confidence>

## Skills found  (Lane 2)

<the target skill plus alternative candidates, marked with the user's
confirmation status>

## Skill content  (Lane 3)

### Trigger phrases (-> protocols)

<extracted from SKILL.md description>

### Procedural steps (-> protocol step lists)

<one block per detected protocol>

### Referenced scripts

<list with each script's purpose, parameters, platforms>

### Referenced artifacts

<list with each artifact's purpose and content shape>

### Configuration keys

<list with each key's purpose, sensitivity, required status>

## Artifacts in the runtime  (Lane 4)

<Cowork sidebar inventory, matched to declared artifacts>

## Context found  (Lane 5)

<memory entries and CLAUDE.md excerpts about the workflow's purpose
and user's role>

## MCPs & tools  (Lane 6)

<dependency list with required/optional status>

## Confidence summary

- **High confidence (N items):** these go straight into intake.json
  without further user confirmation.
- **Medium confidence (M items):** these go into intake.json but
  Phase 1 will surface them for user review.
- **Low confidence (K items):** these are listed as candidates but
  NOT included in intake.json without explicit user confirmation in
  Phase 1.

## Implicit conventions

<conventions observed in the workflow's runtime files but NOT
documented in SKILL.md. From the dogfood findings: section headers
the AI invented mid-workflow, verdict enums, status-update mechanisms.
These are tagged **low confidence** and surfaced to the user with a
"do you want to formalise this convention into the package, or is it
incidental?" question.>

## Draft intake.json

<full intake.json content, ready for Phase 1 review>
```

## How Phase 1 consumes Discovery output

Phase 1 Intake, when starting from a Discovery Report:

1. **Read the Discovery Report.** Acknowledge to the user: "I found
   <N> workflow components. Let me walk through them with you."
2. **Walk the report section by section.** For each item:
   - **High confidence:** state it as established, ask only "any
     changes?".
   - **Medium confidence:** state it with a "I observed X — is that
     what you intended?" framing.
   - **Low confidence (implicit conventions):** ask explicitly
     whether to include in the package, modify, or omit.
3. **Fill any gaps Discovery couldn't extract.** Some intake fields
   (license, author email, target platforms list) Discovery cannot
   detect — Phase 1 still asks these.
4. **Produce the final intake.json.** Same shape as the blank-slate
   Phase 1 output. Scaffold (Phase 2) cannot tell whether the
   intake came from Discovery or blank-slate.

This means Phase 1 has two entry doors but one output. The Phase 2
Scaffold is unchanged.

## Failure modes and edge cases

### The user points at the wrong directory

If Lane 1 finds <2 workflow-shaped subdirectories AND Lane 2 finds no
related skill, Discovery should ask: "I didn't find a recognisable
workflow shape here. Is the workflow you want to package located in a
different directory, or in your Cowork skills rather than the
filesystem?"

### The skill is installed but the workspace is fresh

If Lane 2 finds the target skill but Lane 1 finds no workspace files,
this is a "workflow not yet exercised" case. Discovery should
extract from SKILL.md only (Lanes 2, 3, 4, 6) and note in the report
that the workflow has not been exercised yet — the file conventions
and runtime artifacts will need to come from the user's intent
rather than from observed usage.

### Multiple plausible target skills

Lane 2 returns several candidate skills with similar overlap. Discovery
should ask the user to pick one before Lane 3 runs. Do not run Lane 3
on multiple skills — the report becomes unreadable.

### Implicit conventions conflict with documented ones

If Lane 1 finds a frontmatter schema that differs from what Lane 3
extracts from SKILL.md (e.g., SKILL.md says `authors:` is required but
80% of paper files have `authors: []`), surface this as a
**discrepancy**, not a discovery. The user decides which is correct
— and the answer often informs a package improvement.

### The user has no memory / no CLAUDE.md

Lane 5 simply produces no output for that user. Discovery still
proceeds with the other 5 lanes.

### Running outside Cowork

Lane 2 (`mcp__skills__list_skills`) and Lane 4
(`mcp__cowork__list_artifacts`) are Cowork-specific. On Codex or
Claude Code, Discovery substitutes:

- Lane 2: scan `~/.codex/skills/` or `~/.claude/skills/` for skill
  directories, match by description content.
- Lane 4: no equivalent — note that artifact discovery requires
  Cowork; Phase 1 will need to ask the user about artifacts
  explicitly.

## What this design intentionally does NOT do

- **Discovery does not write any files** to the user's workflow
  directory. It only reads. The Discovery Report is produced in the
  Creator's outputs directory; intake.json comes out at the end of
  Phase 1 like always.
- **Discovery does not assume the workflow is correct.** Implicit
  conventions are surfaced as candidates, not as established
  package contents. The user is the source of truth on what should
  be packaged.
- **Discovery does not bake in a single workflow shape.** The six
  lanes are extraction patterns, not workflow shapes. A research
  workspace, a project management skill, a code review flow, a
  release automation skill — Discovery applies the same lanes to
  each.
- **Discovery does not skip Phase 1.** The Discovery Report is input
  to Phase 1, not a replacement for it. The user still validates the
  intake before Scaffold runs.

## Open questions for the Creator v3.0 SKILL.md integration (#118)

1. **Discovery Report file location.** Probably
   `<creator-outputs>/discovery-report.md` next to where intake.json
   lands. The report should survive Phase 1 (Phase 1 reads it as
   input, then leaves it as a permanent record of what was found).

2. **Confidence values surfaced to the user.** Two display options:
   (a) include "(high)" / "(medium)" / "(low)" annotations inline in
   the report; (b) keep them as machine-readable metadata in
   intake.json and only show the user a count summary. Recommend (a)
   for transparency — the user benefits from knowing why each item
   was flagged.

3. **Should Discovery be idempotent?** Running Discovery twice on
   the same workspace should produce the same report (modulo
   timestamps). Yes. This means Lanes 1-6 are pure read operations
   and the report-synthesis step is deterministic given the same
   inputs.

4. **Integration with `a3ip scaffold`.** Discovery does not call
   `a3ip scaffold` directly — that's Phase 2. But Discovery should
   verify the CLI version is >= 1.5.2 (the version with
   `--platform-config`) before producing intake — earlier versions
   cannot consume the Phase 0.5 platform-config the Creator passes.

## Test cases for the dogfood (#117)

When dogfooding Discovery against `ai-research-workspace`, the report
should find:

- **Lane 1:** `papers/`, `experiments/`, `syntheses/` subdirectories
  (high); frontmatter schema with `title`, `source`, `status`,
  `captured_at`, `captured_by`, `authors`, `year` (high for the first
  5, medium for `authors`/`year` because of the under-extraction
  finding); slug + date-prefix naming convention (high).
- **Lane 2:** the ai-research-workspace skill (high, after user
  confirmation).
- **Lane 3:** 5 trigger phrases (high); 12-question review template
  (high); 4-section synthesis structure (high); bidirectional
  `related_papers` / `related_experiments` linking (high);
  `workspace_dir` and `author_name` config keys (high).
- **Lane 4:** paper-inbox, experiment-log artifacts (high); the
  artifact-creation-on-install gap surfaces as an "artifacts referenced
  in SKILL.md but not present in the runtime" warning.
- **Lane 5:** Max's role as A3IP project lead (high); workflow
  purpose ("research literature review for thesis or paper writing")
  (medium — extracted from context, may need user confirmation).
- **Lane 6:** Python required; PyYAML optional;
  `mcp__cowork__update_artifact` used by the protocols.
- **Implicit conventions surfaced:** `## Review` / `## Observations`
  section headers (low); the verdict enum (low); the sed-based
  status update (low — and Discovery should flag this as
  "fragile mechanism, consider formalising").

If Discovery successfully extracts at least 80% of the v1.0 dogfood
findings, it has met the test bar.
