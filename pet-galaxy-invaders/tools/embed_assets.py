"""Regenerate dependency-free browser assets from preserved binary inputs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
program = (ROOT / 'original/space-invader.prg').read_bytes()
characters = (ROOT / 'original/pet-characters.bin').read_bytes()[:1024]
assert len(program) == 5783
assert len(characters) == 1024
output = '''/* Original uploaded PET program and uppercase/graphics character generator.
 * Provenance and checksums: README.md. */
(function (root) {
  "use strict";
  const bytes = hex => Uint8Array.from(hex.match(/../g), pair => parseInt(pair, 16));
  const data = {
    program: bytes("%s"),
    characters: bytes("%s")
  };
  if (typeof module !== "undefined" && module.exports) module.exports = data;
  else root.PetData = data;
})(typeof globalThis !== "undefined" ? globalThis : this);
''' % (program.hex(), characters.hex())
(ROOT / 'pet-data.js').write_text(output)
