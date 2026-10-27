# Investigation state

> Historical snapshot: later physical orientation and crash retests are recorded in [the current handoff](RESUME-HERE.md). Follow that handoff for the current candidate and defaults.

## Working reference

Here They Lie EU CUSA05344 v01.00. User's Quest 2 connects through Virtual Desktop but was not available for headset tests. Baseline installed emulator is AstroQuest 0.23 at the pinned upstream revision. Its expected executable hash is in upstream.lock.json. Existing test installation remains separate from source and build output.

Flat mode: game command line `-nohmd -NoAsyncLoadingThread`. Normal camera, no HMD calibration. Loading remains intermittent: the async-loading workaround enabled a successful run but did not eliminate crashes. Q/E control turning; WASD movement; N or keypad 2 is Cross; Enter is Options. Preserve the user's current turn behavior.

Opening sequence confirmed by user: alley title with woman; New Game; camera drops; white transition; woman and subway cutscene; doors open; player enters; transition to dark/dreary controllable interior. Do not mistake scripted camera motion for verified movement input.

## VR compatibility adapters

Process-only tracker initialization translation: game supplies 144-byte structure; host expects 128 bytes. Pointer/size groups copied from game offset 0x40 onward to host offset 0x48 onward. Calibration normalized to the supported synthetic path.

GPU submit structure is 0x228 bytes in this title versus 0x288 expected by host. Current host consumes no camera payload after checking the size. The diagnostic changes that comparison in the verified process; this does not prove the payload could be ignored in a full implementation.

Stationary simulated head plus separate recenter event passes startup calibration. Options tap and a four-second held Options press alone did not dismiss it in the comparison run. Prior rotation-only and zero-separation experiments did not resolve the different eye content. Zero separation was verified in returned tracker poses and then restored to 0.063 m.

## Display findings

Original PSVR panel: 1920x1080 total, 960x1080 per eye. Both submitted eye descriptors point at one shared 1920x1080 side-by-side source. Source L/R readbacks are byte-identical entire images; the two halves within that image are NOT identical.

The original presenter shows the full source once for each eye: four views. Spectator mode displays the whole source once: two views. This change does not alpha-blend/collapse four cameras. Separate process-only stereo sampling experiment preserves per-eye scissors and expands the viewport across the output, so each eye samples its half. Actual per-eye UV transforms and output aspect/FOV still need proper implementation.

Game supplies left UV scale approximately 0.209312/0.395923, offset 0.252730/0.5; right offset 0.747270/0.5. Current hmd_reprojection.cpp retains left-derived FOV and drops the per-eye transforms. Correct shared-texture projection must account for these semantics, not merely assume every VR title uses this layout.

Right-eye door behind woman was present while left lacked it. Mismatch appears in earlier surface-like buffers too. A second subway capture retains more surface/material detail than final lit images, but eye content still differs substantially. Cached targets can come from different frames; first faulty draw is NOT yet identified. The double horse poster ALSO exists in flat mode per user observation; it is not proof of stereo leakage.

## Social screen

Source driver recognizes social output handle 2, times its refresh, skips registering its images with the renderer, and completes flips without displaying them. Earlier title logs showed only main video output, not the dedicated social bus. Main TV buffers retained loading art. HMD Start2dVr is stubbed. No claim that a working social image is currently available. Need trace title/system-generated mirror behavior, then add a distinct TV window and headset-pair window.

## Crash and other errors

Known loading fault: guest libc.prx+0x1ee34, runtime address 0x80ad66e34. Instruction is int 0x44 followed by ud2, suggesting an intentional trap; exact triggering assertion remains unknown. Seen on async-loading thread in earlier flat tests and Game:Main during newer VR tests. Two patched-before-load runs failed; unpatched control loaded and patch applied afterward worked. Do not assume causation established.

A separate host PresentThread null-related startup crash was also seen once. NGS2 0x804a0308 is an audio control error, separate from view duplication. Tracker GpuWaitAndCpuProcess and some motion calls log STUBBED but return success; log severity alone does not prove failure.

## Captures and next steps

Local captures/logs are outside this repository. Existing project outputs include the original four/two comparison, corrected-eye subway image, native 1920x1080 surface/material and lit targets, and detailed test notes.

Next work, only when authorized: build source-level instrumentation; implement ABI adapters in source; establish true social output path; fix source UV/projection/aspect; trace exact draws and attachment usage to find remaining distortion. Preserve flat baseline, maintain repeatable comparisons, restore experimental settings, and stop repeating identical failures without new evidence. Overnight work has not started.
