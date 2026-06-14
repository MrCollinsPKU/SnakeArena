# A* (A-Star) Algorithm — Overview & SnakeArena Integration

## What is A*?

A* is a **pathfinding algorithm** that finds the shortest path from point A to point B on a grid (or graph). It's like BFS but **smarter** — instead of blindly spreading in all directions, it uses a **heuristic** to guess which directions are most promising and explores those first.

### How it works

A* maintains a **priority queue** of nodes to explore. Each node has a cost:

```
f(n) = g(n) + h(n)
```

| Term | Meaning |
|---|---|
| `g(n)` | actual distance from start to node `n` |
| `h(n)` | **heuristic** — estimated distance from `n` to the target |
| `f(n)` | total estimated cost — the priority value |

The algorithm always pops the node with the lowest `f(n)` from the queue, so it naturally heads toward the target while still guaranteeing the shortest path.

### Common heuristic for grids

**Manhattan distance** (the most common for 4-directional movement):

```
h(n) = |target_row - n_row| + |target_col - n_col|
```

This is **admissible** (never overestimates) and **consistent**, which guarantees A* finds the optimal path.

### A* vs BFS

| Aspect | BFS | A* |
|---|---|---|
| Search pattern | Expands in all directions equally | Heads toward the target |
| Nodes visited for far targets | Most of the grid | Much fewer (often 10–30% of BFS) |
| Path optimality | Always shortest | Always shortest (with admissible heuristic) |
| Heuristic needed | No | Yes |
| Per-node overhead | Low | Slightly higher (priority queue) |

**Visual comparison** on an open grid (S = start, T = target):

```
BFS:  * * * * * * * * *    A*:          * * *
      * * * * * * * * *                * * * * *
      * * * S * * * * *              * * * S * * *
      * * * * * * * * *                * * * * *
      * * * * * * * T *                  * * * T
```

BFS wastes time expanding in the wrong direction. A* stays focused on the corridor toward the target.

## For SnakeArena specifically

### Why A* might help

Currently `BFSController` runs **2–3 BFS per step**: one to food, one to tail (if food is unreachable), sometimes a fallback. Each BFS on a 30×30 grid visits hundreds of nodes.

With A*:

- **Path to food** — A* visits far fewer nodes on average, especially when the food is close. A snake's head is often within 10–20 cells of the food, so A* would find it almost instantly.
- **Path to tail** — Tail can be further away, but A* still beats BFS by expanding in the right direction first.
- **Result**: lower compute time per step, especially as the snake grows and the board gets more crowded.

### The catch — obstacles and dead ends

BFS has one advantage: when the food is **completely unreachable** (blocked by the snake's body), BFS exhausts the entire reachable area and quickly returns `None`. A* with a greedy heuristic might spend time exploring a dead-end corridor before giving up.

**Solution**: Use A* for the common case (food is reachable), fall back to BFS or your existing tail-chase logic when A* fails.

### Integration sketch

You can add an `AStarController` that follows the same pattern as the existing controllers:

```python
class AStarController(Controller):
    def react(self, game_state, events):
        snake = game_state.snake
        head = snake.head
        food = game_state.food_pos
        tail = snake.tail
        grid_size = game_state.grid_size
        obstacles = set(snake.body)
        obstacles.discard(tail)

        path = self._astar(head, food, obstacles, grid_size)
        if path and len(path) > 1:
            dr = path[1][0] - path[0][0]
            dc = path[1][1] - path[0][1]
            return (dr, dc)

        # fallback: chase tail with A*
        path = self._astar(head, tail, obstacles, grid_size)
        if path and len(path) > 1:
            dr = path[1][0] - path[0][0]
            dc = path[1][1] - path[0][1]
            return (dr, dc)

        # last resort
        return self.bold_react(game_state, tail)
```

### A* pseudocode for your grid

```
function astar(start, target, obstacles, grid_size):
    g_score = 2D array of INF
    g_score[start] = 0
    f_score[start] = manhattan(start, target)

    open = priority queue ordered by f_score
    open.push(start, f_score[start])
    came_from = 2D array of None

    while open is not empty:
        current = open.pop()
        if current == target:
            return reconstruct_path(came_from, current)

        for each neighbor (dr, dc) of current:
            if out of bounds or in obstacles:
                continue
            tentative_g = g_score[current] + 1
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + manhattan(neighbor, target)
                open.push(neighbor, f_score[neighbor])

    return None  # no path
```

### Changing tiebreaker behavior

Like BFS, A* can have the same tiebreaker strategies. When two nodes have the same `f(n)`, which one gets popped first? You can:

- Use a stable priority queue (first-in-first-out for ties)
- Add a tiny random jitter to `f(n)` — `f(n) += random.uniform(0, 0.001)` for variety
- Tiebreak with a second heuristic (prefer nodes closer to target by one axis)

### Expected performance on SnakeArena

| Metric | BFS (current) | A* (estimated) |
|---|---|---|
| Nodes visited per call (avg) | ~500–800 | ~50–200 |
| Time per step | 0.103ms | ~0.03–0.08ms |
| Path quality | Optimal | Optimal |
| Scenario: food 3 cells away | ~50 nodes | ~5–10 nodes |

### Potential issue — Python's `heapq` overhead

Python's `heapq` (priority queue) operations are O(log n) vs BFS's O(1) pops from a deque. On a 30×30 grid the difference is tiny, but it means A* won't be *dramatically* faster for very close targets. The real savings come when the food is far — A* can skip entire quadrants of the grid.

## Summary

- **A* = BFS + heuristic guidance** — same path quality, fewer nodes visited
- **Easy to add** — follows the same `Controller` pattern, same obstacle/fallback logic
- **Best for**: medium-to-long range paths where BFS wastes time expanding in the wrong direction
- **Tiebreaker strategies** work the same way (shuffle_once, no_shuffle, per_node, rotate)
- **Watch out for**: dead-end scenarios where A* can chase a heuristic into a corner — fallback to tail-chase handles this

Want a working `AStarController` I can drop into `controller.py`?
