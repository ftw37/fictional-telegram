> These are investigation notes. See [the final audio correction](AUDIO-FIX-2026-10-25.md) for the current behavior; early single-path gain tests below were superseded.

# Silent audio recording — 2026-10-25

Captured opening/calibration, title/New Game, woman/train transition and train interior using scripted inputs. Final screenshot showed bright train interior; station traversal not included. Game closed normally to finalize recording files. Output device buffers were zeroed after the internal capture points, preserving normal audio pacing and internal captured levels. No microphone or Windows loopback recorded. Normal launchers leave silent capture disabled.

Files:
- ngs2_out0.wav: 178.976 s, 48 kHz, 16-bit, 8 channels. Front-left RMS -7.65 dBFS; front-right -14.32 dBFS. Other channels approximately -61 to -64 dBFS, except silent LFE. About 1.02% of all-channel samples reach full scale, concentrated in front L/R. The WAV writer clips float input to PCM16, so this establishes saturation at the recording conversion, not the exact amount of pre-conversion overrange or proof the same signal reaches the speaker unchanged.
- audio3d-port0.wav: 214.069 s, 48 kHz, 16-bit stereo. RMS left -11.94 dBFS, right -16.99 dBFS. About 0.112% of samples reach full scale at the post-limiter capture point.

The two files start at different internal events and advance with their respective render paths; do not align them by WAV sample zero. They are not tagged dialogue/effects stems. Source identities, loop lifecycle and relative dialogue balance have not yet been established. No claim of listening to live stereo or subjective listening validation.

Analysis: audio-levels.json contains one-second per-channel peak/RMS and low-frequency power; channel-clipping.json contains per-channel full-scale occupancy. analyze_recordings.py reproduces numerical analysis.

Reproduction: existing launcher now supports --record-audio SECONDS (1–600), which enables internal dumps and silent final device output. Use the Record-Here-They-Lie-Silent-Audio.cmd launcher in HTL-Development/test-vr for a manual recording. It does not automatically play WAV files. Recording replaces runtime WAVs, so archive them first. Captures for this run are archived beside this report. Game remains closed.
