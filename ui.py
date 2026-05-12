import pygame
import config

def init_screen():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Classic Snake")
    return screen

def render_game(screen, game):
    screen.fill(config.COLOR_BG)
    draw_grid(screen)
    draw_snake(screen, game.get_snake_body())
    draw_food(screen, game.get_food_pos())
    draw_text(screen, f"SCORE: {game.get_score()}", 10, 10)
    pygame.display.flip()

def draw_game_over(screen):
    """Draw game over message."""
    draw_text(screen, "GAME OVER", config.WINDOW_WIDTH//2 - 130,
              config.WINDOW_HEIGHT//2 -40, 56, (255, 0, 0))
    draw_text(screen, "Press \"R\" to restart", config.WINDOW_WIDTH//2 - 80,
              config.WINDOW_HEIGHT//2 + 20, 24, (255, 0, 0))
    pygame.display.flip()

def draw_grid(screen):
    """Draw grid lines on the screen."""
    for x in range(0, config.WINDOW_WIDTH, config.CELL_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, config.WINDOW_HEIGHT))
    for y in range(0, config.WINDOW_HEIGHT, config.CELL_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (config.WINDOW_WIDTH, y))

def draw_snake(screen, snake_body):
    """Draw the snake using its body list."""
    for segment in snake_body:
        rect = pygame.Rect(segment[1] * config.CELL_SIZE,
                           segment[0] * config.CELL_SIZE,
                           config.CELL_SIZE, config.CELL_SIZE)
        pygame.draw.rect(screen, config.COLOR_SNAKE, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)   # border

def draw_food(screen, food_pos):
    """Draw the food if it exists."""
    if food_pos is None:
        return
    rect = pygame.Rect(food_pos[1] * config.CELL_SIZE,
                       food_pos[0] * config.CELL_SIZE,
                       config.CELL_SIZE, config.CELL_SIZE)
    pygame.draw.rect(screen, config.COLOR_FOOD, rect)

def draw_text(screen, text, x, y, size=24, color=config.COLOR_TEXT):
    """Draw text on screen."""
    font = pygame.font.SysFont("Arial", size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))