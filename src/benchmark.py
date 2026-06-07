import json
import csv
import sys
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Type, Union

from controller import BFSController, GreedyController, DrunkController, AStarController, FloodFillController, LookaheadController, WanderController
from runner import run_game

'''============================ CONFIGURATIONS ==============================='''
NUM_GAMES_PER_CONTROLLER = 100
GRID_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 30
MAX_STEPS = None                   # max steps for each game
SEED_OFFSET = 0                     # for game_i, seed = SEED_OFFSET + i
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
CONTROLLERS = [
    ("Drunk", lambda: DrunkController()),
    ("Greedy", lambda: GreedyController()),
    ("BFS", lambda: BFSController()),
    #("BFS-Rot", lambda: BFSController("rotate")),
    #("BFS-PerNode", lambda: BFSController("per_node")),
    #("BFS-NoShuf", lambda: BFSController("no_shuffle")),
    ("Flood", lambda: FloodFillController()), # default warn_rate = 0.6
    #("Flood-1", lambda: FloodFillController(warn_rate=1)),
    #("Flood-0.8", lambda: FloodFillController(warn_rate=0.8)),
    #("Flood-0.6", lambda: FloodFillController(warn_rate=0.6)),
    #("Flood-0.4", lambda: FloodFillController(warn_rate=0.4)),
    #("Flood-0.2", lambda: FloodFillController(warn_rate=0.2)),
    #("Lookahead", lambda: LookaheadController()),
    ("AStar", lambda: AStarController()),
    ("Wander", lambda: WanderController()),
]

'''============================ DATA STRUCTURES =============================='''
@dataclass
class GameRecord: # record for each game
    controller_name: str
    seed: int
    score: int
    steps: int
    avg_compute_time_ms: float
    max_steps_reached: bool

@dataclass
class ControllerStats: # record for each controller
    controller_name: str
    num_games: int
    avg_score: float
    max_score: int
    min_score: int
    avg_steps: float
    avg_compute_time_ms: float
    timeout_rate: float    # rate of reaching max steps


'''=============================== FUNCTIONS ================================'''
def run_controller(controller_factory, controller_name: str, num_games: int, max_steps: int, seed_offset: int = 0) -> List[GameRecord]:
    """
    Run games with a certain controller.
    output: List[GameRecord]
    """
    records = []
    game_number_width = len(str(num_games))

    for i in range(num_games):
        seed = i + seed_offset
        ctrl = controller_factory() # instantiate a new controller for each game

        game_result = run_game(ctrl, grid_size=GRID_SIZE, screen=None, seed=seed, max_steps=max_steps)

        score, steps, avg_compute_time_ms = game_result.score, game_result.steps, game_result.avg_compute_time_ms
        max_steps_reached = (steps >= max_steps) if max_steps is not None else False

        records.append(GameRecord(
            controller_name = controller_name,
            seed = seed,
            score = score,
            steps = steps,
            max_steps_reached = max_steps_reached,
            avg_compute_time_ms = avg_compute_time_ms
        ))
        
        print(
            f"{f'[{controller_name}]':<10}"
            f"#{i+1:0{game_number_width}d}   "
            f"score: {score:6.1f}   "
            f"steps: {steps:6d}   "
            f"avg_compute_time_ms: {avg_compute_time_ms:6.3f}   "
            f"max_steps_reached: {str(max_steps_reached):5}"
        )
    
    return records

def compute_stats(records: List[GameRecord]) -> ControllerStats:
    scores = [r.score for r in records]
    steps = [r.steps for r in records]
    avg_compute_time_ms_s = [r.avg_compute_time_ms for r in records]
    timeouts = sum(1 for r in records if r.max_steps_reached)
    n = len(records)

    return ControllerStats(
        controller_name=records[0].controller_name,
        num_games=n,
        avg_score=sum(scores)/n,
        max_score=max(scores),
        min_score=min(scores),
        avg_steps=sum(steps)/n,
        avg_compute_time_ms= sum(avg_compute_time_ms_s)/n,
        timeout_rate=timeouts/n
    )

def save_results(all_records: List[GameRecord], stats_list: List[ControllerStats], run_id: str):
    """
    Save data to JSON & CSV
    """

    RESULTS_DIR.mkdir(exist_ok=True)
    
    # 1. Save data to JSON
    json_path = RESULTS_DIR / f"benchmark_{run_id}.json"
    with open(json_path, "w") as f:
        json.dump({
            "records": [asdict(r) for r in all_records],
            "stats": [asdict(s) for s in stats_list],
            "config": {
                "grid_size": GRID_SIZE,
                "num_games_per_controller": NUM_GAMES_PER_CONTROLLER,
                "max_steps": MAX_STEPS,
                "seed_offset": SEED_OFFSET
            }
        }, f, indent=2)
    
    # 2. Save data to CSV
    csv_path = RESULTS_DIR / f"benchmark_{run_id}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["controller_name", "seed", "score", "steps", "avg_compute_time_ms", "max_steps_reached"])
        writer.writeheader()
        for r in all_records:
            writer.writerow(asdict(r))
    
    # 3. Print statistics
    print(f"\nBenchmark results saved to \"{json_path}\" and \"{csv_path}\"")
    print("\n=== Summary ===")
    for stat in stats_list:
        print(f"{stat.controller_name:10s} | avg_score: {stat.avg_score:6.1f} | max_score: {stat.max_score:3d} | avg_compute_time_ms: {stat.avg_compute_time_ms:6.3f}")


''' =============================== MAIN ================================= '''
def main():
    start_time = time.time()
    run_id = time.strftime("%Y%m%d_%H%M%S")
    
    all_records = []
    stats_list = []
    
    for name, ctrl_factory in CONTROLLERS:
        print(f"\nRunning {name}... ({NUM_GAMES_PER_CONTROLLER} games)")
        records = run_controller(ctrl_factory, name, NUM_GAMES_PER_CONTROLLER, MAX_STEPS, SEED_OFFSET)
        all_records.extend(records)
        stats = compute_stats(records)
        stats_list.append(stats)
    
    save_results(all_records, stats_list, run_id)
    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.1f} seconds")

if __name__ == "__main__":
    main()