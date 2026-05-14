import pygame
from pathlib import Path

# Window and grid size
WINDOW_WIDTH = 480
WINDOW_HEIGHT = WINDOW_WIDTH * 4 // 3
GAME_AREA_SIZE = WINDOW_WIDTH
INFO_BAR_HEIGHT = WINDOW_HEIGHT - GAME_AREA_SIZE

# Colors (R, G, B)
COLOR_BG = (30, 30, 30)
COLOR_INFO_BAR = (120, 120, 120)
COLOR_SNAKE = (150,90,250)
COLOR_FOOD = (175,239,2)
COLOR_TEXT = (255, 255, 255)

FONTS_PATH = Path(__file__).parent.parent / "assets" / "fonts"

def get_font(font_name, size):
    return pygame.font.Font(FONTS_PATH / (font_name + '.ttf'), size)
    
def init_screen():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("SnakeArena")
    return screen

def render_game(screen, game, grid_size):
    offset_x = 0
    offset_y = 0
    cell_size = WINDOW_WIDTH // grid_size

    screen.fill((0,0,0))
    pygame.draw.rect(screen, COLOR_BG, (offset_x, offset_y, GAME_AREA_SIZE, GAME_AREA_SIZE))

    draw_grid(screen, cell_size, offset_x, offset_y, GAME_AREA_SIZE)
    draw_snake(screen, game.get_snake_body(), cell_size, offset_x, offset_y)
    draw_food(screen, game.get_food_pos(), cell_size, offset_x, offset_y)
    draw_info_bar(screen, game, offset_x, offset_y + GAME_AREA_SIZE, WINDOW_WIDTH, INFO_BAR_HEIGHT)
    pygame.display.flip()

def draw_game_over(screen):
    """Draw game over message."""
    draw_text(screen = screen,
              text = "GAME OVER",
              font_name = "PressStart2P-Regular",
              x = WINDOW_WIDTH//2 - 130,
              y = WINDOW_HEIGHT//2 -40,
              size = 28,
              color = (255, 0, 0))
    draw_text(screen = screen, 
              text = "Press \"R\" to restart",
              font_name = "PressStart2P-Regular",
              x = WINDOW_WIDTH//2 - 80,
              y = WINDOW_HEIGHT//2 + 20,
              size = 12,
              color = (255, 0, 0))
    pygame.display.flip()

def draw_grid(screen, cell_size, offset_x, offset_y, full_size):
    """Draw grid lines on the screen."""
    for x in range(offset_x, offset_x + full_size, cell_size):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, WINDOW_HEIGHT))
    for y in range(offset_y, offset_y + full_size, cell_size):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WINDOW_WIDTH, y))

def draw_snake(screen, snake_body, cell_size, offset_x, offset_y):
    """Draw the snake using its body list."""
    for segment in snake_body:
        rect = pygame.Rect(offset_x + segment[1] * cell_size,
                           offset_y + segment[0] * cell_size,
                           cell_size, cell_size)
        pygame.draw.rect(screen, COLOR_SNAKE, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)   # border

def draw_food(screen, food_pos, cell_size, offset_x, offset_y):
    if food_pos is None:
        return
    rect = pygame.Rect(offset_x + food_pos[1] * cell_size,
                       offset_y + food_pos[0] * cell_size,
                       cell_size, cell_size)
    pygame.draw.rect(screen, COLOR_FOOD, rect)

def draw_info_bar(screen, game, bar_x, bar_y, bar_width, bar_height):
    pygame.draw.rect(screen, COLOR_INFO_BAR, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.line(screen, (255,255,255), (bar_x, bar_y), (bar_x + bar_width, bar_y), 2)
    
    game_state = game.get_state()

    lines = [
        f'SCORE: {game_state.score}',
        f'STEPS: {game_state.steps}',
        f'AI: BFS',
        f'Press \"R\"',
        f'to restart',
    ]
    font = get_font("PressStart2P-Regular", 24)

    y = bar_y + 10
    for line in lines:
        surf = font.render(line, True, COLOR_TEXT)
        screen.blit(surf, (bar_x + 10, y))
        y += 30

def draw_text(screen, text, font_name, x, y, size=24, color=COLOR_TEXT):
    """Draw text on screen."""
    font = get_font(font_name, size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))