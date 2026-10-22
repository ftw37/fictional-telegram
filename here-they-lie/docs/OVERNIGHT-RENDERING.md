# Rendering investigation — 22 October 2026

The original working emulator remains untouched. All source tests use the pinned AstroQuest 0.23 source and a separate runtime in `Documents/Codex/HTL-Development/test-vr`.

## Reproduced cause and improvement

There were two distinct defects:

1. The title supplies both eyes in one 1920×1080 texture. Each descriptor sampled that entire texture, producing four views. The compatibility patch retains each eye's 960×1080 half and derives its field of view from that half. The combined native preview is 1920×1080.
2. On the NVIDIA driver, the source emulates clip distances using the fragment shader. Depth-only draws have no fragment shader, so their clipping was skipped. Native clipping is available on this GPU. Setting `SHADPS4_HTL_NATIVE_CLIP=1` disables the workaround for this experiment.

With native clipping enabled, both menus became readable and the subway doorway behind the woman appeared in both eyes. The dark subway interior also showed coherent corresponding doors and benches. Simulated head rotation, right-stick snap turns, forward/backward movement and strafing changed the viewpoint without the earlier mixed geometry.

A fresh control run using the same build with native clipping disabled reproduced the smeared right-eye menu and overlapping subway geometry. Re-enabling native clipping on the next build restored the clean menu. This is strong evidence of a clipping defect; it does not establish that every later level is correct.

## Other tests

- Per-draw GPU completion and read-only constant snapshots did not resolve the menu smear. Both diagnostics remain disabled.
- The actual guest tracker result consumer reads poses at offsets matching the emulator's 1520-byte result. The older initialization/submission parameter sizes are adapted separately.
- A second native window displays an explicitly labelled synthetic crop of the left eye. The code can route a dedicated social-port image, but this title has not opened that port in observed logs. The crop is not verified Sony social-screen output.
- Virtual Desktop's registered OpenXR runtime connected successfully and correctly reported that the physical headset was absent.
- The installed SteamVR null-headset simulator was started with a private path registry, settings and log directory. The system's registered Virtual Desktop runtime was not changed. OpenXR created a session, reached focused state and delivered approximately 60 frames per second after loading. The title's first full frame was reported as 960×1080 per eye, with a 1920×1080 swapchain.
- Captures from the actual prepared OpenXR image showed corresponding subway doors and distinct eye views. After accounting for the descriptor's red/blue swizzle and display color conversion, a same-frame source/output comparison differed by about 0.16 byte values per RGB channel on average. This checks the image-copy path; it does not validate the Quest display or physical tracking.
- The simulator's separate compositor viewer could not be inspected because its Computer Use app approval timed out. Tests continued through emulator buffer captures and OpenXR telemetry.
- Audio parsing and custom sampler commands now produce sound; opt-in UserFx2 callbacks feed positional sounds to Audio3D. See [audio findings](AUDIO-COMPATIBILITY.md).

## Reproduce

Apply `patches/htl-compatibility.patch` at the pinned source revision, then rebuild. The launcher enables the tracker adapter, packed-eye sampling and native clipping. It does not use the old binary-address patches.

`python scripts/launch_here_they_lie.py --mode preview` starts the desktop stereo test. `--mode quest` enables OpenXR through the registered runtime. `--mode flat` starts the existing non-VR reference using `-nohmd`.

For VR calibration, hold Options/Enter for at least one second while looking ahead. A brief tap does not trigger the emulator's reset-view event. New Game is Cross (N or numpad 2). WASD and Q/E remain configured in the local runtime.

Launchers restore the previous game command-line file when the emulator exits normally or crashes. A recovery record is saved locally before changing it. Runtime, game files, captures and logs stay outside Git.

## Still under investigation

Validate the updated TV preview colors, the normal manual launchers and the flat reference; extend gameplay and repeatability checks. The dedicated YCbCr social-screen capture path remains unsupported and uses the labelled crop fallback. Physical headset validation requires the Quest to be connected later.
