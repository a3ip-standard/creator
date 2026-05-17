# Windows file operations -- tool selection

This adapter governs filesystem operations on a Windows host. Other axes (AI
runtime) live in `adapters/runtime/<name>/`.

## Tool selection for `~`-prefixed paths

On Windows, `~` is the user's home (typically `C:/Users/<user>/`). Different
tools handle `~` differently:

| Tool | `~` expansion on Windows |
|---|---|
| `mcp__filesystem__read_file` / `__write_file` | YES |
| Windows-native Python `os.path.expanduser('~')` | YES |
| Cowork bash sandbox | NO -- resolves to ephemeral Linux sandbox home |
| Read tool (raw `~/...`) | NO |

**Rule:** for reading/writing persistent files at `~`-prefixed paths on a
Windows host, use a YES-row tool.

## Persistent locations

`C:/Users/<user>/.claude/packages/<name>/` (Cowork / Claude Code) or
`C:/Users/<user>/.codex/packages/<name>/` (Codex).
