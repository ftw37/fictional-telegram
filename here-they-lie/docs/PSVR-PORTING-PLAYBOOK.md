# PSVR compatibility project playbook

Reusable engineering lessons from Here They Lie, October 2026. This is a research workflow, not a universal PSVR patch set. Start with the [current HTL handoff](RESUME-HERE.md) and [history](DEVELOPMENT-HISTORY.md) for the evidence behind it.

## A. Define the target and preserve a baseline

Record game title, region/title ID, exact game version, user-owned data provenance, original executable hash, host OS/GPU/driver, headset, transport and runtime. Distinguish native Quest execution from PC emulation streamed to Quest. Agree on an initial acceptance route and observable end state; a booting title screen is not a playable game.

Use separate source, build, runtime/profile, game, evidence and rollback directories. Pin emulator and donor commits plus dependency/tool hashes. Never include proprietary game/assets/modules/keys/saves in source control. Avoid a single mutable binary named latest with no manifest. Record locally installed hashes and original source pins, and do not promise byte-identical builds without reproducibility work.

Acquire a flat/non-HMD reference if the game supports one. Record the original hardware opening sequence and controls from the user or a justified reference. Keep known-good saves before any reset test. Real game behavior (intentional duplicated artwork, scripted movement, movement-locked scares) can resemble a bug.

## B. Survey upstream without blindly importing it

Read donor source and current compatibility notes; compare API semantics, not just function names. A fix for another PSVR title may depend on a different game engine, camera ABI, clock source, render layout or controller model. Check whether the newer emulator already implements the same repair differently.

Useful sources reviewed in this project include bigmak94/AstroQuest, evertec82/AstroQuest, RandomName729/RushofPCVR and official shadPS4. Our dated review of RushofPCVR found ideas for hitch probes, memory-pressure telemetry, stale texture diagnostics, partial shadow-buffer clears, source/game timing and selectable VDXR/SteamVR. These are leads, not imported/qualified HTL fixes. RushofPCVR also explicitly corrected an earlier claim that long-path support eliminated its black streaks. Recheck current code and reports before a future project; do not treat this snapshot as current release guidance.

Respect upstream GPL and dependency licenses, retain attribution and publish modified source/patches appropriately if distributing builds. Other projects' claims on another game do not establish your title's compatibility or FPS.

## C. Establish ABI and lifecycle correctness

Trace concrete calls from the guest: struct byte size/version, pointers, alignment, enums, callbacks, timing, return codes and lifecycle. Verify pointer-bearing layouts against guest disassembly when necessary. Fail closed for unsupported versions rather than padding blindly or making all errors succeed.

Tracker initialization, pose history, visibility/quality bits, camera GPU operations and HMD presentation may be separate systems. A stub returning success may be an adequate isolated experiment, but is not a full implementation. Logs labelled Error/STUBBED do not automatically identify the crash cause. Compare behavior and effects, not severity text alone.

Simulated stationary tracking is useful for debugging a desktop preview. Do not let scripted head/worn/hand/recenter input override the actual headset during physical tests. Replay validation should reject incompatible pose overrides in headset mode.

## D. Trace the complete display pipeline

Map, in order:

1. Game render target and format/subresources.
2. Eye descriptors: shared texture versus separate textures, layers, UV transform, viewport and scissor.
3. Game-side reprojection or packed output.
4. Emulator copy/resolve and final per-eye sampling.
5. OpenXR swapchain rectangle, FOV, pose and reference space.
6. Runtime/compositor/stream output, then physical headset.

A shared texture pointer does not mean identical eye contents. Displaying a packed image once for each eye creates four apparent views. Conversely, some repeated content is real artwork. Choose a recognizable near/far landmark and compare flat reference, raw target, each crop and final physical presentation at the same scene/time.

Do not assume PSVR panel resolution equals internal game render resolution. Record both. A sharper Quest panel cannot recover detail that the source did not render. Changes to source resolution, FOV, crop, mask, antialiasing, downsampling and stream bitrate are different operations with different costs.

Treat flat theatre screens separately from stereo projection. The game may use flat logos and loading art before VR, then return to flat during interstitials. Track presentation-state generations so queued frames from an older mode are not shown after a switch. A social/TV buffer is another independent question: prove the title opened that output port before calling a left-eye crop native social output.

## E. Reference spaces and orientation

