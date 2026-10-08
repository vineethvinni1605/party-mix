const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const crypto = require("crypto");

const app = express();
const server = http.createServer(app);
const io = new Server(server);
const PORT = process.env.PORT || 3000;
app.use(express.static("public"));

const rooms = new Map();
const MAX_PLAYERS = 8;
const ROUND_MS = 60000;
const ROUND_NAMES = ["Quiz Clash", "Guess the Word", "Draw & Guess", "Secret Spy", "Speed Challenge"];
const QUESTIONS = [
  { q: "Which planet is known as the Red Planet?", options: ["Venus", "Mars", "Jupiter", "Mercury"], answer: 1 },
  { q: "How many sides does a hexagon have?", options: ["Five", "Six", "Seven", "Eight"], answer: 1 },
  { q: "What is the largest ocean on Earth?", options: ["Atlantic", "Indian", "Arctic", "Pacific"], answer: 3 },
  { q: "Which gas do plants absorb from the atmosphere?", options: ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"], answer: 2 },
  { q: "What is the capital of Japan?", options: ["Seoul", "Tokyo", "Kyoto", "Osaka"], answer: 1 }
];
const WORDS = [
  { word: "PIZZA", hint: "A popular food often shared in slices" },
  { word: "GUITAR", hint: "A musical instrument with strings" },
  { word: "VOLCANO", hint: "A mountain that can erupt" },
  { word: "RAINBOW", hint: "A colorful arc seen in the sky" },
  { word: "ASTRONAUT", hint: "A person trained to travel in space" }
];
const SPEED = [
  { q: "What is 7 × 8?", options: ["54", "56", "58", "64"], answer: 1 },
  { q: "Which is the odd one out?", options: ["Triangle", "Square", "Circle", "Carrot"], answer: 3 },
  { q: "Complete the pattern: 2, 4, 8, 16, __", options: ["18", "24", "30", "32"], answer: 3 },
  { q: "How many minutes are in 2 hours?", options: ["60", "90", "120", "180"], answer: 2 },
  { q: "Which animal is a mammal?", options: ["Shark", "Dolphin", "Trout", "Octopus"], answer: 1 }
];

function code() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let s = "";
  for (let i = 0; i < 5; i++) s += chars[crypto.randomInt(chars.length)];
  return s;
}
function publicRoom(room) {
  return {
    code: room.code, phase: room.phase, hostId: room.hostId, round: room.round,
    roundName: ROUND_NAMES[room.round] || "Results",
    players: [...room.players.values()].map(p => ({ id: p.id, name: p.name, score: p.score, connected: p.connected })),
    deadline: room.deadline, game: room.game ? {
      type: room.game.type, question: room.game.question, options: room.game.options,
      hint: room.game.hint, prompt: room.game.prompt, drawerId: room.game.drawerId,
      canvas: room.game.canvas || [], votes: room.game.votes || {}
    } : null,
    results: room.results || null
  };
}
function emitRoom(room) { io.to(room.code).emit("room:update", publicRoom(room)); }
function playerBySocket(room, socketId) { return room.players.get(socketId); }
function addPoints(room, player, points) {
  if (!player) return;
  player.roundScore = Math.max(0, Math.min(1000, (player.roundScore || 0) + points));
}
function startRound(room) {
  clearTimeout(room.timer);
  room.phase = "playing";
  room.deadline = Date.now() + ROUND_MS;
  room.results = null;
  for (const p of room.players.values()) p.roundScore = 0;
  const index = room.round;
  if (index === 0) {
    const q = QUESTIONS[(room.matchSeed + index) % QUESTIONS.length];
    room.game = { type: "quiz", question: q.q, options: q.options, answer: q.answer, answered: {} };
  } else if (index === 1) {
    const w = WORDS[(room.matchSeed + index) % WORDS.length];
    room.game = { type: "word", word: w.word, hint: w.hint, guessed: {} };
  } else if (index === 2) {
    const players = [...room.players.values()];
    const drawer = players[(room.matchSeed + index) % players.length];
    room.game = { type: "draw", prompt: ["A rocket", "A sleepy cat", "A mountain", "A birthday cake"][room.matchSeed % 4], drawerId: drawer.id, canvas: [], guessed: {}, answered: {} };
  } else if (index === 3) {
    const players = [...room.players.values()];
    const spy = players[(room.matchSeed + index) % players.length];
    room.game = { type: "spy", spyId: spy.id, word: ["Pineapple", "Volcano", "Skateboard", "Penguin"][room.matchSeed % 4], prompt: "Describe your secret word in a few words—don't say it directly.", submitted: {}, votes: {}, voting: false };
    players.forEach(p => io.to(p.id).emit("secret:role", {
      role: p.id === spy.id ? "spy" : "player",
      word: p.id === spy.id ? null : room.game.word,
      message: p.id === spy.id ? "You are the SPY. Blend in and avoid being caught." : "Your secret word is: " + room.game.word
    }));
  } else {
    const q = SPEED[(room.matchSeed + index) % SPEED.length];
    room.game = { type: "speed", question: q.q, options: q.options, answer: q.answer, answered: {} };
  }
  emitRoom(room);
  room.timer = setTimeout(() => endRound(room, "Time's up!"), ROUND_MS);
}
function endRound(room, message = "Round complete!") {
  if (!room || room.phase !== "playing") return;
  clearTimeout(room.timer);
  for (const p of room.players.values()) {
    p.score += p.roundScore || 0;
  }
  room.phase = "between";
  room.deadline = null;
  room.results = { message, scores: [...room.players.values()].map(p => ({ name: p.name, roundScore: p.roundScore || 0, score: p.score })).sort((a,b) => b.roundScore-a.roundScore) };
  room.game = room.game && room.game.type === "spy" ? { ...room.game, word: undefined, spyId: undefined } : room.game;
  emitRoom(room);
}
function maybeAllAnswered(room) {
  if (!room || !room.game) return;
  const g = room.game;
  const active = [...room.players.values()].filter(p => p.connected);
  if (["quiz","speed"].includes(g.type) && active.length && active.every(p => g.answered[p.id] !== undefined)) endRound(room, "Everyone answered!");
}
io.on("connection", socket => {
  socket.on("room:create", ({ name }, cb = () => {}) => {
    const safeName = String(name || "Player").trim().slice(0, 18) || "Player";
    let id;
    do { id = code(); } while (rooms.has(id));
    const room = { code: id, hostId: socket.id, players: new Map(), phase: "lobby", round: 0, game: null, results: null, matchSeed: crypto.randomInt(1000), deadline: null, timer: null };
    room.players.set(socket.id, { id: socket.id, name: safeName, score: 0, roundScore: 0, connected: true });
    rooms.set(id, room); socket.join(id); cb({ ok: true, code: id }); emitRoom(room);
  });
  socket.on("room:join", ({ code: rawCode, name }, cb = () => {}) => {
    const id = String(rawCode || "").trim().toUpperCase();
    const room = rooms.get(id);
    if (!room) return cb({ ok: false, error: "Room not found. Check the code and try again." });
    if (room.players.size >= MAX_PLAYERS) return cb({ ok: false, error: "This room is full (8 players maximum)." });
    if (room.phase !== "lobby") return cb({ ok: false, error: "This match has already started." });
    const safeName = String(name || "Player").trim().slice(0, 18) || "Player";
    if ([...room.players.values()].some(p => p.name.toLowerCase() === safeName.toLowerCase())) return cb({ ok: false, error: "That name is already taken in this room." });
    room.players.set(socket.id, { id: socket.id, name: safeName, score: 0, roundScore: 0, connected: true });
    socket.join(id); cb({ ok: true, code: id }); emitRoom(room);
  });
  socket.on("room:start", () => {
    const room = [...rooms.values()].find(r => r.players.has(socket.id));
    if (!room || room.hostId !== socket.id || room.phase !== "lobby") return;
    if (room.players.size < 2) return socket.emit("notice", "At least two players are required.");
    room.round = 0; room.matchSeed = crypto.randomInt(1000);
    for (const p of room.players.values()) { p.score = 0; p.roundScore = 0; }
    startRound(room);
  });
  socket.on("game:answer", ({ answer }) => {
    const room = [...rooms.values()].find(r => r.players.has(socket.id));
    if (!room || room.phase !== "playing" || !room.game) return;
    const p = playerBySocket(room, socket.id), g = room.game;
    if (!p) return;
    if (["quiz","speed"].includes(g.type)) {
      if (g.answered[socket.id] !== undefined) return;
      const correct = Number(answer) === g.answer;
      g.answered[socket.id] = { correct, at: Date.now() };
      if (correct) {
        const elapsed = Math.max(0, 1 - ((Date.now() - (room.deadline - ROUND_MS)) / ROUND_MS));
        addPoints(room, p, Math.min(1000, 800 + Math.round(200 * elapsed)));
      }
      socket.emit("answer:feedback", { correct, message: correct ? "Correct! Nice work." : "Not quite—keep going next round." });
      emitRoom(room); maybeAllAnswered(room);
    } else if (g.type === "word") {
      if (g.guessed[socket.id]) return;
      const correct = String(answer || "").trim().toLowerCase() === g.word.toLowerCase();
      if (correct) {
        g.guessed[socket.id] = true;
        addPoints(room, p, Math.max(200, 1000 - Object.keys(g.guessed).length * 100));
        socket.emit("answer:feedback", { correct: true, message: "You guessed it!" });
        emitRoom(room);
        if ([...room.players.values()].every(pl => pl.id === g.drawerId || g.guessed[pl.id])) endRound(room, "Word guessed!");
      } else socket.emit("answer:feedback", { correct: false, message: "Not that word—try again." });
    } else if (g.type === "spy" && !g.voting) {
      if (g.submitted[socket.id]) return;
      g.submitted[socket.id] = String(answer || "").slice(0, 100);
      if (Object.keys(g.submitted).length === room.players.size) {
        g.voting = true;
        io.to(room.code).emit("spy:vote", { submissions: [...room.players.values()].map(pl => ({ id: pl.id, name: pl.name, response: g.submitted[pl.id] || "" })) });
      }
      emitRoom(room);
    }
  });
  socket.on("spy:cast", ({ targetId }) => {
    const room = [...rooms.values()].find(r => r.players.has(socket.id));
    if (!room || room.phase !== "playing" || room.game?.type !== "spy" || !room.game.voting) return;
    const g = room.game;
    if (g.votes[socket.id] || !room.players.has(targetId) || targetId === socket.id) return;
    g.votes[socket.id] = targetId;
    if ([...room.players.values()].every(p => g.votes[p.id] || !p.connected)) {
      const counts = {};
      Object.values(g.votes).forEach(id => counts[id] = (counts[id] || 0) + 1);
      const caught = Object.entries(counts).sort((a,b) => b[1]-a[1])[0]?.[0] === g.spyId;
      for (const p of room.players.values()) {
        if (p.id !== g.spyId && g.votes[p.id] === g.spyId) addPoints(room, p, 800);
        if (p.id === g.spyId && !caught) addPoints(room, p, 1000);
      }
      io.to(room.code).emit("spy:reveal", { spyId: g.spyId, word: g.word, caught });
      setTimeout(() => endRound(room, caught ? "The spy was caught!" : "The spy escaped!"), 2500);
    }
    emitRoom(room);
  });
  socket.on("draw:stroke", stroke => {
    const room = [...rooms.values()].find(r => r.players.has(socket.id));
    if (!room || room.phase !== "playing" || room.game?.type !== "draw" || room.game.drawerId !== socket.id) return;
    const g = room.game;
    g.canvas.push(stroke);
    if (g.canvas.length > 400) g.canvas.shift();
    socket.to(room.code).emit("draw:stroke", stroke);
  });
  socket.on("draw:guess", ({ guess }) => {
    const room = [...rooms.values()].find(r => r.players.has(socket.id));
    if (!room || room.phase !== "playing" || room.game?.type !== "draw") return;
    const g = room.game, p = playerBySocket(room, socket.id);
    if (!p || p.id === g.drawerId || g.guessed[socket.id]) return;
    if (String(guess || "").trim().toLowerCase() === g.prompt.toLowerCase()) {
      g.guessed[socket.id] = true; addPoints(room, p, Math.max(200, 800 - Object.keys(g.guessed).length * 100));
      const drawer = room.players.get(g.drawerId);
      if (drawer) addPoints(room, drawer, 200);
      socket.emit("answer:feedback", { correct: true, message: "Correct drawing guess!" }); emitRoom(room);
      if ([...room.players.values()].filter(pl => pl.id !== g.drawerId).every(pl => g.guessed[pl.id])) endRound(room, "Drawing guessed!");
    } else socket.emit("answer:feedback", { correct: false, message: "Try another guess." });
  });
  socket.on("round:next", () => {
    const room = [...rooms.values()].find(r => r.players.has(socket.id));
    if (!room || room.hostId !== socket.id || room.phase !== "between") return;
    if (room.round >= 4) {
      room.phase = "finished"; room.results = { message: "Match complete!", scores: [...room.players.values()].map(p => ({ name: p.name, score: p.score })).sort((a,b) => b.score-a.score) };
      emitRoom(room); return;
    }
    room.round++; startRound(room);
  });
  socket.on("match:rematch", () => {
    const room = [...rooms.values()].find(r => r.players.has(socket.id));
    if (!room || room.hostId !== socket.id || room.phase !== "finished") return;
    room.phase = "lobby"; room.round = 0; room.game = null; room.results = null;
    for (const p of room.players.values()) { p.score = 0; p.roundScore = 0; }
    emitRoom(room);
  });
  socket.on("disconnect", () => {
    for (const room of rooms.values()) {
      const p = room.players.get(socket.id);
      if (!p) continue;
      p.connected = false;
      if (room.hostId === socket.id) {
        const next = [...room.players.values()].find(x => x.connected);
        if (next) room.hostId = next.id;
      }
      emitRoom(room);
      setTimeout(() => {
        if (room.players.get(socket.id)?.connected) return;
        room.players.delete(socket.id);
        if (!room.players.size) { clearTimeout(room.timer); rooms.delete(room.code); }
        else emitRoom(room);
      }, 60000);
    }
  });
});
server.listen(PORT, () => console.log(`Party Mix running at http://localhost:${PORT}`));
