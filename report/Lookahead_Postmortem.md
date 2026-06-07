# Lookahead Controller — Postmortem

## What We Tried

A lookahead controller that simulates 4 steps ahead, scores each possible future state, and picks the first move on the best path. No opponent model — just a snake asking "where do I end up if I go this way?"

```
Depth 0:  start
          /  |  |  \
Depth 1:  u   d  l  r      (4 nodes)
         /|\
Depth 2: ...               (16 nodes)
         /|\
Depth 3: ...               (64 nodes)
         /|\
Depth 4: ...               (256 nodes)
```

256 terminal states evaluated, best path propagates up.

## Results

| Controller | Avg Score (15×15) | Time/step |
|---|---|---|
| Flood-0.6 | **48.36** | 0.04ms |
| Lookahead d=4 | 29.23 | 0.26ms |

40% worse. 6× slower.

## What Went Wrong

**1. Lookahead couldn't see far enough**

Depth 4 on a 15×15 grid covers 4 cells. Food can be 14 cells away. Most of the time the lookahead can't even reach the food within its window, so it has no signal about which direction leads to food. It falls back to "how many valid moves do I have here?" — which is barely smarter than random.

BFS doesn't have this problem. It explores the entire reachable grid in one pass, no depth limit.

**2. Scoring was a nightmare**

Every fix created a new problem:

| Attempt | Result |
|---|---|
| `score * 50 + distance * 2 + valid_moves * 5` | Snake stalls near food, won't eat |
| Bump eating to `score * 500` | Too aggressive, charges into death |
| Respawn food locally in simulation | Unrealistic — simulation doesn't match real game |
| No food respawn in simulation | No distance guidance after eating |
| Death penalty to -10000 | Still can't beat "wander aimlessly" baseline |

The core tension: eating food gives a one-time bonus, but the lookahead only sees 4 steps. Staying alive gives a consistent small bonus every step. Over 4 steps, "safe and boring" beat "eat once then face the unknown."

**3. Simulation was slow**

Each simulated step:
- Copies the body deque
- Builds a body set for collision checks
- Spawns food (or doesn't)
- Evaluates valid moves

For depth 4 with branching, that's ~256 simulations per real step. At 0.26ms per step, that's 10× slower than the 0.04ms Flood controller. Not worth it for worse scores.

**4. BFS is just better at this problem**

BFS doesn't need lookahead. It explores the *entire* grid in one pass and finds the *guaranteed* shortest path. On a static grid with a static food target, there's no reason to simulate step-by-step — just compute the full path at once.

Lookahead shines in games where:
- Opponents react to your moves
- Moves change the rules (e.g., placing walls)
- The state space is small enough for deep search (tic-tac-toe, chess endgames)

Snake has none of these. It's a pathfinding problem, not a strategy game.

## Lessons Learned

1. **Pick the right tool for the problem.** For grid pathfinding, BFS and A* are the standard for a reason.
2. **Lookahead needs depth.** If you can't see the goal within the window, you're guessing. Depth 4 on a 15×15 grid is blind 90% of the time.
3. **Scoring functions are fragile.** Every weight adjustment changes behavior in unpredictable ways. What works for one grid size breaks on another.
4. **Speed matters.** A 6× slower controller needs to be *significantly* smarter to be worth it. 40% dumber doesn't justify the cost.

## Where to Go From Here

Lookahead is parked in `controller.py` as `LookaheadController` but not worth running. For actual snake improvements:

- **A\*** — already implemented, 41% faster than BFS but scores slightly lower
- **Flood-fill** — safety check on top of BFS, wins by 4% on 15×15 at warn_rate 0.6
- **Hybrid** — use A* for speed, BFS for scoring, Flood for safety. Pick the best parts.

---

*300-game benchmark on grid_size=15. All controllers ran seeds 0–299. Full data in `results/benchmark_20260605_162554.json`.*