#!/usr/bin/env python3
"""Second pass: the things a blanket rewrite cannot get right.

Four kinds of fix:
  * compile-breaking — the gRPC service name became "Infinite Cut" (a Rust
    identifier with a space in it), and the workspace dependency on the
    root crate still pointed at crates/concat.
  * functionally wrong — the model mirror URL was rewritten to a repository
    that does not exist, the update feed still pointed at upstream's
    releases, and the Windows installer kept upstream's product GUIDs, so
    it would have upgraded over an installed Concat.
  * grammar — "a Infinite Cut", and inflected brand forms in de, hr and ko
    that a word-boundary match never saw.
  * provenance — packaging URLs that should name this fork, not upstream.

Usage: patch.py <tree>
"""

import os
import re
import sys
import uuid

REPO = "infinite-minds-academy/infinite-cut"
VENDOR = "Infinite Minds Academy"


def edit(path, pairs, *, required=True):
    """Apply (old, new) literal replacements to one file."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    for old, new in pairs:
        if old not in text:
            if required:
                raise SystemExit(f"NOT FOUND in {path}: {old!r}")
            continue
        text = text.replace(old, new)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"  patched {path}")


def main() -> int:
    root = sys.argv[1]
    j = lambda *p: os.path.join(root, *p)

    # ---- 1. gRPC: the service is an identifier, it cannot hold a space ---
    print("gRPC service name")
    proto_dir = j("src/crates/infinitecut-server/proto")
    old_proto = os.path.join(proto_dir, "concat.proto")
    new_proto = os.path.join(proto_dir, "infinitecut.proto")
    if os.path.exists(old_proto):
        os.rename(old_proto, new_proto)
    edit(new_proto, [
        ("package concat.v1;", "package infinitecut.v1;"),
        ("service Infinite Cut {", "service InfiniteCut {"),
    ])
    edit(j("src/crates/infinitecut-server/build.rs"), [
        ("proto/concat.proto", "proto/infinitecut.proto"),
        ('"concat.proto compiles"', '"infinitecut.proto compiles"'),
    ])
    # tonic derives the module name from the service name: InfiniteCut
    # snake-cases to infinite_cut, so the generated modules are
    # infinite_cut_server and infinite_cut_client.
    edit(j("src/crates/infinitecut-server/src/grpc.rs"), [
        ("`proto/concat.proto`", "`proto/infinitecut.proto`"),
        ('tonic::include_proto!("concat.v1")',
         'tonic::include_proto!("infinitecut.v1")'),
        ("use proto::infinitecut_server::{Infinite Cut, ConcatServer};",
         "use proto::infinite_cut_server::{InfiniteCut, InfiniteCutServer};"),
        ("impl Infinite Cut for Service", "impl InfiniteCut for Service"),
        ("ConcatServer::with_interceptor", "InfiniteCutServer::with_interceptor"),
        ("use proto::concat_client::ConcatClient;",
         "use proto::infinite_cut_client::InfiniteCutClient;"),
        ("ConcatClient::connect", "InfiniteCutClient::connect"),
    ])

    # ---- 2. the root crate's workspace dependency ------------------------
    print("workspace dependency")
    edit(j("src/Cargo.toml"), [
        ('concat = { path = "crates/concat" }',
         'infinitecut = { path = "crates/infinitecut" }'),
    ])

    # ---- 3. model mirror: upstream's releases really do serve these ------
    print("model mirror")
    edit(j("src/crates/infinitecut-host/src/models.rs"), [
        ('pub const REPO: &str = "jub0t/Infinite Cut";',
         '// The mirror is upstream Concat\'s own release assets, which is\n'
         '// where these model files actually live. Nominative use, and the\n'
         '// honest source: this fork hosts no mirror of its own. Point it at\n'
         '// your own release if you ever upload the same files.\n'
         'pub const REPO: &str = "jub0t/Concat";'),
        ("/// Where `file` is mirrored: Infinite Cut's own release.",
         "/// Where `file` is mirrored: the upstream project's release."),
        ("//! Every model Infinite Cut offers is mirrored onto a release of its own",
         "//! Every model Infinite Cut offers is mirrored onto an upstream release"),
    ], required=False)

    # ---- 4. updates: this fork's own releases ----------------------------
    print("update feed")
    edit(j("src/crates/infinitecut-host/src/updates.rs"), [
        ('"https://api.github.com/repos/jub0t/Infinite Cut/releases?per_page=100"',
         f'"https://api.github.com/repos/{REPO}/releases?per_page=100"'),
        ('format!("Infinite Cut/{}"', 'format!("InfiniteCut/{}"'),
    ])

    # ---- 5. Windows installer: new product identity ----------------------
    print("installer GUIDs and URLs")
    iss = j("assets/windows/infinitecut.iss")
    with open(iss, encoding="utf-8") as handle:
        text = handle.read()
    text = re.sub(r"AppId=\{\{[0-9A-Fa-f-]+\}",
                  "AppId={{" + str(uuid.uuid4()).upper() + "}", text)
    text = text.replace("AppPublisher=Infinite Cut contributors",
                        f"AppPublisher={VENDOR}")
    text = text.replace("https://github.com/jub0t/Concat",
                        f"https://github.com/{REPO}")
    text = text.replace("OutputBaseFilename=Infinite Cut-",
                        "OutputBaseFilename=InfiniteCut-")
    with open(iss, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"  patched {iss}")

    wxs = j("assets/windows/infinitecut.wxs")
    with open(wxs, encoding="utf-8") as handle:
        text = handle.read()
    text = re.sub(r'UpgradeCode="[0-9A-Fa-f-]+"',
                  f'UpgradeCode="{str(uuid.uuid4()).upper()}"', text)
    text = re.sub(r'(<Component Id="StartMenu"[^>]*Guid=")[0-9A-Fa-f-]+(")',
                  lambda m: m.group(1) + str(uuid.uuid4()).upper() + m.group(2),
                  text)
    text = text.replace("https://github.com/jub0t/Concat",
                        f"https://github.com/{REPO}")
    with open(wxs, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"  patched {wxs}")

    # ---- 6. the rest of the packaging ------------------------------------
    print("packaging metadata")
    for path, pairs in {
        j("assets/arch/PKGBUILD"): [
            ('url="https://github.com/jub0t/Concat"',
             f'url="https://github.com/{REPO}"')],
        j("assets/linux/nfpm.yaml"): [
            ("homepage: https://github.com/jub0t/Concat",
             f"homepage: https://github.com/{REPO}")],
        j("flake.nix"): [
            ('homepage = "https://github.com/jub0t/Concat"',
             f'homepage = "https://github.com/{REPO}"')],
        j(".github/workflows/build-app.yml"): [
            ("Exec=concat", "Exec=infinitecut"),
            ("Icon=concat", "Icon=infinitecut"),
            ("/opt/infinitecut/concat", "/opt/infinitecut/infinitecut"),
            ("^Exec=concat", "^Exec=infinitecut"),
        ],
    }.items():
        edit(path, pairs, required=False)

    # ---- 7. English grammar ----------------------------------------------
    print("locale grammar")
    en = j("src/crates/infinitecut/locales/en.json")
    edit(en, [("is not a Infinite Cut project folder",
               "is not an Infinite Cut project folder")], required=False)

    # ---- 8. inflected brand forms a \bConcat\b match never saw -----------
    edit(j("src/crates/infinitecut/locales/de.json"), [
        ("Concats Spiegel", "Infinite Cut Spiegel")], required=False)
    edit(j("src/crates/infinitecut/locales/hr.json"), [
        ("Concatov zrcalni poslužitelj", "Zrcalni poslužitelj Infinite Cuta"),
        ("Preuzimanje Concata", "Preuzimanje Infinite Cuta")], required=False)
    ko = j("src/crates/infinitecut/locales/ko.json")
    with open(ko, encoding="utf-8") as handle:
        text = handle.read()
    text = re.sub(r"Concat(?=[을이가는])", "Infinite Cut", text)
    with open(ko, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"  patched {ko}")

    # ---- 9. src/README.md, the one doc the rewrite half-missed -----------
    print("src/README.md")
    readme = j("src/README.md")
    with open(readme, encoding="utf-8") as handle:
        text = handle.read()
    text = text.replace("crates/concat/", "crates/infinitecut/")
    text = text.replace("proto/concat.proto", "proto/infinitecut.proto")
    text = text.replace("bin/concat", "bin/infinitecut")
    text = text.replace("`concat`", "`infinitecut`")
    text = text.replace("concat -> infinitecut-speech", "infinitecut -> infinitecut-speech")
    with open(readme, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"  patched {readme}")

    # ---- 10. upstream's own governance files do not apply here ----------
    print("removing upstream governance files")
    for name in ("CLA.md", "TRADEMARK.md"):
        path = j(name)
        if os.path.exists(path):
            os.remove(path)
            print(f"  removed {name}")

    print("\ndone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
