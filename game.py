''' class Game: single-snake game logic '''
import random
from snake import Snake
import config
from dataclasses import dataclass

@dataclass
class GameState:
    snake: list[tuple[int, int]]
    food_pos: tuple[int, int] | None
    grid_size: int
    score: int
    game_over: bool

class Game:
    """Main game controller for classic snake."""

    def __init__(self):
        self.grid_size = config.GRID_SIZE
        self.snake = None
        self.food_pos = None
        self.game_over = False
        self.score = 0

    def reset_game(self):
        """
        Initialize or restart the game.
        """
        # Snake starts near the center, moving right
        start_row = self.grid_size // 2
        start_col = self.grid_size // 2
        self.snake = Snake((start_row, start_col), config.DIR_RIGHT)
        self.food_pos = self._random_food_position()
        self.game_over = False
        self.score = 0

    def _random_food_position(self):
        """
        Generate a random position not occupied by the snake.
        Returns None if the grid is completely filled (win condition).
        """
        snake_set = self.snake.get_body_set()
        if len(snake_set) >= self.grid_size * self.grid_size:
            self.game_over = True   # win by filling the grid
            return None
        while True:
            pos = (random.randint(0, self.grid_size-1),
                   random.randint(0, self.grid_size-1))
            if pos not in snake_set:
                return pos

    def update(self, direction):
        """
        Update game state for one frame.
        direction: tuple (dr, dc) the player's chosen movement.
        """

        if self.game_over:
            return

        # Calculate new head position
        dr, dc = direction
        new_head = (self.snake.head[0] + dr, self.snake.head[1] + dc)

        # Check if food will be eaten this step
        will_eat = (new_head == self.food_pos)

        # Collision detection (boundary or self)
        # For self collision, we can ignore the tail if we are not eating
        ignore_tail = not will_eat
        if self.snake.would_collide(new_head, ignore_tail):
            self.game_over = True
            return

        # Perform move
        self.snake.move(new_head, will_eat)

        # Handle food consumption
        if will_eat:
            self.score += 1
            self.food_pos = self._random_food_position()
            # If _random_food_position sets game_over due to full grid, we keep that flag

    def get_state(self):
        return GameState(self.snake, self.food_pos, self.grid_size, self.score, self.game_over)
    
    def get_snake_body(self):
        """Return snake's body list for drawing."""
        return self.snake.body

    def get_food_pos(self):
        """Return current food position."""
        return self.food_pos

    def get_score(self):
        return self.score