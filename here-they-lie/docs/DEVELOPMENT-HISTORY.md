# Here They Lie: investigation history and engineering record

This record reconstructs the project's significant decisions from the conversation, source changes, reports and logs. It is not a verbatim transcript or a claim that every historical test was instrumented. [Resume here](RESUME-HERE.md) is authoritative for today's installed candidate; [the playbook](PSVR-PORTING-PLAYBOOK.md) extracts reusable methods.

## 1. Goal and provenance

The user wanted a personally supplied PSVR game, Here They Lie, playable on Quest 2. Streaming from a Windows PC was acceptable; rewriting a PS4 executable as a native Quest application was not the chosen path. The project initially used AstroQuest/shadPS4 PSVR compatibility work, later integrated onto official shadPS4 0.20 source with pinned donor code and selected official fixes. The Git repository also contains unrelated PET/browser and Inform projects; Here They Lie lives in its own subdirectory.

The tested game is CUSA05344 version 01.00. Game PKGs, extracted executable/assets, Sony modules, keys, saves, captures, runtime dependencies and build binaries stay local. Scripts, source patches, test code, hashes and findings belong in Git. The user corrected an initial repository-name mix-up: the actual remote is ftw37/fictional-telegram, not fictional-bassoon.

## 2. Establishing game behavior before interpreting rendering

The user supplied critical reference behavior: alley title scene with a woman at the end; starting the game drops the viewpoint; white transition; woman outside the subway; doors open and the player enters; dark/dreary controllable car. Those short cinematic transitions are different workloads from stationary gameplay. Movement during them is not evidence that input or tracking works.

Early calibration did not clear with Enter or keypad Enter. Motion simulation initially showed severe clipping, even with rotation only. Game tracker initialization and recenter behavior needed investigation; do not assume repeated OPTIONS taps fix every calibration state.

Earlier process-only ABI diagnostics adapted a 144-byte tracker init structure to a 128-byte host expectation, moving pointer/size groups from guest offset 0x40 to host offset 0x48. A GPU submission struct was 0x228 versus the host's expected 0x288. These observations were specific to the checked game/donor ABI. They are not permission to ignore another title's camera payload or weaken arbitrary size checks. Version-pinned process hooks were later superseded by source compatibility changes; hard-coded hooks must refuse unknown executable hashes.

## 3. Untangling the four views, eye differences and social output

An early presenter displayed the entire packed stereo source once per eye. That explains a four-view display without proving four independent cameras were being combined. Both eye descriptors could point to the same whole 1920x1080 source while the two halves contain different views. Source identity, cropped eye identity and final compositor output must be measured separately.

The user noticed the subway door behind the woman appeared differently between eyes. We used it as a scene landmark. The horse-head poster seemed mirrored/stacked, but the user then found the same double head in the flat image: an important false-positive lesson. Artwork can look like a rendering bug.

Original PSVR panel dimensions are 1920x1080 total (960x1080 per eye); a game may render at a different internal resolution. Source viewports, scissors, per-eye transforms, UVs and format/layout semantics matter more than assuming all PSVR titles use the same packing. Preserve a flat `-nohmd` reference alongside desktop stereo and physical OpenXR checks.

The emulator recognized a separate social output port but originally did not present it. We added an optional TV window. Here They Lie had not been observed opening the dedicated social port, so the fallback is an explicitly labelled left-eye crop. It is not established as Sony's canonical social output. The user wanted TV off by default; it remains optional. Flat non-VR mode is not proof that a native PSVR social buffer exists.

## 4. Geometry corruption: evidence and failed simplifications

The woman/train transition and later subway showed broad colored triangles, wedges and semi-transparent surfaces across an eye. At times distant objects appeared in front. Several isolation results mattered:

- Dense captured runs looked clean while ordinary playback remained corrupt. Readback/capture altered timing; clean screenshots did not qualify the uninstrumented run.
- Copying graphics commands by itself did not remove the triangles.
- A constant-snapshot diagnostic with draw waits stopped flicker. Synchronization-only tests stayed clean, so private constant copies were not necessary for that observed result.
- One GPU/CPU wait per frame seemed adequate in a stationary scene but failed the transition and later produced broad corruption. The user corrected an accidentally selected success answer; final classification was failure.
- Per-draw completion waits recovered correctness but were much too slow (historical present-count estimate around 18/s, not rigorous game FPS).
- GPU dependencies without CPU completion waits recovered observed transition/subway correctness, providing a conservative baseline. Later work narrowed to targeted pass/image ordering and final vertex-input rebinding, real occlusion counters and proper cache readbacks.

