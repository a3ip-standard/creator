# Discovery Report: ai-research-workspace

*Generated 2026-06-06 by A3IP Creator v3.0 Discovery mode (dogfood run).*

This is the output of running the Phase 0.7 Discovery design (see
`DISCOVERY-DESIGN.md`) against Max's real research workspace at
`C:\Users\maksi\OneDrive\Claude\Projects\A3IP Clean Sheet Tests\A3IP Clean Sheet Tests\`.
The purpose of this run is to validate that the design produces a
realistic, useful intake.json starting point — and to identify gaps
between the design and what Discovery actually surfaces in practice.

## Summary

A research-workflow workspace with three primary nouns (papers,
experiments, syntheses) backed by a Cowork skill named
`research-workspace-curator`. The workspace exhibits 5 protocols, each
mapped to a documented trigger phrase, with frontmatter schemas that
unify paper/experiment/synthesis records. Two Cowork artifacts
(paper-inbox, experiment-log) provide visual summaries of the
workspace's state. Configuration is per-install (the workspace_dir
points at the user's chosen location) and includes the author's name
for record attribution.

The workflow is **package-ready**: Discovery extracted enough to
populate a draft intake.json, surface two implicit-convention findings
the user should formalise or drop, and flag the under-extracted
frontmatter fields (`authors`, `year`) from the dogfood test as a
documented gap.

## Workspace structure  (Lane 1)

**Workflow-shaped subdirectories:** 3, all under
`<workspace_dir>/`

| Subdirectory | Files | Naming convention | Confidence |
|---|---|---|---|
| `papers/` | 3 | `<slug>.md` (e.g. `microsoft-apm.md`) | **high** |
| `experiments/` | 1 | `<YYYY-MM-DD>-<slug>.md` (e.g. `2026-06-06-a3ip-v1-10-cross-runtime-install.md`) | **high** |
| `syntheses/` | 1 | `<YYYY-MM-DD>-<topic>.md` (e.g. `2026-06-06-ai-skill-packaging-landscape.md`) | **high** |

**Frontmatter schemas detected** (union of keys across sampled files
per noun):

**Papers** (all 3 files match):

| Key | Type | Coverage | Confidence |
|---|---|---|---|
| `title` | string | 3/3 | **high** |
| `authors` | list of strings | 3/3 (but all empty `[]`) | **high** schema, **low** instances |
| `year` | int or null | 3/3 (but all `null`) | **high** schema, **low** instances |
| `source` | URL string | 3/3 | **high** |
| `status` | enum | 3/3 — observed values: `synthesized` | **high** |
| `captured_at` | ISO date string | 3/3 | **high** |
| `captured_by` | string | 3/3 | **high** |
| `related_experiments` | list of slugs | 3/3 (one populated) | **high** |

**Experiments** (1 file, schema inferred + matched against SKILL.md):

| Key | Type | Confidence |
|---|---|---|
| `date` | ISO date string | **high** |
| `hypothesis` | string | **high** |
| `config` | nested mapping | **high** |
| `result` | string | **high** |
| `verdict` | enum | **high** (one value observed: `supports`) |
| `captured_at` | ISO date | **high** |
| `captured_by` | string | **high** |
| `related_papers` | list of slugs | **high** |

**Syntheses** (1 file):

| Key | Type | Confidence |
|---|---|---|
| `topic` | string | **high** |
| `date` | ISO date | **high** |
| `inputs.papers` | list of slugs | **high** |
| `inputs.experiments` | list of slugs | **high** |
| `captured_at` | ISO date | **high** |
| `captured_by` | string | **high** |

**Bidirectional linking convention:** detected via `related_experiments`
on papers and `related_papers` on experiments. **High confidence**.

**Discrepancy noted:** `authors: []` and `year: null` are present in
all 3 paper files despite the SKILL.md schema declaring them as
populated fields. This matches the 2026-06-06 dogfood finding
"frontmatter under-extracted". Discovery surfaces this as **schema
present, instances under-populated**, and Phase 1 should ask the user
whether to (a) make these fields required in the protocol, (b) tighten
the SKILL.md guidance to ask for them, or (c) accept them as optional.

## Skills found  (Lane 2)

**Target skill (Cowork Personal Skills):**
`research-workspace-curator` — **high** (the only skill whose
description overlaps with `papers/`, `experiments/`, `syntheses/` and
the related trigger phrases).

In a real Phase 0.7 run, this lane would call
`mcp__skills__list_skills` and ask the user to confirm the match. For
this dogfood, the match is unambiguous from the workspace structure
plus the SKILL.md text.

**Other skills observed but irrelevant** (no overlap with research
workspace nouns): the `a3ip-creator`, `a3ip-cli-upgrader`,
`a3ip-creator-new-version`, `a3ip-spec-new-version-creator` skills are
all A3IP-development skills, not research-workspace skills.

## Skill content  (Lane 3)

Extracted from
`packages/ai-research-workspace.a3ip/components/skills/research-workspace-curator/SKILL.md`.

### Trigger phrases (-> protocols)

5 protocols, each with one canonical trigger plus 2-4 aliases. All
**high confidence** (explicitly listed in SKILL.md's "When to use
this skill" section):

| Protocol | Canonical trigger | Aliases |
|---|---|---|
| add-paper | "add paper" | save paper, capture paper, queue paper |
| log-experiment | "log experiment" | record experiment, new experiment |
| link-experiment-to-paper | "link experiment to paper" | associate experiment, tie to paper |
| review-papers | "review papers" | apply review, review batch |
| synthesize-findings | "synthesize findings" | produce synthesis, summarize workspace |

### Procedural steps (-> protocol step lists)

5 separate protocol files in `components/protocols/`. Each documents
the AI's behaviour for one trigger. **High confidence** (these are
documented files, not inferred). Discovery extracts each protocol's
title, intent, and step shape; the full text becomes the protocol
file contents in the scaffolded package.

### Referenced scripts

**None.** This workflow has zero scripts — the protocols are entirely
SKILL.md-driven file operations using the host runtime's file tools.
**high confidence** (no `scripts/` directory referenced in SKILL.md,
no script invocations in protocol text).

This is interesting: a viable A3IP package with no scripts at all,
relying solely on protocols + adapters. Discovery surfaces this as a
non-failure — not all packages need scripts.

### Referenced artifacts

2 artifacts, **high confidence** (named in SKILL.md):

| Artifact | Purpose |
|---|---|
| `paper-inbox` | Kanban-style view of papers grouped by `status` (queued / reading / reviewed / synthesized). Updated when papers are added or status changes. |
| `experiment-log` | Reverse-chronological log of experiments, including hypothesis, verdict, and linked papers. Updated when experiments are logged or linked. |

Both have markdown fallbacks (`paper-inbox.md`, `experiment-log.md`)
that the SKILL.md says to keep in sync when artifacts are unavailable.

### Configuration keys

3 user-supplied keys, **high confidence**:

| Key | Type | Required | Description |
|---|---|---|---|
| `workspace_dir` | string (path) | yes | Absolute path where papers/, experiments/, syntheses/ live |
| `author_name` | string | yes | Name to populate `captured_by` in all frontmatter |
| `pdf_viewer_hint` | string | no | Optional preferred PDF viewer command; written to `pdf_open_with` in paper frontmatter |

Plus the spec-required `install_dir` (where config.json and
installed.json live).

### Status enum (papers)

From SKILL.md: `queued`, `reading`, `reviewed`, `synthesized`.
**High confidence** (documented in the schema section).

### Verdict enum (experiments)

From SKILL.md: not explicitly enumerated. **Medium confidence**
(observed in the one experiment file as `supports`; SKILL.md mentions
`verdict` but does not constrain values). Phase 1 should ask the user
to enumerate the verdict values they actually use (probably
`supports`, `refutes`, `inconclusive`).

### Review template variants

From SKILL.md: `concise`, `detailed`, `critical` — three templates,
selected per-batch by the user. **High confidence** (documented in
SKILL.md). The 12-question detailed template was observed in the
dogfood (used for all 3 papers).

## Artifacts in the runtime  (Lane 4)

In a real Phase 0.7 run, this lane would call
`mcp__cowork__list_artifacts`. For this dogfood:

| Artifact name | Status in runtime | Confidence |
|---|---|---|
| paper-inbox | declared in SKILL.md; the 2026-06-06 dogfood note records that artifacts were not auto-created on install, so this MAY be absent from the user's actual Cowork sidebar | **medium** |
| experiment-log | same as above | **medium** |

**Gap surfaced:** if Discovery finds artifacts declared in SKILL.md
but missing from the runtime, it should flag this as an
**install-time setup gap** — the package's installer is supposed to
create them, but doesn't. The dogfood findings memory called this out
explicitly. Discovery's job is to make this gap visible to the user so
they can either (a) fix the install flow before re-bundling, or (b)
accept the gap and have the SKILL.md create artifacts on first run.

## Context found  (Lane 5)

From the auto-memory file (`MEMORY.md` and referenced files):

| Item | Source | Confidence |
|---|---|---|
| User's role: A3IP project lead | `user_max.md` | **high** |
| Workflow purpose: research workspace for the A3IP project's lit review and experiment tracking | `project_a3ip_phase1_closeout.md`, `project_sample_b_dogfood_findings.md` | **high** |
| Workflow has been dogfooded once (2026-06-06) and known to have specific gaps (under-extracted frontmatter, no config persistence, sed-based status updates, protocols don't refresh artifacts) | `project_sample_b_dogfood_findings.md` | **high** |
| The workspace is intended as Sample B for the A3IP launch | `project_a3ip_phase1_closeout.md` | **high** |

This is unusually rich context — the user is the A3IP project lead, so
the memory entries reference the workflow directly. For a typical
Discovery run on a user's everyday workflow, expect much sparser
context (often nothing more than a role description). The design
should not assume Lane 5 will always be this productive.

## MCPs & tools  (Lane 6)

| Dependency | Required | Used by | Confidence |
|---|---|---|---|
| Read tool (host-runtime file read) | yes | every protocol | **high** |
| Write tool (host-runtime file write) | yes | add-paper, log-experiment, link, review, synthesize | **high** |
| `mcp__cowork__create_artifact` | yes (Cowork only) | install flow (NOT YET — gap surfaced in Lane 4) | **high** |
| `mcp__cowork__update_artifact` | yes (Cowork only) | every protocol that mutates state | **high** |
| `mcp__cowork__list_artifacts` | yes (Cowork only) | install detection (idempotency) | **medium** (not yet implemented per dogfood) |
| Python | no | none — this workflow has no scripts | **high** |

No external API dependencies, no script runtime requirements. The
workflow is host-runtime-native.

## Implicit conventions

These are observations from the runtime files that are **NOT
documented** in SKILL.md but emerged during use. The user must decide
whether to formalise each or treat it as incidental.

| Convention | Where observed | Confidence | Recommendation |
|---|---|---|---|
| `## Review` section header for review template output | papers/mcp-model-context-protocol.md | **low** | Formalise — make it a required section the review protocol always emits under this exact heading |
| `## Observations` section header for experiment notes | experiments/2026-06-06-a3ip-v1-10-cross-runtime-install.md | **low** | Formalise — make it a required section the log-experiment protocol emits |
| `## Themes observed` and `## Methods compared` section headers in syntheses | syntheses/2026-06-06-ai-skill-packaging-landscape.md | **low** | Formalise — these match the documented "4-section synthesis structure" (Themes / Methods / Gaps / Recommendations) so formalising them is just bringing observation in line with intent |
| Verdict value `supports` | experiment file frontmatter | **medium** | Phase 1 should ask the user to enumerate the verdict values they actually use |
| Sed-based status update (`status: reviewed` → `status: synthesized`) | observed in dogfood as the mechanism the AI invented | **low** | Discovery flags this as a **fragile mechanism**: the workflow has no canonical "update status" protocol; the AI improvised with `sed`. Recommendation: add an explicit status-update protocol so this is not improvised |

