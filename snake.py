from collections import deque
import config

class Snake:
    def __init__(self, start_head, start_dir, initial_len = config.INITIAL_LEN):
        """
        start_pos: tuple (row, col) initial head position.
        start_dir: tuple (dr, dc) initial movement direction.
        initial_length: number of segments the snake starts with.
        """
        body_list = [start_head]
        dr, dc = start_dir
        for i in range(initial_len-1):
            prev_block = (body_list[-1][0] - dr, body_list[-1][1] - dc)
            body_list.append(prev_block)

        self.body = deque(body_list)
        self.direction = start_dir
        self.alive = True
        self.score = 0

    @property
    def head(self):
        """Return current head position."""
        return self.body[0]

    @property
    def tail(self):
        """Return current tail position."""
        return self.body[-1]

    def move(self, new_head, ate_food=False):
        """
        Move the snake by inserting new_head at the front.
        If ate_food is False, remove the tail (normal move).
        If ate_food is True, keep the tail (snake grows).
        """
        self.body.appendleft(new_head)
        if not ate_food:
            self.body.pop()

    def get_body_set(self):
        """Return a set of all occupied cells for quick collision checks."""
        return set(self.body)

    def would_collide(self, new_head, ignore_tail=False):
        """
        Check if moving to new_head would cause a collision.
        - ignore_tail: if True, treat the current tail as empty (used when not eating food).
        """
        # Boundary check
        if config.GRID_SIZE is not None:
            if isinstance(config.GRID_SIZE, int):
                rows = cols = config.GRID_SIZE
            else:
                rows, cols = config.GRID_SIZE
            if not (0 <= new_head[0] < rows and 0 <= new_head[1] < cols):
                return True
        
        # Self collision
        body_set = self.get_body_set()
        if ignore_tail:
            body_set.discard(self.tail)
        return new_head in body_set