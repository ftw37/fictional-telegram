# Native game comfort controls — October 26, 2026

Normal local preview, SteamVR, TV and Quest-startup test launchers now select the original extracted game (`HTL-Test/game/uroot`), without the no-turn-vignette overlay. The local overlay directory is retained only as an optional historical experiment. Installer defaults now use the original game too.

Use **Launch-Here-They-Lie.cmd** for desktop preview or **Play-Here-They-Lie-SteamVR.cmd** for the normal headset build in `HTL-Development/test-vr`. Older shortcuts whose names contain No-Vignette now also select original assets for compatibility. The isolated Quest startup test retains its experimental executable but uses original game assets.

Turning is already handled by the game through normal right-stick inputs (Q/E on keyboard). Smooth turning was previously selected by unchecking **Options → Controls → VR Drive Mode**, and is saved by the game. No runtime smooth-turn forcing was found. Change VR Drive Mode and the game's available comfort options in-game; no save/profile reset was performed. The original Blueprint's turn-periphery behavior is restored by using the original archive, so the game can apply its native comfort effects. No promise is made that the game exposes every internal vignette parameter individually.

Controller mappings, audio, graphics settings and emulator executables were not changed. No new build is required. Verified launcher game paths and absence of a `_P.pak` override in the original archive directory. An interactive in-game comfort menu check remains for the next play session. The automated subway route still assumes smooth turning; do not treat it as setting-independent after changing game comfort preferences.
