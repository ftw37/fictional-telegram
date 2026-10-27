# HTL Quest Touch mapping

**October 26 isolated Quest candidate:** both thumbsticks pressed IN now sends OPTIONS while held, consuming L3/R3 and replacing the synthetic recenter chord for HTL. Normal stable builds retain their older mapping. SteamVR/Meta may reserve the physical menu buttons. See [candidate notes](QUEST-CONTROLLER-STARTUP-2026-10-26.md).

## Automatic startup calibration (build 39)

Quest launches now set `SHADPS4_HTL_AUTO_CALIBRATE=1`. After at least 30 delivered game frames, valid tracked headset frames, and three seconds of focused controller updates, the emulator holds Options for two seconds once, then releases it. Face forward during startup. This automates the game's initial heading setup rather than removing its calibration logic. Preview launches leave the helper off.

The countdown restarts if focus/readiness is lost before the hold. An interruption during the hold cancels further automatic attempts, preventing an unexpected pause after returning to the game. Manual Options and both-stick recentering remain available. Physical headset confirmation is pending.

Build 39 compiled and was installed. The actual startup state-machine tests passed hold/release timing, pre-hold focus reset, cancellation without retry after interruption, and clock-gap handling. The compatibility patch applied to 37 pristine files and matched the working source.

The HTL launcher enables `SHADPS4_HTL_TOUCH_CONTROLS=1`. Build 38 sends the left Touch stick as the left gamepad stick and the right stick's horizontal axis as the right gamepad stick's horizontal axis, with a 15% rescaled dead zone. Vertical right-stick input stays neutral; the headset supplies looking direction.

Right A is Cross (interact/accept), left X is Circle (flashlight/back), right trigger is R2 (faster walking), and left menu is Options when the runtime delivers it. Right B is Square, left Y is Triangle, and grips remain L1/R1. Both stick clicks reset the view; an individual right-stick click sends R3.

In this opt-in mapping, touchpad gestures, grip-assisted synthetic view steps, and the two-button microphone gesture are suppressed. Without the flag, the existing Astro Bot-oriented controller mapping is preserved. Smooth versus snap turning remains the game's control preference; uncheck VR Drive Mode for smooth turning.

Validation: Release compilation succeeded; installed executable SHA256 `B43BB070A6C8969E1E0E2287C4C460AA62A9D2846D41CA0BCC2C47FAE11470DC`. The exported compatibility patch applied to 36 pristine files and matched the source tree. Physical Touch controllers and SteamVR delivery are still unverified. The previous build is retained locally as a fallback.
