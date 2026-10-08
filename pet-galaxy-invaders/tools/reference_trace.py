"""Run the unmodified uploaded program in py65, independently of browser JS.

pip install py65==1.2.0
python tools/reference_trace.py > tests/fixtures/reference-trace.json
The small ROM/keyboard adapter matches the documented browser adapter.
"""
from pathlib import Path
import hashlib
import json
import argparse
from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[1]

class Reference:
    def __init__(self, lives=20, columns=6, delay=10):
        self.cpu = MPU()
        m = self.cpu.memory
        program = (ROOT / 'original/space-invader.prg').read_bytes()
        load = int.from_bytes(program[:2], 'little')
        m[load:load + len(program) - 2] = program[2:]
        m[0x8000:0x8400] = [32] * 1024
        m[1:3] = [0x19, 2]
        m[0x219:0x21b] = [0, 0xff]
        m[0x19fe:0x1a00] = [0, 0xff]
        m[0xff00:0xff06] = [0x68, 0xa8, 0x68, 0xaa, 0x68, 0x40]
        m[0xff80:0xff88] = [0x48, 0x8a, 0x48, 0x98, 0x48, 0x6c, 0x19, 0x02]
        m[0xfffe:0x10000] = [0x80, 0xff]
        m[0xe812] = 255
        m[0x12d6] = lives; m[0x12d9] = columns; m[0x12e8] = delay
        self.cpu.pc = 0xd98
        self.cpu.stPushWord(0xff0f)
        self.next_irq = 1_000_000 / 60
        self.target = 0
        self.returned = False
        self.end_reason = ""
        self.run(100_000, {})

    def run(self, cycles, controls):
        c = self.cpu; m = c.memory
        self.target += cycles
        port = 0xfd if controls.get('stop') else (255 & ~(64 if controls.get('left') else 0)
            & ~(128 if controls.get('right') else 0)
            & ~(4 if controls.get('fire') else 0))
        while c.processorCycles < self.target and not self.returned:
            if c.pc == 0xff10:
                self.returned = True
                break
            # Identify exits from the original branches themselves, before ROM/zero-page cleanup.
            if c.pc == 0x1384:
                self.end_reason = 'invasion'
            if c.pc == 0x14e4 and m[0x186e] == 0:
                self.end_reason = 'lives'
            if c.pc == 0x0e26:
                self.end_reason = 'stopped'
            if c.processorCycles >= self.next_irq and not c.p & 4:
                self.next_irq += 1_000_000 / 60
                c.irq()
            m[0xe812] = port
            m[0xe849] = (65535 - c.processorCycles) & 255
            c.step()

    def snapshot(self):
        c = self.cpu
        return dict(pc=c.pc, a=c.a, x=c.x, y=c.y, sp=c.sp, p=c.p,
            cycles=c.processorCycles, returned=self.returned,
            reason=self.end_reason if self.returned else "",
            memory_sha256=hashlib.sha256(bytes(c.memory)).hexdigest(),
            screen_sha256=hashlib.sha256(bytes(c.memory[0x8000:0x83e8])).hexdigest())

sequences = [
    ('default-idle', {}, [(100_000, {})] * 15),
    ('move-fire-stop', {}, [(100_000, {'right': True})] * 6 +
        [(100_000, {'fire': True})] * 35 + [(100_000, {'left': True, 'fire': True})] * 12 +
        [(40_000, {'stop': True})]),
    ('changed-parameters', {'lives': 3, 'columns': 8, 'delay': 20},
        [(100_000, {'right': True, 'fire': True})] * 20),
    ('sustained-play', {}, [(100_000, {'fire': True, 'right': i % 100 < 50,
        'left': i % 100 >= 50}) for i in range(1200)]),
]
parser = argparse.ArgumentParser()
parser.add_argument("--scenario", help="Regenerate only one named trace for diagnosis")
args = parser.parse_args()
result = []
for name, options, steps in sequences:
    if args.scenario and args.scenario != name:
        continue
    ref = Reference(**options)
    checkpoints = [dict(cycles=0, input={}, expected=ref.snapshot())]
    for cycles, controls in steps:
        ref.run(cycles, controls)
        checkpoints.append(dict(cycles=cycles, input=controls, expected=ref.snapshot()))
        if ref.returned:
            break
    result.append(dict(name=name, options=options, checkpoints=checkpoints))
print(json.dumps(result, indent=2))