A separate mip/layer bug used lexicographic ordering as a containment test. Component-wise containment and dimension-wise merge were correct fixes, but did not independently explain all flickering. Keep that distinction. Native tests covered 16,384 combinations.

The damaged OPTIONS graphic and changing grey haze were useful correctness probes. In the newer 0.20 profile, disabled readbacks could lose GPU-written bytes when CPU updates shared a tracked page. Relaxed readbacks restored checked texture mips and surfaces; neighboring mips being correct helped localize corruption. Avoid returning to disabled readbacks to pursue FPS. Cache lifetime/locking and thread-local streaming hashes also addressed warm-cache loading failures. None of these proves every later-game artifact has been fixed.

Earlier broad-barrier notes remain historical. Current qualified launcher flags are `--renderer-sync pass --real-occlusion`; do not copy obsolete `broad`, `frame`, `--fast-graphics` or diagnostic marker settings into normal play merely because an old report calls them the default.

## 5. Repeatable subway traversal and performance

Manual reference route: at the dark controllable start, turn right, stay centered, open the current car's exit door, cross the connection, then separately open the next car's entry. Wait out the pig-headed-creature scare: movement is temporarily locked. Continue through later cars and walk down the center through the fire. Side geometry repeatedly trapped traversal; it was not necessarily a closed door or emulator failure. Eventually the train stops; exit the open left-side doorway onto the station platform. The user later reported artifacts farther along the platform, after turning right and walking alongside the train, rather than immediately on exit.

Feedback replay reads the player's position relative to the moving carriage. Absolute world coordinates mislead because the train itself moves and turns. It uses normal, bounded controller input pulses, no teleportation or game-state writes. Door approach and door interaction are separate events; a movement-base change can happen before the next door is in reach. Detect actual endpoint state and inspect the platform view, rather than counting elapsed script time as a pass.

The automation resets progress and assumes a known menu order, game version and saved smooth-turn setting. It is not an emulator save state or deterministic engine replay. Its hard-coded startup offsets can fail under changed loading/menu conditions. After restoring user-controlled comfort options, the route remains a specialized benchmark requiring its expected turning setting; do not silently reset a user's preferences to make the benchmark work.

Official 0.20 graphics baseline passed three warm-cache New Game-to-platform routes. Audio-build stage medians were near 60 FPS in car/scare/fire intervals and roughly 51–54 FPS at station arrival; the baseline control was about 53 there. Later user areas ran around 40 FPS. Earlier intermittent 12 FPS versus 60 FPS observations at superficially similar views remain incompletely explained. Compare draw count, visibility, shader/cache state, game events and actual frame timing before calling two views equivalent.

Do not confuse monitor refresh, game tick speed, rendered FPS, headset refresh or compositor synthetic frames. Native 90 FPS has not been established. Virtual Desktop SSW is an optional compositor experiment, not an emulator performance fix; 45/90, 40/80 or 60/120 source/display pairings require actual pacing and image-quality checks. Quest 2 source softness follows lower-resolution game eyes; blindly increasing resolution costs render/streaming time and cannot recreate missing texture detail.

Instrumentation must distinguish normal mode, CPU-only scopes, GPU timestamp/capture mode, audio capture and silent device output. Preserve exact executable hash, route/runner hash, configuration, caches and stage-aligned timing. Presenter IDs alone are not rigorous completed game-frame counts. Avoid declaring success from a single capture or noisy test. See dated reports for measured route names and FPS tables.

## 6. Controller polling, Touch ownership and native comfort

Xbox worked elsewhere on Windows but not in this emulator. A polling fix publishes recurrent timestamped controller samples, including held OPTIONS, and keeps HTL's right stick as an ordinary gamepad stick instead of Astro Bot-style touchpad gestures. Xbox Menu held about two seconds cleared calibration, confirmed by the user. Wrong launcher selection later caused another apparent failure; the user corrected it. Always confirm exact launcher and executable before investigating input mappings again.

Keyboard: WASD movement, Q/E right-stick turning, N Cross, B Circle, V Square, C Triangle, O R2, Enter OPTIONS, Space touchpad. Xbox face/shoulder/trigger/stick-click mapping follows ordinary PS4 equivalents; View maps touchpad click. Headset/gamepad ownership depends on which is actually used; a connected controller is not proof it owns active input.

Touch: right A Cross, right B Square, left X Circle/flashlight, left Y Triangle, right trigger R2/faster walking, grips L1/R1, left stick movement, right horizontal stick game turning. Runtime-reserved menus made left Menu and right Meta/system buttons unavailable as dependable game OPTIONS. We repurposed simultaneous left/right thumbstick IN as OPTIONS, forwarding the full held duration and suppressing L3/R3 for the chord. Individual clicks keep L3/R3. For HTL this replaces synthetic recenter; other donor-title behavior is preserved. It does not remap Meta's reserved button itself.

