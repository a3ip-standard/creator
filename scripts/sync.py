#!/usr/bin/env python3
"""
A3IP Creator -- sync.py
Detects changes in a package directory since the last bundle.

Usage:
    python3 sync.py <package_dir>

Reads .a3ip-source.json from the package directory (written by bundle.py at
bundle time). Compares current file states against that baseline.

Reports:
  - Modified / added / deleted files
  - Suggested semver bump type (patch / minor / major) with reasoning
  - A ready-to-paste CHANGELOG '### Files changed' block

Writes .a3ip-sync-report.json into the package directory so that
new_version.py can consume it automatically to produce an accurate
CHANGELOG entry instead of placeholder TODOs.

Exit codes:
  0  success (changes found or no changes — check output)
  1  error (bad arguments, package dir not found, no baseline)
"""

import hashlib
import json
import sys
from pathlib import Path


# ── File collection (mirrors bundle.py logic) ─────────────────────────────────

def collect_files(pkg_dir):
    """Collect all non-hidden, non-pycache files in the package directory."""
    files = []
    for fpath in sorted(pkg_dir.rglob("*")):
        if not fpath.is_file():
            continue
        parts = fpath.relative_to(pkg_dir).parts
        if any(p.startswith(".") for p in parts):
            continue
        if "__pycache__" in parts:
            continue
        files.append(fpath)
    return files


def hash_file(fpath):
    h = hashlib.sha256()
    h.update(fpath.read_bytes())
    return "sha256:" + h.hexdigest()


# ── Bump type heuristics ───────────────────────────────────────────────────────

def suggest_bump(added, modified, deleted):
    """
    Suggest a semver bump type and explain why.
    Returns (bump_type, reasons) where bump_type is 'patch' | 'minor' | 'major'
    and reasons is a list of explanation strings.

    This is a heuristic — the author confirms the final decision.
    The rule of thumb:
      - Deletions of scripts or components → minor (potentially breaking → could be major)
      - manifest.yaml changed → minor (config/dependency additions are non-breaking;
        removals/renames are breaking → author should verify)
      - SKILL.md / protocol / prompt changed → minor (new behaviour)
      - Script or adapter changed (same interface assumed) → patch
      - Artifact changed → patch
      - Added scripts or components → minor
      - Docs/README/CHANGELOG only → patch
    """
    reasons = []
    bump = "patch"

    def upgrade(to, reason):
        nonlocal bump
        reasons.append(reason)
        if to == "major" or (to == "minor" and bump == "patch"):
            bump = to

    if not added and not modified and not deleted:
        return "none", []

    # Deletions
    for f in deleted:
        if any(seg in f for seg in ("scripts/", "components/", "adapters/")):
            upgrade("minor", f"'{f}' deleted — verify if this is a breaking removal (→ major)")
        else:
            upgrade("patch", f"'{f}' deleted")

    # Additions
    for f in added:
        if any(seg in f for seg in ("scripts/", "components/", "adapters/")):
            upgrade("minor", f"'{f}' added — new component")
        else:
            upgrade("patch", f"'{f}' added")

    # Modifications
    for f in modified:
        if f == "manifest.yaml":
            upgrade("minor", "manifest.yaml changed — check for config/dependency additions (minor) or removals/renames (major)")
        elif "SKILL.md" in f or "protocols/" in f or "prompts/" in f:
            upgrade("minor", f"'{f}' changed — behaviour or instructions updated")
        elif "scripts/" in f or "adapters/" in f:
            upgrade("patch", f"'{f}' changed — script updated (patch if interface unchanged)")
        elif "artifacts/" in f:
            upgrade("patch", f"'{f}' changed — artifact updated")
        elif f in ("INSTALL.md", "CONFIGURE.md"):
            upgrade("patch", f"'{f}' changed — install/config instructions updated")
        else:
            upgrade("patch", f"'{f}' changed")

    return bump, reasons


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 sync.py <package_dir>")
        print()
        print("Detects changes since the last bundle. Run bundle.py first to establish a baseline.")
        sys.exit(1)

    pkg_dir = Path(sys.argv[1])
    if not pkg_dir.is_dir():
        print(f"Error: '{pkg_dir}' is not a directory.")
        sys.exit(1)

    source_manifest_path = pkg_dir / ".a3ip-source.json"
    if not source_manifest_path.exists():
        print(f"No .a3ip-source.json found in {pkg_dir}")
        print()
        print("This file is written by bundle.py when a bundle is produced.")
        print("Run bundle.py first to establish a baseline, then make your changes,")
        print("then run sync.py to see what changed.")
        sys.exit(1)

    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    baseline_files = source_manifest["files"]
    baseline_version = source_manifest.get("version", "unknown")
    bundled_at = source_manifest.get("bundled_at", "unknown")
    package_name = source_manifest.get("package", pkg_dir.name)

    # Hash current state
    current_files = collect_files(pkg_dir)
    current_hashes = {}
    for fpath in current_files:
        rel = str(fpath.relative_to(pkg_dir)).replace("\\", "/")
        current_hashes[rel] = hash_file(fpath)

    # Compute diff
    baseline_set = set(baseline_files.keys())
    current_set = set(current_hashes.keys())

    added = sorted(current_set - baseline_set)
    deleted = sorted(baseline_set - current_set)
    modified = sorted(
        f for f in (current_set & baseline_set)
        if current_hashes[f] != baseline_files[f]
    )

    total = len(added) + len(modified) + len(deleted)

    # ── Output ────────────────────────────────────────────────────────────────

    print(f"\nSync: {package_name}  (baseline: v{baseline_version}, bundled {bundled_at})")
    print("─" * 60)

    if total == 0:
        print("No changes since last bundle.")
        print()
        print("Nothing to release. Make your changes, then run sync.py again.")
        return

    print(f"{total} file(s) changed — {len(modified)} modified, {len(added)} added, {len(deleted)} deleted")
    print()

    if modified:
        print("Modified:")
        for f in modified:
            print(f"  ~ {f}")
    if added:
        print("Added:")
        for f in added:
            print(f"  + {f}")
    if deleted:
        print("Deleted:")
        for f in deleted:
            print(f"  - {f}")

    bump_type, reasons = suggest_bump(added, modified, deleted)
    print()
    print(f"Suggested bump type: {bump_type.upper()}")
    for r in reasons:
        print(f"  · {r}")

    # Build CHANGELOG ### Files changed block
    changelog_lines = []
    for f in modified:
        changelog_lines.append(f"- `{f}` — replaced")
    for f in added:
        changelog_lines.append(f"- `{f}` — added")
    for f in deleted:
        changelog_lines.append(f"- `{f}` — deleted")

    print()
    print("### Files changed  (paste into CHANGELOG.md)")
    print("─" * 60)
    for line in changelog_lines:
        print(line)
    print("─" * 60)

    # Write .a3ip-sync-report.json for new_version.py to consume
    report = {
        "package": package_name,
        "baseline_version": baseline_version,
        "modified": modified,
        "added": added,
        "deleted": deleted,
        "suggested_bump_type": bump_type,
        "changelog_files_changed": changelog_lines,
    }
    report_path = pkg_dir / ".a3ip-sync-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print()
    print(f"Sync report written: .a3ip-sync-report.json")
    print("Run new_version.py to cut a release — it will read the report automatically.")
    print()
    print("Next:")
    print(f"  python3 new_version.py {pkg_dir} <new_version>")


if __name__ == "__main__":
    main()
