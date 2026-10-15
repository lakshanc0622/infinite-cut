# Building Infinite Cut

One command, once four prerequisites are installed. The long pole is the
first build: the engine, Skia and whisper.cpp come to about 900 crates, and
on a laptop that is 20–40 minutes. Later builds are seconds.

Sinhala version: [`BUILD-SI.md`](BUILD-SI.md).

---

## Windows

### 1. Rust

<https://rustup.rs> → run `rustup-init.exe` → press Enter for the default.
The repository pins the compiler in `src/rust-toolchain.toml`, so rustup
fetches the right one by itself the first time you build.

### 2. Visual Studio Build Tools

Needed for the C++ compiler and cmake that whisper.cpp builds with.

<https://visualstudio.microsoft.com/visual-cpp-build-tools/> → in the
installer tick **Desktop development with C++**. The default selection in
that workload is enough; it includes cmake.

### 3. FFmpeg 7 development libraries

Windows has no package for these, so unpack them by hand:

1. Download a **shared** build from
   <https://github.com/BtbN/FFmpeg-Builds/releases> —
   `ffmpeg-n7.x-latest-win64-gpl-shared-7.x.zip`. The word **shared**
   matters; the `lgpl` and non-shared builds have no headers.
2. Unpack it somewhere permanent, e.g. `C:\ffmpeg`. You should end up with
   `C:\ffmpeg\bin`, `C:\ffmpeg\include` and `C:\ffmpeg\lib`.
3. Tell the build where it is, in PowerShell:

```powershell
setx FFMPEG_DIR "C:\ffmpeg"
setx PATH "$env:PATH;C:\ffmpeg\bin"
```

Close the terminal and open a new one — `setx` only affects new ones.

### 4. Build

```powershell
cd infinite-cut\src
cargo run --release -p infinitecut
```

The window opens when it finishes. For the binary on its own:

```powershell
cargo build --profile app -p infinitecut
```

It lands in `src\target\app\infinitecut.exe`. That exe needs the FFmpeg DLLs
from `C:\ffmpeg\bin` beside it (or on PATH) to run on another machine.

---

## macOS

```sh
brew install ffmpeg cmake
cd infinite-cut/src
cargo run --release -p infinitecut
```

Rust from <https://rustup.rs>, Xcode command line tools via `xcode-select --install`.

## Linux

Debian and Ubuntu, where the packaged FFmpeg is 7 or newer:

```sh
sudo apt install build-essential cmake pkg-config \
  libavcodec-dev libavformat-dev libavutil-dev libavfilter-dev \
  libavdevice-dev libswscale-dev libswresample-dev \
  libfontconfig-dev libfreetype-dev libxkbcommon-dev
cd infinite-cut/src
cargo run --release -p infinitecut
```

On Ubuntu 24.04 the packaged FFmpeg is 6.1 and the build will stop with
`no field decoded_side_data on type AVCodecContext`. That is the version, not
the code: unpack a BtbN FFmpeg 7 build and point `FFMPEG_DIR` at it, exactly
as on Windows.

With Nix, everything is pinned already:

```sh
nix build          # then ./result/bin/infinitecut
nix develop        # a shell with the toolchain and libraries
```

---

## The installers

`.github/workflows/build-app.yml` builds every platform's package in CI —
the Windows setup and `.msi`, the macOS `.dmg`, the Linux `.deb`, `.rpm`,
`.AppImage` and Arch package. Push a tag and it runs.

Building the Windows installer locally needs
[Inno Setup](https://jrsoftware.org/isdl.php); the script is
`assets/windows/infinitecut.iss`.

## Android

```sh
cargo install cargo-apk
scripts/ffmpeg-mobile.sh      # cross-builds FFmpeg, once, slow
scripts/sherpa-mobile.sh      # fetches the speech runtime
cd src && cargo apk build -p infinitecut-android
```

Needs the Android SDK and NDK, with `ANDROID_HOME` and `ANDROID_NDK_HOME` set.

## Checks

```sh
cd src
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
```

## When something fails

**`libavutil not found` / `FFMPEG_DIR`** — step 3. The path must be the
folder that *contains* `include` and `lib`, not `lib` itself.

**`no field decoded_side_data`** — the FFmpeg found is older than 7.

**`link.exe not found`** on Windows — the C++ workload in step 2 is missing.

**Skia takes forever on the first build** — it is downloading prebuilt
binaries. Let it.

**`error: failed to download` on `rust-toolchain`** — no network, or a proxy.
`rustup toolchain install` the pinned version by hand, or set
`RUSTUP_TOOLCHAIN=stable` to build with whatever is installed; anything from
1.93 upwards works.
