# SnakeArena — Upcoming

## To-Do

- [ ] **Menu theme picker** — cycle through color themes inside the menu instead of editing code
- [ ] **Wander heatmap** — render visited cells as a fading trail in the game view
- [ ] **Game over stats** — show score, steps, controller name on the game over screen
- [ ] **HamiltonianController** — space-filling cycle, literally immortal

## Done

| Controller | Status | Best Score | Notes |
|---|---|---|---|
| Drunk | ✅ | 3.7 | Random moves, baseline |
| Greedy | ✅ | 41.9 | Chase food directly |
| BFS | ✅ | 109.4 | Pathfinding, shuffle_once |
| Flood | ✅ | 48.4 (15×15) | BFS + safety check |
| A* | ✅ | 101.8 | 41% faster than BFS |
| Lookahead | ❌ | 29.2 | RIP |
| Wander | ✅ | 419 (30×30) | Space-filling, 2-mod-4 pattern |
| Menu system | ✅ | — | Parameter UI + color themes |
