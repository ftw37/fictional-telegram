# HTL Quest Touch mapping

The HTL launcher enables `SHADPS4_HTL_TOUCH_CONTROLS=1`. Build 38 sends the left Touch stick as the left gamepad stick and the right stick's horizontal axis as the right gamepad stick's horizontal axis, with a 15% rescaled dead zone. Vertical right-stick input stays neutral; the headset supplies looking direction.

Right A is Cross (interact/accept), left X is Circle (flashlight/back), right trigger is R2 (faster walking), and left menu is Options when the runtime delivers it. Right B is Square, left Y is Triangle, and grips remain L1/R1. Both stick clicks reset the view; an individual right-stick click sends R3.

In this opt-in mapping, touchpad gestures, grip-assisted synthetic view steps, and the two-button microphone gesture are suppressed. Without the flag, the existing Astro Bot-oriented controller mapping is preserved. Smooth versus snap turning remains the game's control preference; uncheck VR Drive Mode for smooth turning.

Validation: Release compilation succeeded; installed executable SHA256 `B43BB070A6C8969E1E0E2287C4C460AA62A9D2846D41CA0BCC2C47FAE11470DC`. The exported compatibility patch applied to 36 pristine files and matched the source tree. Physical Touch controllers and SteamVR delivery are still unverified. The previous build is retained locally as a fallback.
