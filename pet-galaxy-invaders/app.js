(function () {
  "use strict";
  const { Game, WIDTH, HEIGHT, DEFAULTS, rasterize, writeText } = window.PetInvaders;
  const $ = id => document.getElementById(id);
  const canvas = $("game"), context = canvas.getContext("2d");
  context.imageSmoothingEnabled = false;
  const framePixels = context.createImageData(WIDTH, HEIGHT);
  const game = new Game();
  let options = { ...DEFAULTS }, sound = false, audio = null, oscillator = null, gain = null;
  let previousAudio = "", previousView = "", previousWave = 1, dialogPaused = false;
  let lastFrame = null;
  try {
    const saved = JSON.parse(localStorage.getItem("pet-invaders-parameters") || "null");
    if (saved && typeof saved === "object") {
      if ([1, 3, 5, 20].includes(saved.lives)) options.lives = saved.lives;
      if ([4, 6, 8, 10].includes(saved.columns)) options.columns = saved.columns;
      if ([5, 10, 20].includes(saved.delay)) options.delay = saved.delay;
    }
  } catch (_) { /* Local storage is optional. */ }
  game.options = { ...options };
  const keyboard = new Set(), touch = new Set();
  function announce(message) { $("announcement").textContent = message; }
  function clearInput() {
    keyboard.clear(); touch.clear();
    ["left", "right", "fire"].forEach(id => $(id).classList.remove("held"));
  }
  function draw() {
    let screen = game.screen;
    if (game.state === "paused") {
      screen = new Uint8Array(screen);
      for (let row = 10; row <= 14; row++) screen.fill(32, row * 40 + 8, row * 40 + 32);
      writeText(screen, 14, 11, "GAME PAUSED");
      writeText(screen, 11, 13, "PRESS P TO CONTINUE");
    }
    rasterize(screen, framePixels.data);
    context.putImageData(framePixels, 0, 0);
  }
  function syncView() {
    $("pause").disabled = !["playing", "paused"].includes(game.state);
    $("pause").textContent = game.state === "paused" ? "RESUME [P]" : "PAUSE [P]";
    $("start").hidden = game.state === "playing";
    $("start").textContent = game.state === "paused" ? "RESUME [P]" : game.state === "over" ? "PLAY AGAIN [B]" : "BEGIN GAME [B]";
    const view = game.state + ":" + game.reason;
    if (view === previousView) return;
    previousView = view;
    $("status").textContent = game.state === "ready" ? "AWAITING COMMAND" :
      game.state === "playing" ? "ORIGINAL PET PROGRAM RUNNING" : game.state === "paused" ? "PAUSED" :
      game.reason === "stopped" ? "STOPPED — PRESS B TO BEGIN" :
      game.reason === "invasion" ? "INVASION — PRESS B TO BEGIN" : "GAME OVER — PRESS B TO BEGIN";
    announce(game.state === "over" ? `Game ended. Score ${game.score}. ${game.lives} men remaining.` :
      game.state === "paused" ? "Game paused." : game.state === "playing" ? "Game begun or resumed." : "Ready. Press B to begin.");
  }
  function begin() {
    clearInput();
    if (game.state === "paused") game.resume();
    else { game.start(options); previousWave = 1; }
    lastFrame = null;
    canvas.focus({ preventScroll: true });
    syncView(); draw();
  }
  function togglePause() {
    clearInput();
    if (game.state === "playing") game.pause(); else game.resume();
    lastFrame = null;
    syncView(); draw();
  }
  function openDialog(id) {
    clearInput(); dialogPaused = game.state === "playing";
    if (dialogPaused) game.pause();
    if (id === "setup-dialog") {
      $("delay").value = String(options.delay);
      $("starting-lives").value = String(options.lives);
      $("columns").value = String(options.columns);
    }
    $(id).showModal(); syncView(); draw();
  }
  for (const id of ["setup-dialog", "about-dialog"]) {
    $(id).addEventListener("close", () => {
      if (dialogPaused) game.resume();
      dialogPaused = false; clearInput(); lastFrame = null; syncView(); draw();
      if (game.state === "playing") canvas.focus({ preventScroll: true });
    });
  }
  $("start").addEventListener("click", begin);
  $("pause").addEventListener("click", togglePause);
  $("settings").addEventListener("click", () => openDialog("setup-dialog"));
  $("about").addEventListener("click", () => openDialog("about-dialog"));
  $("cancel-setup").addEventListener("click", () => $("setup-dialog").close());
  $("close-about").addEventListener("click", () => $("about-dialog").close());
  $("setup-form").addEventListener("submit", event => {
    event.preventDefault();
    options = { delay: Number($("delay").value), lives: Number($("starting-lives").value), columns: Number($("columns").value) };
    try { localStorage.setItem("pet-invaders-parameters", JSON.stringify(options)); } catch (_) {}
    if (game.state === "ready") game.options = { ...options };
    $("setup-dialog").close();
    announce("Parameters saved for the next game.");
  });
  $("sound").addEventListener("click", () => {
    sound = !sound;
    $("sound").textContent = sound ? "SOUND ON" : "SOUND OFF";
    $("sound").setAttribute("aria-pressed", String(sound));
    if (sound) {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (Audio && !audio) {
        audio = new Audio(); oscillator = audio.createOscillator(); gain = audio.createGain();
        oscillator.type = "square"; gain.gain.value = 0;
        oscillator.connect(gain); gain.connect(audio.destination); oscillator.start();
      }
      if (audio) audio.resume().catch(() => {});
    }
    previousAudio = ""; syncAudio();
  });
  function syncAudio() {
    if (!audio) return;
    // Optional approximation of the original CB2 sound output from its VIA registers.
    const timer = game.memory[0xe848];
    const active = sound && game.state === "playing" && timer !== 255 && game.memory[0xe84b] === 16;
    const key = active + ":" + timer;
    if (key === previousAudio) return;
    previousAudio = key;
    gain.gain.setTargetAtTime(active ? 0.018 : 0, audio.currentTime, 0.006);
    oscillator.frequency.setTargetAtTime(1000000 / (16 * (timer + 2)), audio.currentTime, 0.006);
  }
  const movement = { ArrowLeft: "left", ".": "left", ArrowRight: "right", "=": "right", " ": "fire" };
  window.addEventListener("keydown", event => {
    if ($("setup-dialog").open || $("about-dialog").open || event.ctrlKey || event.metaKey || event.altKey) return;
    const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
    if (movement[key]) {
      event.preventDefault(); if (game.state === "playing") keyboard.add(key); return;
    }
    if (event.repeat) return;
    if (key === "b" && ["ready", "over"].includes(game.state)) { event.preventDefault(); begin(); }
    else if (key === "p" || key === "Escape") { event.preventDefault(); togglePause(); }
    else if (key === "c") { event.preventDefault(); openDialog("setup-dialog"); }
    else if (key === "[" || key === "e") {
      clearInput(); game.stop(); syncView(); draw(); syncAudio();
    }
  });
  window.addEventListener("keyup", event => { keyboard.delete(event.key); });
  function autoPause() { clearInput(); game.pause(); syncView(); draw(); syncAudio(); }
  window.addEventListener("blur", autoPause);
  document.addEventListener("visibilitychange", () => { if (document.hidden) autoPause(); });
  ["left", "right", "fire"].forEach(id => {
    const button = $(id);
    button.addEventListener("pointerdown", event => {
      event.preventDefault(); if (game.state !== "playing") return;
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
    const held = direction => touch.has(direction) || [...keyboard].some(key => movement[key] === direction);
    game.update(dt, { left: held("left"), right: held("right"), fire: held("fire") });
    for (const event of game.events) {
      if (event.type === "wave" && game.wave > previousWave) {
        previousWave = game.wave; announce("Rack " + game.wave + " begins.");
      }
      if (event.type === "damage") announce(game.lives + " men remaining.");
    }
    game.events = [];
    draw(); syncView(); syncAudio(); requestAnimationFrame(frame);
  }
  syncView(); draw(); requestAnimationFrame(frame);
})();
