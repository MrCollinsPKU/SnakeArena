import heapq
import pygame
import random
from collections import deque

from abc import ABC, abstractmethod



class Controller():
    @abstractmethod
    def react(self, game_state, events):
        pass

    @property
    def name(self):
        return type(self).__name__.removesuffix("Controller")

    def would_collide(self, game_state, new_head, ignore_tail=False):
        # ignore_tail: treat the current tail as empty (when not eating food)
        snake = game_state.snake

        # Boundary
        if not (0 <= new_head[0] < game_state.grid_size and 0 <= new_head[1] < game_state.grid_size):
            return True
        
        # Self collision
        body_set = snake.get_body_set()
        if ignore_tail:
            body_set.discard(snake.tail)
        return new_head in body_set
    
    def get_valid_dir(self, game_state):
        snake = game_state.snake
        valid = []
        for dr, dc in ((0,1),(0,-1),(1,0),(-1,0)):
            new_head = (snake.head[0] + dr, snake.head[1] + dc)
            ignore_tail = new_head != game_state.food_pos
            if not self.would_collide(game_state, new_head, ignore_tail):
                valid.append((dr,dc))
        return valid
    
    def bold_react(self, game_state, target):
        valid_dir = self.get_valid_dir(game_state)
        if not valid_dir:
            return (0,0)

        head_pos = game_state.snake.head
        target_vec = (target[0] - head_pos[0], target[1] - head_pos[1])
        max_prod = -float('inf')
        for dir in valid_dir:
            if dir[0]*target_vec[0] + dir[1]*target_vec[1] > max_prod:
                final_dir = dir
                max_prod = dir[0]*target_vec[0] + dir[1]*target_vec[1]
        return final_dir
    
class HumanController(Controller):
    def __init__(self):
        self.current_dir = (0, 1)   # initial direction, e.g., right
        self.key_to_dir = {
            pygame.K_UP:    (-1, 0),
            pygame.K_DOWN:  (1,  0),
            pygame.K_LEFT:  (0, -1),
            pygame.K_RIGHT: (0,  1)
        }

    def react(self, game_state, events):
        KEY_TO_DIR = self.key_to_dir
        final_dir = None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in KEY_TO_DIR:
                final_dir = KEY_TO_DIR[event.key]

        if final_dir and final_dir != (-self.current_dir[0], -self.current_dir[1]):
            self.current_dir = final_dir
            return final_dir
        
        return self.current_dir


class DrunkController(Controller):
    def react(self, game_state, events):
        valid_dir = self.get_valid_dir(game_state)
        return random.choice(valid_dir) if valid_dir else (0,0)


class GreedyController(Controller):
    def react(self, game_state, events):
        food_pos = game_state.food_pos
        return self.bold_react(game_state, food_pos)


class BFSController(Controller):
    """Parameterized BFS — pick your tiebreaker strategy.
    """
    params = [
        {"key": "strategy", "label": "Tiebreaker", "type": "choice",
         "options": ["shuffle_once", "no_shuffle", "rotate", "per_node"]},
    ]


    def __init__(self, strategy="shuffle_once"):
        self.strategy = strategy

    def react(self, game_state, events):
        snake = game_state.snake
        head, tail, food_pos, grid_size = snake.head, snake.tail, game_state.food_pos, game_state.grid_size
        obstacles = set(snake.body)
        obstacles.discard(snake.tail)
        
        # try to find path to food
        dir_to_food = self._bfs_next_direction(head, food_pos, obstacles, grid_size)
        if dir_to_food is not None:
            return dir_to_food
        
        # if can't reach food, try tail
        dir_to_tail = self._bfs_next_direction(head, tail, obstacles, grid_size)
        if dir_to_tail is not None:
            return dir_to_tail
        
        # if can't reach tail, go straightly towards tail
        return self.bold_react(game_state, tail)

    def _bfs_next_direction(self, start, target, obstacles, grid_size):
        if start == target:
            return None

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if self.strategy == "rotate":
            offset = random.randint(0, 3)
            directions = directions[offset:] + directions[:offset]
        elif self.strategy == "shuffle_once":
            random.shuffle(directions)

        queue = deque([start])
        first_dir = [[None] * grid_size for _ in range(grid_size)]

        while queue:
            cur = queue.popleft()
            if self.strategy == "per_node":
                random.shuffle(directions)
            for dr, dc in directions:
                nr, nc = cur[0] + dr, cur[1] + dc
                if (not(0 <= nr < grid_size and 0 <= nc < grid_size) or
                    first_dir[nr][nc] is not None or
                    (nr, nc) in obstacles):
                    continue
                first_dir[nr][nc] = first_dir[cur[0]][cur[1]] if cur != start else (dr, dc)
                if nr == target[0] and nc == target[1]:
                    return first_dir[nr][nc]
                queue.append((nr,nc))

        return None


