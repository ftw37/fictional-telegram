/* Execute the uploaded arcade program. The adapter supplies the PET's keyboard,
 * 60 Hz interrupt wrapper, and character screen; gameplay remains 6502 code. */
(function (root) {
  "use strict";
  const { Cpu6502 } = typeof module !== "undefined" && module.exports ? require("./cpu6502.js") : root.PetCpu;
  const data = typeof module !== "undefined" && module.exports ? require("./pet-data.js") : root.PetData;
  const WIDTH = 320, HEIGHT = 200, COLUMNS = 40, ROWS = 25;
  const CLOCK = 1000000, IRQ_PERIOD = CLOCK / 60;
  const DEFAULTS = Object.freeze({ lives: 20, columns: 6, delay: 10 });
  const clamp = (value, fallback, minimum, maximum) => {
    const n = Number(value);
    return Number.isFinite(n) ? Math.max(minimum, Math.min(maximum, Math.round(n))) : fallback;
  };
  // Text uses PET screen codes, not ASCII/PETSCII byte values.
  const screenCode = ch => {
    const code = ch.toUpperCase().charCodeAt(0);
    return code >= 64 && code <= 95 ? code - 64 : code >= 32 && code <= 63 ? code : 32;
  };
  function writeText(screen, column, row, text) {
    let cursor = row * COLUMNS + column;
    for (const ch of text) {
      if (ch === "\n") cursor = (Math.floor(cursor / COLUMNS) + 1) * COLUMNS;
      else if (cursor >= 0 && cursor < screen.length) screen[cursor++] = screenCode(ch);
    }
  }
  class Game {
    constructor() {
      this.events = [];
      this.options = { ...DEFAULTS };
      this.state = "ready";
      this.reason = "";
      this.elapsed = 0;
      this.resetMachine();
      this.showInstructions();
    }
    get memory() { return this.cpu.memory; }
    get screen() { return this.memory.subarray(0x8000, 0x8000 + COLUMNS * ROWS); }
    get lives() { return this.state === "ready" ? this.options.lives : this.memory[0x186e]; }
    get wave() { return this.memory[0x34] || 1; }
    get score() {
      const digits = Array.from(this.memory.subarray(0x1909, 0x190e), byte =>
        byte >= 48 && byte <= 57 ? String.fromCharCode(byte) : " ").join("").trim();
      return Number(digits) || 0;
    }
    get player() { return { x: this.memory[0x186b] * 8 + this.memory[0x186a], y: 192 }; }
    resetMachine() {
      this.cpu = new Cpu6502();
      const load = data.program[0] | (data.program[1] << 8);
      this.memory.set(data.program.subarray(2), load);
      this.memory.fill(32, 0x8000, 0x8400);
      // BASIC launcher selects the old-ROM IRQ vector at $0219.
      this.memory[1] = 0x19; this.memory[2] = 2;
      this.memory[0x219] = 0; this.memory[0x21a] = 0xff;
      // Saved original IRQ target. The arcade installs its own $0e00 handler.
      this.memory[0x19fe] = 0; this.memory[0x19ff] = 0xff;
      // ROM tail: restore Y/X/A, RTI. ROM entry: save A/X/Y, JMP ($0219).
      this.memory.set([0x68, 0xa8, 0x68, 0xaa, 0x68, 0x40], 0xff00);
      this.memory.set([0x48, 0x8a, 0x48, 0x98, 0x48, 0x6c, 0x19, 0x02], 0xff80);
      this.memory[0xfffe] = 0x80; this.memory[0xffff] = 0xff;
      this.memory[0xe812] = 255;
      this.cpu.pc = 0x0d98; // The launcher's SYS 3480.
      this.cpu.pushWord(0xff0f); // Return from SYS goes to the adapter sentinel.
      this.nextIrq = IRQ_PERIOD;
      this.cycleTarget = 0;
      this.returned = false;
      this.endCause = "";
    }
    showInstructions() {
      this.screen.fill(32);
      writeText(this.screen, 10, 2, "GALAXY INVADERS");
      const lines = [
        " MOVE YOUR MAN USING '.' AND '='",
        "FIRE YOUR GUN WITH 'SPACE'",
        "SCORE BY HITTING ENEMY",
        "DESTROY ALL ENEMY MEN TO BEGIN NEW RACK",
        "'  ' HAS HIGH RANDOM VALUE",
        "GAME ENDS IF ALL YOUR MEN ARE KILLED OR",
        "ENEMY OVERRUNS YOU",
        "STOP GAME WITH '['",
        "    COMMANDS:",
        "'B'-BEGIN GAME",
        "'E'- EXIT PROGRAM",
        "'C'-CHANGE PARAMETERS",
        "",
        "    COMMAND   ?"
      ];
      lines.forEach((line, index) => writeText(this.screen, 0, 5 + index, line));
      // PETSCII $bf in the original PRINT maps to graphics screen code $7f.
      this.screen[9 * 40 + 1] = 0x7f; this.screen[9 * 40 + 2] = 0x7f;
    }
    start(options = {}) {
      this.options = {
        lives: clamp(options.lives, DEFAULTS.lives, 1, 99),
        columns: clamp(options.columns, DEFAULTS.columns, 1, 12),
        delay: clamp(options.delay, DEFAULTS.delay, 1, 255)
      };
      this.resetMachine();
      this.memory[0x12d6] = this.options.lives;
      this.memory[0x12d9] = this.options.columns;
      this.memory[0x12e8] = this.options.delay;
      this.state = "playing"; this.reason = ""; this.elapsed = 0; this.events = [];
      // Let SYS initialize its buffers and paint the first interrupt-driven frame.
      this.runCycles(100000, {});
      this.events.push({ type: "start" });
    }
    pause() { if (this.state === "playing") this.state = "paused"; }
    resume() { if (this.state === "paused") this.state = "playing"; }
    stop() {
      if (!["playing", "paused"].includes(this.state)) return;
      this.state = "playing";
      // '[' is bit 1 low on the keyboard row read by the original IRQ handler.
      this.runCycles(40000, { stop: true });
      if (!this.returned) throw new Error("PET program did not return after its stop key");
    }
    runCycles(cycles, input) {
      this.cycleTarget += cycles;
      const port = input.stop ? 0xfd : (255 & ~(input.left ? 64 : 0) &
        ~(input.right ? 128 : 0) & ~(input.fire ? 4 : 0));
      const before = { score: this.score, lives: this.lives, wave: this.wave };
      while (this.cpu.cycles < this.cycleTarget && !this.returned) {
        if (this.cpu.pc === 0xff10) {
          this.returned = true; this.state = "over";
          this.reason = this.endCause || (input.stop ? "stopped" : "lives");
          this.events.push({ type: "over", reason: this.reason });
          break;
        }
        // Capture the cause before the original exit routine restores BASIC's
        // zero page, which overwrites the live formation-height byte at $50.
        if (this.cpu.pc === 0x0b80)
          this.endCause = input.stop ? "stopped" : this.memory[0x50] < 4 ? "invasion" : "lives";
        if (this.cpu.cycles >= this.nextIrq && !(this.cpu.p & 4)) {
          this.nextIrq += IRQ_PERIOD; this.cpu.irq();
        }
        this.memory[0xe812] = port;
        // The original uses the VIA timer low byte as one of its random sources.
        this.memory[0xe849] = (65535 - this.cpu.cycles) & 255;
        this.cpu.step();
      }
      if (this.score > before.score) this.events.push({ type: "hit" });
      if (this.lives < before.lives) this.events.push({ type: "damage" });
      if (this.wave > before.wave) this.events.push({ type: "wave", wave: this.wave });
    }
    update(seconds, input = {}) {
      if (this.state !== "playing" || !Number.isFinite(seconds) || seconds <= 0) return;
      const dt = Math.min(seconds, 0.1);
      this.elapsed += dt;
      this.runCycles(dt * CLOCK, input);
    }
  }
  // Render all 1,000 screen bytes as actual 8×8 PET character cells. Bit 7 in a
  // screen code reverses the glyph; it is not a second sprite bank.
  function rasterize(screen, target = new Uint8ClampedArray(WIDTH * HEIGHT * 4)) {
    for (let cell = 0; cell < COLUMNS * ROWS; cell++) {
      const code = screen[cell], x = (cell % COLUMNS) * 8, y = Math.floor(cell / COLUMNS) * 8;
      for (let row = 0; row < 8; row++) {
        const bits = data.characters[(code & 127) * 8 + row] ^ (code & 128 ? 255 : 0);
        for (let column = 0; column < 8; column++) {
          const offset = ((y + row) * WIDTH + x + column) * 4;
          const lit = bits & (128 >> column);
          target[offset] = lit ? 100 : 0;
          target[offset + 1] = lit ? 255 : 0;
          target[offset + 2] = lit ? 125 : 0;
          target[offset + 3] = 255;
        }
      }
    }
    return target;
  }
  const api = { Game, WIDTH, HEIGHT, COLUMNS, ROWS, DEFAULTS, rasterize, writeText };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PetInvaders = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
