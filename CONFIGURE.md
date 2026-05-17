---
format: a3ip-configure
spec: "1.6"
package: a3ip-creator
---

# Configuration Wizard: a3ip-creator

You are setting up the a3ip-creator skill. Ask the question below.
Collect the value before moving to installation.

## Before Installation — ask this first

---

### 1. Installation directory
Ask:
> "Where should I install a3ip-creator's state and metadata? The default is
> `~/.claude/packages/a3ip-creator/` on Cowork and Claude Code (matches the
> spec convention). On Codex, the convention is
> `~/.codex/packages/a3ip-creator/`. Press enter to accept the default for your
> platform."

- Key: `install_dir`
- Type: string
- Required: yes
- Default: `~/.claude/packages/a3ip-creator/` (Cowork / Claude Code)
- This is where `installed.json` will live. The install detection in
  INSTALL.md Step 1 looks for `installed.json` here on fresh sessions.

## Confirmation

Before proceeding to installation, confirm:

---
Here's what I'll configure:

- **Installation directory**: {{config.install_dir}}

Shall I proceed with installation?
---

Wait for explicit confirmation before moving to INSTALL.md.
