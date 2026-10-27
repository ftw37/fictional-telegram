# Quest controller and startup follow-up — October 26

The latest physical test showed black logos, then an upright menu, followed by the same later guest crash shortly after loading a save. The earlier startup gate was too restrictive for presentation: it hid the logos until readiness.

## Candidate changes

The isolated Test-Here-They-Lie-Quest-Startup.cmd now uses an updated build. For HTL only, pressing both Touch thumbsticks IN sends PS4 OPTIONS for the duration of the hold. Individual clicks still send L3/R3; the chord consumes both clicks and no longer forces a synthetic recenter. Left Menu still works when the runtime delivers it, but SteamVR/Meta may reserve their menu buttons. A brief simultaneous click is suitable for the game menu; hold both for roughly two seconds if calibration needs a held OPTIONS input. System menus remain reserved.

Before startup tracking readiness, flat logos use an upright headset-relative quad and initial stereo calibration uses headset-relative projection. Layers are no longer hidden by the upright-startup gate. Normal tracked world presentation takes over after readiness. This is a new hypothesis, requiring physical validation; no global image flip was introduced. Audio, renderer synchronization, native game comfort effects and normal stable executables remain unchanged.

Native build passed. No physical headset input or orientation confirmation is claimed. The latest candidate SHA256 is `85b812d79762614ef5e6970b288bdfcdcf84670f6bf39ca83814a3a6fa3945c3`.

## Crash evidence

The preserved test log reports guest image base 0x48a30000 and PC 0x4a5a45eb (RVA 0x1b745eb). Instruction: mov r8d,[rbx+rcx+0x58]. Registers RBX=0, RCX=0, R10=0, R9=0; attempted read address 0x58. This matches the previous long-session failure, now with register evidence. It is not the earlier command-copy overflow assertion. No justified fix has been established, and the candidate does not bypass the faulting instruction. A repeatable save/checkpoint and deeper guest state/caller capture are needed to identify why the render record is absent.


## Tracking regression correction

The user confirmed logos visible but all presentation remained head-locked. The upright-pose gate could never complete in the runtime reference orientation, also blocking game pose updates. Removed the upright heuristic. Valid poses now feed the game independently of presentation readiness; the first fully tracked valid pose enables world-space presentation in any orientation. Theatre screens anchor to the complete initial head orientation rather than assuming runtime up. Both-stick OPTIONS is retained. Native rebuild passed; physical validation remains pending. New candidate SHA256: `89a4cf191e4a928a5508d385a6d54da521b9df9f137468097db193cdccbf38ac`. The earlier candidate descriptions above are historical.


## Guest orientation follow-up

User confirmed upright world-anchored logos and working motion, but inverted stereo calibration/menu/game. Latest isolated candidate uses the full head orientation for HTL/OpenXR seat calibration instead of yaw-only, with a fresh seat reference on the first fully tracked pose. Existing inverse/forward pose transforms preserve relative movement. Native build and 1,000 randomized quaternion round-trip math-model checks passed; no physical confirmation yet. Working logo path and both-stick OPTIONS retained. New candidate SHA256: `69f00f9fd41133819f066b3dc362f6c9c09fdf626fe5478cace4279a8b31bceb`.


## Physical orientation success and crash-isolation test

User confirmed logos, loading, calibration and gameplay all upright with tracking in SHA256 `69f00f9fd41133819f066b3dc362f6c9c09fdf626fe5478cace4279a8b31bceb`. Preserved exact executable as quest-orientation-confirmed.exe. Later gameplay still crashes at the same guest render function.

Disassembly shows leaf-function locals at rbp-0x40, -0x48, -0x50 and -0x58 below the actual stack pointer (six pushes, no explicit stack allocation). The first loop uses a valid record; the subsequent loop reloads saved count/stride/base/offset as zero. Windows exception handling clobbering the PS4/SysV red zone is a plausible cause, not proven. Current log explicitly reports isRedZonePatchingEnabled=false. Enabled the emulator's existing General.redzone_patches in the isolated Quest profile only, without changing the executable or renderer/audio flags. Config backup retained. Physical same-save reproduction and performance check pending. Normal stable profile unchanged.


## Broad stack protection failed; narrow frame experiment

The next physical run still crashed at the same guest RVA with the same null values. The log confirmed red-zone protection enabled, but warned of 222 unrelocatable instructions. This does not prove the mechanism, nor that the particular function was protected. Reverted the broad setting in the isolated profile.

New opt-in `SHADPS4_HTL_LEAF_FRAME=1` in the Quest test launcher reserves an explicit 128-byte stack frame for the specific render leaf function at RVA 0x1b74520. It validates the entire 1,933-byte original function SHA1 (`7625cf6a4bd78e32082708f5275389878fedb1aa`) before modifying in-memory prologue/epilogue jumps. No on-disk game changes, instruction skipping, draw dropping, geometry or audio changes. Trampolines retain frame pointer, saved registers, flags and existing computation. A generation failure restores original entry/exit bytes. Unknown function versions are rejected unchanged.

Native x64 synthetic smoke reproduced local-value loss under simulated below-RSP scratch writes without the frame, and retained its canary and returned normally 1,000 times with the frame. This models stack overwrite; it is not proof that Windows caused the game crash. Native emulator build passed. Full physical replay remains pending. Candidate SHA256 `a91cada6f8352e21b92672ae668b64fa9aed7f230066a70aef9421c0db047470`. Preserved the exact physically upright previous executable as quest-orientation-confirmed.exe.


## User acceptance follow-up

The user reported that the narrow stack-frame candidate no longer crashed in the next play test. The session stopped when the Quest battery ran out; a longer run with a battery bank was contemplated but not yet observed. The current log confirms the explicit 128-byte leaf frame installed and broad red-zone protection disabled. Treat this as a successful limited retest, not full-game stability proof. Orientation/tracking had already been physically confirmed. See [current handoff](RESUME-HERE.md) and [complete history](DEVELOPMENT-HISTORY.md).
