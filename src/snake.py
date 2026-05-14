from collections import deque
INITIAL_LEN = 3

class Snake:
    def __init__(self, start_head, start_dir, grid_size, initial_len=3):
        '''
        start_head: initial head position
        start_dir: initial movement direction
        initial_length: number of blocks the snake starts with
        '''

        body_list = [start_head]
        dr, dc = start_dir
        for i in range(initial_len-1):
            prev_block = (body_list[-1][0] - dr, body_list[-1][1] - dc)
            body_list.append(prev_block)

        self.body = deque(body_list)
        self.direction = start_dir
        self.alive = True
        self.score = 0
        self.grid_size = grid_size

    @property
    def head(self):
        ''' Return current head position '''
        return self.body[0]

    @property
    def tail(self):
        ''' Return current tail position '''
        return self.body[-1]

    def move(self, new_head, will_eat=False):
        '''
        Move the snake by adding new_head to the front
        If will_eat, keep the tail (snake grows)
        '''
        self.body.appendleft(new_head)
        if not will_eat:
            self.body.pop()

    def get_body_set(self):
        ''' Return a set of body block positions '''
        return set(self.body)

    def would_collide(self, new_head, ignore_tail=False):
        # ignore_tail: treat the current tail as empty (when not eating food)
        
        # Boundary check
        if not (0 <= new_head[0] < self.grid_size and 0 <= new_head[1] < self.grid_size):
            return True
        
        # Self collision
        body_set = self.get_body_set()
        if ignore_tail:
            body_set.discard(self.tail)
        return new_head in body_set