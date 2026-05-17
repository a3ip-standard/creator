# A3IP Specification v1.3
**AI Infrastructure Installation Package**

> A platform-agnostic format for packaging and sharing complete AI workspace workflows — a superset of the [SKILL.md](https://agentskills.io) open standard and [Microsoft APM](https://microsoft.github.io/apm/).

**What's new in v1.3:** Formal terminology — precise definitions for every component type, a decision table for choosing the right component, and canonical platform adapter conventions for Cowork, Claude Code, Codex, and generic AI platforms. Packages authored under v1.0, v1.1, or v1.2 remain fully valid.

---

## Overview

*(Unchanged from v1.2.)*

---

## Package Structure

*(Unchanged from v1.2 — see v1.2 spec for directory layout and bundle format.)*

---

## Terminology

Clear, shared vocabulary is the foundation of a consistent ecosystem. Every A3IP package is built from five component types. This section defines each one precisely so authors make deliberate choices and recipients know exactly what they're receiving.

---

### Skill

**A persistent instruction set that changes how the AI behaves in all subsequent interactions.**

A Skill is loaded into the AI's context and remains active for the duration of a session (or permanently, depending on the platform). It does not respond to a specific trigger — it is always in effect once loaded.

**File:** `components/skills/<name>/SKILL.md`  
**Format:** SKILL.md (Anthropic open standard)  
**Loaded by:** The user or the platform at session start, or by the AI after install.

**A Skill is the right choice when:**
- You need to establish rules, preferences, or domain knowledge the AI must always apply.
- You need the AI to know how to handle a category of requests without being explicitly triggered.
- Example: "Always format code review comments as GitHub Flavored Markdown."

**A Skill is NOT the right choice when:**
- You need the AI to perform a specific multi-step workflow on demand → use a **Protocol**.
- You need to generate consistent text output from a template → use a **Prompt**.
- You need a UI view the user can open → use an **Artifact**.
- You need to run code on the host machine → use a **Script**.

---

### Protocol

**A named, triggered workflow that the AI executes step by step when a specific phrase is spoken.**

A Protocol is dormant until its trigger phrase is matched. When triggered, the AI follows the protocol's steps exactly — it is a script for the AI, not for the machine. Protocols are the primary way users invoke the package's capabilities.

**File:** `components/protocols/<name>.md`  
**Trigger:** A natural-language phrase registered as a slash command, skill rule, or remembered instruction.  
**Aliases:** Additional phrases that activate the same protocol.

**A Protocol is the right choice when:**
- The user will say something specific and expect a defined sequence of actions.
- The workflow involves multiple steps, decisions, or tool calls.
- Example: "Move to code review" → creates a GitLab MR, posts to Teams, updates the inbox.

**A Protocol is NOT the right choice when:**
- The behavior should always be active, not triggered → use a **Skill**.
- You only need to generate a block of text from a template → use a **Prompt**.
- The logic is complex enough to require a real programming language → use a **Script** and call it from the protocol.

---

### Prompt

**A parameterized text template the AI fills in at runtime.**

A Prompt is a reusable text fragment with named variables. The AI substitutes `{{variable}}` placeholders with runtime values each time the prompt is invoked. Prompts are typically called from within a Protocol, not directly by the user.

**File:** `components/prompts/<name>.md`  
**Variables:** Runtime values, filled each time the prompt is used. Distinct from `{{config.*}}` values, which are set once at install time.

**A Prompt is the right choice when:**
- You need to generate consistent, structured text (a review comment, a summary, a report) with varying inputs.
- The template is reused across multiple protocols or invoked by name.
- Example: "Review summary" prompt takes `{{mr_title}}`, `{{reviewer}}`, `{{findings}}` and formats a comment.

**A Prompt is NOT the right choice when:**
- The behavior should always be active → use a **Skill**.
- The generation requires tool calls or conditional logic → put it in a **Protocol** step.
- The output is a UI view → use an **Artifact**.

---

### Artifact

**A persistent, interactive UI view the AI creates and the user can open and refresh.**

An Artifact is an HTML page (or its markdown equivalent) that the AI instantiates during installation and the user can revisit at any time. It does not run code on the host machine — it is a rendered view, not a script.

**Files:** `components/artifacts/<name>/artifact.html` (primary), `components/artifacts/<name>/artifact.md` (fallback)  
**Primary format:** Self-contained HTML, typically with embedded JavaScript that calls platform APIs or MCP tools to fetch live data.  
**Fallback:** A markdown file the AI maintains manually when the platform does not support HTML artifacts.

**An Artifact is the right choice when:**
- The user needs a persistent view they can return to between sessions (an inbox, a dashboard, a tracker).
- The view shows live data fetched from an MCP or external API.
- Example: "Review Inbox" showing all open MRs assigned to the user, refreshed on demand.

**An Artifact is NOT the right choice when:**
- The output is a one-time response generated during a protocol run → embed it in the protocol step.
- The view requires server-side logic or a database → use a hosted web service and link to it.
- The platform doesn't support HTML artifacts → use the markdown fallback pattern (the Artifact component still ships; it just degrades gracefully).

---

### Script

**Executable code that runs on the host machine.**

A Script is a file the AI copies to the user's machine and invokes using a shell command. Scripts can read and write the filesystem, call external APIs, run shell commands, and access the local environment. They are the boundary between the AI (which reasons and orchestrates) and the machine (which executes).

**Files:** `scripts/<key>.py` (cross-platform), `adapters/windows/scripts/<key>.ps1` (Windows-preferred)  
**Invoked by:** The AI, from within a Protocol step, using the script `key` — never a hardcoded path.  
**Trust levels (v1.2):** `read-only`, `network`, `write-local`, `shell-exec`.

**A Script is the right choice when:**
- You need to run code: call a REST API with complex auth, manipulate files, parse structured data, run a subprocess.
- The logic is too complex or stateful for the AI to reason through reliably in plain text.
- Example: `create_mr.py` — authenticates with GitLab, constructs the MR payload, handles errors.

**A Script is NOT the right choice when:**
- The action is simple enough for the AI to do directly via an MCP tool → use the MCP in the Protocol.
- The output is a UI view → use an **Artifact**.
- You need persistent AI behavior → use a **Skill**.

---

## Component Decision Table

When designing a new component, use this table:

| What I need | Component type |
|---|---|
| AI always behaves a certain way, no trigger required | **Skill** |
| User says a phrase → AI follows a defined sequence | **Protocol** |
| Reusable text template with runtime variables | **Prompt** |
| Persistent UI view the user can open and refresh | **Artifact** |
| Code that runs on the host machine | **Script** |
| Call a third-party API without complex auth or logic | MCP tool (in Protocol step, no Script needed) |
| Complex API call with auth, retries, or parsing | **Script** (called from Protocol) |
| One-time text output during a protocol run | Protocol step (no separate Prompt needed) |
| User-configurable values set once at install | Config key in manifest + `{{config.key}}` substitution |
| Values that change at runtime | `{{variable}}` in Prompt template |

**Common mistakes to avoid:**

- **Everything in a Skill.** If it requires a trigger, it's a Protocol. If it runs code, it's a Script. Skills should only contain always-on behavioral rules.
- **Protocols that are too long.** If a protocol step says "run this 50-line Python logic," extract it into a Script. Protocols orchestrate; Scripts execute.
- **Scripts for simple MCP calls.** If an MCP tool covers the action cleanly, use it directly in the Protocol step. Scripts add installation complexity — use them only when needed.
- **Artifacts for one-time output.** If the user will only see it once during a protocol run, put it in the protocol output. Artifacts are for views the user returns to.

---

## Platform Conventions

A3IP is platform-agnostic by design. The same bundle can be installed on Cowork, Claude Code, Codex, or any other AI platform. This section defines what "installed" concretely means on each supported platform — specifically where files go, how skills are registered, how scripts are invoked, and where `installed.json` lives.

These are conventions, not enforcement. The receiving AI adapts based on what platform it detects.

---

### Cowork

**Primary platform for knowledge workers. Full support for all A3IP component types.**

| Aspect | Convention |
|---|---|
| **Config directory** | `~/.claude/packages/<package-name>/` (or user-specified via `CONFIGURE.md`) |
| **Skills** | Copied to the workspace skills folder or registered as persistent instructions. Cowork loads them automatically at session start. |
| **Artifacts** | Created as Cowork artifacts (HTML). The AI instantiates the artifact from `artifact.html` and saves it. The user can open it from the artifact panel. |
| **Protocols** | Registered as slash commands or remembered instructions. The trigger phrase activates the protocol. |
| **Scripts** | Copied to the config directory. Invoked by the AI via the Bash tool: `python3 <config_dir>/scripts/<key>.py`. |
| **`installed.json`** | Written to `<config_dir>/installed.json`. |
| **Scheduled tasks** | Use Cowork's built-in scheduler. Reference the task by ID from protocols. |

---

### Claude Code

**Primary platform for developers. Full protocol support; artifacts degrade to markdown.**

| Aspect | Convention |
|---|---|
| **Config directory** | `~/.claude/packages/<package-name>/` (or user-specified) |
| **Skills** | Copied to `~/.claude/skills/` or loaded as project-level CLAUDE.md content. |
| **Artifacts** | HTML artifacts are not natively supported. Use `artifact.md` to maintain a markdown equivalent. The AI updates this file manually each time the relevant protocol runs. |
| **Protocols** | Registered as slash commands (if the platform supports them) or as CLAUDE.md instructions. The trigger phrase activates the protocol. |
| **Scripts** | Copied to the config directory. Invoked by the AI via Bash: `python3 <config_dir>/scripts/<key>.py`. |
| **`installed.json`** | Written to `<config_dir>/installed.json`. |
| **Scheduled tasks** | Use system cron (`crontab -e`) or a system scheduler. The AI writes the cron entry during install. |

---

### Codex

**OpenAI's coding agent. Full protocol and script support; some artifact limitations.**

| Aspect | Convention |
|---|---|
| **Config directory** | `~/.codex/packages/<package-name>/` (or user-specified) |
| **Skills** | Loaded as persistent system instructions or project-level context files. |
| **Artifacts** | Use `artifact.md` fallback. Codex does not natively render HTML artifacts. |
| **Protocols** | Registered as remembered instructions or project context. The trigger phrase activates the protocol. |
| **Scripts** | Copied to the config directory. Invoked via the code execution tool: `python3 <config_dir>/scripts/<key>.py`. |
| **`installed.json`** | Written to `<config_dir>/installed.json`. |
| **Scheduled tasks** | Use system cron or platform task runner. |

---

### Generic

**Any AI platform not listed above. Minimal assumptions; maximum portability.**

| Aspect | Convention |
|---|---|
| **Config directory** | Ask the user where to store package files. Default suggestion: `~/ai-packages/<package-name>/`. |
| **Skills** | Load SKILL.md content as a persistent instruction or paste into the system prompt. |
| **Artifacts** | Use `artifact.md` fallback. Maintain it as a markdown file the AI updates manually. |
| **Protocols** | Register as remembered instructions. The trigger phrase activates the protocol. |
| **Scripts** | Copy to the user-specified directory. Invoke via whatever code execution mechanism the platform provides, or ask the user to run them manually and paste output back. |
| **`installed.json`** | Write to the user-specified config directory. |
| **Scheduled tasks** | Document the schedule in INSTALL.md. Ask the user to set up the scheduler manually. |

---

### Detecting the platform

The AI installer detects the platform from context — it knows what platform it is running on. If uncertain, it should ask the user:

> "Which platform are you installing this on? (e.g. Cowork, Claude Code, Codex, or something else)"

The `platforms.tested` field in `manifest.yaml` lists platforms the author has verified. If the user's platform is not listed, the AI should proceed with the **Generic** conventions and note that this platform has not been tested by the author.

---

### `tested:` field in manifest

The `tested:` list under `platforms:` now has a precise meaning: the author has installed and verified the package on each listed platform using that platform's conventions above.

```yaml
platforms:
  tested:
    - cowork       # Verified: artifacts work, scripts invoke via Bash tool
    - claude-code  # Verified: artifact.md fallback, cron-based scheduling
    - codex        # Verified: artifact.md fallback, script invocation works
```

An AI installing on a platform not in `tested:` should warn the user:
> "This package has not been tested on [platform]. I'll install using generic conventions — some features may need manual adjustment."

---

## manifest.yaml, CONFIGURE.md, INSTALL.md, CHANGELOG.md, installed.json

*(Unchanged from v1.2.)*

---

## Component Formats

*(Unchanged from v1.0 — Skill, Artifact, Protocol, Prompt Template, Script formats are identical.)*

---

## Versioning

*(Unchanged from v1.2. Updated spec compatibility table below.)*

### Spec compatibility

| Spec version | Features added |
|---|---|
| `1.0` | Core: manifest, INSTALL.md, CONFIGURE.md, bundle format, `{{config.*}}` substitution |
| `1.1` | Versioning: CHANGELOG.md, installed.json, `## Upgrading` in INSTALL.md, `refresh:` on config keys, `min_a3ip_spec:`, `latest_change:` |
| `1.2` | Security: `trust_level:` on scripts, `permissions:` block, `## Plan` in INSTALL.md, `storage:` on sensitive config keys |
| `1.3` | Terminology: formal component definitions, decision table, platform adapter conventions |

---

## Design Principles

*(Unchanged from v1.2, with one addition.)*

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

---

*A3IP Specification v1.3*
*Supersedes v1.2. All v1.0, v1.1, and v1.2 packages remain valid under v1.3.*
*Released: 2026-05-12*
