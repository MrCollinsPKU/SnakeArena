# BFS Tiebreaker Strategies — Benchmark Report

## Context

SnakeArena's `BFSController` uses breadth-first search to find the shortest path to food (or the tail if food is unreachable). During BFS, when multiple neighbors are at the same distance, the **tiebreaker order** determines which direction the snake picks.

The original `BFSController` shuffled the direction list once per BFS call. That raised a few questions:

- Does shuffling *more* (every node) help the snake survive longer by creating a curlier trace?
- Does shuffling *less* (fixed order) trap the snake in predictable patterns?
- What's the computational cost of each approach?

To find out, the class was refactored: `BFSController` now takes a `strategy` parameter with four modes, and everything except the tiebreaker logic is shared.

## Contenders

| Variant | Strategy | Tiebreaker | Random calls per BFS |
|---|---|---|---|
| **BFS-ShufOnce** | `"shuffle_once"` | Shuffle direction list once per BFS call | 1 |
| **BFS-NoShuf** | `"no_shuffle"` | Fixed order: up → down → left → right | 0 |
| **BFS-Rot** | `"rotate"` | Random start offset, then fixed cycle | 1 (randint) |
| **BFS-PerNode** | `"per_node"` | Shuffle direction list at every node | ~500+ |

All four share the same optimized code path — 2D array visited tracking, no tuple allocations, `random.shuffle` pulled out of the loop. Only the tiebreaker differs.

## Methodology

- **Grid**: 30×30 (900 cells)
- **Games per variant**: 100
- **Max steps per game**: 10,000 (counts as timeout)
- **Seeds**: 0–99, identical across all variants
- **Metrics**: average score, max/min score, avg compute time per step, timeout rate

### Baseline controllers (for reference)

| Variant | Avg score | Avg compute time (ms/step) |
|---|---|---|
| Drunk (random moves) | 3.7 | 0.002 |
| Greedy (chase food directly) | 41.9 | 0.004 |

## Results — BFS variants

### Speed

| Variant | Avg compute time (ms/step) | Relative cost |
|---|---|---|
| BFS-NoShuf | **0.102** | 1.00× (baseline) |
| BFS-ShufOnce | **0.103** | 1.01× |
| BFS-Rot | 0.104 | 1.02× |
| BFS-PerNode | **0.227** | **2.23×** |

The optimization work (2D array + shuffle moved outside the loop) brought the original BFS from **0.299ms** (v0.2.1) down to **0.103ms** — a ~3× improvement before even touching tiebreakers.

PerNode is **2.2× slower** than the rest — shuffling ~500 times per BFS call is pure waste. NoShuf, ShufOnce, and Rot are essentially tied; a single shuffle or `randint` is invisible at this scale.

### Score

| Variant | Avg score | Max | Min | Timeout rate |
|---|---|---|---|---|
| **BFS-ShufOnce** | **109.4** | 175 | 36 | 0% |
| BFS-NoShuf | 107.7 | 171 | 26 | 0% |
| BFS-Rot | 103.2 | 169 | 20 | 0% |
| BFS-PerNode | 102.6 | 177 | 43 | 0% |

### Key observations

1. **Zero timeouts** — All four variants finished every game within 10,000 steps. BFS rarely gets into true death spirals on a 30×30 grid.

2. **ShufOnce leads on average score** (109.4) — Edges ahead by 1.6% over NoShuf and 6% over Rot/PerNode. One shuffle per BFS call gives enough variety to dodge early traps without degrading path quality.

3. **NoShuf has the lowest min** (26) — The fixed up→down→left→right order sometimes builds a straight corridor that boxes the snake in early. But when it works, it's nearly as good as ShufOnce (max 171 vs 175).

4. **PerNode has the highest min** (43) — Maximum randomness means it almost never gets cornered. But the average is the lowest (102.6), suggesting the random paths are consistently mediocre rather than occasionally brilliant.

5. **Rot underperformed** — Same randomness budget as ShufOnce (one random draw per BFS), but scores 6% lower. Possible explanation: cycling `[up, down, left, right]` from a random start preserves the *relative* order (up always comes before down), while a true shuffle breaks all ordering relationships, creating more variety.

## Conclusion

| Strategy | Verdict |
|---|---|
| **`"shuffle_once"`** | 🥇 **Best balance** — highest avg score, negligible cost |
| **`"no_shuffle"`** | 🥈 Slightly lower avg, zero random calls, but riskier early-game |
| **`"rotate"`** | ❌ Same cost as shuffle_once but scores lower — no reason to use it |
| **`"per_node"`** | ❌ 2.2× slower, no score benefit — avoid |

**Final call**: `"shuffle_once"` is the sweet spot. One shuffle per BFS call costs nothing measurable, gives the highest average score, and avoids the occasional early trap that fixed ordering causes.

If you want fully deterministic runs for debugging, `"no_shuffle"` is a decent backup at a ~1.5% score penalty. The other two strategies offer no advantage and can be dropped.

---

*Generated from 100-game benchmark on grid_size=30, max_steps=10000. All variants ran the same seeds 0–99. Raw data in `benchmark_20260604_191757`.*