class FloodFillController(BFSController):
    """BFS + Flood-fill Safety Check"""
    params = [
        {"key": "strategy", "label": "Tiebreaker", "type": "choice",
         "options": ["shuffle_once", "no_shuffle", "rotate", "per_node"]},

        {"key": "warn_rate", "label": "Safety", "type": "choice",
         "options": [0.2, 0.4, 0.6, 0.8, 1.0]},
    ]

    def __init__(self, strategy="shuffle_once", warn_rate=0.6):
        super().__init__(strategy)
        self.warn_rate = warn_rate
    def react(self, game_state, events):
        direction = super().react(game_state, events)
        if self._is_safe(game_state, direction):
            return direction

        # not safe: try other valid directions in random order
        valid = self.get_valid_dir(game_state)
        random.shuffle(valid)
        for alt_dir in valid:
            if alt_dir != direction and self._is_safe(game_state, alt_dir):
                return alt_dir

        return direction  # nothing safe, pray

    def _is_safe(self, game_state, direction):
        """Flood-fill to check if next state is safe"""
        snake = game_state.snake
        head, tail = snake.head, snake.tail
        food = game_state.food_pos
        grid_size = game_state.grid_size

        dr, dc = direction
        new_head = (head[0] + dr, head[1] + dc)

        if not (0 <= new_head[0] < grid_size and 0 <= new_head[1] < grid_size):
            return False

        will_eat = (new_head == food)

        # simulate new body after the move
        new_body = set(snake.body)
        new_body.add(new_head)
        if not will_eat:
            new_body.discard(tail)

        # new tail position after the move
        if will_eat or len(snake.body) < 2:
            new_tail = tail
        else:
            new_tail = snake.body[-2]

        # flood-fill from new_tail through empty cells
        visited = [[False] * grid_size for _ in range(grid_size)]
        q = deque([new_tail])
        visited[new_tail[0]][new_tail[1]] = True
        reachable = 0

        while q:
            r, c = q.popleft()
            reachable += 1
            if reachable >= len(new_body) * self.warn_rate:
                return True
            for dr, dc in ((0,1),(0,-1),(1,0),(-1,0)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < grid_size and 0 <= nc < grid_size
                    and not visited[nr][nc]
                    and (nr, nc) not in new_body):
                    visited[nr][nc] = True
                    q.append((nr, nc))

        return reachable >= len(new_body) * self.warn_rate


class AStarController(Controller):
    """A* pathfinding — uses Manhattan heuristic to find food faster than BFS."""

    def react(self, game_state, events):
        snake = game_state.snake
        head, tail, food_pos, grid_size = snake.head, snake.tail, game_state.food_pos, game_state.grid_size
        obstacles = set(snake.body)
        obstacles.discard(tail)

        # try to find path to food
        dir_to_food = self._astar_first_dir(head, food_pos, obstacles, grid_size)
        if dir_to_food is not None:
            return dir_to_food

        # if can't reach food, try tail
        dir_to_tail = self._astar_first_dir(head, tail, obstacles, grid_size)
        if dir_to_tail is not None:
            return dir_to_tail

        # if can't reach tail, go straightly towards tail
        return self.bold_react(game_state, tail)

    @staticmethod
    def _manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _astar_first_dir(self, start, target, obstacles, grid_size):
        if start == target:
            return None

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        g_score = [[float('inf')] * grid_size for _ in range(grid_size)]
        g_score[start[0]][start[1]] = 0
        first_dir = [[None] * grid_size for _ in range(grid_size)]
        
        heap = [(self._manhattan(start, target), 0, start[0], start[1])]
        while heap:
            f, tb, r, c = heapq.heappop(heap)   # tb for tie-breaker

            if r == target[0] and c == target[1]:
                return first_dir[r][c]

            ng = g_score[r][c] + 1
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < grid_size and 0 <= nc < grid_size) or (nr, nc) in obstacles:
                    continue

                if ng < g_score[nr][nc]:
                    g_score[nr][nc] = ng
                    nf = ng + self._manhattan((nr, nc), target)
                    ntb = (nr*grid_size + nc*target[0] - nf*target[1]) % 100
                    heapq.heappush(heap, (nf, ntb, nr, nc))

                    # track first direction from start
                    if r == start[0] and c == start[1]:
                        first_dir[nr][nc] = (dr, dc)
                    else:
                        first_dir[nr][nc] = first_dir[r][c]

        return None


