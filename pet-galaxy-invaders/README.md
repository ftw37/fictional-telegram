# Galaxy Invaders — PET browser edition

A playable browser recreation of the Commodore PET game supplied in `Space Invader.zip`. The original program calls itself **Galaxy Invaders**.

## Play

Download and unzip `Galaxy-Invaders-Browser.zip`, then open `index.html` in a modern browser. All assets are local; no account, installation, build, or internet connection is needed. If your browser restricts local HTML, serve this folder instead:

```sh
python3 -m http.server 8080
```

Then open `http://localhost:8080` in your browser. With Node.js installed, `npm start` runs the same server bound to your own computer.

| Command | Action |
| --- | --- |
| B / Begin Game | Begin or restart |
| . / = | Move left / right |
| Arrow keys | Alternative movement |
| Space | Fire; hold for repeated shots |
| [ / E | Stop |
| P / Escape | Pause or resume |
| C / Setup | Change settings for the next game |

Touch devices have movement and fire buttons. Sound is optional and initially off. Changing tabs automatically pauses the game. Your best score and settings are saved locally when browser storage is available.

Clear each formation to start another wave. Enemies reverse direction and descend at the edges; the game ends when they invade or you run out of lives. Shelters stop both sides' shots and gradually erode. Hit the passing mystery ship for a random bonus. Setup offers difficulty, starting lives, and formation width.

## What was recovered

`original/space-invader.prg` is the unmodified 5,783-byte program from the supplied archive. Its SHA-256 is `6b0e22e95798f28c201c4107c8c4f282b1a6f798d6d7fa4db081ccaf1c560a92`.

The program loads at `$0401` and contains a tokenized BASIC menu/instruction launcher plus 6502 machine code. The launcher starts the arcade code with `SYS 3480` (`$0D98`). `original/launcher.bas` is a readable listing, with graphics/control bytes written as `{PETSCII:XX}` placeholders; it is a reference listing, not a directly importable BASIC file. `original/program-info.json` records recovered parameter names and byte values. The supplied program's author was not identified.

The original instructions establish the title, movement/fire/stop commands, successive enemy racks, random mystery-ship bonus, and loss on invasion or exhaustion of men. Original defaults recovered from the parameter table include **20 men**, **six initial enemy columns**, and **one additional column per rack**.

## Browser adaptations

This is newly written JavaScript based on the recovered program and instructions. It does not execute the PET machine code and has not been validated as a cycle-accurate port. The 320×200 green monochrome screen evokes a 40-column PET display; sprites are newly drawn pixel art rather than extracted PET glyphs.

Movement speeds, firing intervals, collision boxes, three enemy rows, destructible shelter shapes, brief invulnerability, and difficulty choices are browser implementations. Enemy scores are 30/20/10 by row; mystery bonuses are 50/100/150/200/300. Formations grow to a maximum of 12 columns and shelters renew each wave. These details are adaptations, not claims about the original executable. Arrow keys, touch input, pause, optional synthesized sound, and a persistent best score are conveniences added for this edition.

## Develop and verify

No runtime dependencies or build step. Edit `game.js` for simulation rules, `app.js` for rendering/input, and `styles.css` for presentation. Run the gameplay tests with Node.js 18 or newer:

```sh
npm test
```

Validation completed: 12 gameplay tests passed, covering movement limits, shooting/scoring, shelter damage, life loss/invulnerability, invasion, edge reversal/descent, wave progression, mystery bonuses, pause, and restart. Chromium checks also passed for startup over a local HTTP server, original keyboard controls, scoring, pause, settings on restart, and a 390-pixel touch layout, with no JavaScript errors. Chromium's managed policy blocked `file:` navigation in the test environment, so double-click startup was not browser-tested here; the scripts use no imports, network requests, or other server-only features.
