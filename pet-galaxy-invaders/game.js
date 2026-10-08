/* Browser reconstruction of the PET game. No machine code runs in the browser.
 * The model has no DOM dependencies, so gameplay can be tested independently. */
(function (root) {
  "use strict";
  const WIDTH = 320, HEIGHT = 200, PLAYER_Y = 180;
  const DEFAULTS = Object.freeze({ lives: 20, columns: 6, difficulty: 1 });
  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
  const overlaps = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x &&
    a.y < b.y + b.h && a.y + a.h > b.y;

  class Game {
    constructor(random = Math.random) {
      this.random = random;
      this.start(DEFAULTS);
      this.state = "ready";
    }
    start(options = {}) {
      this.options = {
        lives: clamp(Math.round(Number(options.lives) || DEFAULTS.lives), 1, 20),
        columns: clamp(Math.round(Number(options.columns) || DEFAULTS.columns), 4, 10),
        difficulty: clamp(Math.round(Number(options.difficulty) || 1), 1, 3)
      };
      this.state = "playing";
      this.score = 0;
      this.lives = this.options.lives;
      this.wave = 1;
      this.elapsed = 0;
      this.player = { x: 152, y: PLAYER_Y, w: 16, h: 8 };
      this.cooldown = 0;
      this.invincible = 0;
      this.effects = [];
      this.events = [];
      this.reason = "";
      this.mystery = null;
      this.mysteryTimer = 9 + this.random() * 6;
      this.pendingWave = 0;
      this.createWave();
    }
    createWave() {
      const columns = Math.min(12, this.options.columns + this.wave - 1);
      const left = Math.floor((WIDTH - ((columns - 1) * 24 + 16)) / 2);
      this.enemies = [];
      for (let row = 0; row < 3; row++) {
        for (let column = 0; column < columns; column++) {
          this.enemies.push({ x: left + column * 24, y: 32 + row * 16 +
            Math.min(3, this.wave - 1) * 4, w: 16, h: 12, row, column,
            points: (3 - row) * 10, alive: true });
        }
      }
      this.direction = 1;
      this.enemyClock = 0;
      this.enemyFrame = 0;
      this.fireClock = 0;
      this.playerShots = [];
      this.enemyShots = [];
      this.shields = [48, 148, 248].map(x => ({ x, y: 142, cells:
        ["00111100", "01111110", "11111111", "11111111",
          "11111111", "11100111", "11000011", "11000011"]
          .map(row => Array.from(row, c => c === "1")) }));
      this.events.push({ type: "wave", wave: this.wave });
    }
    pause() { if (this.state === "playing") this.state = "paused"; }
    resume() { if (this.state === "paused") this.state = "playing"; }
    stop() {
      if (this.state === "playing" || this.state === "paused") this.end("stopped");
    }
    end(reason) {
      this.state = "over";
      this.reason = reason;
      this.events.push({ type: "over", reason });
    }
    livingEnemies() { return this.enemies.filter(e => e.alive); }
    firePlayer() {
      if (this.cooldown > 0 || this.playerShots.length || this.pendingWave) return;
      this.playerShots.push({ x: this.player.x + 7, y: PLAYER_Y - 6, w: 2, h: 6 });
      this.cooldown = 0.24;
      this.events.push({ type: "shot" });
    }
    hitShield(shot) {
      for (const shield of this.shields) {
        for (let row = 0; row < 8; row++) {
          for (let col = 0; col < 8; col++) {
            if (!shield.cells[row][col]) continue;
            const cell = { x: shield.x + col * 3, y: shield.y + row * 2, w: 3, h: 2 };
            if (!overlaps(shot, cell)) continue;
            for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
              if (shield.cells[row + dr] && col + dc >= 0 && col + dc < 8)
                shield.cells[row + dr][col + dc] = false;
            }
            return true;
          }
        }
      }
      return false;
    }
    killEnemy(enemy) {
      enemy.alive = false;
      this.score += enemy.points;
      this.effects.push({ x: enemy.x + 8, y: enemy.y + 6, ttl: 0.28, points: enemy.points });
      this.events.push({ type: "hit" });
      if (!this.livingEnemies().length) {
        this.pendingWave = 0.85;
        this.enemyShots = [];
      }
    }
    damagePlayer() {
      if (this.invincible > 0) return;
      this.lives--;
      this.effects.push({ x: this.player.x + 8, y: PLAYER_Y, ttl: 0.45 });
      this.events.push({ type: "damage" });
      if (!this.lives) this.end("lives");
      else this.invincible = 1.5;
    }
    update(seconds, input = {}) {
      if (this.state !== "playing" || !Number.isFinite(seconds) || seconds <= 0) return;
      let remaining = Math.min(seconds, 0.1);
      while (remaining > 0 && this.state === "playing") {
        const step = Math.min(remaining, 1 / 120);
        this.advance(step, input);
        remaining -= step;
      }
    }
    advance(dt, input) {
      this.elapsed += dt;
      this.cooldown = Math.max(0, this.cooldown - dt);
      this.invincible = Math.max(0, this.invincible - dt);
      this.effects.forEach(e => { e.ttl -= dt; });
      this.effects = this.effects.filter(e => e.ttl > 0);
      const motion = Number(Boolean(input.right)) - Number(Boolean(input.left));
      this.player.x = clamp(this.player.x + motion * 128 * dt, 8, WIDTH - 24);
      if (this.pendingWave > 0) {
        this.pendingWave -= dt;
        if (this.pendingWave <= 0) { this.wave++; this.pendingWave = 0; this.createWave(); }
        return;
      }
      if (input.fire) this.firePlayer();
      const enemies = this.livingEnemies();
      const multiplier = [1, 1.3, 1.65][this.options.difficulty - 1];
      const interval = Math.max(0.12, (0.53 - 0.28 * (1 - enemies.length / this.enemies.length)
        - 0.02 * (this.wave - 1)) / multiplier);
      this.enemyClock += dt;
      if (this.enemyClock >= interval && enemies.length) {
        this.enemyClock -= interval;
        this.enemyFrame = 1 - this.enemyFrame;
        const edge = enemies.some(e => e.x + this.direction * 8 < 8 ||
          e.x + e.w + this.direction * 8 > WIDTH - 8);
        if (edge) this.direction *= -1;
        for (const enemy of enemies) {
          if (edge) enemy.y += 8;
          else enemy.x += this.direction * 8;
          // Descending enemies chew through any shelter they overlap.
          for (const shield of this.shields) {
            for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) {
              if (overlaps(enemy, { x: shield.x + c * 3, y: shield.y + r * 2, w: 3, h: 2 }))
                shield.cells[r][c] = false;
            }
          }
        }
        this.events.push({ type: "step" });
        if (enemies.some(e => e.y + e.h >= PLAYER_Y)) { this.end("invasion"); return; }
      }
      this.fireClock += dt;
      if (this.fireClock >= Math.max(0.35, 1.35 / multiplier - this.wave * 0.035)) {
        this.fireClock = 0;
        if (this.enemyShots.length < 4 && enemies.length) {
          const bottom = new Map();
          for (const enemy of enemies) {
            if (!bottom.has(enemy.column) || enemy.y > bottom.get(enemy.column).y)
              bottom.set(enemy.column, enemy);
          }
          const shooters = [...bottom.values()];
          const enemy = shooters[Math.min(shooters.length - 1, Math.floor(this.random() * shooters.length))];
          this.enemyShots.push({ x: enemy.x + 7, y: enemy.y + enemy.h, w: 2, h: 6 });
        }
      }
      this.mysteryTimer -= dt;
      if (!this.mystery && this.mysteryTimer <= 0) {
        this.mystery = { x: -24, y: 12, w: 24, h: 8 };
        this.mysteryTimer = 11 + this.random() * 7;
      }
      if (this.mystery) {
        this.mystery.x += 36 * dt;
        if (this.mystery.x > WIDTH + 24) this.mystery = null;
      }
      this.playerShots = this.playerShots.filter(shot => {
        shot.y -= 210 * dt;
        if (shot.y + shot.h < 0 || this.hitShield(shot)) return false;
        if (this.mystery && overlaps(shot, this.mystery)) {
          const points = [50, 100, 150, 200, 300][Math.min(4, Math.floor(this.random() * 5))];
          this.score += points;
          this.effects.push({ x: this.mystery.x + 12, y: 12, ttl: 0.7, points });
          this.mystery = null;
          this.events.push({ type: "mystery" });
          return false;
        }
        const enemy = this.enemies.find(e => e.alive && overlaps(shot, e));
        if (enemy) { this.killEnemy(enemy); return false; }
        return true;
      });
      this.enemyShots = this.enemyShots.filter(shot => {
        shot.y += (82 + this.wave * 5) * multiplier * dt;
        if (shot.y > HEIGHT || this.hitShield(shot)) return false;
        if (overlaps(shot, this.player)) { this.damagePlayer(); return false; }
        const playerShot = this.playerShots.find(s => overlaps(s, shot));
        if (playerShot) {
          this.playerShots = this.playerShots.filter(s => s !== playerShot);
          return false;
        }
        return true;
      });
    }
  }
  const api = { Game, WIDTH, HEIGHT, PLAYER_Y, DEFAULTS };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PetInvaders = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
