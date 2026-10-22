# Audio compatibility work

The title calls `sceNgs2ParseWaveformData`. In the pinned source this returned success without filling the output, so later sampler setup interpreted unrelated memory as a sound format. The compatibility path now parses bounded RIFF/WAVE metadata, including PCM and ATRAC9. It rejects truncated chunks, unsupported formats, inconsistent channel/rate configurations and size overflow.

The game's observed sounds are ATRAC9 WAVE files. Their configuration GUID, configuration bytes and fact-chunk sample count/delay match the container conventions independently described in the [vgmstream RIFF reader](https://github.com/vgmstream/vgmstream/blob/master/src/meta/riff.c). No decoder implementation is copied: the build uses its existing LibAtrac9 dependency. The new parser fills NGS2 format, frame, sample-count and waveform-block information.

The returned block offset must include the WAVE header. An initial test omitted that offset and sent RIFF bytes to the ATRAC9 decoder, causing a decoder crash. The corrected block points at the encoded payload. A decoder guard rejects a mistakenly queued RIFF header. The corrected build subsequently stayed up through the opening and subway.

Custom-sampler stream commands also used different IDs that the engine rejected. The compatibility path maps the six basic commands whose payload structures match the existing sampler implementation. Other custom modules are not silently accepted.

The title's positional-sound path uses a custom UserFx2 callback. Opt-in support allocates the module's common/parameter/work storage, calls its setup/control/process/cleanup hooks, propagates parameter changes and releases active sound objects when a voice stops. Live traces then showed sound buffers and changing positions arriving at the existing Audio3D mixer. The remaining custom filter command is still unsupported.

`SHADPS4_HTL_AUDIO_DB=1` tests decibel interpretation for NGS2 port volumes and Audio3D gain. Zero/negative values had otherwise muted or inverted routes. With conversion enabled the captured 90-second NGS2 mix and the separate 90-second Audio3D stereo mix both contained nonzero sound. This is a compatibility interpretation under test, not proof of matching PS4 audio quality.

Synthetic tests in `tests/waveform_smoke.cpp` cover PCM/ATRAC9 metadata, padded chunks, payload offsets, seeks, invalid configurations, overflow and every truncated prefix of the fixtures. Run `scripts/Test-Waveform.ps1` after the emulator's LibAtrac9 library has been built. Fixtures contain metadata and zero-filled data, not game audio.

Diagnostic captures are local only. `SHADPS4_AUDIO3D_DUMP=<seconds>` records up to ten minutes of the final stereo mix; the default launcher disables it. Physical Quest sound, spatial accuracy and later-level playback still need validation.
