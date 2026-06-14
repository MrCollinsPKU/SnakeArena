import sys
import pygame
from pathlib import Path

# Window and grid size
WINDOW_WIDTH = 480
WINDOW_HEIGHT = WINDOW_WIDTH * 4 // 3
GAME_AREA_SIZE = WINDOW_WIDTH
INFO_BAR_HEIGHT = WINDOW_HEIGHT - GAME_AREA_SIZE

# Colors (R, G, B)

# Purple & Gold
COLOR_THEME_A       = (200, 180, 255)
COLOR_THEME_B       = (255, 200, 100)
COLOR_BG            = (20, 20, 30)

# Synthwave
#COLOR_THEME_A = (255, 50, 150)
#COLOR_THEME_B = (0, 230, 255)
#COLOR_BG = (20, 10, 30)

# Retro Console — aged yellowed plastic
#COLOR_THEME_A = (180, 175, 120)
#COLOR_THEME_B = (200, 190, 100)
#COLOR_BG = (195, 192, 185)

# Retro Terminal
#COLOR_THEME_A = (0, 255, 65)
#COLOR_THEME_B = (255, 255, 85)
#COLOR_BG = (10, 10, 10)

# Firewatch
#COLOR_THEME_A = (255, 140, 50)
#COLOR_THEME_B = (255, 210, 80)
#COLOR_BG = (30, 20, 15)

# Ocean
#COLOR_THEME_A = (80, 200, 220)
#COLOR_THEME_B = (255, 220, 80)
#COLOR_BG = (10, 20, 35)

# Monochrome
#COLOR_THEME_A = (200, 200, 200)
#COLOR_THEME_B = (255, 255, 255)
#COLOR_BG = (15, 15, 15)

COLOR_TITLE         = COLOR_THEME_A
COLOR_TEXT          = (200, 200, 200)

COLOR_INFO_BAR      = COLOR_BG
COLOR_SNAKE         = COLOR_THEME_A
COLOR_SNAKE_BORDER  = (0, 0, 0)
COLOR_FOOD          = COLOR_THEME_B
COLOR_GRID          = (50, 50, 50)
COLOR_GAME_OVER     = (255, 0, 0)

COLOR_MENU_BG       = COLOR_BG
COLOR_MENU_TITLE    = COLOR_TITLE

COLOR_SELECTED      = COLOR_THEME_B
COLOR_UNSELECTED    = (200, 200, 200)

COLOR_VALUE         = (255, 255, 255)
COLOR_INSTRUCTION   = (120, 120, 120)


FONTS_PATH = Path(__file__).parent.parent / "assets" / "fonts"
def get_font(font_name, size):
    return pygame.font.Font(FONTS_PATH / (font_name + '.ttf'), size)


GAME_OVER_FONT = "Jacquard12-Regular"


def init_screen():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("SnakeArena")
    return screen

def render_game(screen, game, grid_size, ctrl_name=""):
    offset_x = 0
    offset_y = 0
    cell_size = WINDOW_WIDTH // grid_size

    screen.fill(COLOR_SNAKE_BORDER)
    pygame.draw.rect(screen, COLOR_BG, (offset_x, offset_y, GAME_AREA_SIZE, GAME_AREA_SIZE))

    draw_grid(screen, cell_size, offset_x, offset_y, GAME_AREA_SIZE)
    draw_snake(screen, game.get_snake_body(), cell_size, offset_x, offset_y)
    draw_food(screen, game.get_food_pos(), cell_size, offset_x, offset_y)
    draw_info_bar(screen, game, offset_x, offset_y + GAME_AREA_SIZE, WINDOW_WIDTH, INFO_BAR_HEIGHT, ctrl_name)
    pygame.display.flip()