A no-vignette experiment created a one-asset `_P.pak` override of BP_DGPlayer's turn-active VRPeripheryGoal from 0.8 to 0, with strict archive/asset/signature checks. Large prerequisites were hard-linked into a separate view; no original archive modification. Smooth turning was independently selected by unchecking native VR Drive Mode. Later the user asked to restore in-game comfort control. Launchers now select original game assets, leaving saved comfort preferences untouched. Existing shortcut names containing No-Vignette are legacy labels only. Never assume the overlay and saved turning setting are the same mechanism.

## 7. Audio: the loud train was a gain interpretation error

The user first heard deafening train/title ambience, nearly inaudible dialogue and a train sound persisting even at the station. Reducing system/game volume cannot repair relative balance. Both NGS2 port levels and Audio3D object gains were incorrectly treated as dB, although game commands contained linear fades (0, 0.0025, 0.067, 0.223, 0.447). A dB conversion turns 0 into unity and a tiny fade into almost full output. Both paths had to be fixed; one-path experiments were incomplete.

Finite nonnegative gains now remain linear; invalid/negative values are silent. Legacy dB overrides are diagnostic only. A custom sampler-filter module 0x13 uses the existing biquad path. Guest disassembly independently checked callback layout and 0x20 finish/unreserve semantics: no guessed stop flag, fixed train timer or blanket ambience mute was adopted.

A linked-channel peak ceiling of 0.25 (about -12.04 dBFS), immediate attenuation and 250 ms release adds output headroom without boosting quiet content or changing stereo balance. It is not the primary balance fix: correct linear gains are. Startup volume is 20%, independent of Windows/headset volume.

Bounded internal and device-bound recordings allowed objective checks without playing the old deafening mix. Final playback could be zeroed after capture while preserving audio processing/pacing. Native tests covered overload, silence, nonfinite samples, stereo ratios and spatial mirror/multi-block behavior. A complete accepted 418.112-second device-bound capture had no full-scale samples. Offline Vosk recovered 48 words (34 high-confidence) versus 4 in a bad interpretation test. Recognition supports intelligibility, not proof of perfect source mastering or HRTF. The user subsequently explicitly confirmed speech, footsteps and ambience sounded good.

Three exact-audio-binary routes and a preserved graphics control showed no consistent sampled-stage FPS regression. No renderer changes were made for the audio correction. Temporary captures, model and duplicate binaries were cleaned; a final output, short comparisons and reports remain local. No audio was uploaded. See AUDIO-FIX-2026-10-25.md for numerical details and cleanup accounting.

## 8. Physical Quest startup: the successful reference-space fix and its failed predecessors

Virtual Desktop initially reported no computer because Streamer had no account configured. Resolve connectivity/account prerequisites before touching emulator code. Actual physical testing used Virtual Desktop plus SteamVR/OpenXR, with private simulator overrides cleared. Desktop mirror/compositor probe results did not predict every physical behavior.

The first physical run showed upside-down logos/calibration; Menu could make it upright. Logs showed initial quaternion near `(0,0,-1,0)`, a 180-degree roll, first with valid-but-untracked flags 0x3 and later actively tracked flags 0xf. Recentring alone did not resolve it. Do not assume all active runtime reference spaces are upright, or that valid means tracked.

Failed candidate sequence, retained here to prevent repetition:

1. Waiting for eight tracked **upright** poses before feeding tracking/display suppressed logos until the menu. Calibration could then appear upright, but startup was black.
2. Showing head-relative theatre/projection while waiting brought the logos back but never released a reference that remained rolled. The user reported no turning at all: everything moved with the head. This was our regression, not a headset defect.
3. Removing the upright prerequisite restored tracking; theatre screens anchored to the full initial head pose became upright and world-anchored. But calibration/main menu/game stereo remained upside down.
4. Inspection showed guest seat calibration used YawOnly(host_head). That removed heading but retained runtime roll in the guest camera. For HTL/OpenXR, the candidate now uses the complete normalized starting orientation, with the inverse for guest poses and matching forward transform when presenting render poses. On the first fully tracked valid pose, it refreshes the seat to replace any earlier untracked boot reference. Tracking updates are independent of presentation-readiness heuristics.

The user then confirmed logos, loading, calibration and gameplay upright with working tracking. Full orientation reference round-trip and movement-preservation math-model checks passed, but the physical user result was the actual orientation acceptance. Keep the theatre path and guest/projection path distinct. No global texture Y flip was added; the existing XR_FLIP_Y=0 remains.

