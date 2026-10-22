# Validation record — 22 October 2026

## Source and reproducibility

- Pinned upstream: `57650d2c5aeb09dda2689a2baad23396a9900c49`.
- Source-only repository checkpoint: `d61ed3d` on `ftw37/fictional-telegram/main`.
- The patch applied cleanly to 23 pristine source files and reproduced the edited checkout after newline normalization.
- Synthetic PCM/ATRAC9 waveform tests passed, including every truncated prefix of both fixtures, padded chunks, payload offsets, invalid configurations and arithmetic overflow.
- The saved patch helper detects an already applied patch and leaves the checkout intact.

## Rendering controls

Native clipping on produced readable menus and corresponding subway doors in both eyes. The same executable with native clipping off reproduced the smeared right-eye menu and overlapping geometry. Turning it on in subsequent source builds restored coherent views. Scripted rotation, snap turns, forward/backward motion and strafing changed the scene without the large previous overlays.

The game submits one 1920×1080 packed stereo image. The prepared headset target is 1920×1080, with a 960×1080 half per eye. A same-frame raw-source/prepared-target comparison matched to approximately 0.158 RGB byte values on average after the expected descriptor red/blue mapping and display color conversion. The two eye views were distinct.

## Extended OpenXR run

SteamVR's installed null-headset driver used a private config, log and OpenVR path registry. The Windows registered OpenXR runtime remained Virtual Desktop throughout. The focused tracked-pose run began at about 02:15 Toronto and remained responsive beyond 07:19, with fresh prepared headset captures still being produced. The game stayed in the controllable subway during this idle stability test; this was not a full-level walkthrough.

After loading, sampled OpenXR telemetry reported about 60 delivered/shown frames per second, focused session state and zero-degree difference between the submitted and tracked view. The log reached its 100MiB cap at 05:24; subsequent timestamped image captures independently confirmed continued rendering. The separate SteamVR compositor viewer was not inspected because its app approval timed out.

## Audio

The corrected parser and custom sampler commands reached the opening and subway without the initial decoder crash. A 90-second eight-channel NGS2 capture and a 90-second Audio3D stereo capture both contained sound. With UserFx2 enabled, Audio3D traces showed active sound buffers at changing positions. Gain interpretation and spatial accuracy remain compatibility work, not a claim of exact PS4 reproduction.

## Normal launchers

The normal flat launcher reached the alley menu with a single coherent view and no VR calibration prompt. Normal window closure completed, and the previous game command-line file was restored byte-for-byte.

Input tracing confirmed that N reaches the Cross button on a connected controller with headset input ownership disabled. The UI automation's key-down and key-up had identical timestamps, so zero-duration automated taps were not used as evidence of physical keyboard failure. Held diagnostic input is used for navigation tests.

Desktop stereo preview colors, the final normal Quest launcher and extended gameplay are still being checked. The physical Quest 2 was unavailable; headset display, comfort and physical tracking are not certified by the simulator run.

## Desktop calibration correction
The first user launch exposed that hold-Options gestures were enabled only by an active OpenXR session. Preview mode now explicitly enables desktop view gestures through SHADPS4_VR_DESKTOP_GESTURES. A two-second Options input through the controller path logged OPTIONS held: view reset, passed calibration and removed the broad white calibration veil. The normal main menu remained coherent in both eyes. This test used scripted held input; physical Enter confirmation is still pending.


TV preview is now off by default. Pass --tv-preview to enable it in preview or Quest mode. The local test-vr folder has a separate Play Here They Lie with TV.cmd launcher for this option.