Write down transformations explicitly: host/world to seated guest, guest render pose back to host, and controller/audio directions. Use the inverse and forward of the same basis, consistently for orientation and position. Test identity, yaw, pitch, roll, a 180-degree starting roll and random round trips. Keep quaternion sign equivalence in mind: q and -q describe the same rotation.

VALID and TRACKED bits are different. A startup runtime can report a valid but untracked pose; active tracking may also use a rolled reference space. Do not require physical uprightness as a prerequisite for pose updates. That can deadlock readiness and leave everything head-locked. Avoid a permanent head-relative gameplay layer as a workaround for incorrect transforms.

Flat screen anchoring and stereo camera orientation must be debugged independently. In HTL, complete initial screen orientation corrected theatre logos, but a yaw-only guest origin left stereo gameplay inverted. Full reference calibration with matching forward/inverse transforms fixed the physically tested case. That does not mean every title needs full pitch/roll recentering. Scope any exception and verify movement, comfort and recenter behavior.

An unconditional texture flip is not a substitute for diagnosing a reference-space roll. Keep the last physically correct image-copy orientation unchanged until evidence specifically implicates texel orientation.

## F. Input and calibration

Test enumeration, connection, ownership, per-frame sampling timestamps, held states, focus and release behavior. A controller working elsewhere on Windows says little about an emulator's polling. A Menu press may need a duration, not a tap; preserved samples must show the entire hold.

System-reserved headset buttons are not reliable game input. Provide a chord involving ordinary exposed buttons and suppress its constituent game actions while active. HTL uses both thumbstick clicks as held OPTIONS; this must not also send L3/R3 or an unrelated recenter. Keep an Xbox/keyboard fallback and identify which executable/profile contains each mapping.

Prefer native comfort options. Distinguish a saved game option from a patched game asset, a compositor vignette/mask, and emulator-generated turn steps. Do not silently force smooth/snap turning for normal play just because a benchmark assumes one. Asset variants should be separate, signature-checked and reversible; original files stay unchanged.

Automatic calibration is a lifecycle convenience, not removal of the game's calibration logic. Gate it on relevant readiness/focus, bound holds, and prevent surprise retries after returning from a system menu. Physical controller/runtime testing is necessary; simulated button injection is not equivalent.

## G. Diagnose graphics corruption before optimizing

Use a minimal defect scene: near/far geometry, one door or poster, a transition and a dark section. Preserve both clean and faulty evidence. Classify candidate causes: wrong target/eye, stale frame, bad vertex binding, overwritten constants, resource aliasing, missing barriers, partial clears, texture streaming and subresource extent.

Use broad synchronization as an isolation tool, then narrow resource dependencies while preserving correctness. Do not ship per-draw CPU completion waits merely because they hide a race. One wait per frame may not protect intermediate work. Verify normal uninstrumented runs: screenshot/readback/recording can serialize away the bug.

Containment is component-wise for dimensions such as mips/layers. Ordinary ordering operators may be lexicographic. Unit tests should cover crossed dimensions, not mirror the code's assumptions. CPU writes and GPU readbacks sharing tracked pages require careful invalidation; disabling readbacks may improve a number while losing real data.

Texture-cache references must survive growth/lifetime changes. Streaming data may not have all mips populated; falling back to a lower mip is a title/format-sensitive policy, not a universal corruption cure. Investigate which bytes are wrong before choosing a fix.

## H. Audio: separate gain, mix, lifecycle and output protection

Never fix relative mix by repeatedly lowering Windows volume. Capture bounded internal and final device-bound streams, optionally silence final playback after capture while retaining processing/pacing. Check sample format, channel ordering, gain units, range, headroom, object/port accumulation, callback completion and filter semantics independently.

A value of 0 means mute for a linear gain but unity for a dB gain. Tiny linear fades mistaken for dB can raise almost-muted ambience to full output. Confirm semantics from guest command traces and API behavior rather than the variable name. If both port and object gains exist, test both together before claiming balance fixed.

A linked-channel limiter can protect output without changing panning ratios; it cannot repair a wrong mix upstream. Do not blanket-mute ambience or use guessed object timeouts that would suppress legitimate effects. Callback stop/unreserve flags need evidence. Synthetic spatial tests, speech recognition, waveforms and physical listening provide complementary evidence, none sufficient alone.

