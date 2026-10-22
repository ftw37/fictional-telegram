# Original four-view comparison — 21 October 2026

Test used AstroQuest 0.23, stationary synthetic head, tracker initialization/GPU compatibility adapters, no OpenXR headset connection, and -NoAsyncLoadingThread. Flat-mode command line was preserved and restored for future ordinary launches.

- Original desktop Stereo presentation reproduced four views.
- Keyboard Options tap and recorded four-second Options hold did not dismiss calibration.
- Separate recenter event dismissed calibration. Four views persisted at main menu and in subway.
- Captured source L/R PNGs are 1920x1080, byte-identical. Each contains a side-by-side stereo pair. Identical whole-image submissions do not mean the two halves within that image are identical.
- In the same running subway scene, changed only the process-local desktop presentation enum from Stereo (0) to Spectator (1). Four views became two larger views. Distorted horizontal bands remained.
- Captured subway source image already contains those bands before the host presentation copy. This narrows the remaining problem to the guest rendering/reprojection or earlier emulation; it does not identify the first faulty draw.
- Source hmd_reprojection.cpp copies both texture descriptors but retains only a FOV derived from left-eye UV data. It does not preserve each eye's UV transform. Correct per-eye source sampling is the next presentation fix to investigate.

Evidence: HTL-original-before-options.png, HTL-original-held-options.png, HTL-original-after-recenter.png, HTL-four-view-subway.png, HTL-two-view-same-subway.png, HTL-original-source-L.png/R.png, HTL-subway-source-L.png/R.png.

Menu source L/R SHA256: B95BB2B0024A2B48109B28C61139BBA20D2AA09562C918DAF544571F4C76AD3B
Subway source L/R SHA256: 0C77C794CAAD1EDEF3B28BAFA96CF1D9F95933628A0CC2E1E1AE6374CDF3A532

The test was returned to four-view presentation and periodic readback disabled. No permanent emulator binary edits were made. Flat launcher remains configured for -nohmd -NoAsyncLoadingThread. Actual headset output was not tested.
