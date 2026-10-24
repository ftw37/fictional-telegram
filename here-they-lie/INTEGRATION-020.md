# Experimental shadPS4 0.20 integration

This candidate is isolated from the normal launchers. It is not a clean or performance-qualified release.

`upstream-020.lock.json` pins the official 0.20.0 release, the PSVR adapter donor, and selected subsequent official fixes. `scripts/Build-Integration020.ps1` builds the integration patch with the prepared portable toolchain. Game data, captures, saves and caches are local prerequisites and are not included.

The integration retains desktop stereo/theatre presentation, OpenXR, controller input, automatic headset calibration, and an optional social window. The social window remains off by default. Physical headset behavior still needs verification on this newer core.

## Measured progress

- Multiple scripted New Game-to-platform traversals completed without emulator crashes. The route opens both connecting doors, waits through the pig scare, stays centered through the fire and exits onto the platform.
- Experimental real GPU visibility counters reduced a heavy scene from roughly 6,200 draws to roughly 1,100. Reusing queries within rendering passes and integrating the official backing-memory optimization brought most woman, dark-subway, scare and fire intervals close to 60 FPS in the combined candidate.
- One combined run completed the movement portion in about 113 seconds. Station arrival and some distant station views still fell below 60 FPS.
- Targeted image/pass dependencies removed the depth hazards found by synchronization validation. Rebinding vertex input after uploads removed the reported lost-input errors in a full route validation run.
- A fresh full-route synchronization-validation run completed in about 116 seconds without shader-interface VUIDs, query errors, lost vertex inputs or depth hazards. Ten presentation-only WRITE_AFTER_PRESENT reports remain; this is not a validation-clean result.

## GPU readback configuration

The isolated runtime originally inherited `GPU.readbacks_mode = 0` (disabled). A RenderDoc capture traced the corrupted OPTIONS graphic to a BC3 texture whose 64-by-64 mip level contained colored garbage. The full-size level and neighboring levels were correct. A bounded GPU-source readback found the damaged bytes before texture conversion; this was not a final stereo-copy defect.

Changing the isolated profile to `GPU.readbacks_mode = 1` (relaxed) restored the OPTIONS graphic in both capture-tool and normal-speed tests. The first two complete relaxed-readback traversals reached the platform in about 113 and 118 seconds. Checked woman/entry, flashlight-lit subway and station views were clean. The first run's additional walk along the train also showed clear distant station surfaces at 60 FPS.

Use relaxed readbacks in the **isolated 0.20 profile** when reproducing these results. Disabling readbacks can discard GPU-written bytes when CPU updates share a tracked page. This setting change does not modify the normal runtime.

## Remaining qualification

The earlier station bands and misplaced surfaces have not reappeared in the checked relaxed-readback views, but more complete repetitions are required. Waiting for GPU completion once per frame had failed to eliminate them before the readback setting was corrected. A diagnostic native-interpolation comparison also failed to fix the button and was withdrawn.

Most measured subway sections in the relaxed-readback runs were near 59.5–60 FPS. The woman transition was typically around 55–58 FPS; station arrival was around 52–56 FPS before recovering to 60. This is not a sustained 60-FPS result. Measured relaxed-readback cost was generally below 0.2 ms per frame, with no readback waits in the slow woman windows. A zero-sleep scheduling experiment did not show a repeatable benefit against its restoration control and was withdrawn.

Three consecutive clean acceptance runs, a controlled cold/warm cache comparison, presentation synchronization investigation and headset verification remain outstanding. Capture-tool and validation runs have substantial overhead and must not be compared with normal-speed performance results.

## Replaying an isolated candidate

Pass `--development-root` pointing to an isolated runtime. The normal launcher defaults retain the existing broad synchronization workaround. Experimental comparisons can select `--renderer-sync pass` or `frame` and opt into `--real-occlusion`.

`replay_subway.py --startup-profile stable020 --fresh-checkpoint` archives the isolated profile's checkpoint inside that run's evidence folder before selecting New Game. Add `--flashlight` to toggle the light after the verified first-car spawn. This avoids accidentally testing Continue from a station save and makes dark-car inspection more useful. The normal profile must not be used for destructive progression experiments.

The exported patch applies to a pristine temporary index of the pinned official source. Twelve local script tests pass, including randomized address-index checks. Those checks do not establish graphical correctness.

## OpenXR qualification in progress

The newer renderer's fixed-capacity Vulkan device-extension list overflowed when SteamVR added its required extensions. Replacing it with a dynamic list fixed the reproduced OpenXR startup crash. A private SteamVR null-headset profile reaches a focused session and submits 960-by-1080 eye images and a 1920-by-1080 theatre screen. The null driver's missing room setup initially produces an invalid seated transform; this test profile is separate from the user's actual SteamVR configuration.

`replay_subway.py --mode quest` uses `--replay-buttons`: only buttons and sticks are scripted while OpenXR supplies the headset pose. Both Python validation and native parsing exclude pose, recenter and worn overrides, and button-only scripts do not define the host's seat. This route still schedules a manual Options press, so it does not establish automatic calibration with physical Touch controllers. Physical headset, tracking and controller comfort remain unverified.
