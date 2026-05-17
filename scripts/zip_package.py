#!/usr/bin/env python3
"""
A3IP Creator — zip_package.py
Generates a .a3ip.zip file from a package directory.

Usage:
    python3 zip_package.py <package_dir> [output_path]

If output_path is omitted, the zip is written next to the package directory
as <name>.a3ip.zip.
"""

import sys
import zipfile
from pathlib import Path


def get_package_name(pkg_dir: Path) -> str:
    name = pkg_dir.name
    if name.endswith(".a3ip"):
        name = name[:-5]
    return name


def build_zip(pkg_dir: Path, output_path: Path) -> int:
    """Generate the .a3ip.zip file. Returns total file count."""
    file_count = 0
    pkg_name = pkg_dir.name  # e.g. "my-workflow.a3ip"

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fpath in sorted(pkg_dir.rglob("*")):
            if not fpath.is_file():
                continue
            parts = fpath.relative_to(pkg_dir).parts
            if any(p.startswith(".") for p in parts):
                continue
            if "__pycache__" in parts:
                continue

            # Archive path includes package folder name at root
            arcname = f"{pkg_name}/{'/'.join(parts)}"
            zf.write(fpath, arcname)
            file_count += 1

    return file_count


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 zip_package.py <package_dir> [output_path]")
        sys.exit(1)

    pkg_dir = Path(sys.argv[1])
    if not pkg_dir.is_dir():
        print(f"Error: '{pkg_dir}' is not a directory.")
        sys.exit(1)

    name = get_package_name(pkg_dir)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = pkg_dir.parent / f"{name}.a3ip.zip"

    print(f"Building zip: {pkg_dir} → {output_path}")

    file_count = build_zip(pkg_dir, output_path)
    size_kb = output_path.stat().st_size / 1024

    print(f"✅ Zip created: {output_path}")
    print(f"   Files: {file_count}")
    print(f"   Size:  {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
