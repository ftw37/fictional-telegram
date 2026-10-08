(function () {
  "use strict";
  const { Game, WIDTH, HEIGHT, DEFAULTS } = window.PetInvaders;
  const $ = id => document.getElementById(id);
  const canvas = $("game"), context = canvas.getContext("2d");
  context.imageSmoothingEnabled = false;
  const game = new Game();
  game.events = [];
  let options = { ...DEFAULTS }, best = 0, sound = false, audio = null;
  try {
    best = Math.max(0, Math.floor(Number(localStorage.getItem("pet-invaders-best")) || 0));
    const saved = JSON.parse(localStorage.getItem("pet-invaders-settings") || "null");
    if (saved && typeof saved === "object") {
      if ([1, 2, 3].includes(saved.difficulty)) options.difficulty = saved.difficulty;
      if ([1, 3, 5, 20].includes(saved.lives)) options.lives = saved.lives;
      if ([4, 6, 8, 10].includes(saved.columns)) options.columns = saved.columns;
    }
  } catch (_) { /* Storage is optional, including when opening a local file. */ }
  game.start(options); game.state = "ready"; game.events = [];
  const keyboard = new Set(), touch = new Set();
  let lastFrame = null, dialogPaused = false, lastView = "";
  const sprites = {
    alien0: [
      ["0000011111100000", "0001111111111000", "0011111111111100", "0110011111100110", "1111111111111111", "0011100000011100", "0010011111100100", "0100100000010010"],
      ["0000011111100000", "0001111111111000", "0011111111111100", "0110011111100110", "1111111111111111", "0011100000011100", "0100011111100010", "0010000000000100"]
    ],
    alien1: [
      ["0010000000000100", "0001000000001000", "0011111111111100", "0111001111001110", "1111111111111111", "1011111111111101", "1010000000000101", "0001100000011000"],
      ["0010000000000100", "1001000000001001", "1011111111111101", "1111001111001111", "1111111111111111", "0011111111111100", "0010000000000100", "0100000000000010"]
    ],
    alien2: [
      ["0001111111111000", "0111111111111110", "1110011111100111", "1111111111111111", "0001111111111000", "0011011111101100", "0110000000000110", "1100000000000011"],
      ["0001111111111000", "0111111111111110", "1110011111100111", "1111111111111111", "0001111111111000", "0110011111100110", "1100000000000011", "0011000000001100"]
    ],
    player: ["0000000110000000", "0000000110000000", "0001111111111000", "0011111111111100", "0111111111111110", "1111111111111111", "1111111111111111", "1111111111111111"],
    mystery: ["000000001111111100000000", "000001111111111111100000", "000111111111111111111000", "011111111111111111111110", "111001110011001110011111", "011111111111111111111110", "000111001110011100111000", "000001100000000001100000"]
  };
  function sprite(bitmap, x, y, color = "#8effaa") {
    context.fillStyle = color;
    bitmap.forEach((row, dy) => Array.from(row).forEach((pixel, dx) => {
      if (pixel === "1") context.fillRect(Math.round(x) + dx, Math.round(y) + dy, 1, 1);
    }));
  }
  function draw() {
    context.fillStyle = "#020805";
    context.fillRect(0, 0, WIDTH, HEIGHT);
    context.fillStyle = "#132b1b";
    for (let x = 8; x < WIDTH; x += 16) context.fillRect(x, 5, 1, 1);
    for (const enemy of game.enemies) if (enemy.alive)
      sprite(sprites["alien" + enemy.row][game.enemyFrame], enemy.x, enemy.y);
    for (const shield of game.shields) {
      context.fillStyle = "#68bc80";
      shield.cells.forEach((row, r) => row.forEach((active, c) => {
        if (active) context.fillRect(shield.x + c * 3, shield.y + r * 2, 3, 2);
      }));
    }
    if (!game.invincible || Math.floor(game.elapsed * 10) % 2 === 0)
      sprite(sprites.player, game.player.x, game.player.y, "#b4ffc6");
    if (game.mystery) sprite(sprites.mystery, game.mystery.x, game.mystery.y, "#ceffb5");
    for (const shot of game.playerShots) {
      context.fillStyle = "#caffd6";
      context.fillRect(Math.round(shot.x), Math.round(shot.y), shot.w, shot.h);
    }
    for (const shot of game.enemyShots) {
      context.fillStyle = "#8effaa";
      const y = Math.round(shot.y);
      context.fillRect(Math.round(shot.x), y, 2, 6);
      context.fillRect(Math.round(shot.x) + (Math.floor(game.elapsed * 10) % 2 ? -1 : 1), y + 2, 2, 2);
    }
    for (const effect of game.effects) {
      context.fillStyle = "#d3ffdb";
      for (let i = 0; i < 8; i++) {
        const angle = i * Math.PI / 4, distance = (0.5 - Math.min(0.45, effect.ttl)) * 24 + 3;
        context.fillRect(Math.round(effect.x + Math.cos(angle) * distance),
          Math.round(effect.y + Math.sin(angle) * distance), 2, 2);
      }
      if (effect.points && effect.ttl > 0.35) {
        context.font = "7px monospace";
        context.textAlign = "center";
        context.fillText(String(effect.points), effect.x, effect.y + 15);
      }
    }
    context.fillStyle = "#2c5838";
    context.fillRect(8, 193, 304, 1);
  }
  function announce(message) { $("announcement").textContent = message; }
  function syncView() {
    if (game.score > best) {
      best = game.score;
      try { localStorage.setItem("pet-invaders-best", String(best)); } catch (_) {}
    }
    $("score").textContent = String(game.score).padStart(6, "0");
    $("best").textContent = String(best).padStart(6, "0");
    $("wave").textContent = String(game.wave).padStart(2, "0");
    $("lives").textContent = String(game.lives).padStart(2, "0");
    $("pause").disabled = !["playing", "paused"].includes(game.state);
    $("pause").innerHTML = game.state === "paused" ? 'RESUME <span>[P]</span>' : 'PAUSE <span>[P]</span>';
    const view = game.state + ":" + game.reason;
    $("overlay").hidden = game.state === "playing";
    $("wave-message").hidden = !(game.state === "playing" && game.pendingWave > 0);
    $("wave-message").textContent = "WAVE CLEARED";
    if (view === lastView) return;
    lastView = view;
    if (game.state === "ready") {
      $("overlay-kicker").textContent = "40 COLUMNS. ONE MISSION.";
      $("overlay-title").textContent = "DEFEND THE EARTH";
      $("overlay-text").innerHTML = "Move your man. Fire your gun.<br>Don’t let the invaders through.";
      $("start").innerHTML = 'BEGIN GAME <span>[B]</span>';
      $("start-note").textContent = options.lives === 20 ? "Original PET setting: 20 lives." : "Ready with " + options.lives + " lives.";
      $("status").textContent = "AWAITING COMMAND";
    } else if (game.state === "paused") {
      $("overlay-kicker").textContent = "TAKE A BREATHER";
      $("overlay-title").textContent = "GAME PAUSED";
      $("overlay-text").textContent = "The invaders can wait.";
      $("start").innerHTML = 'RESUME GAME <span>[P]</span>';
      $("start-note").textContent = "Your wave and score are safe.";
      $("status").textContent = "PAUSED";
      announce("Game paused.");
    } else if (game.state === "over") {
      $("overlay-kicker").textContent = game.reason === "stopped" ? "COMMAND RECEIVED" : "THE LAST LINE OF DEFENSE";
      $("overlay-title").textContent = game.reason === "stopped" ? "GAME STOPPED" : "GAME OVER";
      $("overlay-text").textContent = game.reason === "invasion" ? "The invaders have overrun your position." :
        game.reason === "lives" ? "All your men have been lost." : "You can begin another mission whenever you’re ready.";
      $("start").innerHTML = 'PLAY AGAIN <span>[B]</span>';
      $("start-note").textContent = "Final score: " + game.score + " · Wave " + game.wave;
      $("status").textContent = "MISSION ENDED";
      announce("Game ended. Score " + game.score + ", wave " + game.wave + ".");
    } else $("status").textContent = "MISSION IN PROGRESS";
  }
  function clearInput() {
    keyboard.clear(); touch.clear();
    ["left", "right", "fire"].forEach(id => $(id).classList.remove("held"));
  }
  function begin() {
    clearInput();
    if (game.state === "paused") game.resume();
    else { game.start(options); announce("Game begun. " + game.lives + " lives."); }
    canvas.focus({ preventScroll: true });
    syncView();
  }
  function togglePause() {
    clearInput();
    if (game.state === "playing") game.pause(); else game.resume();
    syncView();
  }
  function openDialog(id) {
    clearInput();
    dialogPaused = game.state === "playing";
    if (dialogPaused) game.pause();
    if (id === "setup-dialog") {
      $("difficulty").value = String(options.difficulty);
      $("starting-lives").value = String(options.lives);
      $("columns").value = String(options.columns);
    }
    $(id).showModal(); syncView();
  }
  function closeDialog(id) { $(id).close(); }
  for (const id of ["setup-dialog", "about-dialog"]) {
    $(id).addEventListener("close", () => {
      if (dialogPaused) game.resume();
      dialogPaused = false; clearInput(); syncView();
      if (game.state === "playing") canvas.focus({ preventScroll: true });
    });
  }
  $("start").addEventListener("click", begin);
  $("pause").addEventListener("click", togglePause);
  $("settings").addEventListener("click", () => openDialog("setup-dialog"));
  $("about").addEventListener("click", () => openDialog("about-dialog"));
  $("cancel-setup").addEventListener("click", () => closeDialog("setup-dialog"));
  $("close-about").addEventListener("click", () => closeDialog("about-dialog"));
  $("setup-form").addEventListener("submit", event => {
    event.preventDefault();
    options = { difficulty: Number($("difficulty").value), lives: Number($("starting-lives").value), columns: Number($("columns").value) };
    try { localStorage.setItem("pet-invaders-settings", JSON.stringify(options)); } catch (_) {}
    if (game.state === "ready" || game.state === "over") {
      game.start(options); game.state = "ready"; game.events = []; lastView = "";
    }
    closeDialog("setup-dialog");
    announce("Settings saved for your next game.");
  });
  $("sound").addEventListener("click", () => {
    sound = !sound;
    $("sound").textContent = sound ? "SOUND ON" : "SOUND OFF";
    $("sound").setAttribute("aria-pressed", String(sound));
    if (sound) {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (Audio && !audio) audio = new Audio();
      if (audio) audio.resume().catch(() => {});
    }
  });
  function beep(event) {
    if (!sound || !audio || audio.state !== "running") return;
    const frequencies = { shot: 450, hit: 160, damage: 65, mystery: 900, step: 90, wave: 550, over: 50 };
    const oscillator = audio.createOscillator(), gain = audio.createGain(), now = audio.currentTime;
    oscillator.type = "square";
    oscillator.frequency.setValueAtTime(frequencies[event.type] || 180, now);
    oscillator.frequency.exponentialRampToValueAtTime(35, now + 0.09);
    gain.gain.setValueAtTime(event.type === "step" ? 0.006 : 0.022, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.1);
    oscillator.connect(gain); gain.connect(audio.destination);
    oscillator.start(now); oscillator.stop(now + 0.11);
    oscillator.onended = () => { oscillator.disconnect(); gain.disconnect(); };
  }
  const movement = { ArrowLeft: "left", ".": "left", ArrowRight: "right", "=": "right", " ": "fire" };
  window.addEventListener("keydown", event => {
    if ($("setup-dialog").open || $("about-dialog").open || event.ctrlKey || event.metaKey || event.altKey) return;
    const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
    if (movement[key]) {
      event.preventDefault();
      if (game.state === "playing") keyboard.add(key);
      return;
    }
    if (event.repeat) return;
    if (key === "b" && ["ready", "over"].includes(game.state)) { event.preventDefault(); begin(); }
    else if (key === "p" || key === "Escape") { event.preventDefault(); togglePause(); }
    else if (key === "c") { event.preventDefault(); openDialog("setup-dialog"); }
    else if (key === "[" || key === "e") { clearInput(); game.stop(); syncView(); }
  });
  window.addEventListener("keyup", event => { keyboard.delete(event.key); });
  window.addEventListener("blur", () => { clearInput(); game.pause(); syncView(); });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) { clearInput(); game.pause(); syncView(); }
  });
  ["left", "right", "fire"].forEach(id => {
    const button = $(id);
    button.addEventListener("pointerdown", event => {
      event.preventDefault();
      if (game.state !== "playing") return;
      button.setPointerCapture(event.pointerId); touch.add(id); button.classList.add("held");
    });
    const release = () => { touch.delete(id); button.classList.remove("held"); };
    button.addEventListener("pointerup", release);
    button.addEventListener("pointercancel", release);
    button.addEventListener("lostpointercapture", release);
  });
  function frame(time) {
    const dt = lastFrame === null ? 0 : Math.min(0.05, (time - lastFrame) / 1000);
    lastFrame = time;
    const held = direction => touch.has(direction) || [...keyboard].some(k => movement[k] === direction);
    game.update(dt, { left: held("left"), right: held("right"), fire: held("fire") });
    for (const event of game.events) {
      beep(event);
      if (event.type === "wave" && game.wave > 1) announce("Wave " + game.wave + " begins.");
      if (event.type === "damage") announce(game.lives + " lives remaining.");
    }
    game.events = [];
    draw(); syncView(); requestAnimationFrame(frame);
  }
  syncView(); draw(); requestAnimationFrame(frame);
})();
