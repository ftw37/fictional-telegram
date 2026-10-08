"""Small test oracle executing the recovered 6502 game, not a reimplementation.

Only C64 text output, screen clearing and keyboard input are hooked. Game
logic and table lookup execute as the original instructions in py65.
The tape save/retry routines are not emulated.
"""
from pathlib import Path
from py65.devices.mpu6502 import MPU


class OriginalGame:
    def __init__(self):
        self.cpu = MPU()
        self.cpu.memory = list((Path(__file__).parent / "unpacked-memory.bin").read_bytes())
        self.cpu.sp = 255
        self.cpu.pc = 0x603c
        self.output = []
        self.ended = False
        self.run()

    def return_from_subroutine(self):
        m = self.cpu
        m.sp = (m.sp + 1) & 255
        low = m.memory[256 + m.sp]
        m.sp = (m.sp + 1) & 255
        high = m.memory[256 + m.sp]
        m.pc = ((high << 8) | low) + 1

    def run(self):
        m = self.cpu
        for _ in range(1_000_000):
            if m.pc == 0x643f:
                return
            if m.pc in (0x680c, 0x676c):
                self.ended = True
                return
            if m.pc in (0x6a8d, 0x69e9):
                self.return_from_subroutine()
            elif m.pc == 0x69c9:
                m.a = ord("N")
                self.return_from_subroutine()
            elif m.pc == 0x69ee:
                if m.a == 13:
                    self.output.append("\n")
                elif 32 <= m.a < 127:
                    self.output.append(chr(m.a))
                self.return_from_subroutine()
            elif m.pc == 0x6a04:
                a = m.memory[0xb0] | (m.memory[0xb1] << 8)
                for i in range(256):
                    c = m.memory[a + i]
                    if c == 0:
                        break
                    self.output.append("\n" if c == 13 else chr(c) if 32 <= c < 127 else "")
                self.return_from_subroutine()
            elif m.pc == 0x6a78:
                self.output.append("\n")
                self.return_from_subroutine()
            else:
                if m.memory[m.pc] == 0:
                    raise RuntimeError(f"Unexpected BRK at {m.pc:04x}")
                m.step()
        raise RuntimeError("Original game failed to return to input")

    def command(self, text):
        assert not self.ended
        encoded = text.upper().encode("ascii") + b"\r"
        assert len(encoded) <= 49
        self.cpu.memory[0x6444:0x6444 + len(encoded)] = encoded
        self.output.clear()
        self.return_from_subroutine()
        self.run()
        return "".join(self.output)

    def state(self):
        m = self.cpu.memory
        bcd = lambda v: (v >> 4) * 10 + (v & 15)
        return dict(site=m[0x6007], registers=m[0x6008:0x6026],
                    places=m[0x7dcc:0x7dfc],
                    score=100 * bcd(m[0x603b]) + bcd(m[0x603a]), ended=self.ended)


if __name__ == "__main__":
    game = OriginalGame()
    print("".join(game.output))
    for command in ["take bran", "cut bran", "i", "s", "look door", "with bran", "u", "look wind", "take rock", "with rock", "e", "r"]:
        print(">", command)
        print(game.command(command))
        print(game.state())