class LookaheadController(Controller):
    """Simulates N moves ahead and picks the best path.
    depth: how many steps to look ahead (default 4)
    beam_width: if set, only keep top K paths per depth (default None = full tree)
    """
    params = [
        {"key": "depth", "label": "Depth", "type": "choice",
         "options": [2, 3, 4, 5, 6]},
        {"key": "beam_width", "label": "Beam", "type": "choice",
         "options": [None, 2, 3, 5]},
    ]

    def __init__(self, depth=4, beam_width=None):
        self.depth = depth
        self.beam_width = beam_width

    def react(self, game_state, events):
        snake = game_state.snake
        body_deque = deque(snake.body)
        thin_state = {
            "head": snake.head,
            "body": body_deque,
            "food": game_state.food_pos,
            "score": game_state.score,
            "alive": True,
            "grid_size": game_state.grid_size,
        }

        best_dir = None
        best_score = -float('inf')

        for direction in self.get_valid_dirs(thin_state):
            next_thin_state = self._simulate(thin_state, direction)
            score = self.lookahead(next_thin_state, self.depth - 1)
            if score > best_score:
                best_score = score
                best_dir = direction

        return best_dir or (0, 0)

    def lookahead(self, thin_state, depth):
        if depth == 0 or not thin_state["alive"]:
            return self._evaluate(thin_state)

        candidates = []
        for direction in self.get_valid_dirs(thin_state):
            next_state = self._simulate(thin_state, direction)
            score = self.lookahead(next_state, depth - 1)
            candidates.append((score, direction))

        if not candidates:
            return self._evaluate(thin_state)

        if self.beam_width is not None and depth > 1:
            candidates.sort(key=lambda x: -x[0])
            candidates = candidates[:self.beam_width]

        return max(s for s, _ in candidates)

    def get_valid_dirs(self, thin_state):
        ''' A customized get_valid_dirs() function for thin_state '''
        head = thin_state["head"]
        body_set = set(thin_state["body"])
        tail = thin_state["body"][-1]
        valid = []
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = head[0] + dr, head[1] + dc
            if not (0 <= nr < thin_state["grid_size"] and 0 <= nc < thin_state["grid_size"]):
                continue
            new_head = (nr, nc)
            ignore_tail = new_head != thin_state["food"]
            collision_body = body_set - {tail} if ignore_tail else body_set
            if new_head not in collision_body:
                valid.append((dr, dc))
        return valid
    

    def _simulate(self, thin_state, direction):
        dr, dc = direction
        head = thin_state["head"]
        new_head = (head[0] + dr, head[1] + dc)

        # collision check BEFORE moving — same order as real game
        will_eat = new_head == thin_state["food"]
        body_set = set(thin_state["body"])
        tail = thin_state["body"][-1]
        if will_eat:
            collides = new_head in body_set
        else:
            collides = new_head in (body_set - {tail})

        alive = (not collides and
                 0 <= new_head[0] < thin_state["grid_size"] and
                 0 <= new_head[1] < thin_state["grid_size"])

        # then simulate the move
        new_body = deque(thin_state["body"])
        new_body.appendleft(new_head)
        if not will_eat:
            new_body.pop()

        new_score = thin_state["score"]
        if will_eat and alive:
            new_score += 1

        # food is consumed — set to None, no distance penalty in evaluation
        new_food = None if (will_eat and alive) else thin_state["food"]

        return {
            "head": new_head,
            "body": new_body,
            "food": new_food,
            "score": new_score,
            "alive": alive,
            "grid_size": thin_state["grid_size"],
        }

    def _evaluate(self, thin_state):
        if not thin_state["alive"]:
            return -10000 + thin_state["score"]

        score = thin_state["score"] * 500

        if thin_state["food"] is not None:
            score -= (abs(thin_state["head"][0] - thin_state["food"][0]) +
                      abs(thin_state["head"][1] - thin_state["food"][1])) * 20

        valid_moves = len(self.get_valid_dirs(thin_state))
        score += valid_moves * 50

        return score


class WanderController(Controller):
    def __init__(self):
        self.last_visited = None
        self.step = 0

    def react(self, game_state, events):
        # lazy init on first call — uses actual grid size
        if self.last_visited is None:
            gs = game_state.grid_size
            self.last_visited = [[0] * gs for _ in range(gs)]

        # reset on new game
        if game_state.steps == 0 and self.step > 0:
            gs = game_state.grid_size
            self.last_visited = [[0] * gs for _ in range(gs)]
            self.step = 0

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
    
CONTROLLER_REGISTRY = [
    ("Human",   HumanController),
    ("Drunk",   DrunkController),
    ("Greedy",  GreedyController),
    ("BFS",     BFSController),
    ("AStar",   AStarController),
    ("Flood",   FloodFillController),
    ("Lookahead", LookaheadController),
    ("Wander",  WanderController),
]

def make_controller(config):
    """Create a controller from a config dict returned by run_menu()."""
    name = config["controller"]
    for display_name, cls in CONTROLLER_REGISTRY:
        if display_name == name:
            # Collect params that this controller accepts
            kwargs = {}
            if hasattr(cls, 'params') and cls.params:
                for p in cls.params:
                    key = p["key"]
                    if key in config:
                        kwargs[key] = config[key]
            return cls(**kwargs)
    return BFSController()