The theatre path aligns the quad to the complete initial head orientation; it is world-anchored once tracking is ready, not permanently head-locked. Before readiness a head-relative fallback can show startup imagery. Recalibrating while looking/tilting establishes that reference, so face forward for the initial check. Do not reintroduce a permanent head-relative stereo projection.

## 9. Separate crashes: command ownership versus render-leaf stack corruption

### A. Loading command-copy arena overflow

First physical crash: Liverpool CopyCmdBuffers assertion, DCB copy buffer out of reserved space. Fixed-size command arenas were 2 MB. Reallocating a vector while in-flight spans point into it, disabling copies, or removing the assertion would be unsafe substitutes.

Current candidate serializes reservations with SubmitDone, keeps the usual arena allocation unchanged, and uses independently owned vectors for submissions exceeding remaining capacity. Owners move into graphics/CE coroutines and live through parsing. No extra GPU completion wait. A native helper test covered exact capacity, overflow, source isolation, offset behavior, arena pointer stability and moved ownership. The later physical session passed loading and several checkpoints, so this initial assertion did not recur in that observed session.

### B. Repeating guest render leaf crash

Multiple physical sessions later failed on guest RenderThread 2 at image RVA **0x1b745eb** (absolute address changes with load base), reading address **0x58**. Instruction: `mov r8d,[rbx+rcx+0x58]`. Added register logging showed RBX=RCX=R9=R10=0, RSI=1, R14=0, while prior inner work had produced output. This is not the same as command-buffer exhaustion or a host texture-cache reference crash.

Disassembly of the enclosing leaf at RVA 0x1b74520 showed a frame pointer and five saved registers, no explicit local stack allocation, locals at rbp-0x40/-0x48/-0x50/-0x58/-0x68, and reloads of count/stride/base/offset before the second loop. These sit below current RSP in PS4/SysV red-zone storage. Windows may use that area on exception dispatch. Reloaded zeros fit that hypothesis, but no direct overwrite watchpoint identified the precise event.

We tried existing broad Windows guest red-zone static protection. The log confirmed it active and warned of 222 unrelocatable instructions; the same crash recurred. Thus this setting alone was not a fix, and partial coverage cannot be treated as proof the target function was protected. Reverted `General.redzone_patches=false` in the isolated profile.

The narrower experiment reserves a real 128-byte frame for this one function:

- Opt-in `SHADPS4_HTL_LEAF_FRAME=1`, only invoked for CUSA05344 eboot.
- Full 1,933-byte function SHA1 must match `7625cf6a4bd78e32082708f5275389878fedb1aa`; unknown versions are untouched.
- Original 13-byte prologue replayed in a trampoline, then flag-preserving LEA reserves 128 bytes. RBP and saved-register locations retain their meaning.
- Epilogue trampoline restores RSP, replays original pops and rejoins the original return sequence. No null-read bypass, dropped draw, altered loop bounds or on-disk game patch.
- If trampoline generation fails, original entry/exit bytes are restored. Keep this narrowly scoped rather than generalizing it to unknown functions.
- Native x64 synthetic smoke deliberately overwrote memory below actual RSP. Original leaf lost its canary; reserved-frame leaf retained it and returned correctly 1,000 times. This is a controlled stack-mechanics test, not a full reproduction of Windows exception handling or the whole game.

Build a91cada6f8352e21b92672ae668b64fa9aed7f230066a70aef9421c0db047470 logged the explicit frame installed. The user reported the next run did not crash; the session ended at headset battery exhaustion. This supports the fix and the stack hypothesis, with limited duration. Preserve orientation-confirmed binary 69f00... as a comparison and longer-test before full-game claims.

## 10. Lessons about investigation practice

User corrections were often decisive: an accidentally selected success response, the intentional double-horse artwork, missed transition observation, wrong launcher, center-aisle navigation, and battery-limited session all changed interpretation. Record corrected conclusions, not the first convenient answer.

A reboot may clear driver/runtime/memory pressure across process launches, but its association with cleaner visuals does not establish a particular cache bug. A fresh emulator process does not reset every driver/OS/headset state. Isolate instead of hand-waving away variation.

Preserve accepted executables/configs and exact rollback points. The same build-output folder has held multiple different candidates; hashes and manifests beat names. Keep experimental profile separate, TV off by default, diagnostics opt-in, and intrusive capture separate from performance evidence. Report what changed, why, what passed and what remains unqualified.

For another PSVR title, reuse framework and methods, not this game's ABI sizes, asset signature, render-leaf address, memory offsets, social assumptions, timing patches or measured route. GPL upstream/source provenance and separate proprietary data are part of a reproducible project, not an afterthought.
