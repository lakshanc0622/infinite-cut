#!/usr/bin/env python3
"""Concat -> Infinite Cut rebrand.

Deliberately conservative. Three things are NEVER rewritten, because
rewriting them would be either unlawful, dishonest, or a bug:

  1. SPDX-FileCopyrightText lines. The AGPL requires upstream's copyright
     notices to survive in the fork. They stay verbatim.
  2. Links to github.com/jub0t/Concat. Those are real upstream issues that
     explain why the code is the way it is, plus the model mirror that
     actually serves the ONNX downloads. Pointing them elsewhere would make
     the comments lie and the downloads 404.
  3. Data identifiers: effect ids ("concat.mono", "concat.dissolve", ...),
     the concat! std macro, .concat() calls, and wgpu debug labels. Effect
     ids are written into saved project files and into every effect
     manifest; renaming them orphans the catalogue and breaks any project
     made with upstream builds. They are never shown to a user.

Everything a user can see or that carries product identity is rewritten.

Usage: rebrand.py <source-tree> <destination-tree>
"""

import os
import re
import shutil
import sys

DISPLAY = "Infinite Cut"      # what a human reads
SLUG = "infinitecut"          # crate / binary / file-name form
APP_ID = "online.aisolution.infinitecut"
VENDOR = "Infinite Minds Academy"
REPO = "infinite-minds-academy/infinite-cut"   # change when the repo exists

CRATES = [
    "core", "media", "project", "render", "export", "host", "api",
    "server", "speech", "effects", "text", "vision", "android", "cli",
]

SKIP_DIRS = {".git", "target", "node_modules"}
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".ico", ".icns", ".af", ".webp", ".gif",
    ".woff", ".woff2", ".ttf", ".otf", ".zip", ".pdf", ".onnx", ".bin",
}

# Lines matching any of these are copied through untouched.
PROTECTED_LINE = re.compile(
    r"SPDX-FileCopyrightText"
    r"|github\.com/jub0t/Concat"
    r"|github\.com/jub0t/concat"
    r"|crates\.io-index"
    r"|concat!\s*\("
    r"|\.concat\(\)"
    r"|label:\s*Some\(\"concat "
)

# Applied in order to every unprotected line.
RULES = [
    # --- identity -------------------------------------------------------
    (r"app\.concat\.editor", APP_ID),
    (r"app/concat/editor", APP_ID.replace(".", "/")),
    (r"\bConcatFiles\b", "InfiniteCutFiles"),

    # --- crate names ----------------------------------------------------
    (r"\bconcat-(" + "|".join(CRATES) + r")\b", SLUG + r"-\1"),
    (r"\bconcat_(" + "|".join(CRATES) + r")\b", SLUG + r"_\1"),

    # --- the root crate / binary ----------------------------------------
    (r"\bconcat::", SLUG + "::"),
    (r"\bconcat\.workspace\b", SLUG + ".workspace"),
    (r"\bprofile\.quick\.package\.concat\b", f"profile.quick.package.{SLUG}"),
    (r'(\bname\s*=\s*)"concat"', r'\1"' + SLUG + '"'),
    (r'("concat")(\s*:\s*")', '"' + SLUG + r'"\2'),
    (r"(-p|--package|--bin|\bbin)\s+concat\b", r"\1 " + SLUG),
    (r"\bconcat\.exe\b", SLUG + ".exe"),
    (r"\bconcat\.desktop\b", SLUG + ".desktop"),
    (r"\bconcat\.png\b", SLUG + ".png"),
    (r"\bconcat\.ico\b", SLUG + ".ico"),
    (r"\bconcat\.wxs\b", SLUG + ".wxs"),
    (r"\bconcat\.iss\b", SLUG + ".iss"),
    (r"/opt/concat\b", "/opt/" + SLUG),
    (r'"concat --', '"' + SLUG + " --"),
    (r"\bconcat --(version|smoke)\b", SLUG + r" --\1"),
    (r"\brun-concat\b", "run-" + SLUG),
    (r"\bconcat_logo", SLUG + "_logo"),
    (r"\bnew_concat_logo", "new_" + SLUG + "_logo"),
    (r"\bconcat-mark", SLUG + "-mark"),
    (r"\.concat-(video|audio|muxed)\b", "." + SLUG + r"-\1"),

    # --- display name ---------------------------------------------------
    # File-name shapes first, so they stay space-free.
    (r"\bConcat-(\d)", "InfiniteCut-" + r"\1"),
    (r"\bConcat\.app\b", "InfiniteCut.app"),
    (r"\bConcat/(\d)", "InfiniteCut/" + r"\1"),      # User-Agent
    (r"\bConcat\b", DISPLAY),
]

