# Lookahead Controller — One-Player Simulation for Snake

## The Idea

Minimax is overkill for snake. There's no real opponent — the food just sits there, the walls don't move. So why simulate two players when you only need one?

**Lookahead** works like this: at each step, simulate every possible move 3-5 steps ahead, scoring each path. Pick the first move that leads to the best future. No Min layer, no opponent model — just pure "what happens if I go this way?"

## Why It Works for Snake

| Problem | Minimax | Lookahead |
|---|---|---|
| Snake has no opponent | Forces an artificial Min player | Doesn't need one — just simulates itself |
| Tree is too big | 4^depth branches (huge) | Still 4^depth, but no alternating layers |
| Score ambiguity | Needs two scoring systems | One scoring function is enough |
| Implementation | Complex (alpha-beta, two eval modes) | Simple (loop + simulate + score) |

Lookahead doesn't try to be clever about "what would my enemy do." It just runs N steps forward, sees where each path leads, and picks the most promising one. Less elegant on paper, often just as good in practice.

## How It Works

```
For each valid direction I can move right now:
    Simulate that move → snapshot A
    For each valid direction from snapshot A:
        Simulate that move → snapshot B
        For each valid direction from snapshot B:
            Score the final state
        Pick the best score at depth 3
    Pick the best score at depth 2
Pick the best direction at depth 1 → that's your move
```

No alternating turns. No Min. Just a snake looking into its own future and deciding which path is safest.

## The Tree

At depth 3 with full branching:

```
Depth 0:         start
              /   |   |   \
Depth 1:     u    d    l    r       (4 nodes)
            /|\   /|\  /|\  /|\
Depth 2:   u d l r ...            (16 nodes)
           /|\
Depth 3:  u d l r ...             (64 nodes)
```

64 nodes to score at depth 3. That's cheap. Depth 4 pushes it to 256, depth 5 to 1024. Still manageable on a 30×30 grid.

## Scoring Function

At the final depth, you assign a score to the simulated state. Components:

| Factor | Why | Suggested Weight |
|---|---|---|
| **Game over** | Dead snake is bad. Penalty should be huge. | −1000 |
| **Ate food** | Food is the goal. Large bonus. | +100 |
| **Distance to food** | Closer is better. Guides the search toward food even when it can't reach it. | −2 per cell |
| **Valid moves remaining** | More options = less trapped. | +5 per option |

A simple scoring function:

```python
def evaluate(sim_state, sim_snake):
    if sim_state.game_over:
        return -1000 + sim_state.score

    score = sim_state.score * 50
    score -= manhattan(sim_snake.head, sim_state.food_pos) * 2
    score += len(get_valid_moves(sim_state)) * 5
    return score
```

## Pruning — Making It Faster

Even at depth 4 (256 nodes), you can cut branches:

1. **Dead branch pruning** — If a simulated move dies early, stop exploring deeper from that path. Dead ends propagate up quickly.

2. **Beam search** — At each depth, only keep the top K scoring paths. K=3 means at depth 3 you evaluate 4×3×3 = 36 nodes instead of 64. Loses some accuracy but runs much faster.

3. **Early food bonus** — If any path reaches food within the lookahead window, boost its score immediately. The snake learns to value "guaranteed food now" over "maybe food later."

## Integration into SnakeArena

```python
class LookaheadController(Controller):
    def __init__(self, depth=4, beam_width=None):
        self.depth = depth
        self.beam_width = beam_width

    def react(self, game_state, events):
        best_dir = None
        best_score = -float('inf')

        for direction in self.get_valid_dir(game_state):
            sim = self._simulate(game_state, direction)
            score = self._lookahead(sim, self.depth - 1)
            if score > best_score:
                best_score = score
                best_dir = direction

        return best_dir or (0, 0)
```

The `_simulate` method is the trickiest part. You need a lightweight copy of the game state — head, tail, body set, food, score, alive flag. You don't need a full Pygame game object. A small dataclass is enough:

```python
@dataclass
class SimState:
    head: tuple
    body: set
    food: tuple
    score: int
    alive: bool
    grid_size: int
```

## Speed Estimates on 30×30

| Depth | Full tree | Beam K=3 | Time estimate |
|---|---|---|---|
| 2 | 16 nodes | 12 | < 0.1ms |
| 3 | 64 nodes | 36 | ~0.1ms |
| **4** | **256 nodes** | **108** | **~0.3ms** |
| 5 | 1024 nodes | 324 | ~1ms |
| 6 | 4096 nodes | 972 | ~4ms |

Depth 4 with beam search is probably the sweet spot — comparable to BFS speed but with lookahead intelligence.

## How It Compares

| Controller | Avg Score (15×15) | Speed |
|---|---|---|
| BFS | 46.9 | 0.028ms |
| Flood-0.6 | 48.4 | 0.038ms |
| Lookahead d=4 | ? | ~0.3ms (estimated) |
| Lookahead d=5 | ? | ~1ms (estimated) |

The question is whether the score gain is worth the speed cost. On a 15×15 grid, lookahead might push past 50. On 30×30, BFS might still win because there's enough room to not *need* planning.

## Summary

- **Lookahead** = simulate all your own moves N steps ahead, pick the best path
- **Simpler than Minimax** — no opponent model, no alternating turns
- **Fast enough at depth 3-4** with beam search
- **Scoring function is flexible** — tweak weights and see what works
- **Worth testing** on small grids where BFS and Flood are already close