"""Recover the uploaded T64 and generate an Inform 7 story (requires py65).

Usage: python recover.py INCACURS.T64
The 6502 is emulated only until the decompressor has finished and game startup
first reaches the absent C64 output vector. No uploaded code runs on the host.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys

from py65.devices.mpu6502 import MPU

HERE = Path(__file__).resolve().parent


def unpack(path):
    tape = Path(path).read_bytes()
    assert tape.startswith(b"C64 tape image file"), "Not the expected T64 format"
    used = struct.unpack_from("<H", tape, 36)[0]
    assert used == 1, "Expected one tape entry"
    start, end = struct.unpack_from("<HH", tape, 66)
    offset = struct.unpack_from("<I", tape, 72)[0]
    payload = tape[offset:offset + end - start]
    assert len(payload) == end - start
    m = MPU()
    m.memory[start:start + len(payload)] = payload
    m.pc = 2061
    for steps in range(2_000_000):
        if m.pc == 0 and m.memory[m.pc] == 0:
            break
        m.step()
    else:
        raise RuntimeError("Decompression did not reach expected output vector")
    memory = bytes(m.memory)
    assert b"I AM IN A JUNGLE CLEARING" in memory[0x7071:0x709f]
    (HERE / "unpacked-memory.bin").write_bytes(memory)
    (HERE / "original.prg").write_bytes(struct.pack("<H", start) + payload)
    return memory, hashlib.sha256(tape).hexdigest(), steps


def recover(memory):
    def word(addr):
        return int.from_bytes(memory[addr:addr + 2], "little")

    def text(addr):
        end = memory.index(0, addr)
        data = memory[addr:end]
        return "".join("\n" if b == 13 else chr(b) if 32 <= b < 127
                       else chr(b - 128) if 193 <= b <= 218 else ""
                       for b in data).strip()

    def program(addr, condition):
        result = []
        for _ in range(100):
            op = memory[addr]
            addr += 1
            if op == 255:
                return result
            arg = memory[addr]
            addr += 1
            result.extend([op, arg])
            if (condition and op == 6) or (not condition and op in (15, 18)):
                result.append(memory[addr])
                addr += 1
            if not condition and op in (0, 6, 7, 12, 13, 14, 20, 21, 22):
                # These routines return/jump away. The nominal argument of a
                # one-byte terminal opcode can actually be the next program's
                # first byte: it is fetched but unused by the C64 interpreter.
                result[-1] = 0
                return result
        raise RuntimeError(f"Unterminated program at {addr:04x}")

    def rules(addr):
        result = []
        while memory[addr]:
            result.append(dict(address=f"{addr:04x}", verb=memory[addr],
                               noun=memory[addr + 1],
                               conditions=program(word(addr + 2), True),
                               actions=program(word(addr + 4), False)))
            addr += 6
        return result

    rooms = []
    exits = []
    for n in range(58):
        description = text(word(0x7000 + 2 * n))
        title = description.splitlines()[0].removeprefix("I AM ").title()
        rooms.append(dict(id=n, title=title, description=description))
        a = word(0x7dfd + 2 * n)
        while memory[a] != 255:
            exits.append(dict(source=n, verb=memory[a], target=memory[a + 1]))
            a += 2
    objects = [dict(id=n, name=text(word(0x7a6f + 2 * n)),
                    place=memory[0x7d9b + n]) for n in range(48)]
    vocabulary = []
    a = 0x7fd5
    while memory[a] != 255:
        vocabulary.append(dict(key=memory[a:a + 4].decode("ascii"), code=memory[a + 4]))
        a += 5
    messages = [dict(id=n, text=text(word(0x89c7 + 2 * n))) for n in range(39)]
    return dict(rooms=rooms, exits=exits, objects=objects,
                vocabulary=vocabulary, messages=messages,
                automatic_rules=rules(0x8210), command_rules=rules(0x8250))


def generate(data):
    def quoted(text):
        return '"' + text.replace('"', '[quotation mark]').replace('\n', '[line break]') + '"'

    def listing(numbers):
        return "{" + ", ".join(map(str, numbers)) + "}"

    tables = []
    def table(name, columns, rows):
        tables.append(name + "\n" + "\t".join(columns) + "\n" +
                      "\n".join("\t".join(row) for row in rows))
    table("Table of Recovered Rooms", ["site-id", "site-title", "site-description"],
          [[str(r["id"]), quoted(r["title"]), quoted(r["description"])] for r in data["rooms"]])
    table("Table of Recovered Objects", ["item-id", "item-name", "item-place"],
          [[str(r["id"]), quoted(r["name"]), str(r["place"])] for r in data["objects"]])
    table("Table of Recovered Exits", ["exit-source", "exit-verb", "exit-target"],
          [[str(r[c]) for c in ["source", "verb", "target"]] for r in data["exits"]])
    table("Table of Recovered Vocabulary", ["word-key", "word-code"],
          [[quoted(r["key"]), str(r["code"])] for r in data["vocabulary"]])
    table("Table of Recovered Messages", ["message-id", "message-text"],
          [[str(r["id"]), quoted(r["text"])] for r in data["messages"]])
    for kind, prefix in [("automatic", "auto"), ("command", "rule")]:
        table(f"Table of Recovered {kind.title()} Rules",
              [f"{prefix}-verb", f"{prefix}-noun", f"{prefix}-conditions", f"{prefix}-actions"],
              [[str(r["verb"]), str(r["noun"]), listing(r["conditions"]), listing(r["actions"])]
               for r in data[f"{kind}_rules"]])
    source = (HERE / "engine-template.ni").read_text().replace("@RECOVERED_TABLES@", "\n\n".join(tables))
    (HERE / "Inca Curse.ni").write_text(source)
    (HERE / "recovered-data.json").write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    memory, digest, steps = unpack(sys.argv[1])
    data = recover(memory)
    generate(data)
    print(f"T64 SHA256: {digest}; decompressor: {steps} instructions")
    print({key: len(value) for key, value in data.items()})
