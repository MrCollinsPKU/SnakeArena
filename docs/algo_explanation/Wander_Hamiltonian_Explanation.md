# Two New Controller Ideas

## 1. WanderController

### The Idea

Most controllers chase food. That's the obvious thing to do. But chasing food builds long straight tails, and long straight tails box the snake in.

WanderController ignores food entirely. Instead, it scores each direction by **how long it's been since the snake last visited that cell**. The snake naturally spreads out, avoids revisiting recent spots, and fills the grid evenly.

### How It Works

Keep a 2D array the size of the grid, initialized to 0. Every time the snake moves into a cell, set it to the current step count. To pick a direction, score each valid move by:

```
score = current_step - last_visited[cell]
```

Higher = fresher cell = more interesting. The snake wants to go where it hasn't been in a while.

### Example

```
Grid at step 50, snake head at (7, 7):

Cell (7, 8) was last visited at step 45 → score = 50 - 45 = 5
Cell (7, 6) was last visited at step 10 → score = 50 - 10 = 40  ← prefers this
Cell (8, 7) was last visited at step 48 → score = 50 - 48 = 2
Cell (6, 7) was last visited at step 30 → score = 50 - 30 = 20
```

The snake turns toward the cell it hasn't seen in the longest time. This creates a natural wandering pattern that fills space efficiently.

### Food Handling

When the snake happens to step onto food, it eats it and grows. No special logic needed — food is just a bonus that happens along the way. The snake doesn't change behavior for it.

### Expected Behavior

- **Early game**: Snake spreads evenly across the grid. No straight lines, no self-trapping.
- **Mid game**: Snake fills open space methodically. Rarely gets stuck because it always prefers fresh cells.
- **Late game**: When the grid is mostly body, the snake naturally follows corridors of unvisited cells — it practically solves the Hamiltonian problem without computing it.

### Scoring function

```python
class WanderController(Controller):
    def __init__(self, grid_size=30):
        self.last_visited = [[0] * grid_size for _ in range(grid_size)]
        self.step = 0

    def react(self, game_state, events):
        head = game_state.snake.head
        self.last_visited[head[0]][head[1]] = self.step
        self.step += 1

        best_dir = None
        best_score = -1

        for direction in self.get_valid_dir(game_state):
            dr, dc = direction
            nr, nc = head[0] + dr, head[1] + dc
            score = self.step - self.last_visited[nr][nc]
            if score > best_score:
                best_score = score
                best_dir = direction

        return best_dir or (0, 0)
```

### Pros and Cons

| Pros | Cons |
|---|---|
| Very simple, almost no compute | Ignores food — eats by accident |
| Naturally avoids traps | Score depends on food luck |
| No pathfinding needed | Large grids → slow to fill |
| Spreads the tail evenly | No strategy, pure instinct |

---

## 2. HamiltonianController

### The Idea

A **Hamiltonian cycle** is a path that visits every cell on the grid exactly once and returns to the start. If the snake follows this cycle, it can **never die** — every step is predetermined, and as long as the cycle exists, the snake always has a safe move.

The trick is maintaining the cycle when the snake eats food and grows. Each time the body gets longer, the cycle needs to be patched.

### How Hamiltonian Cycles Work

On a grid graph, a Hamiltonian cycle is a loop that touches every cell:

```
Start → * → * → * → *
  ↑                 ↓
  * → * → * → * → *
  ↑                 ↓
  * → * → * → * → *
  ↑                 ↓
  * ← * ← * ← * ← *
```

The snake's head follows the arrows. The tail follows behind. As long as the head stays on the cycle and doesn't skip ahead, it never collides with itself.

### Generating the Cycle

The simplest method: **spanning tree + walkaround**.

1. Treat every cell as a node in a grid graph.
2. Generate a spanning tree of the grid (DFS, random walk, whatever).
3. Walk around the tree — every edge is traversed twice (once forward, once back). This creates a cycle that visits each cell once.
4. The cycle length = number of cells on the grid.

For a 15×15 grid, that's a cycle of length 225. The snake follows this cycle step by step.

### The Growth Problem

When the snake eats food:

- The body grows by 1 cell.
- The old tail doesn't move.
- Now the cycle is broken — the snake's body occupies one more cell than before.
- The cycle needs to be **patched** to accommodate the new body length.

Patch technique: find the cell that was the food, and insert it into the cycle as a detour. The snake now takes one extra step to loop around that cell, which accounts for the extra body segment.

This is the hard part. There's research on this — "Hamiltonian cycles for snake" is a known problem in competitive snake AI.

### Simplified Variant

Instead of a true Hamiltonian cycle, use a **spanning tree walk**:

1. Generate a spanning tree of the reachable area.
2. Walk the tree in DFS order.
3. The snake follows the DFS path.
4. When it eats food and grows, regenerate the tree from the new state.

This is cheaper and simpler, but doesn't guarantee optimal behavior. The snake might walk inefficient paths between food spawns.

### Expected Behavior

- **Immortal** on any grid where a Hamiltonian cycle exists (n×n grid with both even dimensions, or similar).
- **Score limited** by cycle length — the snake must traverse ~half the grid between each food spawn.
- **Boring to watch** — the snake follows the same pattern every game.
- **Interesting as a proof of concept** — "my snake literally cannot die."

### Pseudocode

```python
class HamiltonianController(Controller):
    def __init__(self, grid_size):
        self.cycle = self._build_cycle(grid_size)
        self.index = 0

    def _build_cycle(self, grid_size):
        # Generate a Hamiltonian cycle on grid_size × grid_size
        # Returns a list of (r, c) positions in cycle order
        ...

    def react(self, game_state, events):
        # Move to the next cell in the cycle
        self.index = (self.index + 1) % len(self.cycle)
        next_cell = self.cycle[self.index]
        head = game_state.snake.head
        return (next_cell[0] - head[0], next_cell[1] - head[1])
```

### Pros and Cons

| Pros | Cons |
|---|---|
| Literally immortal on suitable grids | Complex to implement correctly |
| Guaranteed safety every step | Cycle patching on growth is hard |
| Fills the entire grid eventually | Low score ceiling — slow between food |
| Beautiful math | Boring to watch |

---

## Which One to Try First?

| Controller | Effort | Expected score | Cool factor |
|---|---|---|---|
| **Wander** | Low (1 evening) | ~30-40 (pure luck on food) | Medium |
| **Hamiltonian** | High (needs graph theory) | ~50-80 (immortal but slow) | Very high |

Wander is a quick win — simple code, interesting behavior. Hamiltonian is a project. If you want to build something impressive, go Hamiltonian. If you want to see results fast, go Wander.
