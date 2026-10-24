# shadPS4 0.20 Windows candidate

The usual local launchers now select the isolated 0.20 candidate. Three consecutive normal warm-cache routes reached the platform in 113.0, 114.4 and 119.6 seconds; checked views were clear. Most car/scare/fire intervals were near 60 FPS, but loading/entry and station arrival still dipped below it. Physical Quest playback remains unverified, and a presentation-validation warning remains unresolved. See the [measured run report](docs/COMPREHENSIVE-RUN-2026-10-24.md).

## Source and build

`upstream-020.lock.json` pins official shadPS4 0.20.0, the AstroQuest PSVR donor and selected subsequent official fixes. `scripts/Build-Integration020.ps1` builds `patches/htl-shadps4-020-integration.patch` with the prepared portable toolchain. The patch applies to pristine pinned source. Existing modified sources are checked before applying it; the dependency-junction owner is validated.

The tested executable's SHA-256 is `6343dd676780cba57a811a2c56b997b33057be2c9604b8595517472e52c0045f`. This identifies the local tested binary, not a promise of byte-identical builds on another machine. Game data, captures, saves, caches and built executables are not distributed.

## Correctness and performance

The isolated profile had inherited `GPU.readbacks_mode = 0` (disabled). A capture traced the damaged OPTIONS graphic to a BC3 mip whose upper half was already corrupted in the GPU source buffer. Neighboring mips were correct. Relaxed readbacks (`GPU.readbacks_mode = 1`) restored the graphic and the checked station/subway surfaces. Disabling readbacks can lose GPU-written bytes when CPU updates share a tracked page.

Real GPU visibility counters reduced a heavy scene from roughly 6,200 draws to roughly 1,100 in the earlier comparison. Targeted image/pass dependencies and final vertex-input rebinding retain necessary synchronization without per-draw completion waits. The depth-only auxiliary shader's interface is corrected.

An initial pipeline-cache warm launch asserted during scene loading. Image unregistration now shares the CPU-fault mutex and streaming hashes use per-thread state. The corrected binary passed three separate warm-cache processes and the OpenXR route. Pipeline caching is enabled only for this tested candidate. No assertion was suppressed. These passes do not establish that every possible crash has been eliminated.

Readback timing was generally below 0.2 ms per frame in the profiled sample and did not account for the slow woman windows. A zero-sleep scheduling experiment failed its restoration comparison and was withdrawn. No claim of sustained 60 or native 90 FPS is made.

## Presentation and controls

The candidate retains stereo theatre preview, OpenXR, smooth turning, no vignette, the existing controller mappings and automatic headset calibration. The normal TV window is off; the new With-TV launchers opt in. It is explicitly labelled as a synthetic left-eye crop because native game social output has not been established. Closing it leaves the game open.

A dynamic graphics-extension list fixes the reproduced OpenXR startup overflow. Compositor readbacks exposed an unnecessary vertical flip that the desktop mirror concealed. The launcher now uses `SHADPS4_HTL_XR_FLIP_Y=0`; both compositor eyes were checked upright. The private simulator's missing seated-room transform was repaired only in its separate profile. Physical Touch/Quest tracking, automatic calibration with active Touch controllers, streaming and comfort remain unverified.

## Validation and replay

A full corrected-build validation route reached the platform in about 118 seconds, with no shader-interface VUIDs, query errors, lost vertex inputs or depth hazards. Ten WRITE_AFTER_PRESENT presentation reports remain; they have not been established as harmless. This is not a validation-clean build. Diagnostic FPS is excluded from normal comparisons.

Twelve Python tests pass, including 16,384 randomized exact-address checks. The native emulator and compositor probe compile. These component checks do not prove graphical correctness.

`replay_subway.py --startup-profile stable020 --fresh-checkpoint --reset-progress --renderer-sync pass --real-occlusion --flashlight --label <new-label> --development-root <isolated-root>` archives the isolated checkpoint, selects New Game and traverses to the platform. Add `--mode quest` for OpenXR with buttons-only input; scripted head, hand, worn and recenter overrides are excluded in both Python validation and native parsing. That route still schedules a manual Options hold and does not test automatic calibration with physical Touch controllers.

`scripts/Install-CandidateLaunchers.ps1` checks three matching successful route records and the executable hash before changing launchers. Previous launchers are backed up; the earlier emulator/profile remain available.

## Related-project review

[RPCSX](https://github.com/RPCSX/rpcsx) documents an experimental Linux emulator; [fpPS4](https://github.com/red-prig/fpPS4) documents early compatibility and a core rewrite. Their reviewed documentation does not establish a working Here They Lie/OpenXR replacement. This is an evidence limit, not a claim that no other project could support it.

[AstroQuest's PC performance fork](https://github.com/evertec82/AstroQuest/blob/main/README-PC-VR.md) describes separate graphics queues, recovery from half-refresh pacing and precise Windows timers. Its [port notes](https://github.com/evertec82/AstroQuest/blob/main/docs/elliotttate-performance-port.md) also explain cache serialization repairs and caution against importing parallel-copy/memoization experiments with unresolved corruption. The official 0.20 core used here already has inline image/sampler resource storage and newer cache formats; the older pointer-storage repair is not directly applicable. Its pacing claims concern another game and do not establish a Here They Lie improvement. No speculative parallel-copy changes were imported.

[RushofPCVR](https://github.com/RandomName729/RushofPCVR) demonstrates another AstroQuest-derived PSVR game path and recommends matching a game cap to headset pacing. It is useful context for presentation, not evidence that this game's renderer can meet every frame budget.
