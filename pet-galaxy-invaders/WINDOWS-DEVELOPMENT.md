# Galaxy Invaders on this computer

This is a full Git checkout of https://github.com/ftw37/fictional-telegram.
The game is in `pet-galaxy-invaders`; other projects in the repository are preserved.

Double-click `Play-Galaxy-Invaders.cmd` to open the game in your default browser.
Press B to start, arrow keys to move, Space to fire, and P to pause.
After editing a file, refresh the browser to see the change.

Double-click `Test-Galaxy-Invaders.cmd` to run the 13 existing tests using
the Node.js runtime bundled with Codex. No package installation is needed.

Files to edit:
- `app.js`: browser controls, drawing, and sound
- `game.js`: game adapter and settings
- `styles.css`: appearance
- `index.html`: page layout
- `cpu6502.js`: original machine-code interpreter

The original game runs from preserved PET machine code. Changes to its original
rules may require modifying the adapter or original program bytes.

For future Codex work, open this repository folder as a local project:
`C:\Users\frank\Documents\Codex\SpaceInvaders-Development`

Git is available at:
`C:\Users\frank\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe`

The checkout keeps the GitHub origin and history. Local setup files are uncommitted.
Pushing changes will require GitHub authentication if local credentials are absent.
