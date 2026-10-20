"""Extract the exact archive disk entry and regenerate offline browser assets."""
from pathlib import Path
from hashlib import sha1, sha256

ROOT = Path(__file__).resolve().parents[1]
disk = (ROOT / 'original/PET_Games_Disk_04_19xx_-.d64').read_bytes()
assert sha1(disk).hexdigest() == 'a4c10db6937a609e15f30d448b08f2130663250a'

def sector(track, number):
    sizes = [21 if t <= 17 else 19 if t <= 24 else 18 if t <= 30 else 17 for t in range(1, 36)]
    assert 1 <= track <= 35 and 0 <= number < sizes[track - 1]
    offset = (sum(sizes[:track - 1]) + number) * 256
    return disk[offset:offset + 256]

track, number = 18, 1
entry = None
while track:
    block = sector(track, number)
    for i in range(8):
        row = block[i * 32:(i + 1) * 32]
        if row[2] and row[5:21].rstrip(b'\xa0') == b'SPACE INVADERS':
            entry = row
    track, number = block[:2]
assert entry is not None
track, number = entry[3:5]
program = bytearray()
seen = set()
while track:
    assert (track, number) not in seen
    seen.add((track, number))
    block = sector(track, number)
    program += block[2:] if block[0] else block[2:block[1] + 1]
    track, number = block[:2]
assert sha256(program).hexdigest() == 'b3a350bc7b74b017f70961588c661529390d04efdd588e268bc89b2cc445b8ef'
(ROOT / 'original/space-invaders.prg').write_bytes(program)
characters = (ROOT / 'original/pet-characters.bin').read_bytes()
assert sha256(characters).hexdigest() == 'da3374c21d6ea440cef5f338ce3f524e0a1e40dcb1ef64446c695f92c636f1fa'
(ROOT / 'data.js').write_text(
    '/* Unmodified Internet Archive SPACE INVADERS program and PET character ROM. See README.md. */\n'
    '(function(root){ const bytes=s=>Uint8Array.from(s.match(/../g),h=>parseInt(h,16)); '
    'const data={program:bytes("' + program.hex() + '"),characters:bytes("' + characters.hex() + '")}; '
    'if(typeof module!=="undefined"&&module.exports)module.exports=data;else root.ArchiveData=data;})(globalThis);\n'
)
print('Verified disk, extracted SPACE INVADERS, and regenerated data.js.')
