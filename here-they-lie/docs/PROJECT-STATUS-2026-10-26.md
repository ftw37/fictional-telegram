# Here They Lie progress — October 26, 2026

This project adapts an AstroQuest-derived PSVR compatibility layer onto pinned shadPS4 0.20 source. The PS4 game runs on a Windows PC; OpenXR sends stereo views to SteamVR and Virtual Desktop streams them to Quest 2. It is not a native Quest application and does not distribute the game.

## What has been demonstrated

- The user played on a physical Quest 2 through several checkpoints; head tracking worked. A later crash ended that long run.
- Desktop runs repeatedly traversed New Game, the woman/train transition, successive subway cars, jump scare, fire and station platform.
- Earlier combined/mirrored views and major subway artifacts were addressed with stereo/render-state fixes, targeted dependencies, real visibility counters and relaxed readbacks. This is not proof that every later area is artifact-free.
- Audio mixer and object gains were corrected from mistaken decibel interpretation to linear values. Quiet fades no longer become nearly full volume. Linked-channel output protection preserves channel balance. The user confirmed audible speech, footsteps and ambient sounds with good overall audio.
- Xbox controller polling now lets Menu act as PS4 OPTIONS; sticks, face buttons and triggers work. Keyboard controls and Quest Touch mappings are also implemented; a full physical Touch acceptance pass is not recorded.
- Smooth turning and a local no-turn-vignette game variant are available. Stereo desktop theatre preview works. Optional TV window defaults off and is a labelled synthetic left-eye crop, not confirmed native PSVR social output.

## Performance evidence

Normal audio-build replay medians were approximately 60 FPS in car/scare/fire sections and 51–54 FPS on station arrival. The older comparison had about 53 FPS on arrival. Other later areas were reported around 40 FPS, and earlier runs had intermittent deeper dips. These measurements do not establish sustained 60 FPS or native 90 FPS. First-run shader compilation and cache warmth affect comparisons. Frame generation/spacewarp has not been benchmarked for this game. Avoid disabling readbacks or enabling experimental fast-graphics settings to chase FPS: earlier tests introduced corruption.

## Build tracks

| Track | Local executable SHA-256 | Evidence / limits |
| --- | --- | --- |
| Stable desktop/audio profile | `e15671da356ec81e937ffb871d1935f102c278916380dfad5aa1e6587579a660` | Three audio-build opening-to-platform routes; user confirmed good audio. Default local launchers retain this profile. |
| First Quest command-copy candidate | `9080a7aae3d573715fd4226723b4213f6a47136b766ee68cdf81dbc810877c3f` | Physical long run crossed several checkpoints; startup upside down, later guest crash. |
| Latest isolated Quest startup candidate | `d13fb23779eba7c3c11b9feac208fe039e671d2ef2bda1f32f8d8f272e2a4ced` | Builds and startup logic checks passed; physical retest pending. |

These hashes identify local builds, not reproducible byte hashes promised for another computer. `patches/htl-shadps4-020-integration.patch` is the stable baseline. `patches/htl-quest-startup-copyfix.patch` applies after it and includes the experimental Quest changes. Do not infer the current executable from the build-folder name: that folder now contains the latest experimental build.

## Open issues and latest candidate

1. **Upside-down startup:** splash and calibration were inverted, becoming upright after Menu. Logs contained a valid but untracked 180-degree-roll pose, then tracked inverted poses, then upright poses. The candidate waits for eight consecutive tracked, upright poses before setting the initial game head reference or displaying headset layers, and delays theatre anchoring. After startup, roll is unrestricted. This is a hypothesis-driven fix, not a physically verified solution. If the runtime keeps reporting inverted poses, startup may remain blank; do not promote it as stable without a headset test. No global texture flip was added.
2. **Loading assertion:** the first physical attempt exhausted a fixed CPU command-copy arena. The candidate uses independently owned overflow buffers retained by graphics/CE coroutines, without moving in-flight arena storage or adding GPU waits. Native overflow/lifetime/capacity tests passed. The subsequent physical run passed loading and continued through checkpoints.
3. **Later long-session crash:** guest RenderThread 2 read address `0x58` at image RVA `0x1b745eb`, instruction `mov r8d,[rbx+rcx+0x58]`. This is distinct from the command-copy assertion. Missing register/caller context prevents a justified root-cause fix. The latest candidate adds fault-register logging; it does not skip the read or claim to fix the crash.
4. Full-game stability, all-area visual correctness, headset comfort, physical Touch behavior, and spacewarp quality remain unqualified. Earlier presentation validation warnings remain unresolved.

## Next acceptance run

Use the isolated Quest test build, wear/recenter the headset, check splash/calibration orientation, then load and continue through checkpoints. Preserve the stdout log before another launch overwrites it. If it crashes, retain the executable hash, manifest, logs, area/checkpoint and recent actions. Keep the verified desktop/audio executable available for comparison.

See [installation instructions](GETTING-STARTED.md), [audio evidence](AUDIO-FIX-2026-10-25.md), [Quest controls](QUEST-CONTROLS.md), and [repeatable subway route](SUBWAY-REPLAY.md).
