> These are investigation notes. See [the final audio correction](AUDIO-FIX-2026-10-25.md) for the current behavior; early single-path gain tests below were superseded.

# Train/dialogue balance diagnostic

User reports loud train masking dialogue and continuing through station arrival. Inspection found SHADPS4_HTL_AUDIO_DB enabled decibel conversion for both NGS2 port volumes and Audio3D positional object gain. The upstream OpenAL path passes object gain directly to AL_GAIN. Linear fade 0.01 becomes 1.001 under the old dB interpretation, and mute 0 becomes 1. This is a plausible cause, not a confirmed diagnosis.

Added a separate SHADPS4_HTL_AUDIO3D_DB override: 0 tests direct linear object gain while retaining existing NGS2 compatibility. Ordinary launchers retain previous audio behavior. --audio-balance-test selects the override and bounded raw-gain logging (first 128 values) plus existing rate-limited object traces. No audio recording is enabled.

Local test launcher: HTL-Development/test-vr/Launch-Here-They-Lie-Audio-Balance-Test.cmd. Rebuild is staged for application by the launcher only after the current game exits. Includes the controller polling fix. Native compilation and Python syntax validation passed. Listening comparison and full route with this audio interpretation remain unverified. No hardcoded train suppression or global volume reduction was made.

## First listening test failed

The user reports no improvement: title/train still overpower speech. Captured first 128 Audio3D raw gain values were zero. Direct linear interpretation mutes these positional sounds; that was not a valid balance fix. Reversed the test to Audio3D decibels and isolated linear NGS2 port volumes, with bounded raw port logging to determine whether volume/mute commands are being incorrectly expanded. The normal launcher's behavior remains unchanged. Windows Sound panel launch was reported, but no mmsys/control.exe/ms-settings/ShellExecute command was found in launcher scripts or emulator source; cause unresolved.

## Revised test: separate stereo output balance

Live NGS2 raw levels include 0, 1 and -4, so blanket linear NGS2 interpretation is also inappropriate; no fix was established by the linear tests. Restored both original decibel interpretations in --audio-balance-test. The current opt-in test instead sets SHADPS4_HTL_NGS2_OUTPUT_GAIN=0.2: conventional NGS2 mastering output is attenuated by about 14 dB after limiter processing, without attenuating the separate Audio3D object output. This is a diagnostic balance workaround, not sound-specific train suppression or verified voice lifecycle repair. It may also attenuate dialogue routed through the conventional output. Default gain remains 1 and ordinary launchers clear the override.

Invalid gain text/nonfinite values fall back to 1; valid values clamp to [0,1]. Native compilation, Python syntax and diff whitespace checks passed. Updated binary staged for next launch, current game not interrupted. A listening test and confirmation that train looping ends are still required.