COMPILED = [(re.compile(p), r) for p, r in RULES]


def rename_path(path: str) -> str:
    """The destination name for one path component."""
    for crate in CRATES:
        if path == f"concat-{crate}":
            return f"{SLUG}-{crate}"
    if path == "concat":
        return SLUG
    out = path
    out = out.replace("ConcatFiles", "InfiniteCutFiles")
    out = re.sub(r"\bnew_concat_logo", "new_" + SLUG + "_logo", out)
    out = re.sub(r"\bconcat_logo", SLUG + "_logo", out)
    out = re.sub(r"\bconcat-mark", SLUG + "-mark", out)
    # Only real file extensions. `concat.adjust`, `concat.mono` and friends
    # are effect-package directories named by their effect id, which stays
    # as it is -- see the module docstring.
    out = re.sub(
        r"^concat\.(ico|wxs|iss|png|svg|desktop|exe|toml|json)$",
        SLUG + r".\1",
        out,
    )
    out = re.sub(r"^concat_", SLUG + "_", out)
    return out


def rewrite(text: str) -> tuple[str, int]:
    changed = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if PROTECTED_LINE.search(line):
            continue
        new = line
        for pattern, repl in COMPILED:
            new = pattern.sub(repl, new)
        if new != line:
            lines[i] = new
            changed += 1
    return "\n".join(lines), changed


def main() -> int:
    src, dst = sys.argv[1], sys.argv[2]
    if os.path.exists(dst):
        shutil.rmtree(dst)

    files = 0
    touched = 0
    lines_changed = 0
    renamed = []

    for root, dirs, names in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel = os.path.relpath(root, src)
        rel_out = os.sep.join(
            rename_path(p) for p in (rel.split(os.sep) if rel != "." else [])
        )
        out_dir = os.path.join(dst, rel_out) if rel_out else dst
        os.makedirs(out_dir, exist_ok=True)
        if rel != "." and rel_out != rel:
            renamed.append((rel, rel_out))

        for name in names:
            src_file = os.path.join(root, name)
            out_name = rename_path(name)
            out_file = os.path.join(out_dir, out_name)
            if out_name != name:
                renamed.append((os.path.join(rel, name), os.path.join(rel_out, out_name)))
            files += 1

            if os.path.splitext(name)[1].lower() in BINARY_EXT:
                shutil.copy2(src_file, out_file)
                continue
            try:
                text = open(src_file, encoding="utf-8").read()
            except (UnicodeDecodeError, ValueError):
                shutil.copy2(src_file, out_file)
                continue
            new_text, n = rewrite(text)
            if n:
                touched += 1
                lines_changed += n
            with open(out_file, "w", encoding="utf-8") as handle:
                handle.write(new_text)
            shutil.copystat(src_file, out_file)

    print(f"files seen       : {files}")
    print(f"files rewritten  : {touched}")
    print(f"lines rewritten  : {lines_changed}")
    print(f"paths renamed    : {len(renamed)}")
    for a, b in sorted(renamed)[:40]:
        print(f"  {a}  ->  {b}")
    if len(renamed) > 40:
        print(f"  ... and {len(renamed) - 40} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
