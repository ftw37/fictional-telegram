# Here They Lie: October 24 candidate

The candidate integrates official shadPS4 0.20.0, selected subsequent official fixes and the existing AstroQuest-derived PSVR adapter. Three consecutive normal warm-cache runs and an OpenXR simulator run reached the platform. Checked calibration, woman/train, subway, scare, fire and platform views no longer showed the reproduced colored planes or damaged OPTIONS graphic. This is not a sustained 60-FPS or physical-headset qualification.

## Changes that mattered

- **GPU memory correctness:** the isolated profile had readbacks disabled. A capture traced the OPTIONS corruption to a partially damaged BC3 mip in the GPU source buffer before texture conversion. Relaxed readbacks preserve GPU-written data when CPU updates share a tracked page.
- **Visibility and dependencies:** real GPU occlusion counters avoid drawing thousands of hidden objects. Targeted image/pass dependencies and vertex-input rebinding retain the synchronization fixes without the earlier per-draw completion waits. The depth-only helper-shader interface is corrected.
- **Texture concurrency:** image unregistration now uses the same mutex as CPU fault invalidation; streaming hashes use per-thread state. An earlier warm-cache process asserted during scene loading. The corrected executable subsequently passed three fresh-process warm-cache routes. This supports the correction but does not prove every crash cause is eliminated.
- **OpenXR:** a fixed-capacity graphics-extension list overflowed when SteamVR added extensions. A dynamic list fixes that reproduced startup crash. Compositor readbacks also exposed an extra vertical flip that the desktop mirror concealed; the launcher now disables that flip. Both compositor eyes were checked upright.
- **Launch behavior:** retain smooth turning, the no-vignette game variant, motion-controller mappings, automatic headset calibration and stereo theatre presentation. The TV window stays optional and off by default. It is labelled as a synthetic left-eye crop; a native game social output is not established.

## Normal-speed repetitions

All three used executable SHA-256 `6343dd676780cba57a811a2c56b997b33057be2c9604b8595517472e52c0045f`, relaxed readbacks, pipeline caching, targeted pass synchronization and real occlusion counters. Validation and capture layers were off. Runs started in separate processes after resetting only the isolated test checkpoint.

| Run | Controlled route | First car | Second car | Scare region | Third car | Fire | Station arrival |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Warm 1 | 113.0 s | 60.0 | 60.0 | 60.0 | 60.0 | 60.0 | 55.1 |
| Warm 2 | 114.4 s | 60.0 | 58.1 | 58.6 | 60.0 | 60.0 | 54.3 |
| Warm 3 | 119.6 s | 60.0 | 60.0 | 59.9 | 60.0 | 60.0 | 56.2 |

FPS columns are medians of five-second windows entirely contained in each route stage, aligned using shared Unix timestamps. They are game-frame throughput, not headset refresh. Scene loading/entry still had windows around 50 FPS. Checked platform endpoints recovered to 60 FPS. These measurements do not establish native 90 FPS.

The route opens the exit and entrance doors between cars, stays centered through the fire, and exits onto the platform. The OpenXR check also visibly confirmed the scare creatures appearing and disappearing; they were not simply culled away.

## Validation and limits

A full validation traversal of the corrected executable reached the platform in about 118 seconds. Its additional walk along the train showed clear distant station walls. It reported no shader-interface VUIDs, query errors, lost vertex inputs or depth hazards. Ten `SYNC-HAZARD-WRITE-AFTER-PRESENT` reports remain. That presentation warning has not been established as harmless, and this is not a validation-clean build. Validation-mode FPS is excluded from normal performance comparisons. An additional normal route and the same along-train walk showed clear distant walls, initially about 58 FPS and then 59.8-60.0 FPS while stationary, versus about 11 FPS in the diagnostic run. The poses were nearby rather than pixel-identical.

The private SteamVR null headset received 960-by-1080 game eye images. Its compositor mirror was 1440-by-1620 because of runtime supersampling. The desktop game render remains 1920-by-1080 combined. The private simulator initially lacked seated-room data; supplying its own room profile restored a valid upright pose without changing the user's real SteamVR profile. Its dashboard overlay remained visible in some compositor readbacks.

Physical Quest tracking, Touch input, automatic calibration with active Touch controllers, network streaming and comfort are unverified. The simulated route supplies only buttons/sticks and a manual Options hold; OpenXR supplies the head pose. Resume-from-checkpoint positioning is not part of the New Game route qualification. Start New Game for a comparable test.

## Reproduce

Build with `scripts/Build-Integration020.ps1` using the pinned `upstream-020.lock.json` and prepared portable toolchain. The exported patch applies to pristine pinned source. Twelve local Python tests pass, including 16,384 randomized exact-address checks; those tests do not prove graphical correctness.

Run `scripts/replay_subway.py --reset-progress --startup-profile stable020 --fresh-checkpoint --renderer-sync pass --real-occlusion --flashlight --label <new-label> --development-root <isolated-root>`. This archives the isolated checkpoint before New Game. Add `--mode quest` for OpenXR with buttons-only replay; the headset must already be available.

Private evidence is under the isolated runtime's `performance-runs` directory: inputs, waypoint events, five-second frame logs, settings, binary hashes and checked images. Captures, game files, saves, shader caches, toolchains and built executables are excluded from Git.

`diagnostics/openvr_mirror_probe.cpp` reads compositor eyes through Valve's public mirror API. Build it with the prepared clang-cl environment, SDL's `openvr_capi.h` include directory and `d3d11.lib`/`dxgi.lib`; pass the installed `openvr_api.dll` and a local output prefix. Keep both mirror requests alive before reading, since an immediate first right-eye read may be stale.

## Installed launchers and rollback

The existing `HTL-Development/test-vr/Launch-Here-They-Lie-No-Vignette.cmd` and `Play-Here-They-Lie-SteamVR-No-Vignette.cmd` now select the tested isolated runtime. Desktop startup was checked through the actual installed CMD: one window, upright stereo loading panels, clear calibration and 60 FPS. No emulator or private SteamVR test instance is intentionally left running.

`Launch-Here-They-Lie-With-TV.cmd` and `Play-Here-They-Lie-SteamVR-With-TV.cmd` opt into the labelled synthetic TV crop. The normal launchers keep it off. The TV window was opened, inspected and closed without closing the game.

Original launchers are retained in `HTL-Development/test-vr/launcher-backups/20261024-163714-713`. The older executable and its user profile were not replaced. The isolated test checkpoint was archived privately so the candidate starts with a clean New Game menu.