Keep audio-only fixes independent from rendering changes and compare matched performance routes. Remove diagnostic dumps/model downloads after retaining a bounded accepted evidence set. Never upload user audio or game captures without authorization.

## I. Crash triage: identify the failing layer

First preserve log/manifest before relaunch overwrites them. Compute module-relative PC; absolute addresses change across runs. Distinguish a host access violation, a deliberate guest trap/assertion, command arena exhaustion, GPU/device loss, and a guest data-pointer failure.

For guest crashes retain registers, exact instruction bytes, stack/frame pointers and, where justified, bounded local state/callers. Missing symbols do not prevent disassembly. A null read does not justify returning zero or skipping the draw: determine where the pointer came from. Track both the source value and any saved/restored copy.

PS4/SysV code may use a red zone below RSP; Windows exceptions can use the same area. Repeated saved locals reloaded as zero in a leaf is a clue, not automatic proof. Verify existing protection really activated and covered the relevant function. Broad static protection may be partial. Prefer a structural fix that preserves computation over disabling an assertion or ignoring a failed instruction.

HTL's narrow render-leaf reservation is **not reusable as an address patch for another title**. It validates an entire specific function, reserves actual local storage with preserved frame/register/flag behavior, and restores original bytes if generation fails. Unknown versions are untouched. To generalize, derive a correct ABI-aware mechanism and test it; do not cargo-cult the RVA or hash.

For owned command copies, keep span storage alive through asynchronous parsing. Avoid reallocating an arena with outstanding spans. A bounded ordinary arena plus owned overflow blocks/coroutine keepalive can preserve semantics without GPU waits. Test ownership moves, exact capacity, reuse and source mutation.

## J. Reproducible performance and acceptance

Create a feedback-driven route and an independently checked endpoint. Track progress resets explicitly. Use read-only game telemetry with version/path checks when helpful; do not teleport the player to make a navigation test pass. Maintain centered movement in constrained moving geometry and detect genuine game-imposed pauses.

For every candidate record:

| Item | Why |
| --- | --- |
| Upstream/donor/patch revision and executable SHA | Identifies the code actually executed |
| Game identity, source/variant, save/checkpoint | Avoids comparing different workloads |
| Profile, all diagnostic env flags, cache policy | Captures hidden runtime differences |
| Runtime/headset/refresh/transport | Separates display pacing from game speed |
| Route inputs/events/endpoint | Proves progression rather than elapsed time |
| Frame times/FPS/draws/CPU/GPU waits by stage | Explains dips and comparable work |
| Audio/visual/input/physical observations | Prevents an FPS-only regression |
| Failure or interruption classification | Battery/abort/crash are different outcomes |

Use a warm-up and several matched runs, plus fresh controls where needed. Align clocks before assigning FPS windows to events. Short events may lack a whole sample window. Captured/diagnostic runs are not performance acceptance runs. Reboot effects may involve persistent runtime/driver state outside a process, but require isolation before naming a cause.

Prefer a hitch probe that snapshots thread state at actual stalls and lightweight memory/commit telemetry over endless averages. If importing external diagnostics, bound overhead and recheck the normal build. SSW/reprojection can improve presentation at a sustainable source rate but does not make a 40 FPS game render 90 genuine frames; verify image artifacts and latency physically.

## K. Packaging, documentation and continuation

Use a launcher that checks game/runtime paths, isolates profiles, selects OpenXR runtime explicitly, clears obsolete diagnostics, captures provenance and avoids leaving altered game flags after exit. Preserve settings/saves on update. Do not copy the original developer's absolute paths or cached FOV into another machine's installer. Keep source build and runtime install distinct.

After each meaningful result update a short resume document and link it from repository instructions. Include current launcher, exact hash, local-only paths, patch order, feature flags, configuration assumptions, known regressions, failed hypotheses, user-confirmed outcomes and next uncertainty. Preserve detailed historical reports, but clearly mark them historical rather than letting contradictory defaults accumulate.

Clean up redundant generated captures/build variants only after retaining useful evidence and rollback points. Check Windows absolute bounds before deletion; large hard-linked game assets are not independent duplicate files. Keep secrets/game data out of commits, validate links, check patches against pinned source, and explicitly state when clean-machine setup or physical testing is still missing.

The most valuable reusable result is the process: separate layers, make one interpretable change, preserve accepted behavior, and let evidence invalidate the preferred explanation.
