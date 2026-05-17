---
name: cut-version
trigger: "cut a new version"
aliases:
  - "bump the version"
  - "release a new version"
  - "new release"
---

## What this protocol does

Cuts a new package version: bumps manifest, prepends changelog entry, validates, and rebundles.

## Steps

1. Run script sync on the package directory to detect what changed since the last bundle.
2. Review the sync output with the user — confirm the suggested bump type (patch/minor/major).
3. Determine the new version number (semver) and confirm with the user.
4. Run script new_version with the package directory and new version number.
   (It reads the sync report automatically and populates ### Files changed.)
5. Fill in the remaining changelog entry fields: Summary, Upgrade steps, Breaking changes.
6. Apply any remaining file changes the version describes.
7. Run script validate and fix any errors.
8. Run script bundle to produce the updated distributable bundle and reset the baseline.

## Outputs

- Updated `manifest.yaml` (bumped version)
- Updated `CHANGELOG.md` (new version entry prepended)
- New `.a3ip.bundle` file
- Reset `.a3ip-source.json` baseline for the next sync
