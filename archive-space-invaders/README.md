# Space Invaders — Internet Archive PET edition

This browser port uses **SPACE INVADERS from the exact disk linked by the user**:
[Internet Archive item d64_petgame_space_invaders](https://archive.org/details/d64_petgame_space_invaders).
It is a different executable from the earlier `pet-galaxy-invaders` project.

## Play

Open `index.html` in a modern browser, or double-click `Play-Space-Invaders.cmd` on Windows.
No installation, dependencies, network connection, or build step is required.
If local HTML is restricted, run `npm start` with Node.js 18+ and open
<http://127.0.0.1:8082/>. The server binds only to this computer.

- **B / Begin Game:** start or restart with the original three lives.
- **Arrow keys:** move; comma and period are alternatives.
- **Space:** fire. Release and press again for each shot.
- **P / Escape:** pause or resume. Switching tabs also pauses.
- **Original Opening Screen:** show the original external-amplifier wiring diagram.
- **Sound:** optional approximation of the PET CB2 audio output; off initially.

Touch devices have movement and fire buttons. Refresh the page after editing.

## Exact source and preservation

The downloaded disk is preserved as `original/PET_Games_Disk_04_19xx_-.d64`.
Its SHA-1 matches the Internet Archive metadata:
`a4c10db6937a609e15f30d448b08f2130663250a`.

The disk directory entry **SPACE INVADERS** was extracted by following its
Commodore DOS sector chain. The unmodified 7,169-byte result is preserved as
`original/space-invaders.prg` and embedded without modification in `data.js`.
Its SHA-256 is:
`b3a350bc7b74b017f70961588c661529390d04efdd588e268bc89b2cc445b8ef`.
It loads at `$0401`; its BASIC stub is `10 SYS(1039)`.

The original 1,000-byte opening screen is copied by the executable from `$1C00`
to PET screen RAM. It matches the amplifier diagram in the archive's screenshot.
The game's author and original publication date have not been established.
Archival availability is not a claim that the game is public domain.

`original/pet-characters.bin` is the existing project's preserved VICE PET ROM
`characters-2.901447-10.bin`, from
[VICE's PET data](https://github.com/VICE-Team/svn-mirror/blob/main/vice/data/PET/characters-2.901447-10.bin).
Its SHA-256 is `da3374c21d6ea440cef5f338ce3f524e0a1e40dcb1ef64446c695f92c636f1fa`.

## How the port works

`cpu6502.js` interprets the original machine code. `game.js` supplies 1 MHz CPU
time, 60 Hz interrupts, the ROM IRQ register-save/restore convention and `$0090`
dispatch vector, keyboard input at `$E812`, a descending timer byte, and the VIA
port B retrace bit at `$E840`. The renderer draws the original `$8000` screen RAM
using PET character glyphs, including inverse characters. Gameplay, formations,
projectiles, collisions, scores, shelters, lives and waves remain original code.

The browser's Begin button calls the original parameter initializer at `$0E00`
and new-game entry at `$0490`. It skips the original animated attract sequence;
the original amplifier opening screen is retained. The host supplies the small
ROM entry points used here instead of loading BASIC/KERNAL ROMs. This is a
focused adapter, not a complete or cycle-accurate PET emulator. The retrace duty
cycle and optional sound are approximations; exact hardware timing and sound
parity with VICE are not claimed. Original live gameplay bytes are not patched.

## Develop and verify

Edit `app.js` for browser controls/audio, `styles.css` and `index.html` for the
page, and `game.js` for PET host behavior. Regenerate embedded assets from the
disk and preserved font with `python tools/rebuild_assets.py`.

Run `npm test`, or double-click `Test-Space-Invaders.cmd` on this computer.
Eight tests verify source disk identity and extraction, original startup screen,
formation progression, keyboard movement and bounds, original firing logic,
pause/restart, a complete game ending, and PET inverse glyphs. The existing
`pet-galaxy-invaders` suite additionally exercises the shared CPU interpreter.

Browser checks cover startup, starting/restarting, keyboard input, pause/resume,
and the opening screen. No game JavaScript errors were observed. The responsive
touch layout is included but has not yet been exercised on a physical touch device.
The default browser's double-click launch is provided but was not independently
tested; automated browser checks use the loopback HTTP server.
