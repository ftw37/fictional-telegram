# Here They Lie — PSVR compatibility investigation

Development tools, reproducible build instructions and diagnostic experiments for running a personally supplied copy of Here They Lie through AstroQuest/shadPS4, ultimately on a Quest 2 via Virtual Desktop.

**Status (October 24):** the usual local launchers now use the isolated official shadPS4 0.20-based candidate. Three consecutive warm-cache New Game-to-platform routes passed, with clear checked views and mostly 60 FPS car sections. Loading/arrival dips and a presentation-validation warning remain; physical Quest playback is unverified. See the [measured report](docs/COMPREHENSIVE-RUN-2026-10-24.md) and [current build instructions](INTEGRATION-020.md).

## Current and earlier build workflows

Use `scripts/Build-Integration020.ps1` and `upstream-020.lock.json` for the current candidate. The steps below preserve the earlier AstroQuest-based build workflow for comparison. Normal launchers select the tested isolated profile; the old executable/profile remain available.

PowerShell scripts default to portable tools in `Documents/Codex/DevTools/htl`, source in `Documents/Codex/HTL-Development/AstroQuest`, and a separate build in `Documents/Codex/HTL-Development/build/win-x64`.

1. `./scripts/Prepare-Toolchain.ps1` downloads pinned portable Git, CMake, Ninja, LLVM and the Windows SDK/runtime libraries. It verifies archive hashes, uses the SDK's Windows layout, and accepts the Microsoft SDK license for these development tools. No system PATH changes or full Visual Studio IDE are required.
2. `./scripts/Get-EmulatorSource.ps1` obtains the public source revision in `upstream.lock.json` and the dependencies needed for Windows.
3. `./scripts/Apply-CompatibilityPatch.ps1` applies our source changes at that exact revision, checking for conflicts first.
4. `./scripts/Build-Emulator.ps1` configures and builds a Release emulator with OpenXR enabled. `-ConfigureOnly` checks configuration; `-Jobs 8` controls build parallelism.

The build is separate from the original working emulator. Its addresses and hash differ, so the existing hard-coded diagnostic adapters must NOT be used with a rebuilt binary; their hash checks deliberately refuse it. The new `scripts/launch_here_they_lie.py` enables the source compatibility options directly. It expects a locally prepared `HTL-Development/test-vr` runtime and the user's extracted game; it does not copy game modules or install an emulator automatically.

## Existing experiments

`diagnostics/` contains the temporary tracker-ABI adapters, flat launcher, original four-view launcher, per-eye sampling experiment and crash observer. They default to `Documents/Codex/HTL-Test`; set `HTL_TEST_ROOT` to use a different local test installation. Launch helpers expect these diagnostics to be copied into that installation's `tools` folder before use.

The experimental sampling hook is process-local and restricted to the verified AstroQuest 0.23 executable. Two runs with it enabled before New Game crashed at the known guest loading trap; a control loaded, and applying the patch after reaching the subway worked during observation. Causation remains unproven. See `docs/HTL-Eye-Sampling-Test-Notes.md`.

## Social screen findings

The original matching source recognized the social-screen port but skipped presenting it. Our source patch adds a separate native window and routes dedicated social-port frames when available. Here They Lie has not opened that port in observed runs, so its second window currently displays an explicitly labelled synthetic crop of the left eye. That crop is not claimed to reproduce Sony's social output exactly.

The TV preview window is off by default. Add `--tv-preview` to the source launcher to enable it. Current transition-flicker isolation and its validation limits are recorded in `docs/TRANSITION-RENDERING.md`; `scripts/Test-TextureExtent.ps1` runs the mip/layer containment regression checks.

Goal: one TV/social window (identify actual game output versus a synthetic crop), plus one window showing the two headset eyes. Preserve WASD/Q/E controls, smooth turning and the no-vignette variant. The flat `-nohmd` mode is a reference, not evidence that a separate TV output already works.

## Boundaries and provenance

Only our scripts, text findings, build instructions and upstream references belong here. Game packages, extracted binaries, Sony modules, keys, saves, screenshots, render dumps, toolchains and built executables stay outside Git. No game files are distributed.

AstroQuest and shadPS4 are upstream GPL-2.0-or-later projects; see the pinned upstream LICENSE and THIRD-PARTY-NOTICES.md before distributing a modified build. Upstream source and dependency licenses are retained in the separate checkout.

The overnight investigation was explicitly authorized on 22 October 2026. Scripts remain manual launch/build tools; they do not create scheduled jobs.

Performance investigation and optional faster graphics mode: [measurements and limits](docs/PERFORMANCE.md). Native 90 FPS remains unverified.
