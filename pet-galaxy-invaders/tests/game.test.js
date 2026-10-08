const { test } = require("node:test");
const assert = require("node:assert/strict");
const { Game, DEFAULTS } = require("../game.js");
const fresh = () => { const g = new Game(() => 0.5); g.start(); return g; };
const tick = (g, seconds, input = {}) => {
  for (let n = 0; n < Math.ceil(seconds * 120); n++) g.update(1 / 120, input);
};

test("original defaults produce 20 lives and three rows of six enemies", () => {
  const g = fresh();
  assert.equal(g.lives, DEFAULTS.lives);
  assert.equal(g.livingEnemies().length, 18);
  assert.equal(g.wave, 1);
});
test("movement remains inside the playfield and opposite inputs cancel", () => {
  const g = fresh(); tick(g, 5, { left: true }); assert.equal(g.player.x, 8);
  tick(g, 5, { right: true }); assert.equal(g.player.x, 296);
  const x = g.player.x; tick(g, 1, { left: true, right: true }); assert.equal(g.player.x, x);
});
test("a player shot kills an enemy and awards its row's points once", () => {
  const g = fresh(), enemy = g.enemies.find(e => e.row === 2);
  g.shields = []; g.enemyClock = -100; g.fireClock = -100;
  g.player.x = enemy.x; tick(g, 0.7, { fire: true });
  assert.equal(enemy.alive, false); assert.equal(g.score, 10);
});
test("shelters absorb shots and sustain lasting damage", () => {
  const g = fresh(), shield = g.shields[0];
  const before = shield.cells.flat().filter(Boolean).length;
  g.playerShots.push({ x: shield.x + 9, y: shield.y + 9, w: 2, h: 6 });
  g.update(1 / 120);
  assert.equal(g.playerShots.length, 0);
  assert.ok(shield.cells.flat().filter(Boolean).length < before);
});
test("an enemy shot costs a life; the respawn interval protects against a second hit", () => {
  const g = fresh(); g.shields = [];
  const hit = () => g.enemyShots.push({ x: g.player.x + 7, y: 178, w: 2, h: 6 });
  hit(); g.update(1 / 120); assert.equal(g.lives, 19);
  hit(); g.update(1 / 120); assert.equal(g.lives, 19);
});
test("losing the last life ends the game", () => {
  const g = fresh(); g.start({ lives: 1 }); g.shields = [];
  g.enemyShots.push({ x: g.player.x + 7, y: 178, w: 2, h: 6 });
  g.update(1 / 120); assert.equal(g.state, "over"); assert.equal(g.reason, "lives");
});
test("enemy formation reverses and descends at the edge", () => {
  const g = fresh();
  g.enemies.forEach(e => { e.x += 100; });
  const y = g.enemies[0].y; tick(g, 0.55);
  assert.equal(g.direction, -1); assert.equal(g.enemies[0].y, y + 8);
});
test("invasion ends a game even when the player has lives left", () => {
  const g = fresh(); g.enemies.forEach(e => { e.x = 300; e.y = 163; });
  tick(g, 0.55); assert.equal(g.state, "over"); assert.equal(g.reason, "invasion");
  assert.equal(g.lives, 20);
});
test("clearing a wave adds another column and preserves score and lives", () => {
  const g = fresh(); g.enemies.forEach(e => { e.alive = false; });
  g.enemies[0].alive = true;
  g.shields = []; g.enemyClock = -100; g.fireClock = -100;
  g.playerShots.push({ x: g.enemies[0].x + 7, y: g.enemies[0].y + 4, w: 2, h: 6 });
  g.update(1 / 120); assert.ok(g.pendingWave > 0);
  tick(g, 0.9); assert.equal(g.wave, 2); assert.equal(g.livingEnemies().length, 21);
  assert.equal(g.score, 30); assert.equal(g.lives, 20);
});
test("a mystery ship hit awards its random bonus and removes the ship", () => {
  const g = fresh(); g.shields = []; g.mystery = { x: 150, y: 12, w: 24, h: 8 };
  g.playerShots.push({ x: 155, y: 16, w: 2, h: 6 });
  g.update(1 / 120); assert.equal(g.score, 150); assert.equal(g.mystery, null);
});
test("pause freezes the whole simulation and resume continues it", () => {
  const g = fresh(); g.pause();
  const before = JSON.stringify(g); tick(g, 3, { left: true, fire: true });
  assert.equal(JSON.stringify(g), before);
  g.resume(); tick(g, 0.1, { left: true }); assert.ok(g.player.x < 152);
});
test("restart clears score, bullets, damage, and a stopped game", () => {
  const g = fresh(); g.score = 100; g.lives = 4; g.wave = 6; g.stop();
  g.start({ lives: 3, columns: 8, difficulty: 2 });
  assert.equal(g.state, "playing"); assert.equal(g.lives, 3); assert.equal(g.score, 0);
  assert.equal(g.wave, 1); assert.equal(g.livingEnemies().length, 24);
  assert.equal(g.playerShots.length, 0); assert.equal(g.enemyShots.length, 0);
});
