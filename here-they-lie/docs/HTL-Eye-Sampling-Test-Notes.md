# Eye-sampling experiment — 21 October 2026

Implemented a hash-guarded, reversible process-only correction in the stereo post-processing path. For two submissions sharing the same Vulkan image, preserve each eye's destination rectangle as a scissor and expand the source viewport across the whole output. This makes each eye sample its corresponding half of the shared side-by-side texture, rather than squeezing the whole pair into each eye.

Validation:
- Applied in two fresh calibrated menu runs: four views became two, with distinct source halves.
- Both runs crashed on New Game at the previously observed guest libc+0x1ee34 trap. The relationship to the patch or timing is not established.
- A third control loaded without the sampling patch. It reached the subway. Applied the patch there successfully, producing HTL-corrected-eye-subway.png; game remained running during observation.
- Therefore the repeatable workflow now applies the experimental patch AFTER loading, rather than before.
- Full-resolution 1920x1080 cached render targets were captured. Saved material-colour-looking, surface-normal-looking, and lit outputs. These are cached targets from one capture operation, not a guaranteed synchronized sequence of one frame, and their roles have not been conclusively mapped draw by draw.
- Surface images retain much more detail than the lit images, but the left/right scene contents still differ substantially. Do not call the underlying stereo projection fixed or assume that lighting alone is at fault.
- Desktop aspect/FOV remains incorrect; the sampling change alone does not repair that metadata. Real Quest/OpenXR output has not been tested.

Repeat:
1. Close the emulator.
2. Run Test-Here-They-Lie-Eye-Sampling.cmd. It launches stationary VR, with recenter at 65 seconds.
3. Start New Game with N once at the menu and wait for the subway to finish loading.
4. Run Apply-Here-They-Lie-Eye-Sampling.cmd once.

Closing the emulator discards the patch. Existing flat-launch command-line settings are restored by the test launcher. Q/E and WASD mappings are retained. Periodic eye readback was disabled after captures.

Evidence:
- HTL-corrected-eye-menu.png
- HTL-corrected-eye-subway.png
- HTL-subway-before-lighting.png (material-colour-looking target; role inferred)
- HTL-subway-surface-normals.png (normal-looking target; role inferred)
- HTL-subway-lit-output.png

Next investigation: establish exact per-eye projection/source-UV semantics, correct output aspect, and trace the draw/pass that introduces the visible bands. Current results are a diagnostic improvement, not a complete VR fix.
