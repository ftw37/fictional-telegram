# Resume here: Here They Lie / reusable PSVR research

Last reconciled with source, installed executable hashes, logs and user reports: **October 26, 2026**. This is the current handoff. Dated reports describe their own historical builds; their claims of unverified physical playback are superseded where explicitly stated below.

## Read in this order

1. This file for current state, exact builds and next steps.
2. [Development history](DEVELOPMENT-HISTORY.md) for the experiments and causal evidence, including failures.
3. [PSVR porting playbook](PSVR-PORTING-PLAYBOOK.md) for applying the lessons to another title.
4. [New-PC setup](GETTING-STARTED.md) for build/runtime preparation. Apply the latest-candidate qualifications below.

## Current result and limits

The user physically tested Here They Lie CUSA05344 v01.00 on Quest 2 via Virtual Desktop and SteamVR. Logos, loading, calibration, main menu and gameplay are now upright; head tracking works. Pressing both Touch thumbsticks IN together sends PS4 OPTIONS; holding the chord forwards a held OPTIONS input. Audio was explicitly confirmed good: speech, footsteps and ambience audible. Native comfort settings now control turning/periphery effects, with original game assets selected.

A repeating guest render-thread crash was addressed by an exact-function-checked, explicit 128-byte stack reservation. The user reported no crashes in the subsequent test; the session ended because the headset battery ran out. This is a successful retest, not a full-game or multi-hour stability qualification. Do not label the issue definitively eliminated. No claim of sustained native 90 FPS, artifact-free later areas, or fully qualified positional/HRTF audio is justified.

## Exact build tracks — do not confuse them

| Track | SHA-256 | Qualification |
| --- | --- | --- |
| Stable desktop/audio executable | `e15671da356ec81e937ffb871d1935f102c278916380dfad5aa1e6587579a660` | Three audio-build opening-to-platform routes; user confirmed audio. Older headset orientation/control behavior. |
| Physically upright orientation checkpoint | `69f00f9fd41133819f066b3dc362f6c9c09fdf626fe5478cace4279a8b31bceb` | All screens upright and tracking works, but repeated later crash remains. |
| Latest Quest candidate | `a91cada6f8352e21b92672ae668b64fa9aed7f230066a70aef9421c0db047470` | Upright work plus narrow render-leaf stack reservation; user reports crash-free retest, battery-limited. |

These identify installed local binaries, not a promise of bit-identical independent builds.

The launcher to continue the latest physical work is **`HTL-Development/test-vr/Test-Here-They-Lie-Quest-Startup.cmd`**. Its name is historical: it now also includes the OPTIONS mapping and narrow crash fix. It selects `experiments/quest-startup-fix-v1`, the original `HTL-Test/game/uroot`, `--mode quest --renderer-sync pass --real-occlusion`, real SteamVR's OpenXR manifest, clears `VR_PATHREG_OVERRIDE`, and sets **`SHADPS4_HTL_LEAF_FRAME=1`**.

Normal `Launch-Here-They-Lie.cmd` / `Play-Here-They-Lie-SteamVR.cmd` still select `experiments/stable020-a`; they have NOT silently been promoted to the latest Quest candidate. Old names containing No-Vignette now also select original assets. Both-thumbstick OPTIONS is in the latest candidate, not the older stable binary.

## Important source/config contract

- Pinned upstream: shadPS4 `529ceb32f5546b820588f194b903cc39d08015fe`; donor/pins in `upstream-020.lock.json`.
- Stable patch: `patches/htl-shadps4-020-integration.patch`.
- Incremental current Quest patch: `patches/htl-quest-startup-copyfix.patch`, applied AFTER the stable patch. Includes command-copy ownership, orientation/reference handling, OPTIONS chord, crash registers, and opt-in targeted leaf frame. Its name no longer describes its whole scope.
- Latest local source/build directory: `HTL-Development/integration-020` and `build/integration-020`. The build directory contains the experimental candidate, not the stable audio executable. Hash before copying.
- Latest profile `user/config.json`: `General.redzone_patches=false`, `GPU.readbacks_mode=1`, `GPU.copy_gpu_buffers=true`, pipeline cache enabled, Vulkan validation off. The broad red-zone experiment failed and was reverted. The narrower leaf-frame protection is a separate environment-controlled mechanism.
- Keep `SHADPS4_HTL_XR_FLIP_Y=0`. No global Y flip or blanket per-frame GPU completion wait was used for the final fixes.
- Headset theatre screens use the complete initial view orientation; guest calibration uses a full orientation basis for HTL/OpenXR, not yaw alone. Poses continue regardless of an upright heuristic. Never restore the failed upright-pose gate.
- Original game archive is unmodified. The optional no-vignette `_P.pak` lives in a separate historical view and is not selected for normal play. Smooth turning was a saved game option (VR Drive Mode unchecked), not a runtime force. Do not overwrite the user's comfort choices or reset saves casually.

## Local map on the original development PC

All paths below are local references, not prerequisites on someone else's machine. They were under `C:/Users/frank/Documents/Codex` despite this chat's later workspace changing to `Documents/ChatGPT/Vibe Coding`.

- Repository: `SpaceInvaders-Development` → `https://github.com/ftw37/fictional-telegram.git`.
- Main runtime/baseline: `HTL-Development/experiments/stable020-a/test-vr`.
- Latest Quest runtime: `HTL-Development/experiments/quest-startup-fix-v1/test-vr`.
- Rollback `quest-orientation-confirmed.exe` in latest runtime is the known-upright pre-leaf-frame binary, hash above.
- Original extracted game: `HTL-Test/game/uroot`; optional linked variant: `HTL-Test/no-vignette-v1/uroot`.
- Latest stdout log: `experiments/quest-startup-fix-v1/source-launcher-stdout.log`; manifest/active-run JSON beside it. Another launch overwrites stdout.
- Earlier evidence: `2026-10-20/new-chat/outputs/Here-They-Lie-Audio-Fix` and `Here-They-Lie-Quest-Startup`; later local crash evidence: `Documents/ChatGPT/Vibe Coding/htl-followup`.
- Toolchain: `DevTools/htl`; helper `scripts/Enter-BuildEnvironment.ps1`. Git there is portable; Python path is machine-specific, pass your own.

Do not move/delete linked game data, caches, profile/save directories or rollback executables based solely on these descriptions. Check actual paths, ownership and disk links.

## Next useful work

1. Longer physical play from the same save/checkpoint and later areas; record elapsed time and exact endpoint. Battery exhaustion is not a software crash.
2. Keep the current candidate intact until that result is known. Verify log contains `HTL render leaf: explicit 128-byte stack frame installed` and no new Critical entry; record actual binary hash.
3. Compare frame times/visuals with the known baseline under the same workload; there is no measured acceptance route for the latest Quest crash fix yet.
4. Consider VDXR versus SteamVR only as a separate controlled experiment. Inspect RushofPCVR hitch/memory diagnostics before changing good rendering code.
5. Promote the latest candidate to normal launchers only with deliberate acceptance evidence, not by assuming its filename means stable. The install script checks exact-binary route evidence.

Future work should update this handoff and keep observations, plausible explanations, implemented changes and verification limits distinct. Never require the user to rediscover old launcher distinctions or repeat a failed experiment without new evidence.
