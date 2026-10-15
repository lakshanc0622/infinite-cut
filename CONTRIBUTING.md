# Contributing to Infinite Cut

Infinite Cut is a video editor that runs entirely on the user's own machine.
It gets better mostly through people editing real footage with it and saying
where it broke.

## The most useful thing you can do

Build it ([`BUILD.md`](BUILD.md)) and cut something real with it. Real
footage finds what reading the source never does. A good report — what you
did, what happened, your OS, the media you used — is worth more than most
patches.

## Before writing code

Open an issue first for anything beyond a small fix, so the work is not
duplicated or aimed at a part of the engine that is being rewritten anyway.

## Setting up

Rust (the version pinned in `src/rust-toolchain.toml`), the FFmpeg 7+
development libraries, cmake, and a C++ compiler. Then:

```sh
cd src && cargo run -p infinitecut
```

That is the editor window. The engine, the host layer and the Slint
interface are one Cargo workspace under `src/`.

| Path | What lives there |
|---|---|
| `src/crates/infinitecut-core` | Time, frames, the data the rest agrees on |
| `src/crates/infinitecut-media` | Pixels and samples in and out of files; the only crate that knows FFmpeg exists |
| `src/crates/infinitecut-project` | The document model, commands, undo, `concat.json` IO |
| `src/crates/infinitecut-render` | The compositor, CPU and GPU |
| `src/crates/infinitecut-export` | Encoding a timeline to a file |
| `src/crates/infinitecut-host` | A session held together: playback, jobs, models, logs |
| `src/crates/infinitecut-api` | One dispatcher every transport calls |
| `src/crates/infinitecut-cli` | The command line and the daemon |
| `src/crates/infinitecut` | The editor window, in Slint |

[`src/README.md`](src/README.md) explains how they fit together and where
the sharp edges are. Read it before touching the engine.

## Checks

```sh
cd src && cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test
```

If you changed text the interface shows, run `python3 scripts/locales.py` so
the string inventory follows — CI checks it. Translations are one JSON file
per language; see [`TRANSLATING.md`](TRANSLATING.md).

If you added a downloadable model, add it to
[`models/manifest.toml`](models/manifest.toml) and run
`python3 scripts/models.py --check`.

Write what happens through the `log` facade rather than to standard output:
a packaged build has no terminal. `INFINITECUT_LOG=debug` turns the level up.

## Licence

Infinite Cut is AGPL-3.0-or-later, and contributions are accepted under that
licence. There is no contributor licence agreement and no copyright
assignment — your commits stay yours.

Please do not paste in code whose licence you have not checked. Anything
derived from a GPL-incompatible source cannot go in, however small.

## Where this came from

Infinite Cut is a fork of [Concat](https://github.com/jub0t/concat). If a
bug you have found also happens in Concat, upstream is the better place for
it — they wrote most of this, and a fix there reaches both projects. See
[`NOTICE.md`](NOTICE.md).
