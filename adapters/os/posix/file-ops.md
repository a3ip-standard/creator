# POSIX (macOS / Linux) file operations -- tool selection

This adapter governs filesystem operations on a POSIX host.

## Tool selection for `~`-prefixed paths

On POSIX, `~` is the user's home. Most tools handle it natively:

| Tool | `~` expansion |
|---|---|
| Python `os.path.expanduser('~')` | YES |
| Shell `$HOME` | YES |
| `mcp__filesystem` if available | YES |

No special precautions needed.

## Persistent locations

`~/.claude/packages/<name>/` (Cowork / Claude Code) or
`~/.codex/packages/<name>/` (Codex).