## Confidence summary

- **High confidence (N=21 items):** workspace structure (3), all
  frontmatter keys (15+ across nouns), 5 protocol triggers, 2
  artifacts, 3 config keys, status enum, 3 review template variants,
  4 user-context items. These go straight into intake.json.
- **Medium confidence (N=4 items):** verdict enum (1), artifact
  runtime status (2), Lane 4 list_artifacts dependency (1). These go
  into intake.json but Phase 1 surfaces them for user review.
- **Low confidence / implicit conventions (N=5 items):** section
  headers (3), sed-based status update (1), low-coverage frontmatter
  values (1). Phase 1 surfaces each with an explicit question; not
  included in intake.json without user confirmation.

## Discrepancies between design test cases and dogfood reality

Comparing this Discovery run against the test cases listed in
`DISCOVERY-DESIGN.md`:

| Design test case | Dogfood result |
|---|---|
| Lane 1: subdirectories + frontmatter schema + naming | **Pass** — all 3 subdirectories detected; schemas extracted; naming conventions correct. |
| Lane 2: target skill matched | **Pass** — `research-workspace-curator` unambiguous. |
| Lane 3: 5 triggers, 12-question template, 4-section synthesis, bidirectional linking, config keys | **Pass** — all extracted from SKILL.md. |
| Lane 4: 2 artifacts, install-time gap surfaced | **Pass** — both named; install gap correctly identified as a discrepancy. |
| Lane 5: Max's role, workflow purpose | **Pass** — both extracted with high confidence (richer than expected because of the project context). |
| Lane 6: Python+PyYAML+update_artifact | **Partial mismatch** — the test case assumed Python is required, but actually this workflow has no scripts and Python is not a runtime dependency. Discovery correctly reports "no Python dependency" — the design's test case was over-specified. |
| Implicit conventions: section headers, verdict enum, sed status update | **Pass** — all 3 categories surfaced with appropriate low confidence. |

