# Windows development setup validation — 2026-10-21

- Exact AstroQuest source commit: 57650d2c5aeb09dda2689a2baad23396a9900c49 (0.23).
- Windows x64 Release, Clang/LLVM 20.1.8, CMake 4.4.4, Ninja 1.13.2.
- Portable Microsoft Windows SDK 10.0.26100 and CRT 14.44.17.14, prepared with xwin 0.10.0 in native winsysroot layout. SDK/CRT version selection was checked.
- OpenXR ON. Updater and Discord integration OFF. Release compiler probes avoid requiring debug runtime libraries.
- CMake configure and generation passed. Baseline compilation and linking completed (1,911 build steps).
- New executable responded to `--help` with exit code 0. No game or headset run was performed with the new binary.
- PowerShell build/preparation scripts and Python diagnostics passed syntax checks. Staged repository content was checked to contain only project text/scripts and no game/runtime assets.

Local source: Documents/Codex/HTL-Development/AstroQuest.
Local build: Documents/Codex/HTL-Development/build/win-x64/shadps4.exe.
Portable tools: Documents/Codex/DevTools/htl.

The working HTL-Test emulator has not been replaced. New builds have different hashes/addresses; old process-patching diagnostics must not be used on them. No social-screen rendering implementation has been added yet, and no overnight task has been started.

The saved Build-Emulator.ps1 was also executed successfully end to end. The resulting executable passed its command-line help check (exit 0). Resulting SHA256: 06733f887558f9eb9e9824f7bb41298f573a92b17dcf052d585e33d5118b388e.
