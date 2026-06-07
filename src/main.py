import pygame
import sys
from controller import (make_controller, CONTROLLER_REGISTRY,
                        HumanController, DrunkController, GreedyController,
                        BFSController, AStarController, FloodFillController,
                        LookaheadController, WanderController)
from ui import init_screen, draw_game_over, run_menu
from runner import run_game

def main():
    while True:
        ''' Run menu '''
        screen = init_screen()
        config = run_menu(screen, CONTROLLER_REGISTRY)
        ctrl = make_controller(config)

        while True:
            ''' Run game '''
            clock = pygame.time.Clock()
            game_result = run_game(ctrl, screen=screen, clock=clock,
                                grid_size=config["grid_size"],
                                logic_fps=config["logic_fps"])
            if game_result == "RESTART": # Game restarted
                continue
            elif game_result == "MENU":
                break

            ''' Game over '''
            draw_game_over(screen)
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                        
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        waiting = False
                        break
                clock.tick(12)

if __name__ == "__main__":
    main()