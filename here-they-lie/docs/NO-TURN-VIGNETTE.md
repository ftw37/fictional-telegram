# Smooth turning and no turning vignette

October 22 test: a separate local game view successfully loaded a one-asset override, used smooth turning, traversed the opening train, and exited through the open left-side doorway onto the station platform. No new save checkpoint was verified. The station beyond the train remains a separate traversal test.

`scripts/build_no_turn_vignette.py` builds this local variant from the user's extracted CUSA05344 v01.00 copy. It validates the original archive index, asset hash, and a unique assignment signature. It changes only the four-byte float for the turn-active `VRPeripheryGoal` from 0.8 to 0, then writes a separate `_P.pak` overlay. The original archive and executable are not patched. Large prerequisites are hard-linked into a new local game directory; command-line and other small files are copied separately.

The script and documentation contain no game assets. The generated archive, linked game files, memory inspections, and screenshots stay private and must never be committed or distributed.

The effect is in `/Game/Blueprints/GameMode/BP_DGPlayer`, in its main event graph and `SetPeripheryCircle` event. The material collection is `MP_PeripheryCircleVR`; the radius and fade parameters are `CircleRadius` and `CircleFadeArea`. Cinematic effects, scene fog, and ordinary postprocessing remain outside the changed assignment.

Smooth turning was selected by unchecking **VR Drive Mode** in Options → Controls. This preference is saved by the game and shared with other runs using the same emulator user profile; the overlay itself changes only the turning vignette. Recheck the setting if manually changed later. Desktop stereo output retains its normal circular eye boundaries; the additional narrowing during turning is the disabled effect.

Validation: overlay index SHA-1, entry SHA-1, entry-header/index agreement, correct mount/path, equal asset length, and an exact four-byte change all passed. A smooth turn kept the full eye view visible. Calibration, New Game, the opening transition, carriage door interactions, fire-car traversal, station arrival, and leaving the train all worked in the conservative renderer with the original frame limiter. Physical Quest headset output was not tested in this run.

## Train route established in the test

1. At the dark controllable start, turn right and proceed down the aisle.
2. Approach the end doors closely and press Cross. Walk across the short connection, center on the next closed doors, and press Cross again. Each pair requires separate interactions.
3. Continue through the following car. The user describes pig-headed creatures and a temporary movement lock; wait for them to disappear. The test progressed beyond this car, but did not capture the creatures clearly enough to verify that event visually.
4. Open the next two sets of doors separately to reach the burning car.
5. Center the player in the aisle before moving through the fire. The test repeatedly caught on side geometry until this was corrected. Carriage-relative read-only measurements established the player was about a metre off center; normal sideways input brought it within a few centimetres. No teleportation or player-memory writes were used.
6. Proceed through the fire and let its scripted sequence finish. The test saw fire followed by darkness/embers and progressed to the far connection; the burning figure itself was not clearly captured.
7. Open the next two doors, enter the lit station car, and walk along it.
8. Turn left, line up with the open side doorway, and walk onto the platform. Platform geometry surrounding the player confirmed exit from the train.

The private exploratory input log is `HTL-Development/performance-runs/smooth-no-vignette-subway/inputs.txt`. It contains lengthy pauses and unsuccessful sidesteps; it is evidence of this session, not a validated unattended regression replay. A compact, repeatable replay still needs a separate run.

Useful measured control behavior: a full sideways-stick hold moved approximately 33–38 cm per second in this section; normal forward walking was around 43 cm per second, and R2 walking covered about 9.7 metres in an eight-second input. These are observations from this run, not fixed game constants. Raw world coordinates are unsuitable for aisle centering because the train moves and turns; use the movement-base transform.