def draw_game_over(screen):
    """Draw game over message."""
    draw_text(screen, "GAME OVER", GAME_OVER_FONT,
              WINDOW_WIDTH//2 - 130, WINDOW_HEIGHT//2 - 40, 48, COLOR_GAME_OVER)
    draw_text(screen, 'Press "R" to restart', GAME_OVER_FONT,
              WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT//2 + 20, 24, COLOR_GAME_OVER)
    pygame.display.flip()

def draw_grid(screen, cell_size, offset_x, offset_y, full_size):
    """Draw grid lines on the screen."""
    for x in range(offset_x, offset_x + full_size, cell_size):
        pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(offset_y, offset_y + full_size, cell_size):
        pygame.draw.line(screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

def draw_snake(screen, snake_body, cell_size, offset_x, offset_y):
    """Draw the snake using its body list."""
    for segment in snake_body:
        rect = pygame.Rect(offset_x + segment[1] * cell_size,
                           offset_y + segment[0] * cell_size,
                           cell_size, cell_size)
        pygame.draw.rect(screen, COLOR_SNAKE, rect)
        pygame.draw.rect(screen, COLOR_SNAKE_BORDER, rect, 1)

def draw_food(screen, food_pos, cell_size, offset_x, offset_y):
    if food_pos is None:
        return
    rect = pygame.Rect(offset_x + food_pos[1] * cell_size,
                       offset_y + food_pos[0] * cell_size,
                       cell_size, cell_size)
    pygame.draw.rect(screen, COLOR_FOOD, rect)

def draw_info_bar(screen, game, bar_x, bar_y, bar_width, bar_height, ctrl_name=""):
    pygame.draw.rect(screen, COLOR_INFO_BAR, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.line(screen, COLOR_TEXT, (bar_x, bar_y), (bar_x + bar_width, bar_y), 2)
    
    game_state = game.get_state()

    font = get_font("PressStart2P-Regular", 14)

    # game state
    for i, line in enumerate([f'Score: {game_state.score}',
                              f'Steps: {game_state.steps}',
                              f'AI: {ctrl_name}']):
        surf = font.render(line, True, COLOR_TEXT)
        screen.blit(surf, ((bar_x + 20,
                            bar_y + 20 + 25 * i)))
    
    # instruction
    for i, text in enumerate(reversed(["[R] Restart game",
                                       "[M] Restart from menu"])):
            instruction = font.render(text, True, COLOR_INSTRUCTION)
            screen.blit(instruction, (bar_x + 20,
                                      WINDOW_HEIGHT - 10 - 25 * (i+1)))
    

def draw_text(screen, text, font_name, x, y, size=24, color=COLOR_TEXT):
    """Draw text on screen."""
    font = get_font(font_name, size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def run_menu(screen, controller_registry):
    """Show a configuration menu and return a config dict.

    controller_registry: list of (display_name, controller_class)
    
    Returns: {"controller_name": str, "grid_size": int, ...params}
    """

    clock = pygame.time.Clock()

    ctrl_names = [name for name, _ in controller_registry]
    fields = [
        {"key": "controller", "label": "Controller",
         "type": "controller", "options": ctrl_names,
         "value": ctrl_names[0]},

        {"key": "grid_size", "label": "Grid Size",
         "type": "choice", "options": [15, 20, 24, 30, 36, 42, 60, 100],
         "value": 30},

         {"key": "logic_fps", "label": "Logic FPS",
         "type": "choice", "options": [4, 10, 30, 60, 120, 360, 540, 1080],
         "value": 60},
    ]

    selected = 0
    prev_controller = None
    param_fields = []

    while True:
        controller_key = fields[0]["value"]

        if controller_key != prev_controller:
            if controller_key == "Human":
                fields[2]["value"] = 4
            elif controller_key == "Wander":
                fields[2]["value"] = 540
            else:
                fields[2]["value"] = 60
            
            prev_controller = controller_key
            ctrl_class = next((cls for name, cls in controller_registry if name == controller_key), None)

            param_fields = []
            if hasattr(ctrl_class, 'params') and ctrl_class.params:
                for p in ctrl_class.params:
                    param_fields.append({
                        "key": p["key"],
                        "label": f' {p["label"]}',
                        "type": "choice",
                        "options": p["options"],
                        "value": p["options"][0],
                    })

        display_fields = fields[0:1] + param_fields + fields[1:]
        # clamp selected index
        if selected >= len(display_fields):
            selected = len(display_fields) - 1

        # --- Draw ---
        screen.fill(COLOR_MENU_BG)
        
        title_font = get_font("PressStart2P-Regular", 36)
        
        title_surf = title_font.render("SNAKE ARENA", True, COLOR_MENU_TITLE)
        screen.blit(title_surf, ((WINDOW_WIDTH - title_surf.get_width()) // 2, 50))

        title_snake = title_font.render("_--_--_->", True, COLOR_MENU_TITLE)
        screen.blit(title_snake, ((WINDOW_WIDTH - title_snake.get_width()) // 2, 100))


        text_font = get_font("PressStart2P-Regular", 14)

        # Start fields about a third down the tall window
        for i, field in enumerate(display_fields):
            color = COLOR_SELECTED if i == selected else COLOR_UNSELECTED

            cursor = text_font.render(f"{"> " if i == selected else "  "}", True, color)
            screen.blit(cursor, (30, 200 + 45 * i))

            label = text_font.render(f"{field['label']}", True, color)
            screen.blit(label, (60, 200 + 45 * i))

            value_str = str(field["value"])
            val_surf = text_font.render(value_str, True, COLOR_VALUE)
            val_x = WINDOW_WIDTH - val_surf.get_width() - 60
            screen.blit(val_surf, (val_x, 200 + 45 * i))

        # Instructions at the bottom
        for i, text in enumerate(reversed(["[UP/DOWN]: Navigate",
                                           "[LEFT/RIGHT]: Change",
                                           "[SPACE]: Start  [Q]: Quit"])):
            instruction = text_font.render(text, True, COLOR_INSTRUCTION)
            screen.blit(instruction, ((WINDOW_WIDTH - instruction.get_width()) // 2,
                                       WINDOW_HEIGHT - 40 - 30 * (i+1)))
        
        # Footage
        footage_font = get_font("PressStart2P-Regular", 12)
        footage = footage_font.render("SnakeArena v1.0.0 @MrCollinsPKU", True, COLOR_TEXT)
        screen.blit(footage, ((WINDOW_WIDTH - footage.get_width()) // 2,
                                       WINDOW_HEIGHT - 30))

        pygame.display.flip()

        # --- Input ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(display_fields)

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(display_fields)

                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    field = display_fields[selected]
                    opts = field["options"]
                    idx = opts.index(field["value"])
                    delta = -1 if event.key == pygame.K_LEFT else 1
                    field["value"] = opts[(idx + delta) % len(opts)]

                if event.key == pygame.K_SPACE:
                    config = {f["key"]: f["value"] for f in display_fields}
                    return config

        clock.tick(30)