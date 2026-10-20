# Devil Crash MD â€” Windows development project

Windows x64 player with Xbox controller support and game-specific native instruction specialization. Genesis Plus GX provides the hardware compatibility layer. This is not a recovered high-level rewrite of the game's physics.

## Source and setup

`DevilCrash-source.zip` contains the complete compatibility/player source, instruction generator, pinned build settings, licenses, and validation records. Extract it into this folder before building. The main player and build files are also available directly under `source/` for browsing.

The commercial cartridge image is **not included**. Supply your own matching `game.md` beside this README. Required SHA256:

`9e9734a2904d61d27585496edad830e329dd6bfe4e5859c11535532046d07262`

Install Python 3.10+ and Zig 0.17.0, and make `python` and `zig` available in your command window. No third-party Python packages are required. From this folder:

```
python source/build.py --zig zig --jobs 2
```

Builds need several GB of free RAM. `Build-and-check.cmd` shows the build output live, saves `build-log.txt`, and runs the self-test after a successful build. If the tools are not on PATH, set `DEVIL_PYTHON` and `DEVIL_ZIG` to their executable paths first.

The build creates `DevilCrash.exe` and `devil-native.dll`. Keep them beside `game.md` to play. Build caches, debug symbols, generated instruction code, compiled binaries, and the cartridge are excluded from Git.

## Controls

Enter starts; Z/X/C map to Genesis A/B/C; arrows move; P pauses; F5 resets; F11 toggles fullscreen; Escape exits. Xbox X/A/B map to Genesis A/B/C, Menu starts, D-pad/left stick move, LB/LT also map to A, and RB/RT also map to C.

## Verification

On October 20, 2026, a Windows rebuild completed and its 1,800-frame self-test matched the reference:

```
video_fnv64=b0b1283c528accec
audio_fnv64=35754a014bf0e099
native_instructions=20712440
```

This checks the exercised replay, not every possible game state. Earlier agent-launched builds failed with cache-renaming or LLD errors; launching the build script manually in the normal Windows session succeeded.

## Provenance and licenses

Compatibility runtime: Genesis Plus GX revision `393f70cd64c7334564c19a424c383f53986c13f4`. Preserve the included LICENSE files and individual source notices. Its upstream noncommercial and component license terms apply. No rights to the original game or assets are granted.
