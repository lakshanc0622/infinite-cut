# How the rebrand was done, and how to redo it

Upstream Concat keeps moving. When you want its newer work, you do not
hand-merge it into this tree — you re-run the rebrand against a fresh
upstream checkout and diff the result against your own changes. The scripts
in [`tools/rebrand/`](tools/rebrand) are what did it the first time, and they
are deterministic.

```sh
git clone --depth 1 https://github.com/jub0t/concat.git /tmp/concat
python3 tools/rebrand/rebrand.py /tmp/concat /tmp/infinite-cut
python3 tools/rebrand/patch.py   /tmp/infinite-cut
python3 tools/rebrand/patch2.py  /tmp/infinite-cut
python3 tools/rebrand/make_logo.py /tmp/infinite-cut
diff -ru /tmp/infinite-cut .      # your own work shows up as the difference
```

`patch.py` and `patch2.py` fail loudly if a string they expect has moved,
which is the point: a silent miss is how a fork ends up with a broken update
feed or a log file nobody writes to.

## What each script does

| Script | Job |
|---|---|
| `rebrand.py` | The bulk rewrite: crate names, directories, binaries, identifiers, locales, installers. Protects the lines that must not change. |
| `patch.py` | The things a blanket rewrite gets wrong: the gRPC service name, the workspace dependency, the model mirror, update feed, installer GUIDs, inflected brand words in German, Croatian and Korean. |
| `patch2.py` | Identifiers that are neither a crate name nor a word: `CONCAT_*` environment variables, the log file prefix, the log target filter, the Arch PKGBUILD. |
| `make_logo.py` | The mark, every icon size, the `.ico`, Android launcher densities, README wordmarks. |

## The four things that are never rewritten

1. **`SPDX-FileCopyrightText` lines.** Upstream's copyright notices. The
   AGPL requires they survive; rewriting them would be a licence violation,
   not a style choice.
2. **`github.com/jub0t/Concat` links.** Real upstream issues that explain
   why code looks the way it does, plus the release assets the AI models are
   actually downloaded from.
3. **Effect ids** — `concat.blur`, `concat.dissolve`, and 120 more. They are
   written into saved projects and into every effect package's manifest and
   directory name. Renaming them orphans the catalogue and breaks every
   project made in Concat. No user ever sees one.
4. **`concat.json`** — the project manifest filename, and the `concat`
   version field inside it. Keeping both means Infinite Cut opens Concat
   projects and Concat opens Infinite Cut projects.

## Things worth knowing when you change the branding again

**The gRPC service name is load-bearing.** `service InfiniteCut` in
`infinitecut.proto` generates `infinite_cut_server::{InfiniteCut,
InfiniteCutServer}` and `infinite_cut_client::InfiniteCutClient` — tonic
snake-cases the service name, so `InfiniteCut` becomes `infinite_cut`, not
`infinitecut`. `grpc.rs` has to match exactly.

**The log target filter.** `logs.rs` decides a line is the app's own by
asking whether its target starts with the crate prefix. Change the crate
prefix without changing that string and the app's own logs quietly stop
being written.

**Windows installer GUIDs.** `AppId` in the `.iss` and `UpgradeCode` in the
`.wxs` are the product's identity to Windows. Reusing upstream's means your
installer upgrades over — and uninstalls — an installed Concat.

**The app identifier is also the folder name.** `IDENTIFIER` in `dirs.rs`
names the settings and data directories on every platform. Changing it
strands existing users' settings, recents and downloaded models.

## What was verified, and what was not

Verified here: all 15 workspace manifests resolve; `infinitecut-core`,
`-project`, `-effects` and `-text` compile clean; the generated gRPC module
and type names match what `grpc.rs` imports; all 26 locale files parse; every
effect package's directory name still matches the `id` in its manifest.

Not verified here: a full build. `infinitecut-media` needs FFmpeg 7 headers
and `infinitecut-speech` downloads an ONNX Runtime binary, neither of which
was available in the machine this was prepared on. Both are environment, not
code — see [`BUILD.md`](BUILD.md).
