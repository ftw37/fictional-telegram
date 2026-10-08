const { test } = require("node:test");
const assert = require("node:assert/strict");
const { createHash } = require("node:crypto");
const { readFileSync } = require("node:fs");
const { Game, COLUMNS, ROWS, rasterize, DEFAULTS } = require("../game.js");
const { Cpu6502 } = require("../cpu6502.js");
const data = require("../pet-data.js");
const sha = bytes => createHash("sha256").update(bytes).digest("hex");
const fresh = options => { const g = new Game(); g.start(options); return g; };
const tick = (g, seconds, input = {}) => {
  for (let n = 0; n < Math.round(seconds * 10); n++) g.update(0.1, input);
};

test("embedded executable is byte-for-byte the uploaded PET PRG", () => {
  assert.deepEqual(data.program, new Uint8Array(readFileSync(require.resolve("../original/space-invader.prg"))));
  assert.equal(sha(data.program), "6b0e22e95798f28c201c4107c8c4f282b1a6f798d6d7fa4db081ccaf1c560a92");
  assert.deepEqual(data.characters, new Uint8Array(readFileSync(require.resolve("../original/pet-characters.bin")).subarray(0, 1024)));
});

for (const scenario of require("./fixtures/reference-trace.json")) {
  test(`original CPU/memory/screen match py65: ${scenario.name} (${scenario.checkpoints.length} checkpoints)`, () => {
    const g = fresh(scenario.options);
    for (const [index, point] of scenario.checkpoints.entries()) {
      if (point.cycles) g.runCycles(point.cycles, point.input);
      const e = point.expected;
      assert.equal(sha(g.memory), e.memory_sha256, `memory at checkpoint ${index}`);
      assert.equal(sha(g.screen), e.screen_sha256, `screen at checkpoint ${index}`);
      for (const register of ["pc", "a", "x", "y", "sp", "p", "cycles"])
        assert.equal(g.cpu[register], e[register], `${register} at checkpoint ${index}`);
      assert.equal(g.returned, e.returned);
      assert.equal(g.reason, e.reason, `exit cause at checkpoint ${index}`);
    }
  });
}

test("instructions and game occupy exactly 40 by 25 character cells", () => {
  const g = new Game();
  assert.equal(COLUMNS, 40); assert.equal(ROWS, 25); assert.equal(g.screen.length, 1000);
  assert.deepEqual(Array.from(g.screen.subarray(90, 105)), [7, 1, 12, 1, 24, 25, 32, 9, 14, 22, 1, 4, 5, 18, 19]);
  g.start(); assert.equal(g.lives, DEFAULTS.lives); assert.equal(g.wave, 1);
  // All graphics are bytes written by the executable into $8000 screen RAM.
  assert.strictEqual(g.screen.buffer, g.memory.buffer);
});

test("PET inverse character reverses every pixel of an 8 by 8 cell", () => {
  const screen = new Uint8Array(1000).fill(32); screen[0] = 1; screen[1] = 129;
  const pixels = rasterize(screen);
  for (let row = 0; row < 8; row++) for (let column = 0; column < 8; column++) {
    const normal = (row * 320 + column) * 4;
    const inverse = (row * 320 + 8 + column) * 4;
    assert.equal(pixels[normal + 1] + pixels[inverse + 1], 255);
    assert.equal(pixels[normal + 3], 255);
  }
});

test("pause freezes CPU, VIA time, memory, and character screen", () => {
  const g = fresh(); g.pause();
  const hash = sha(g.memory), cycles = g.cpu.cycles, elapsed = g.elapsed;
  tick(g, 2, { right: true, fire: true });
  assert.equal(g.cpu.cycles, cycles); assert.equal(g.elapsed, elapsed); assert.equal(sha(g.memory), hash);
  g.resume(); tick(g, 0.2, { right: true });
  assert.ok(g.cpu.cycles > cycles); assert.ok(g.player.x > 18);
});

test("parameters patch original bytes; restart restores original code and state", () => {
  const g = fresh({ lives: 3, columns: 8, delay: 20 });
  assert.equal(g.memory[0x12d6], 3); assert.equal(g.memory[0x12d9], 8); assert.equal(g.memory[0x12e8], 20);
  tick(g, 0.1); // The original starts with a short spawn blink before showing the selected count.
  assert.equal(g.lives, 3);
  tick(g, 0.3, { right: true }); g.stop();
  assert.equal(g.state, "over"); assert.equal(g.reason, "stopped"); assert.equal(g.cpu.pc, 0xff10);
  g.start(); const original = fresh();
  assert.equal(sha(g.memory), sha(original.memory)); assert.equal(g.score, 0);
  assert.equal(g.lives, 20); assert.equal(g.player.x, original.player.x);
});

test("6502 indexed page crossing and JMP indirect wrap match NMOS behavior", () => {
  const c = new Cpu6502();
  c.memory.set([0xbd, 0xff, 0x20], 0); c.x = 1; c.memory[0x2100] = 42; c.step();
  assert.equal(c.a, 42); assert.equal(c.cycles, 5);
  c.memory.set([0x6c, 0xff, 0x30], 3); c.memory[0x30ff] = 0x34;
  c.memory[0x3000] = 0x12; c.memory[0x3100] = 0xab; c.step(); assert.equal(c.pc, 0x1234);
});

test("6502 carry/borrow, overflow, and BCD decimal arithmetic", () => {
  const c = new Cpu6502();
  c.memory.set([0x69, 1, 0xe9, 1, 0x69, 1, 0xe9, 1]);
  c.a = 127; c.p = 48; c.step(); assert.equal(c.a, 128); assert.ok(c.p & 64);
  c.a = 0; c.p = 49; c.step(); assert.equal(c.a, 255); assert.equal(c.p & 1, 0);
  c.a = 0x99; c.p = 56; c.step(); assert.equal(c.a, 0); assert.equal(c.p & 1, 1);
  c.a = 0; c.p = 57; c.step(); assert.equal(c.a, 0x99); assert.equal(c.p & 1, 0);
});

test("the original fires once per Space press rather than continuously when held", () => {
  const launches = tapped => {
    const g = fresh(); let count = 0, previous = 255;
    for (let i = 0; i < 600; i++) {
      g.update(0.01, { fire: !tapped || i % 20 < 10 });
      const shot = g.memory[0x1870];
      if (shot < 25 && previous === 255) count++;
      previous = shot;
    }
    return count;
  };
  assert.equal(launches(false), 1); assert.ok(launches(true) > 1);
});

test("last-man loss remains distinct from invasion after BASIC zero-page restoration", () => {
  const g = fresh({ lives: 1 }); tick(g, 0.2);
  assert.equal(g.lives, 1);
  // Seed the last tick of the original hit/blink counter, then let its 6502
  // damage routine remove the man and return through the real SYS exit path.
  g.memory[0x186d] = 1;
  tick(g, 0.2);
  assert.equal(g.state, "over"); assert.equal(g.reason, "lives");
  assert.equal(g.cpu.pc, 0xff10);
});
