import pygame
import sys
from game import Game
from ui import render_game
import config
import random
import time
from dataclasses import dataclass

@dataclass
class GameResult:
    score: int
    steps: int
    avg_compute_time_ms: float  # ms

def run_game(ctrl, grid_size, screen=None, clock=None, seed=None, max_steps=100000):
    if seed is not None:
        random.seed(seed)
    
    game = Game(grid_size)
    game.reset_game()
    
    step_count, total_compute_time, render_mode = 0, 0.0, (screen is not None)
    if render_mode:
        render_count, render_term = 0, max(1, config.LOGIC_FPS//config.RENDER_FPS) 


    while not game.game_over and step_count < max_steps:
        
        events = pygame.event.get() if render_mode else []

        t_start = time.perf_counter()
        reaction_dir = ctrl.react(game.get_state(), events)
        t_end = time.perf_counter()
        total_compute_time += (t_end - t_start)

        game.update(reaction_dir)
        
        step_count += 1

        if render_mode:
            
            ''' Quit & restart detection '''
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game.reset_game()
            
            ''' Render '''
            if render_count % render_term == 0:
                render_game(screen, game, grid_size)

            render_count = (render_count + 1) % render_term
            clock.tick(config.LOGIC_FPS)
    
    return GameResult(
        score = game.get_score(),
        steps = step_count,
        avg_compute_time_ms = (total_compute_time / step_count * 1000) if step_count > 0 else 0.0,
    )