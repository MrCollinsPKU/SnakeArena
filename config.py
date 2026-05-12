import pygame

# Window and grid size
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

GRID_SIZE = 30
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE

# Colors (R, G, B)
COLOR_BG = (30, 30, 30)         # dark gray
COLOR_SNAKE = (0, 255, 0)       # green
COLOR_FOOD = (255, 255, 0)      # yellow
COLOR_TEXT = (255, 255, 255)    # white

# Game settings
LOGIC_FPS = 180
RENDER_FPS = 60
INITIAL_LEN = 3

# direction vectors (delta row, delta col)
DIR_UP    = (-1, 0)
DIR_DOWN  = (1,  0)
DIR_LEFT  = (0, -1)
DIR_RIGHT = (0,  1)

# Key mapping for player control
KEY_TO_DIR = {
    pygame.K_UP:    DIR_UP,
    pygame.K_DOWN:  DIR_DOWN,
    pygame.K_LEFT:  DIR_LEFT,
    pygame.K_RIGHT: DIR_RIGHT
}
