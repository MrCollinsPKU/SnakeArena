import pygame
import config
import random
from collections import deque

from abc import ABC, abstractmethod
class Controller():
    @abstractmethod
    def react(self, game_state, events):
        pass
    
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

    def react(self, game_state, events):
        final_dir = None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in config.KEY_TO_DIR:
                final_dir = config.KEY_TO_DIR[event.key]

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
        queue = deque([start])
        first_dir = {start: None} 
        # store the first direction chosen for every block reached 

        while queue:
            cur = queue.popleft()
            random.shuffle(directions)
            for dr, dc in directions:
                nr, nc = cur[0] + dr, cur[1] + dc
                nu = (nr, nc)
                if (not(0 <= nr < grid_size and 0 <= nc < grid_size) or
                    nu in first_dir or
                    nu in obstacles):
                    continue
                first_dir[nu] = first_dir[cur] if cur != start else (dr, dc)
                if nu == target:
                    return first_dir[nu]
                queue.append(nu)
        
        return None
