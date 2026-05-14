import pygame

# Speed setting
LOGIC_FPS = 240
RENDER_FPS = 60

# Direction vectors (delta row, delta col)
DIR_UP    = (-1, 0)
DIR_DOWN  = (1,  0)
DIR_LEFT  = (0, -1)
DIR_RIGHT = (0,  1)

# Key mapping
KEY_TO_DIR = {
    pygame.K_UP:    DIR_UP,
    pygame.K_DOWN:  DIR_DOWN,
    pygame.K_LEFT:  DIR_LEFT,
    pygame.K_RIGHT: DIR_RIGHT
}