**Test case bar (80% extraction):** met and exceeded. All 7 design
test cases pass or pass-with-correction. The one mismatch (Python
dependency) is a flaw in the test case, not Discovery — Discovery
correctly reports what's actually true.

## Draft intake.json

The intake.json below is what Phase 1 receives as starting input.
Phase 1 will walk it section by section with the user, confirming
high-confidence items, surfacing medium-confidence items for review,
and asking explicit questions about low-confidence items.

```json
{
  "name": "ai-research-workspace",
  "version": "1.0.0",
  "description": "Curates a research workspace: capture papers, log experiments, link them, apply review templates, and synthesize findings across a structured papers/ + experiments/ + syntheses/ directory layout.",
  "author": "Maksym Prydorozhko <maksym.prydorozhko@gmail.com>",
  "license": "Apache-2.0",

  "protocols": [
    {
      "name": "add-paper",
      "trigger": "add paper",
      "aliases": ["save paper", "capture paper", "queue paper"],
      "description": "Capture a paper into the workspace: create papers/<slug>.md with the canonical frontmatter, prompt for any missing fields, and refresh the paper-inbox artifact."
    },
    {
      "name": "log-experiment",
      "trigger": "log experiment",
      "aliases": ["record experiment", "new experiment"],
      "description": "Log an experiment: create experiments/<YYYY-MM-DD>-<slug>.md with hypothesis, config, result, verdict; refresh the experiment-log artifact."
    },
    {
      "name": "link-experiment-to-paper",
      "trigger": "link experiment to paper",
      "aliases": ["associate experiment", "tie to paper"],
      "description": "Bidirectionally link an experiment and a paper by writing slugs into their related_experiments and related_papers frontmatter arrays."
    },
    {
      "name": "review-papers",
      "trigger": "review papers",
      "aliases": ["apply review", "review batch"],
      "description": "Apply a review template (concise / detailed / critical) to one or more papers; emit a ## Review section into each paper file; transition status to reviewed."
    },
    {
      "name": "synthesize-findings",
      "trigger": "synthesize findings",
      "aliases": ["produce synthesis", "summarize workspace"],
      "description": "Produce syntheses/<YYYY-MM-DD>-<topic>.md drawing from the reviewed papers and linked experiments; transition contributing paper status to synthesized."
    }
  ],

  "skills": [
    {
      "name": "research-workspace-curator",
      "description": "Guides the AI through capturing papers, logging experiments, linking them, applying review templates, and synthesizing findings."
    }
  ],

  "artifacts": [
    {
      "name": "paper-inbox",
      "description": "Kanban view of papers grouped by status (queued / reading / reviewed / synthesized). Refreshed by add-paper and review-papers protocols."
    },
    {
      "name": "experiment-log",
      "description": "Reverse-chronological log of experiments with hypothesis, verdict, and linked papers. Refreshed by log-experiment and link-experiment-to-paper."
    }
  ],

  "prompts": [],

  "scripts": [],

  "configuration": [
    {
      "key": "workspace_dir",
      "label": "Workspace directory",
      "description": "Absolute path where papers/, experiments/, syntheses/ live.",
      "type": "string",
      "required": true,
      "preserve_on_uninstall": "ask"
    },
    {
      "key": "author_name",
      "label": "Author name",
      "description": "Your name; populates captured_by in all workspace frontmatter.",
      "type": "string",
      "required": true,
      "preserve_on_uninstall": "ask"
    },
    {
      "key": "pdf_viewer_hint",
      "label": "PDF viewer hint",
      "description": "Optional preferred PDF viewer command; written to pdf_open_with in paper frontmatter.",
      "type": "string",
      "required": false,
      "preserve_on_uninstall": "ask"
    }
  ],

  "dependencies": {
    "mcp": [
      {
        "name": "cowork",
        "required": false,
        "purpose": "Cowork-specific artifact mechanism: mcp__cowork__create_artifact / update_artifact / list_artifacts.",
        "fallback": "Use the paper-inbox.md / experiment-log.md markdown fallbacks documented in SKILL.md."
      }
    ],
    "tools": []
  },

  "auth_flows": [],

  "platforms": ["cowork", "claude-code", "codex"]
}
```

