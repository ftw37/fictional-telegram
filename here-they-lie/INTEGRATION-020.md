# Experimental shadPS4 0.20 integration

This candidate is isolated from the normal launchers. It is not a clean or performance-qualified release.

`upstream-020.lock.json` pins the official 0.20.0 release, the PSVR adapter donor, and selected subsequent official fixes. `scripts/Build-Integration020.ps1` builds the integration patch with the prepared portable toolchain. Game data, captures, saves and caches are local prerequisites and are not included.

The integration retains desktop stereo/theatre presentation, OpenXR, controller input, automatic headset calibration, and an optional social window. The social window remains off by default. Physical headset behavior still needs verification on this newer core.

## Measured progress

- Multiple scripted New Game-to-platform traversals completed without emulator crashes. The route opens both connecting doors, waits through the pig scare, stays centered through the fire and exits onto the platform.
- Experimental real GPU visibility counters reduced a heavy scene from roughly 6,200 draws to roughly 1,100. Reusing queries within rendering passes and integrating the official backing-memory optimization brought most woman, dark-subway, scare and fire intervals close to 60 FPS in the combined candidate.
- One combined run completed the movement portion in about 113 seconds. Station arrival and some distant station views still fell below 60 FPS.
- Targeted image/pass dependencies removed the depth hazards found by synchronization validation. Rebinding vertex input after uploads removed the reported lost-input errors in a full route validation run.
- A depth-only helper shader interface correction is compiled but still needs a fresh validation run.

## Remaining failures

Intermittent station bands or misplaced surfaces remain. Waiting for GPU completion once per frame did not eliminate them. A stereo calibration capture also reproduces the corrupted OPTIONS graphic. A local RenderDoc trace shows that graphic is already damaged in game-rendered source images before the desktop preview copies it. The final preview copy is therefore not the source of this particular defect.

Three consecutive clean acceptance runs, a controlled cold/warm cache comparison, presentation synchronization investigation and headset verification remain outstanding. Capture-tool and validation runs have substantial overhead and must not be compared with normal-speed performance results.

## Replaying an isolated candidate

Pass `--development-root` pointing to an isolated runtime. The normal launcher defaults retain the existing broad synchronization workaround. Experimental comparisons can select `--renderer-sync pass` or `frame` and opt into `--real-occlusion`.

`replay_subway.py --startup-profile stable020 --fresh-checkpoint` archives the isolated profile's checkpoint inside that run's evidence folder before selecting New Game. This avoids accidentally testing Continue from a station save. The normal profile must not be used for destructive progression experiments.

The exported patch applies to a pristine temporary index of the pinned official source. Nine local script tests pass, including randomized address-index checks. Those checks do not establish graphical correctness.
