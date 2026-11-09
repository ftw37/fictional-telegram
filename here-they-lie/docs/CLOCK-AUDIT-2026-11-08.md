# Here They Lie clock audit against DriveclubPCVR — November 8, 2026

## Finding

No evidence of DriveclubPCVR's fixed-1.6-GHz conversion defect was found in the inspected Here They Lie main engine/frame timing path. A console-frequency default exists in the game file, but initialization replaces it with the inverse of the frequency returned by the emulator. This report records static inspection and earlier live engine-clock evidence; no new gameplay timing/performance comparison was run and no runtime/game/settings/saves were changed.

## Driveclub evidence reviewed

Read the separate local DriveClubPCVR project's docs/CLOCK-PACING-CHECKPOINT.md and tools/dcvr_clock_scale.h. It found three hard-coded integer coefficients (10486) assuming a 1.6 GHz timestamp counter; the measured host counter in those tests was about 3.8 GHz. An 80-million-cycle interval was consequently estimated near 50 ms rather than 21.05 ms, consistent with periodic backward corrections and extra requested sleeps. Its title/hash-guarded patch recomputes those three coefficients (4415 on that host). This is a timestamp-counter rate mismatch, not a requirement to underclock the processor or a CPU performance deficit.

Driveclub's repeated ordinary-replay evidence reported 74 intervals above 33.333 ms uncorrected versus two corrected over three runs each, but only about 0.61 percent median FPS improvement. It did not establish sustained 60 FPS or that every freeze had the same cause. Do not transplant its addresses, coefficient writes, or CUSA03296 guard into HTL.

## HTL inspected path

Tested game CUSA05344 v01.00; original SELF SHA256 `6366eb9964b7be8eddcf10a14261a2db7655ad477ed7bc4b599df4c8757415a5`.

- Frame-time function at image RVA 0x1e58ce0 calls a PLT entry resolved through the game's relocation/symbol tables to `sceKernelGetProcessTimeCounter` (NID fgxnMeTNUtY).
- It converts the counter using the shared double at RVA 0x429d810.
- On disk the double is 6.274579e-10 seconds/tick, corresponding to approximately 1.593732424 GHz. Merely finding that constant would give a misleading diagnosis.
- Initialization at RVA 0x420d60 calls a PLT entry resolved to `sceKernelGetProcessTimeCounterFrequency` (NID BNowx2l588E), converts its return to double, divides the constant 1.0 by it, and stores the result into that same shared factor. Thus the normal initialized clock adapts to the returned frequency.
- The inspected emulator's src/core/libraries/kernel/time.cpp returns elapsed NativeClock host TSC counts from GetProcessTimeCounter and the same NativeClock's measured TSC frequency from GetProcessTimeCounterFrequency. NativeClock estimates frequency and uses matching conversion factors. These paired APIs are consistent with the game's initialization.

A static instruction scan also found no decoded RDTSC/RDTSCP in the EH-table-covered main-game function range. Follow-up inspection started at the EH function boundaries for 1,500 functions containing 2,520 raw timestamp-opcode byte patterns; none decoded as an actual timestamp instruction. A naive scan of the entire executable segment initially decoded apparent reads in non-function data; those are not evidence of real executed reads. This is supporting evidence, not proof that every module, uncovered function or runtime-generated path has been audited. Raw disassembly and symbol-table extracts remain private.

## Independent earlier live evidence

The October 22 read-only engine-time samples in [FRAME-LIMITER.md](FRAME-LIMITER.md) measured:

| Scene | Wall seconds | Engine advance | Ratio |
| --- | ---: | ---: | ---: |
| Uncapped menu, first | 10.004797 | 10.001375 | 0.999658 |
| Uncapped menu, repeat | 10.012661 | 10.009636 | 0.999698 |
| Heavy woman/train sequence | 10.010959 | 10.016440 | 1.000547 |

This agrees with a near-real-time engine clock despite large frame-rate differences. It is historical evidence from experimental builds, not a new measurement of the latest physical Quest build, and does not qualify every physics/audio/secondary timer or long-duration behavior.

## Decision and possible next step

No clock patch is justified by this comparison. Keep the accepted runtime's clock, graphics, audio and pacing settings intact. Intermittent HTL frame-rate dips cannot currently be attributed to Driveclub's particular clock defect. If timing is investigated further, use an isolated diagnostic copy to sample the initialized shared factor and returned counter frequency, engine time versus wall time, and full sleep-request traces through a known hitch. A periodic correction could exist in another subsystem even when the main clock is correct; require evidence before changing it.

The Driveclub project was consulted read-only. Its runtime/source/profiles and HTL's runtime/source/profiles were left untouched. This documentation is the only repository change for the clock comparison. See [current handoff](RESUME-HERE.md) for accepted builds and other open limits.
