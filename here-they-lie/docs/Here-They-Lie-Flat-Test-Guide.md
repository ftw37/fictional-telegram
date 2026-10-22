# Here They Lie — flat test

Launch Test-Here-They-Lie-2D.cmd (or Play-Here-They-Lie-Flat.cmd).
The emulator must be closed before starting another session.
This uses the single-camera -nohmd configuration. There is no VR calibration,
Options hold, simulated head movement, or automatic menu/button sequence.

| Key | Action |
| --- | --- |
| W / S | Move forward / backward |
| A / D | Move sideways left / right |
| Q / E | Turn left / right |
| N or keypad 2 | Cross / accept / start |
| Enter | Options / pause, available when needed; not required for calibration |
| T / G | Previous Q/E shoulder actions (L1 / L2) |

Opening sequence supplied by the user:

1. Title/menu scene: an alley with a woman at the far end.
2. Start the game; the viewpoint drops down.
3. White transition.
4. Cutscene: the woman stands in front of the subway.
5. Subway doors open in front of her; the player enters the subway.
6. Transition to a controllable interior that becomes dark and dreary.

Wait for the final stage before evaluating walking and turning. Camera movement
in the preceding sequence is scripted and is not evidence that input works.
Do not use the double horse-head artwork alone as a stereo-error indicator:
the user confirmed it is also visible in the 2D image.

The flat launcher now also disables Unreal's asynchronous package-loading thread as a workaround for the observed New Game loading crash. One retry reached the dark subway successfully; long-term stability is not yet established.
