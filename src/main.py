import pygame
import sys
from controller import HumanController, DrunkController, GreedyController, BFSController
from ui import init_screen, render_game, draw_game_over
from runner import run_game

def main():
    ctrl = BFSController()
    screen = init_screen()
    clock = pygame.time.Clock()

    while True:
        ''' Run game '''
        game_result = run_game(ctrl, grid_size=30, screen=screen, clock=clock)
        
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