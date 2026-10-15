#!/usr/bin/env python3
"""Audit the rebranded tree. Usage: audit.py <upstream> <tree>"""

import json
import os
import re
import subprocess
import sys

CRATES = ["core", "media", "project", "render", "export", "host", "api",
          "server", "speech", "effects", "text", "vision", "android", "cli"]

fails: list[str] = []
notes: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" â€” {detail}" if detail else ""))
    if not ok:
        fails.append(name)


def walk(root: str):
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", "target", "node_modules"}]
        for name in names:
            yield os.path.join(dirpath, name)


def text_files(root: str):
    for path in walk(root):
        if os.path.splitext(path)[1].lower() in {
            ".png", ".ico", ".jpg", ".af", ".woff", ".woff2", ".ttf", ".otf",
            ".onnx", ".bin", ".zip",
        }:
            continue
        try:
            yield path, open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, ValueError, IsADirectoryError):
            continue


def main() -> int:
    upstream, tree = sys.argv[1], sys.argv[2]

    print("\nBuild integrity")
    stale = [
        f"{os.path.relpath(p, tree)}:{i}"
        for p, t in text_files(tree)
        for i, line in enumerate(t.split("\n"), 1)
        if re.search(r"\bconcat[-_](" + "|".join(CRATES) + r")\b", line)
        and "SPDX-FileCopyrightText" not in line
    ]
    check("no stale crate references", not stale, "; ".join(stale[:3]))

    bad_ident = [
        f"{os.path.relpath(p, tree)}:{i}"
        for p, t in text_files(tree)
        if p.endswith((".rs", ".slint", ".proto"))
        for i, line in enumerate(t.split("\n"), 1)
        if "Infinite Cut" in line and '"' not in line and "//" not in line
    ]
    check("no spaced brand name in code positions", not bad_ident, "; ".join(bad_ident[:3]))

    meta = subprocess.run(
        ["cargo", "metadata", "--no-deps", "--offline", "--format-version", "1"],
        cwd=os.path.join(tree, "src"), capture_output=True, text=True,
        env={**os.environ, "RUSTUP_TOOLCHAIN": "stable-x86_64-unknown-linux-gnu"},
    )
    names = sorted(p["name"] for p in json.loads(meta.stdout)["packages"]) if meta.returncode == 0 else []
    check("workspace resolves, 15 crates", len(names) == 15, f"{len(names)} found")
    check("every crate is infinitecut*",
          all(n == "infinitecut" or n.startswith("infinitecut-") for n in names))

    print("\nLicence compliance")
    def spdx(root: str) -> int:
        return sum(t.count("SPDX-FileCopyrightText") for _, t in text_files(root))
    before, after = spdx(upstream), spdx(tree)
    check("upstream copyright notices kept", after >= before * 0.9,
          f"{after} of {before} (files were removed, so fewer is expected)")
    kept = [
        n for n in ("LICENSE", "LICENSE-EXCEPTIONS.md", "THIRD_PARTY_NOTICES.md", "NOTICE.md")
        if os.path.exists(os.path.join(tree, n))
    ]
    check("licence files present", len(kept) == 4, ", ".join(kept))
    with open(os.path.join(tree, "LICENSE"), encoding="utf-8") as handle:
        check("LICENSE is still the AGPL", "AFFERO GENERAL PUBLIC LICENSE" in handle.read())

    print("\nData compatibility")
    packages = os.path.join(tree, "src/crates/infinitecut-effects/packages")
    mismatched = []
    for entry in sorted(os.listdir(packages)):
        folder = os.path.join(packages, entry)
        if not os.path.isdir(folder):
            continue
        for item in os.listdir(folder):
            if item.endswith(".toml"):
                found = re.search(r'^id\s*=\s*"([^"]+)"',
                                  open(os.path.join(folder, item), encoding="utf-8").read(), re.M)
                if found and found.group(1) != entry:
                    mismatched.append(entry)
    check("effect ids match their directories", not mismatched,
          f"{len(os.listdir(packages))} packages")
    manifest = open(os.path.join(tree, "src/crates/infinitecut-host/src/projects.rs"),
                    encoding="utf-8").read()
    check("project manifest is still concat.json", 'const MANIFEST: &str = "concat.json"' in manifest)

    print("\nUser-facing strings")
    locales = os.path.join(tree, "src/crates/infinitecut/locales")
    leftover, unparsed = [], []
    for name in sorted(os.listdir(locales)):
        try:
            data = json.load(open(os.path.join(locales, name), encoding="utf-8"))
        except Exception as error:
            unparsed.append(f"{name}: {error}")
            continue
        leftover += [f"{name}:{k}" for k, v in data.items()
                     if isinstance(v, str) and re.search(r"Concat\w*", v)]
    check("all 26 locales parse", not unparsed, "; ".join(unparsed[:2]))
    check("no old brand left in any translation", not leftover, "; ".join(leftover[:3]))

    print("\nIdentity")
    dirs_rs = open(os.path.join(tree, "src/crates/infinitecut-host/src/dirs.rs"), encoding="utf-8").read()
    check("app identifier is its own",
          'IDENTIFIER: &str = "online.aisolution.infinitecut"' in dirs_rs)
    logs = open(os.path.join(tree, "src/crates/infinitecut-host/src/logs.rs"), encoding="utf-8").read()
    check("log target filter matches the crates",
          'target.starts_with("infinitecut")' in logs)
    iss = open(os.path.join(tree, "assets/windows/infinitecut.iss"), encoding="utf-8").read()
    check("Windows AppId is not upstream's",
          "7B1E5C3A-3B9E-4F0B-9C6D-2F1D0C0A0C47" not in iss)
    wxs = open(os.path.join(tree, "assets/windows/infinitecut.wxs"), encoding="utf-8").read()
    check("MSI UpgradeCode is not upstream's",
          "6C4D5D8E-9B2A-4F3B-8E1C-5A7D2B9F0C11" not in wxs)
    updates = open(os.path.join(tree, "src/crates/infinitecut-host/src/updates.rs"), encoding="utf-8").read()
    check("update feed points at this fork",
          "api.github.com/repos/lakshanc0622/infinite-cut" in updates)

    print("\nAssets and links")
    referenced = [
        "assets/icons/infinitecut.ico", "assets/icons/infinitecut_logo_256.png",
        "assets/icons/infinitecut_logo_512.png", "assets/icons/infinitecut_logo_16.png",
        "assets/infinitecut_logo_512.png", "assets/infinitecut-mark.png",
        "assets/infinitecut-mark-dark.png",
        "src/crates/infinitecut-android/res/mipmap-xxxhdpi/ic_launcher.png",
        "assets/new_infinitecut_logo_512_rounded_light_theme.svg",
    ]
    missing = [r for r in referenced if not os.path.exists(os.path.join(tree, r))]
    check("every referenced icon exists", not missing, "; ".join(missing))

    broken = []
    for path, body in text_files(tree):
        if not path.endswith(".md"):
            continue
        here = os.path.dirname(path)
        for target in re.findall(r"\]\((?!https?:|#|mailto:)([^)#\s]+)", body):
            if not os.path.exists(os.path.normpath(os.path.join(here, target))):
                broken.append(f"{os.path.relpath(path, tree)} -> {target}")
    check("no markdown link points at a removed file", not broken, "; ".join(broken[:4]))

    print("\n" + ("ALL CHECKS PASSED" if not fails else f"{len(fails)} FAILED: " + ", ".join(fails)))
    for note in notes:
        print("  note:", note)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
