# Run Here They Lie on another Windows PC

This is an experimental Windows source build, not a native Quest app. Read [current status](PROJECT-STATUS-2026-10-26.md). These instructions follow the checked-in scripts and working local layout; a clean-machine installation has not yet been tested end to end.

## Prerequisites

- Windows x64, Vulkan-capable GPU and suitable graphics driver; performance depends on hardware. No minimum specification or sustained 60/90 FPS guarantee is established.
- Git, Python 3, PowerShell, internet access, and substantial free disk space for tools, dependencies, build and game (potentially tens of GB beyond game files). Normal launching needs no third-party Python packages.
- Your own extracted PS4 Here They Lie game. Tested release: **CUSA05344, version 01.00**. A PKG alone is not launchable by this helper. Game extraction and any required console files are local prerequisites, not automated here. Preserve `eboot.bin`, `sce_sys`, `sce_module` and content in their original extracted layout.
- For VR: Quest 2 with Virtual Desktop, Virtual Desktop Streamer on the PC and SteamVR. Monitor preview needs neither headset nor SteamVR.

No game, Sony modules, keys, firmware, saves or emulator binaries are distributed. The tested game's `sce_module` includes libc, AudioLatencyEstimation, Face/FaceTracker, Fios2, Hand/HandTracker, HeadTracker, JobManager, NpToolkit, S3DConversion and Smart PRX modules. This inventory does not prove every module is required. Supply your own local files; don't copy another person's private runtime profile.

## 1. Clone and build

In PowerShell, choose your paths. The tool preparation script downloads pinned tools and accepts Microsoft's development SDK license. It does not change system PATH permanently.

```powershell
git clone https://github.com/ftw37/fictional-telegram.git
Set-Location .\fictional-telegram\here-they-lie
$repo = (Get-Location).Path
$dev = "$HOME\Documents\Codex\HTL-Development"
$tools = "$HOME\Documents\Codex\DevTools\htl"
$python = (Get-Command python.exe -ErrorAction Stop).Source
& $python --version
.\scripts\Prepare-Toolchain.ps1 -ToolsRoot $tools
.\scripts\Build-Integration020.ps1 -DevelopmentRoot $dev -ToolsRoot $tools -Python $python -Jobs 8
```

Replace `$python` with the real executable path if Windows resolves a Store alias. Review/unblock scripts according to your machine's PowerShell policy if necessary. The build uses pinned official shadPS4 and AstroQuest/OpenXR donor revisions; do not blindly substitute latest upstream. `-ConfigureOnly` checks configuration without compiling.

### Optional experimental Quest candidate

For the latest exact builds, physical retest evidence and feature flags, read [RESUME-HERE](RESUME-HERE.md). The latest Quest candidate has a user-confirmed upright image and a battery-limited crash-free retest, not full-game qualification.

The baseline above contains the verified audio/rendering work. The additional Quest patch contains the loading-assertion fix, initial-pose hypothesis and crash diagnostics. Earlier startup gates failed; the current full-reference fix has now been physically verified upright. Longer crash stability remains unqualified. Prefer a separate development root to retain a baseline.

```powershell
. .\scripts\Enter-BuildEnvironment.ps1 -ToolsRoot $tools
$questPatch = Join-Path $repo 'patches\htl-quest-startup-copyfix.patch'
git -C "$dev\integration-020" apply --check $questPatch
# Continue only if the check succeeds; never apply twice.
git -C "$dev\integration-020" apply $questPatch
cmake --build "$dev\build\integration-020" --target shadps4 --parallel 8
```

Apply after the baseline patch/build. Subsequent rebuilds use the explicit cmake command: the baseline script may reject an already modified experimental checkout rather than force conflicting patches. Keep a copy of the baseline executable before installing an experimental one.

## 2. Prepare a fresh runtime

These commands copy settings into a new profile. Back up existing personal settings instead of overwriting them.

```powershell
$runtime = Join-Path $dev 'test-vr'
New-Item -ItemType Directory -Force "$runtime\user\input_config" | Out-Null
Copy-Item "$dev\build\integration-020\shadps4.exe" "$runtime\shadps4.exe"
Copy-Item .\examples\config.json "$runtime\user\config.json"
Copy-Item .\examples\default.ini "$runtime\user\input_config\default.ini"
$game = 'D:\Games\HereTheyLie\uroot'  # replace with your extracted game
Test-Path "$game\eboot.bin"          # must print True
```

Examples contain settings only, not accounts/keys/saves. They retain GPU command copies, relaxed readbacks (`GPU.readbacks_mode=1`), pipeline cache, background controller input, 1920x1080 internal output, validation off and startup volume 20%. Disabling readbacks caused corruption in earlier tests. The tested executable is statically linked; resolve any reported missing dependency specifically rather than mixing DLLs from unrelated builds. Let the bridge obtain your headset's FOV; don't copy the developer's cached FOV file.

The launcher temporarily writes `ue4commandline.txt` in the game directory and restores it on normal exit. Keep that folder writable. If forcibly terminated, inspect `$dev\launcher-commandline-recovery.json` before the next run.