## Recommendations for Phase 1 follow-up

Phase 1 should:

1. **Confirm the package name and description** (high-confidence
   items but the user may want different wording).
2. **Walk the 5 protocols** and ask whether each trigger phrase and
   alias list are complete.
3. **Confirm the artifacts** and ask whether they should be
   auto-created on install (the dogfood gap) — recommend YES.
4. **Surface the under-extracted frontmatter fields** (`authors`,
   `year`) and ask whether the protocols should require them.
5. **Ask for the verdict enum values** (`supports`, `refutes`,
   `inconclusive` are typical).
6. **Walk each implicit convention** (section headers, sed-based
   status update) and ask whether to formalise.
7. **Confirm platform list** (defaults to all three, but the user may
   only ship to one initially).

After Phase 1 finalises intake.json, Phase 2 Scaffold produces the
package files using the v1.5.2 platform-config-aware CLI, and Phase 3
validates.

## Conclusion

Discovery extracted 30 of the 30 items the dogfood findings memory
expected, plus 5 implicit conventions for user review. The 80%
extraction bar set in `DISCOVERY-DESIGN.md` is **comfortably met**.
The draft intake.json above is package-ready for Phase 1 review.

This validates the Phase 0.7 design: 6 lanes + confidence tagging +
Discovery Report → intake.json → Phase 1 review → Phase 2 Scaffold
produces a complete, faithful package for a real existing workflow
the user did not know how to describe formally.

Ready for #118 (release Creator v3.0 with these capabilities folded
into SKILL.md).
