# Woman/subway transition rendering investigation

The reported defect is exploding geometry: broad triangles cover an eye while thin wedges cross the other. It begins during the short woman-outside-the-train sequence and can continue in the dark subway. The user supplied screenshots and the same defect was observed in the live normal-speed preview.

## Confirmed isolation

- A dense frame-readback run looked clean. The user then reproduced the defect with readback disabled. Clean captured frames were therefore not evidence that the normal run was fixed; capture changes scheduling.
- Copying submitted graphics command buffers did not solve the defect. The normal run still showed the wedges with that setting enabled.
- Enabling the private `user/htl-snapshot-constants` diagnostic stopped the flicker, confirmed by the user. That diagnostic makes private constant buffers and waits after draws.
- Switching to `user/htl-sync-gpu` alone, with constant snapshots disabled, stayed clean, also confirmed by the user. A synchronization change is sufficient for the observed stationary subway test; private constant copies are not necessary for that result.
- A cheaper once-per-HMD-frame wait was tested through `SHADPS4_HTL_FRAME_SYNC=1`. Although some inspected stills looked clean, a subsequent observed replay still had the wedges and progressed to broadly corrupted subway imagery. The user confirmed that failure. Frame waiting is insufficient and is disabled in the normal launcher.
- Restoring per-draw synchronization recovered the stationary subway. A 43.9-second sample produced 800 completed present IDs, approximately 18 per second. This is a conservative diagnostic fallback, not acceptable final VR performance.
- A GPU-only global dependency before draws and compute dispatches is enabled by the normal launcher through `SHADPS4_HTL_GPU_BARRIER=1`. It ends rendering before inserting an all-command memory dependency and does not call a CPU wait. The user watched this replay and confirmed that the woman/subway transition had no flickering triangles, then confirmed the dark subway stayed clean while walking and turning. A scripted strafe and snap turn also changed the view coherently. A 47.3-second subway sample produced 1,888 completed present IDs, approximately 40 per second. Both CPU draw and frame waits are disabled in this configuration.

The test isolates missing GPU ordering or memory visibility as the practical target. The broad dependency is conservative; the exact resource needing the missing dependency has not yet been identified, and narrowing it may recover more performance. Physical Quest output and full-game stability remain unverified.

The prepared runtime retained `GPU.copy_gpu_buffers=true` for these tests; that setting alone had already failed to resolve the wedges. Native clipping and the packed-eye separation changes remained enabled. No render readback, TV preview, constant snapshots or private synchronization flag files were active in the successful GPU-barrier run.

One frame-wait replay hit the existing guest loading trap before the transition. Retrying with a longer title-screen pause loaded successfully. This does not establish that frame waiting fixes loading stability. The physical Quest 2 still needs testing.

## Separate cache correctness fix

SubresourceExtent's default ordering is lexicographic: `{12 mip levels, 1 layer}` compares greater than `{1 mip level, 6 layers}`. The cache used that ordering as a containment test, potentially accepting an image without enough layers. A new component-wise `Contains` check replaces those capacity decisions; depth recreation merges each dimension separately. The ordering operator is retained for actual ordering uses.

`scripts/Test-TextureExtent.ps1` checks 16,384 mip/layer combinations and explicit crossed-dimension regressions. These checks passed. This is a real correctness fix, but it did not resolve the user's normal-speed geometry flicker and is not claimed as its cause.

A dense earlier replay also encountered a subresource-state assertion after a compressed image was requested with a floating-point view. An expanded assertion now records address, format, image resource dimensions and the requested range if it recurs. No assertion was suppressed or bypassed.

## Private diagnostics

Bounded source/target sequences can be enabled with `SHADPS4_DBG_EYE_SCAN`, `SHADPS4_HTL_CAPTURE_FRAMES` (maximum 1200 sets) and `SHADPS4_HTL_CAPTURE_START` (seconds after the first scanned frame). Defaults do not record. Captures, logs, game data and builds stay local and are excluded from this repository.
