# Identified frame limiter - 22 October 2026

The remaining approximately 62 FPS ceiling was an intentional game-side frame deadline. An experimental bypass raised completed off-screen menu frames to approximately 88-93 FPS across two runs. This is not a sustained 90 FPS result through the game or a physical Quest test.

## Evidence

Opt-in aggregate sleep profiling found Game:Main calling the same timed sleep about 310 times per five seconds. The sampled interval requested about 3.94 seconds of sleep, then made roughly 357,000 zero-duration yield calls while waiting for the deadline. Other worker-thread sleeps were left alone. Nanosleep reports are nested inside usleep reports and must not be added together.

Read-only inspection of the identified caller confirmed a rate-derived frame deadline followed by a sleep-and-yield loop. Simply skipping the sleep would leave the busy wait. The experiment instead takes the existing no-cap branch, preserving the following real-time delta calculation. The limiter's repeated waits disappeared and the completed-frame rate rose when this branch was bypassed.

| Test | Completed game frames |
|---|---:|
| Original limiter, no desktop presentation | about 62 FPS |
| Bypass, first menu run | about 91-93 FPS |
| Bypass, rebuilt repeat menu run | about 88-93 FPS |
| Bypass, heavy woman/train scene | about 17-19 FPS |
| Bypass, settled subway view near wall | about 105-109 FPS |

Both menu experiments used pipeline-rebinding graphics and experimental 180 Hz virtual vblank. These are completed composed frames, with GPU completion checked before recycling; they are not desktop refresh counts. The first run had sleep tracing enabled; the repeat disabled it. Run-to-run variation remains. No physical headset was connected.

## Real-time checks

Read-only samples of the engine current-time and delta-time globals gave:

| Scene/run | Wall seconds | Engine-clock advance | Clock/wall ratio |
|---|---:|---:|---:|
| First uncapped menu | 10.004797 | 10.001375 | 0.999658 |
| Repeat uncapped menu | 10.012661 | 10.009636 | 0.999698 |
| Heavy woman/train sequence | 10.010959 | 10.016440 | 1.000547 |

Mean frame delta was approximately 10.8-11.3 ms in menu samples and 53.8 ms in the heavy scene, rather than being held at 1/60 second. This supports a real-time engine clock at both frame rates; it does not prove all physics, frame-count-based behavior or audio synchronization are correct.

The replay showed coherent sampled views of the woman, train doors and train entry. Desktop presentation was restored for those observations, so they must not be described as 90 FPS headset views. Scripted snap turning, strafing and walking changed the subway viewpoint coherently in the sampled views. With the preview disabled again, that settled wall-facing view measured 105.6-108.7 FPS at 286-301 seconds. This is a light-view sample, not a complete level benchmark. The existing heavy rendering cost remains a separate problem.

## Safety and scope of the experiment

The branch change is opt-in through SHADPS4_HTL_TEST_UNCAP=1, requires preview mode (SHADPS4_OPENXR=0), and applies only to CUSA05344 with a matching 26-byte code signature at the expected site. A missing, truncated, altered or already-patched signature is refused without writes. The patched branch reaches the same destination as the game's existing no-cap branch, and only its six bytes change. The game file on disk is never modified; restarting without the flag restores original behavior.

Regression tests verify signature rejection, unchanged surrounding bytes and identical branch destinations. The normal launcher clears both the uncap and sleep-trace environment variables. Neither experiment is enabled by ordinary launchers. The user-verified executable remains preserved privately.

## Next work

Trace/optimize the roughly 48-51 ms of guest graphics-command processing in the heavy scene. A frame limiter change cannot remove that CPU work. Then test correct headset-driven pacing, movement, collisions, cutscene duration and audio with the actual Quest. Do not copy Astro Bot's timestep or physics patches: this game already derives a changing delta from real elapsed time in the observed path.

## Validation and privacy

Build 37 compiled. Test-FrameCap.ps1 passed signature, bounds, write-scope and jump-destination checks. The source compatibility patch applied to 35 pristine files and matched the working source tree. Full disassembly, raw process memory samples, binaries and logs remain private; the repository contains emulator source, the small validated patch definition, tests and aggregate findings only.

## Subsequent visual regression

The user reported overlapping objects and transition glitches in the visible fast-graphics plus uncap demo. The combined configuration is not reliable despite the sampled views above. It is disabled for the conservative comparison replay. The causal split between graphics mode and faster timing is not yet known.
