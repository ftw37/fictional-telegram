# Desktop presentation comparison - 22 October 2026

The monitor contributes a small limit, but does not explain the whole ceiling. Windows reports the NVIDIA-connected desktop at 3840x2160, 60 Hz. Removing desktop presentation raised completed game frames from 60.0 to approximately 62.0 FPS. Increasing the virtual headset clock did not raise the remaining ceiling.

| Emulated vblank | Preview enabled | Preview disabled | Preview restored |
|---|---:|---:|---:|
| Normal 120 Hz | 60.0 FPS | 62.0 FPS | 60.0 FPS |
| Experimental 180 Hz | 60.0 FPS | 62.0 FPS | 60.0 FPS |

These are steady five-second completed-frame intervals in the main-menu alley. Each row switches presentation on, off, then on inside the same process. Graphics pipeline rebinding, stationary head pose, native clipping, packed eye handling and scene were unchanged within each comparison. TV preview, recording, GPU timestamp profiling and per-call CPU timers were off. Roughly 980 guest draws/frame continued throughout.

## What was disabled

Build 34 bypasses desktop swapchain acquisition, the final desktop pass and presentation in a preview-only diagnostic. The guest still renders and composes its eye images. It waits for the GPU completion timeline before recycling the composed frame and counting it, so these are not empty submissions. Restoring presentation returned a coherent stereo menu. Neither run deadlocked during repeated frame recycling.

Normal-clock off intervals at 75-110 seconds repeatedly reported 62.0 FPS; restored intervals at 120-125 seconds reported 60.0. Higher-clock off intervals at 90-121 seconds repeatedly reported 62.0 FPS; restored intervals at 131-151 seconds reported 60.0. Boundary intervals were excluded. The second run explicitly logged experimental 180 Hz vblank.

## Interpretation

The 60 Hz desktop path limits the preview to 60 FPS, but removing it exposes another ceiling around 62 FPS. Changing the monitor alone is therefore not a demonstrated route to native 90 FPS. The additional ceiling could be game frame smoothing/limiting or another emulator timing path; this test does not identify which. Next, trace the guest's frame waits and limiter while desktop presentation is disabled.

These menu measurements do not establish physical Quest performance. The approximately 19 FPS heavy woman/train sequence is a separate processing bottleneck and was not benchmarked again here.

## Reproduction and restoration

With HTL compatibility enabled and SHADPS4_OPENXR=0, SHADPS4_HTL_NO_PRESENT=1 or private file user/htl-no-present disables desktop presentation. The file is polled about once a second. Removing it restores presentation if the environment override is unset. The normal launcher clears the diagnostic environment variable.

No diagnostic file was left behind. Both test processes were closed and their startup flags restored. Source-only changes and this summary are saved in the repository; raw logs, binaries and game files remain private. Build 34 compiled successfully, and its patch applied to 32 pristine files and matched the source tree.
