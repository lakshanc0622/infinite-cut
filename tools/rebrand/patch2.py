#!/usr/bin/env python3
"""Third pass: the identifiers that are neither a crate name nor a word.

The important one is logs.rs. It decides whether a log line belongs to the
app by asking whether its target starts with "concat" -- and after the
rename every target starts with "infinitecut", so the app's own lines would
have been treated as a dependency's and dropped from the log file. A silent
one, and only findable by reading.

The rest: environment variables the user types (CONCAT_LOG,
CONCAT_API_TOKEN), the ones CI sets, the log file's own name, and the Arch
PKGBUILD, which names the binary half a dozen times in positions no pattern
caught.

Usage: patch2.py <tree>
"""

import os
import re
import sys

SKIP_DIRS = {".git", "target", "node_modules"}
TEXT_EXT = {
    ".rs", ".toml", ".md", ".yml", ".yaml", ".sh", ".ps1", ".py", ".json",
    ".slint", ".proto", ".nix", ".iss", ".wxs", ".desktop", ".java", "",
}


def main() -> int:
    root = sys.argv[1]
    changed = []

    # --- 1. the log target filter, and the log file's name ---------------
    logs = os.path.join(root, "src/crates/infinitecut-host/src/logs.rs")
    with open(logs, encoding="utf-8") as handle:
        text = handle.read()
    before = text
    text = text.replace('target.starts_with("concat")',
                        'target.starts_with("infinitecut")')
    if text == before:
        raise SystemExit("logs.rs: the target filter was not where it was")
    with open(logs, "w", encoding="utf-8") as handle:
        handle.write(text)
    print("  logs.rs: own() now recognises infinitecut* targets")

    # --- 2. everything else, file by file --------------------------------
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            path = os.path.join(dirpath, name)
            if os.path.splitext(name)[1].lower() not in TEXT_EXT:
                continue
            try:
                text = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, ValueError):
                continue
            original = text

            # Environment variables the user or CI sets.
            text = re.sub(r"\bCONCAT_", "INFINITECUT_", text)

            # Log and scratch file names: "concat-2026…log", "concat-lut-…".
            if name.endswith(".rs"):
                text = re.sub(r'(["/])concat-', r"\1infinitecut-", text)

            if text != original:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(text)
                changed.append(os.path.relpath(path, root))

    # --- 3. the Arch package, which names the binary everywhere ----------
    pkgbuild = os.path.join(root, "assets/arch/PKGBUILD")
    with open(pkgbuild, encoding="utf-8") as handle:
        text = handle.read()
    text = re.sub(r"(?<![\w./-])concat(?![\w.-])", "infinitecut", text)
    text = text.replace("/opt/infinitecut/concat", "/opt/infinitecut/infinitecut")
    text = text.replace("licenses/concat/", "licenses/infinitecut/")
    text = text.replace('"$stage/concat"', '"$stage/infinitecut"')
    with open(pkgbuild, "w", encoding="utf-8") as handle:
        handle.write(text)
    changed.append("assets/arch/PKGBUILD")

    for path in sorted(set(changed)):
        print(f"  patched {path}")
    print(f"\n{len(set(changed))} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
