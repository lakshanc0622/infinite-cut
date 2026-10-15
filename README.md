<div align="center">

<img src="assets/infinitecut-mark.png#gh-light-mode-only" alt="Infinite Cut" height="96">
<img src="assets/infinitecut-mark-dark.png#gh-dark-mode-only" alt="Infinite Cut" height="96">

**A free video editor that runs entirely on your own machine.**

[![Licence: AGPL-3.0-or-later](https://img.shields.io/badge/Licence-AGPL%20v3-8B2BFF?style=flat-square&logo=gnu&logoColor=F8F8F8&labelColor=212123)](LICENSE)
[![Version 0.2.7](https://img.shields.io/badge/Version-0.2.7-00D1C1?style=flat-square&logo=semver&logoColor=F8F8F8&labelColor=212123)](NOTICE.md)
[![Built on Concat](https://img.shields.io/badge/fork%20of-Concat-212123?style=flat-square&logo=github&logoColor=F8F8F8)](https://github.com/jub0t/concat)

</div>

---

Infinite Cut cuts video the way people actually use CapCut — captions,
voice-over, background removal, effects, multi-track trimming, 4K export —
with no watermark, no account, no subscription, and nothing uploaded
anywhere. Footage stays on the disk it is already on.

It is a fork of [Concat](https://github.com/jub0t/concat), rebuilt and
maintained under its own name by Infinite Minds Academy. See
[`NOTICE.md`](NOTICE.md) for what that means and what changed.

## What it does

| | |
|---|---|
| **Cut** | Split, trim, ripple, merge, freeze frame, speed. Multi-track, multi-timeline, magnetic if you want it. |
| **Captions** | Whisper runs locally. Pick a model size, get styled captions on the timeline. |
| **Voice** | Text-to-speech, voice cloning from a few seconds of a recording, denoise and loudness levelling. |
| **Cutout** | Remove the background from people and objects, or paint the mask yourself. |
| **Look** | 170+ GPU effects, filters, transitions and text animations, live in the preview. |
| **Keyframes** | Position, scale, rotation, opacity, volume and effect parameters, with a curve editor. |
| **Titles** | Fonts, stroke, shadow, background plate, presets. |
| **Export** | H.264, HEVC, AV1, up to 4K 60 at 10-bit. |
| **Scripting** | JSON-RPC, gRPC and MCP, plus a command line — scripts and agents can cut video with it. |

Everything runs on a native Rust engine with a GPU compositor. The AI models
download once from Settings and work offline afterwards.

## Running it

There are no prebuilt downloads yet — build it from source, which takes one
command once the prerequisites are in place. See [`BUILD.md`](BUILD.md), or
[`BUILD-SI.md`](BUILD-SI.md) for the same thing in Sinhala.

```sh
cd src
cargo run --release -p infinitecut
```

Supported: Windows, macOS, Linux, Android, and iOS when sideloaded. 25
interface languages.

## The code

`src/` is one Cargo workspace. The engine is split into crates by job —
`infinitecut-core`, `-media`, `-render`, `-export`, `-project` — with
`infinitecut-host` above them holding a session together, and `infinitecut`
itself being the editor window in Slint.

[`src/README.md`](src/README.md) explains how the crates fit together and
where the sharp edges are. [`ARCHITECTURE.md`](ARCHITECTURE.md) is the long
version. Both are upstream's, and both are worth reading before changing the
engine.

```
infinitecut → infinitecut-speech → infinitecut-host → {export, project, media} → core
```

## Licence

AGPL-3.0-or-later. Anyone you give a copy to is entitled to the source of
the version you gave them, under the same licence — including over a
network. [`LICENSE`](LICENSE), [`LICENSE-EXCEPTIONS.md`](LICENSE-EXCEPTIONS.md),
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

Infinite Cut is derived from Concat, © Jareer and the Concat contributors.
It is not Concat and is not endorsed by that project.
