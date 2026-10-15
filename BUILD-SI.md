# Infinite Cut — Build කරන හැටි (සිංහල)

පියවර 4ක්. මුල්ම build එකට විනාඩි 20–40ක් යනවා (crates 900ක් පමණ compile
වෙනවා). ඊට පස්සේ තත්පර ගණනයි.

English: [`BUILD.md`](BUILD.md).

---

## Windows

### පියවර 1 — Rust install කරන්න

<https://rustup.rs> → `rustup-init.exe` download කරලා run කරන්න → Enter ගහන්න
(default එක හරි).

Compiler version එක `src/rust-toolchain.toml` එකේ pin කරලා තියෙනවා, ඒ නිසා
හරි version එක rustup විසින්ම ගන්නවා.

### පියවර 2 — Visual Studio Build Tools

C++ compiler එකයි cmake එකයි ඕනේ (whisper.cpp build කරන්න).

<https://visualstudio.microsoft.com/visual-cpp-build-tools/> → installer එකේ
**Desktop development with C++** කියන එක tick කරන්න. Default selection එක
ඇති — cmake එකත් ඒකේ තියෙනවා.

### පියවර 3 — FFmpeg 7 development libraries

Windows එකට මේකට package එකක් නෑ, manually දාන්න ඕනේ:

1. <https://github.com/BtbN/FFmpeg-Builds/releases> එකෙන්
   **shared** build එකක් download කරන්න —
   `ffmpeg-n7.x-latest-win64-gpl-shared-7.x.zip`.
   **shared** කියන වචනේ වැදගත් — `lgpl` හෝ shared නැති builds වල headers නෑ.
2. `C:\ffmpeg` වගේ permanent තැනකට unzip කරන්න. ඇතුළේ `bin`, `include`,
   `lib` කියන folders 3 තියෙන්න ඕනේ.
3. PowerShell එකේ මේක run කරන්න:

```powershell
setx FFMPEG_DIR "C:\ffmpeg"
setx PATH "$env:PATH;C:\ffmpeg\bin"
```

ඊට පස්සේ terminal එක close කරලා **අලුත් එකක්** open කරන්න — `setx` වැඩ කරන්නේ
අලුත් terminal වලට විතරයි.

### පියවර 4 — Build කරන්න

```powershell
cd infinite-cut\src
cargo run --release -p infinitecut
```

ඉවර වුණාම window එක open වෙනවා.

Binary එක විතරක් ඕනේ නම්:

```powershell
cargo build --profile app -p infinitecut
```

ඒක එන්නේ `src\target\app\infinitecut.exe` එකට. වෙන machine එකක run කරන්න නම්
`C:\ffmpeg\bin` එකේ DLL files ඒ exe එක ළඟ තියෙන්න ඕනේ (නැත්නම් PATH එකේ).

---

## macOS

```sh
brew install ffmpeg cmake
cd infinite-cut/src
cargo run --release -p infinitecut
```

Rust — <https://rustup.rs>. Xcode tools — `xcode-select --install`.

## Linux (Ubuntu / Debian)

```sh
sudo apt install build-essential cmake pkg-config \
  libavcodec-dev libavformat-dev libavutil-dev libavfilter-dev \
  libavdevice-dev libswscale-dev libswresample-dev \
  libfontconfig-dev libfreetype-dev libxkbcommon-dev
cd infinite-cut/src
cargo run --release -p infinitecut
```

Ubuntu 24.04 එකේ FFmpeg 6.1 නිසා build එක
`no field decoded_side_data` කියලා නවතිනවා. ඒක code එකේ ප්‍රශ්නයක් නෙවෙයි —
version එකේ. Windows වලදී වගේ BtbN FFmpeg 7 build එකක් දාලා `FFMPEG_DIR`
point කරන්න.

---

## Installer එක හදන්න

`.github/workflows/build-app.yml` එක හැම platform එකකටම package හදනවා
(Windows setup + `.msi`, macOS `.dmg`, Linux `.deb`/`.rpm`/`.AppImage`,
Arch package). GitHub එකට tag එකක් push කළාම ඒක run වෙනවා.

Windows installer එක locally හදන්න [Inno Setup](https://jrsoftware.org/isdl.php)
ඕනේ. Script එක: `assets/windows/infinitecut.iss`.

---

## Error එකක් ආවොත්

**`libavutil not found` / `FFMPEG_DIR`** — පියවර 3 බලන්න. Path එක
`include` සහ `lib` **තියෙන** folder එක වෙන්න ඕනේ, `lib` එක නෙවෙයි.

**`no field decoded_side_data`** — FFmpeg version එක 7ට වඩා පරණයි.

**`link.exe not found`** — පියවර 2 (C++ workload එක) නැහැ.

**Skia download එක ගොඩක් වෙලා යනවා** — ඒක normal, prebuilt binaries
download වෙනවා. ඉන්න දෙන්න.

**`failed to download` rust-toolchain** — network/proxy ප්‍රශ්නයක්.
`RUSTUP_TOOLCHAIN=stable` දාලා build කරන්න පුළුවන් — 1.93ට වඩා අලුත් ඕනම
version එකක් වැඩ කරනවා.

---

## මතක තියාගන්න ඕනේ දේවල්

- **Licence එක AGPL-3.0.** Infinite Cut කාටහරි දුන්නොත් (installer එකක්
  විදිහට හෝ network එකක් හරහා), ඒ අයට source code එකත් ඒම licence එකේ
  ඉල්ලන්න අයිතියක් තියෙනවා. Closed source කරන්න බෑ.
- **Credit එක තියාගන්න ඕනේ.** මේක [Concat](https://github.com/jub0t/concat)
  (Jareer / @jub0t) ගේ වැඩේ උඩ හැදිච්ච fork එකක්. විස්තර [`NOTICE.md`](NOTICE.md)
  එකේ.
- **Concat කියන නමයි logo එකයි පාවිච්චි කරන්න බෑ** — ඒවා licence එකෙන්
  එන්නේ නෑ. ඒකයි අලුත් නමයි අලුත් logo එකයි. (Upstream එකම ඉල්ලන්නේ ඒක තමයි.)
