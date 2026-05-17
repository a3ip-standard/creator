#!/usr/bin/env python3
"""
A3IP Creator -- new_version.py
Cuts a new package version: bumps manifest.yaml, prepends a CHANGELOG.md entry.

Run sync.py first to auto-populate the '### Files changed' section.

Usage:
    python3 new_version.py <package_dir> <new_version>

Example:
    python3 new_version.py ./my-workflow.a3ip 1.1.0
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def bump_manifest(pkg_dir: Path, new_version: str) -> str:
    """Update version: and latest_change: in manifest.yaml. Returns old version."""
    manifest_path = pkg_dir / "manifest.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.yaml not found in {pkg_dir}")

    text = manifest_path.read_text(encoding="utf-8")

    # Extract old version
    old_version = "unknown"
    m = re.search(r'^version:\s*["\']?([^"\'\\n]+)["\']?', text, re.MULTILINE)
    if m:
        old_version = m.group(1).strip()

    # Replace version:
    text = re.sub(
        r'^(version:\s*)["\']?[^"\'\\n]+["\']?',
        f'version: "{new_version}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )

    # Replace or add latest_change:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if re.search(r'^latest_change:', text, re.MULTILINE):
        text = re.sub(
            r'^latest_change:.*',
            f'latest_change: {today}',
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        text = re.sub(
            r'^(version:.*)',
            rf'\1\nlatest_change: {today}',
            text,
            count=1,
            flags=re.MULTILINE,
        )

    manifest_path.write_text(text, encoding="utf-8")
    print(f"  updated  manifest.yaml  (version: {old_version} -> {new_version})")
    return old_version


def load_sync_report(pkg_dir: Path):
    """Load .a3ip-sync-report.json if present. Returns dict or None."""
    report_path = pkg_dir / ".a3ip-sync-report.json"
    if report_path.exists():
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def consume_sync_report(pkg_dir):
    """Read the sync report, attempt to delete it, and return it. Returns None if absent."""
    report_path = pkg_dir / ".a3ip-sync-report.json"
    if not report_path.exists():
        return None
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    try:
        report_path.unlink()
    except Exception:
        pass  # Cannot delete (permissions) -- not fatal; report is already read
    return report


def prepend_changelog(pkg_dir: Path, new_version: str) -> str:
    """Prepend a changelog entry for new_version. Returns the entry text.

    If .a3ip-sync-report.json exists in the package directory, its file list
    is used to populate '### Files changed' automatically. The report is
    consumed (deleted) after reading so it is not accidentally reused.
    """
    changelog_path = pkg_dir / "CHANGELOG.md"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    sync = consume_sync_report(pkg_dir)

    # manifest.yaml and CHANGELOG.md are always modified by new_version.py itself,
    # so they appear in every release regardless of what sync.py detected.
    always_changed = (
        "- `manifest.yaml` — bumped\n"
        "- `CHANGELOG.md` — replaced"
    )

    if sync and sync.get("changelog_files_changed"):
        sync_files = "\n".join(sync["changelog_files_changed"])
        files_changed_block = always_changed + "\n" + sync_files
        files_changed_note = ""
    else:
        files_changed_block = (
            always_changed + "\n"
            "TODO: List every other file that changed.\n"
            "Format: `path/to/file.ext` — replaced | added | deleted"
        )
        files_changed_note = (
            "\n*(Run sync.py before new_version.py to auto-populate this section.)*"
        )

    entry = (
        f"## {new_version}\n\n"
        f"*Released: {today}*\n\n"
        "### Summary\n\n"
        "TODO: Describe what changed in this version and why.\n\n"
        "### Upgrade steps\n\n"
        "TODO: Write concise INSTALL.md-style steps for only what changed.\n"
        "For example:\n"
        "- Replace `components/artifacts/<name>/artifact.html` with the new version.\n"
        "- Re-register the artifact in your platform.\n\n"
        "*(If nothing requires active upgrade steps, write: "
        '"No action required -- non-breaking update.")*\n\n'
        "### Breaking changes\n\n"
        "TODO: List any breaking changes. For each one, state:\n"
        "- What was renamed, removed, or added\n"
        "- What the AI must do (re-ask config wizard for affected keys, re-copy scripts, etc.)\n\n"
        '*(If none, write: "None.")*\n\n'
        "### Files changed\n\n"
        f"{files_changed_block}{files_changed_note}\n\n"
    )

    if changelog_path.exists():
        existing = changelog_path.read_text(encoding="utf-8")
        lines = existing.splitlines(keepends=True)
        in_frontmatter = False
        header_end = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                if i == 0:
                    in_frontmatter = True
                    continue
                elif in_frontmatter:
                    in_frontmatter = False
                    header_end = i + 1
                    break

        first_version_line = None
        for i in range(header_end, len(lines)):
            if lines[i].startswith("## "):
                first_version_line = i
                break

        if first_version_line is not None:
            new_content = (
                "".join(lines[:first_version_line])
                + "---\n\n"
                + entry
                + "".join(lines[first_version_line:])
            )
        else:
            new_content = existing.rstrip("\n") + "\n\n---\n\n" + entry

        changelog_path.write_text(new_content, encoding="utf-8")
        print(f"  updated  CHANGELOG.md  (prepended entry for {new_version})")
    else:
        header = (
            "---\n"
            'format: a3ip-changelog\n'
            'spec: "1.1"\n'
            "---\n\n"
            "# Changelog\n\n"
            "New version entries go at the **top** of this file (newest first).\n\n"
            "---\n\n"
        )
        changelog_path.write_text(header + entry, encoding="utf-8")
        print(f"  created  CHANGELOG.md  (first entry: {new_version})")

    return entry


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 new_version.py <package_dir> <new_version>")
        print()
        print("Example: python3 new_version.py ./my-workflow.a3ip 1.1.0")
        print()
        print("Tip: run sync.py first to auto-populate '### Files changed'.")
        sys.exit(1)

    pkg_dir = Path(sys.argv[1])
    new_version = sys.argv[2]

    if not pkg_dir.is_dir():
        print(f"Error: '{pkg_dir}' is not a directory.")
        sys.exit(1)

    if not re.match(r'^\d+\.\d+(\.\d+)?$', new_version):
        print(f"Error: '{new_version}' is not a valid version (expected x.y or x.y.z).")
        sys.exit(1)

    print(f"\nCutting version {new_version} for: {pkg_dir}\n")

    # Surface sync report info before proceeding
    sync = load_sync_report(pkg_dir)
    if sync:
        suggested = sync.get("suggested_bump_type", "").upper()
        n_changed = (
            len(sync.get("modified", []))
            + len(sync.get("added", []))
            + len(sync.get("deleted", []))
        )
        print(f"  sync report found: {n_changed} file(s) changed since last bundle")
        if suggested:
            print(f"  suggested bump type: {suggested}")
        print("  '### Files changed' will be auto-populated from the sync report")
        print()

    old_version = bump_manifest(pkg_dir, new_version)
    entry = prepend_changelog(pkg_dir, new_version)

    print()
    print(f"Version bumped: {old_version} -> {new_version}")
    print()
    print("CHANGELOG.md entry added (fill in the TODOs):")
    print("-" * 60)
    print(entry)
    print("-" * 60)
    print()
    print("Next steps:")
    print("  1. Edit CHANGELOG.md -- fill in the Summary, Upgrade steps, Breaking changes")
    print("     (### Files changed is already populated if sync.py was run first)")
    print("  2. Make the actual file changes the version describes")
    print("  3. Run validate.py to check for errors")
    print("  4. Run bundle.py to generate the updated distributable bundle")


if __name__ == "__main__":
    main()
