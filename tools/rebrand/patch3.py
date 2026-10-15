#!/usr/bin/env python3
"""Fourth pass: the space in "Infinite Cut" is not safe everywhere.

Upstream's name was one word, so the build scripts use it unquoted in
places where a two-word name breaks outright:

    iconset=Infinite Cut.iconset          -> "Cut.iconset: command not found"
    hdiutil create -volname Infinite Cut  -> -srcfolder eats the wrong argument
    signtool /d Infinite Cut              -> the description swallows the path

So: file, bundle and artifact names lose the space and become InfiniteCut;
names a person reads (the .desktop entry, CFBundleDisplayName, the Inno
Setup display names, permission prompts) keep it, and the two places a
display name sits on a command line get quoted.

Also here: packaging metadata that still carried upstream's maintainer
address, the Linux package installing the binary under its old name, and
the model script pointing at a repository that does not exist.

Usage: patch3.py <tree>
"""

import os
import re
import sys

WORKFLOWS_AND_SCRIPTS = (".yml", ".yaml", ".sh", ".ps1", ".py", ".md")


def main() -> int:
    root = sys.argv[1]
    changed = []

    def edit(rel, pairs, *, regex=False):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            print(f"  (absent) {rel}")
            return
        text = open(path, encoding="utf-8").read()
        before = text
        for old, new in pairs:
            text = re.sub(old, new, text) if regex else text.replace(old, new)
        if text != before:
            open(path, "w", encoding="utf-8").write(text)
            changed.append(rel)

    # --- 1. file and bundle names lose the space -------------------------
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", "target"}]
        for name in names:
            if not name.endswith(WORKFLOWS_AND_SCRIPTS):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            if rel.startswith(("NOTICE", "README", "BUILD", "REBRAND",
                               "CONTRIBUTING", "TRADEMARK", "SECURITY",
                               "ARCHITECTURE", "tools/")):
                continue
            text = open(path, encoding="utf-8").read()
            before = text
            # "Infinite Cut-0.2.7-windows-x86_64" and friends.
            text = text.replace("Infinite Cut-", "InfiniteCut-")
            # Bundles and intermediate folders.
            for suffix in (".AppDir", ".iconset", ".icns", ".app", ".dmg"):
                text = text.replace(f"Infinite Cut{suffix}", f"InfiniteCut{suffix}")
            if text != before:
                open(path, "w", encoding="utf-8").write(text)
                changed.append(rel)

    # --- 2. the two display names that sit on a command line -------------
    edit(".github/workflows/build-app.yml", [
        ("hdiutil create -volname Infinite Cut -srcfolder",
         'hdiutil create -volname "Infinite Cut" -srcfolder'),
        ("/td SHA256 /d Infinite Cut $file.FullName",
         '/td SHA256 /d "Infinite Cut" $file.FullName'),
        ("/td SHA256 /d Infinite Cut $file",
         '/td SHA256 /d "Infinite Cut" $file'),
    ])

    # --- 3. the Android smoke test greps for the logcat tag --------------
    edit("scripts/ci/smoke-android.sh", [
        (r" concat \+:", " infinitecut +:"),
    ], regex=True)

    # --- 4. the model script's mirror, which is upstream's releases ------
    edit("scripts/models.py", [
        ('REPO = "jub0t/Infinite Cut"',
         '# Upstream Concat\'s releases: where these model files actually\n'
         '# live. This fork hosts no mirror of its own.\nREPO = "jub0t/Concat"'),
    ])

    # --- 5. Linux packaging: maintainer, vendor, the binary's name -------
    edit("assets/linux/nfpm.yaml", [
        ("maintainer: Infinite Cut contributors <jub0trd@gmail.com>",
         "maintainer: Infinite Minds Academy"),
        ("vendor: Infinite Cut contributors", "vendor: Infinite Minds Academy"),
        ("dst: /opt/infinitecut/concat", "dst: /opt/infinitecut/infinitecut"),
    ])

    # --- 6. the MSI's manufacturer ---------------------------------------
    edit("assets/windows/infinitecut.wxs", [
        ('Manufacturer="Infinite Cut contributors"',
         'Manufacturer="Infinite Minds Academy"'),
    ])

    # --- 7. upstream's screenshot SOP, for artwork no longer here --------
    sop = os.path.join(root, "scripts/editor-preview-sop.md")
    if os.path.exists(sop):
        os.remove(sop)
        print("  removed scripts/editor-preview-sop.md")

    for rel in sorted(set(changed)):
        print(f"  patched {rel}")
    print(f"\n{len(set(changed))} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
