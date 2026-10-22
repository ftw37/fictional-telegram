# Performance investigation — 22 October 2026

Native 90 FPS has not been achieved or verified on a Quest. The physical headset was unavailable. A faster experimental graphics path is available, with the user-verified broad-barrier path retained as the normal default.

## Measured results

Measurements below use completed-frame `FrameStats` intervals, not presenter IDs. GPU timestamp profiling and per-call CPU timers were disabled for the comparable runs. Scene complexity changes substantially during startup.

| Workload | Broad GPU barriers | Experimental pipeline rebinding |
|---|---:|---:|
| Woman/train transition, around 5,500 draws/frame | about 10 FPS | about 19 FPS |
| Rendering passes in that workload | about 5,500/frame | about 140/frame |
| Settled dark subway | about 60 FPS | about 60 FPS |

The transition comparison was repeated inside one process: pipeline mode at 121–131 seconds measured 18.8–19.0 FPS, broad mode at 141–146 seconds measured 9.9–10.5 FPS, and pipeline mode again at 176–191 seconds measured 18.2–18.7 FPS. A preview-only 180 Hz vblank experiment was active throughout that comparison; it did not uncap the menu. These are changing scene samples, not a deterministic frame-for-frame benchmark.

Multiple native window observations of the woman, opening doors, train entry, and dark subway showed coherent eyes with pipeline rebinding. Scripted walking/strafe and snap turning also changed the viewpoint coherently without the large wedges in the sampled views. Discrete observations cannot exclude every intermittent defect. Two other replays crashed in the previously known guest loading path before the scene; those were not counted as visual passes.

Earlier estimates using presenter IDs are superseded by completed-frame measurements. They must not be compared as precise FPS benchmarks.

## Changes

- Optional `--fast-graphics` forces the title's graphics pipeline to be rebound before each draw, without ending every rendering pass or inserting the broad global dependency. This is a diagnostic candidate, not a proven explanation of the missing synchronization.
- Normal launches explicitly select broad barriers. Both modes retain native clip distances, packed-eye separation, and the existing controls. TV preview remains off by default.
- A hot dirty-page query now examines only the requested bit range instead of constructing a temporary bitset. It passed 12,644,424 comparisons against the previous behavior, including invalid/empty ranges and all word/page boundaries. No standalone FPS gain is attributed to this change.
- Preview-only vblank experiments accept 120/180/240 Hz through `SHADPS4_HTL_TEST_VBLANK_HZ`, require HTL compatibility and `SHADPS4_OPENXR=0`, and are never enabled by ordinary launches. These are not physical headset modes and do not establish correct game timing.

## Use and fallback

The prepared test folder contains `Test Faster Graphics.cmd`. The source launcher accepts `--fast-graphics` with preview or Quest mode, but only preview has been observed. Existing normal launchers retain the broad-barrier fallback. The original user-verified executable is also retained privately as `source-build28-gpu-barrier-user-verified.exe`.

Diagnostic barrier modes are `broad`, `compute`, `pass`, `pipeline`, and `state` through `SHADPS4_HTL_BARRIER_MODE`. `compute` reproduced severe stretched geometry and must not be promoted. `pass` kept render-pass boundaries but removed the explicit global barrier; sampled views were clean, with much less performance benefit. `state` is an additional unvalidated experiment. A private `user/htl-barrier-mode` file overrides the environment; remove test overrides before regular use.

## Remaining work toward smoother VR

The heavy sequence still spends roughly 46–48 ms/frame translating/submitting thousands of guest draws in the faster path. Reducing resolution alone cannot remove that CPU cost. Optimize resource binding and guest-command translation next, using a sampled heavy scene rather than the settled subway.

The menu remains at 60 FPS even when the emulated vblank is increased. A temporary `-ExecCmds="t.MaxFPS 90"` startup attempt also left it at 60 FPS; acceptance of that command by this shipping game was not confirmed. Identify the game's frame limiter and verify real-time cutscene duration, movement, physics, and audio before accepting a higher game rate. A compositor's 90/120 Hz output is separate from native game FPS. PSVR supports 60 FPS rendering reprojected to 120 Hz as well as native 90/120 FPS (Sony PSVR FAQ: https://blog.playstation.com/2017/10/02/playstation-vr-the-ultimate-faq/comment-page-4/).

The physical Quest/Virtual Desktop path still needs testing with the headset. Do not label this a verified 90 FPS VR release.

## Validation

- Source build 33 completed with the prepared Windows toolchain.
- Compatibility patch applied to 32 pristine source files and matched the working tree.
- Bit-range regression: 12,644,424 cases passed.
- The patch contains source changes only; game data, binaries, captures, saves, modules, and raw logs remain private.
