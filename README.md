# Inca Curse — recovered Inform 7 edition

The repository also contains [Galaxy Invaders, a playable PET-style browser game](pet-galaxy-invaders/README.md). Download its [standalone browser ZIP](pet-galaxy-invaders/Galaxy-Invaders-Browser.zip), unzip it, and open `index.html`.

This is a working, table-driven Inform 7 reconstruction of the game in
`INCACURS.T64`. It is not the original author's high-level source: the tape
contains a compressed 6502 executable, not BASIC or Inform source. The game
identifies itself as **Adventure B: Inca Curse**, published by Artic Computing.

## Open it in Inform 7

1. Create a new Inform 7 project.
2. Open `Inca Curse.ni` in a text editor and paste the entire file into the
   project's Source pane, replacing the starter source.
3. Choose **Glulx** as the story format and click **Go**.

No extensions, T64 reader, emulator, or Python packages are needed to compile
or play the Inform story. The source was compiled with Inform 7 **10.1.2** and
Inform 6 **6.41**, and played with Glulxe. It also compiles with Inform 7
**6M62** and Inform 6 **6.33**. The explicit `Use MAX_STATIC_DATA of 2000000.`
setting accommodates the recovered tables in that older compiler.
`Inca Curse.ulx` is also included for a Glulx-compatible interpreter.

If you copied the earlier source into 6M62 and got an Inform 6 memory error,
replace it with the updated source, or add `Use MAX_STATIC_DATA of 2000000.`
near the top. Keep the story format set to Glulx. The generic error page's
`MAX_PROP_TABLE_SIZE` text is only an example; the reproduced failure is
actually `MAX_STATIC_DATA` at its old default of 180000.

The included `Inca Curse.inform/Source/story.ni` contains the same source for
those who prefer a project directory. Creating a new project and pasting the
single source file is the most portable route across Inform IDEs.

## Playing

The game retains its original short-command vocabulary. Words are identified
by their first four letters, and unknown connecting words are skipped. Use
`I` for inventory, `R` to redescribe, and `LOOK something` to examine things.
`L` and `X something` are added convenience aliases. `HELP` gives the original
location-dependent hints.

For example, the opening puzzle uses `CUT LEAVES`, `TAKE BRANCH`, `SOUTH`,
`WITH BRANCH`, and `UP`. Later, `DOOR` alone enters the unlocked inner temple;
the original parser does not treat every modern verb/noun combination as a
synonym. With multiple treasure types, specify `TAKE EAGLE`, `TAKE COINS`,
etc.; `GOLD` refers to the gold bar.

`SAVE`, `RESTORE`, `RESTART`, `UNDO`, `QUIT`, and transcript commands use Inform's
normal machinery. C64 tape saves cannot be loaded into this port. The source
does not reproduce the original screen colours, cassette prompts, or screen
wrapping.

**Spoilers:** `walkthrough.txt` contains a tested 72-command route which exits
with the golden chandeliers and a score of 200. It is not a maximum-score
walkthrough.

## What was recovered

- 58 location entries, including separately numbered maze cells.
- 149 directed map exits, plus puzzle-controlled movement rules.
- 48 object/state entries and their starting positions.
- 114 vocabulary entries, 39 puzzle messages, 163 command rules, and 4
  automatic rules.
- Six-item carrying limit, state transformations, BCD scoring, light/fire
  state, the boat, keys/panels, stones/ring, treasure and the escape condition.

The engine is written in Inform 7, with the recovered data in editable tables
at the bottom of the source. It deliberately uses numbered location and item
states rather than replacing them with Inform's native room/thing model; this
keeps the recovered rules and one-way map faithful and easy to audit against
the executable. The native Inform room is an interpreter shell. To redesign
the game with conventional Inform rooms and actions, use these tables as the
authoritative starting point rather than inventing missing puzzle logic.

## Fidelity and known quirks in this tape

The comparison tests execute the original 6502 instructions; the reference is
not a second implementation of the same port. Each tested command compares
the location, score, all 30 state registers, all 48 object positions, and the
ending flag. See `validation.txt` for the results. Validation includes an
escape with treasure, failed commands, the carrying limit, the fire ending,
and the sand countdown. This does not prove every possible command sequence.

Some surprising behavior is present in the uploaded executable and is retained:

- Darkness checks whether the lit lamp is in the current room, rather than
  whether it is carried. Consequently carrying it can still produce the
  darkness message; the original game continues to accept commands.
- The fire's fatal timer uses the sand/suffocation message.
- The sand timer is started in room 25, but its fatal automatic rule checks
  room 26. Remaining in the dungeon until that timer expires therefore does
  not kill the player in this uploaded build.
- The vocabulary has a duplicate `STRI` entry. As in the original lookup,
  the first entry wins.
- Other unusual object transitions in the command tables are preserved,
  including the lamp and stone/powder states.

The port safely limits vocabulary keys to four characters rather than
reproducing the original parser's buffer overwrite on long words. It also
corrects the inventory typo `NOTHING AT BLL` to `NOTHING AT ALL`, uses decimal
score display without four-digit padding, adds an Inform endgame prompt, and
reports a theoretical maximum score of 5650 from the eight treasure awards.
These are deliberate presentation/runtime adaptations, not recovered original
source text.

## Recovery files

- `original.prg`: the T64's single entry, with its C64 load address prefixed.
- `unpacked-memory.bin`: the 64 KiB memory image after decompression/startup.
- `recovered-data.json`: decoded map, objects, vocabulary, messages and rules.
- `recover.py`: reproducible extraction and Inform source generation.
- `engine-template.ni`: editable engine template used by the generator.
- `c64_reference.py`: emulator test oracle with keyboard/output hooks.
- `validate_port.py`: compilation and differential validation harness.
- `walkthrough-reference.json`: state and text from the original executable
  along the winning route.
- `validation.txt`: validation result summary.

To regenerate, install `py65==1.2.0` in your Python environment and run:

```sh
python recover.py /path/to/INCACURS.T64
```

To rerun validation, supply your local Inform compiler/resource directories
and Glulxe executable as described by `python validate_port.py --help`.
The extra tools are needed only for recovery/validation, not for the Inform
program itself.

## Technical provenance

Input size: 7456 bytes. T64 entry: load address `$0801`, exclusive end `$24C1`,
payload offset 96. Entry name: `INCA CURSE`. The tokenised BASIC stub executes
`SYS 2061`. Emulation takes 719372 instructions to decompress the game and
reach the missing C64 output vector. The actual recovered game begins at
`$603C`.

Important recovered addresses:

| Data | Address |
|---|---|
| Current location | `$6007` |
| State registers | `$6008`–`$6025` |
| BCD score | `$603A`–`$603B` |
| Room text pointer table | `$7000` |
| Object text pointer table | `$7A6F` |
| Initial object positions | `$7D9B` |
| Mutable object positions | `$7DCC` |
| Exit pointer table | `$7DFD` |
| Vocabulary | `$7FD5` |
| Automatic rules | `$8210` |
| Command rules | `$8250` |
| Message pointer table | `$89C7` |

Object positions 252, 253 and 254 mean absent, worn and carried. Condition
opcodes test room, available item, probability, absent item, not-worn item,
nonzero register, register equality, zero register and held item (0–8).
Action opcodes are documented by the corresponding cases in the source's
`execute recovered actions` phrase. Terminal action operands are unused;
the generator normalizes those to zero without changing their effect.

T64 SHA-256:
`ec9c4d832f56250b5c37ff99b48a1295a62a2839edd2948ed490d13ef0c3bc7e`