### Optional no-turn-vignette variant

This script supports one checked asset signature and refuses unknown versions. Destination must be new and on the same filesystem supporting hard links. Large game files are linked to the original: neither copy is an independent backup, so avoid modifying linked files afterward.

```powershell
& $python .\scripts\build_no_turn_vignette.py --source $game --destination 'D:\Games\HereTheyLie\no-vignette-uroot'
$game = 'D:\Games\HereTheyLie\no-vignette-uroot'
```

## 3. Start on the monitor

```powershell
& $python .\scripts\launch_here_they_lie.py --development-root $dev --game $game --mode preview --renderer-sync pass --real-occlusion
```

Preview shows stereo eyes and theatre-style flat splash/loading screens with FPS. TV preview defaults off; add `--tv-preview` for a labelled synthetic left-eye crop. `--mode flat` is a non-HMD reference. Avoid diagnostic `--fast-graphics`, profiling and recording during normal performance checks.

Connect an Xbox controller before launch. Hold **Menu** for about two seconds when calibration asks for OPTIONS. Enter is also mapped; focus the game window. Xbox A/B/X/Y map to PS4 Cross/Circle/Square/Triangle; LB/RB to L1/R1, LT/RT to L2/R2, stick clicks to L3/R3 and View to touchpad click. WASD moves, Q/E turns, N/B/V/C map to Cross/Circle/Square/Triangle, O is R2, Space touchpad. See [Xbox notes](XBOX-CONTROLLER-2026-10-25.md) and [Quest mappings](QUEST-CONTROLS.md). Turning follows the game's selected smooth-turn settings.

Use the launcher: running an old executable directly may omit required compatibility settings. Start with low device volume; Windows/headset volume is separate from the 20% game setting.

## 4. Quest 2 via Virtual Desktop / SteamVR

1. Add the appropriate account in Virtual Desktop Streamer, following the headset app's account instructions. First establish that the headset can discover this PC and show its desktop.
2. Start SteamVR through Virtual Desktop, complete any room setup and verify tracking in its ordinary environment. Select SteamVR as the OpenXR runtime.
3. Wear/recenter the headset. In the same PowerShell session, clear any private test-runtime override and select your installed SteamVR manifest:

```powershell
Remove-Item Env:VR_PATHREG_OVERRIDE -ErrorAction SilentlyContinue
$env:SHADPS4_HTL_LEAF_FRAME = '1' # latest Quest patch only; enable its exact-function stack fix
$env:XR_RUNTIME_JSON = 'C:\Program Files (x86)\Steam\steamapps\common\SteamVR\steamxr_win64.json'
Test-Path $env:XR_RUNTIME_JSON  # must print True; adjust if Steam is elsewhere
& $python .\scripts\launch_here_they_lie.py --development-root $dev --game $game --mode quest --renderer-sync pass --real-occlusion
```

Quest mode enables OpenXR tracking, Touch mappings, theatre transitions and automatic calibration; Xbox input is also available. The latest candidate admits tracked poses regardless of roll and uses a full initial reference basis. Broad `General.redzone_patches` remains false; the separate `SHADPS4_HTL_LEAF_FRAME=1` enables the exact-function stack reservation. The old upright-pose gate caused black/head-locked output and must not be restored. Don't force a global texture flip: gameplay tracking/orientation worked in the previous physical run.

Source eyes are approximately 960x1080 each, lower than Quest 2 panels; expect softness. Full FOV/comfort validation remains open. Virtual Desktop Synchronous Spacewarp is an optional headset-side experiment (for example 90 Hz / 45 FPS source), not a qualified performance solution for this game.

For a double-click launcher, put the relevant command in a local `.cmd` using full Python/script/game/development paths; include the runtime variables for Quest mode. Don't copy the original developer's absolute-path shortcuts unchanged. `Install-CandidateLaunchers.ps1` is an internal acceptance-gated deployment tool, not a fresh-PC installer.

## 5. Reproduce and diagnose

The [subway replay guide](SUBWAY-REPLAY.md) describes automation and progress resets; it is not necessary for manual play. Manual route: enter the train, turn right, stay central, open both exit and subsequent entry doors, wait for the pig-creature scare to end, move centrally through the fire, then leave left onto the platform when the train stops.

Before another launch overwrites evidence, preserve `$dev\source-launcher-stdout.log`, `$dev\launch-manifest.json` and relevant `$runtime\user\log` files. Record executable SHA-256 (`Get-FileHash "$runtime\shadps4.exe" -Algorithm SHA256`), GPU/driver, patch track, headset/runtime, checkpoint and recent actions. Say whether caches were warm and whether monitor preview also fails; shader compilation makes first runs different.

Known issues: startup inversion, later guest render-thread crash, area-dependent FPS and unresolved presentation validation warnings. The extra patch adds diagnostics for the later crash; it is not a proven fix. Check logs/manifests for private data before sharing. Keep all game content, modules, keys, captures and saves out of Git.
