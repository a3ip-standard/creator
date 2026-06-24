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

## Recovery from path-expansion drift

If a tool you expected to be in the YES row above returns "file not found"
for a `~`-prefixed path, suspect that `~` may have expanded to the wrong
root before concluding the file is absent. The most common cause is the AI
reaching for `bash` first out of habit, where `~` resolves to the ephemeral
Linux sandbox home rather than `C:/Users/<user>/`.

Verification procedure:

1. Call `mcp__windows-cli` with shell `powershell` and the command
   `echo $env:USERPROFILE`. This prints the authoritative Windows user
   home — typically `C:/Users/<user>/` or the OneDrive-redirected variant.
2. Compare it to the root your first read used. If the two roots differ,
   path expansion is the cause of the "not found", not the file's
   absence.
3. Re-read from the corrected absolute path (substitute the verified
   `$env:USERPROFILE` for the leading `~`).

Do not conclude "the package is not installed" until step 2 has confirmed
that the lookup was against the right user-home root. This guards against
the failure mode where an installed package gets misreported as missing
purely because the AI's first tool choice expanded `~` to a sandbox path.
