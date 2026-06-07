"""Run benchmark on every grid size from 12 to 60.
Usage: python run_all_sizes.py
Output: one JSON file per size in results/
"""

import subprocess
import sys

for size in range(12, 61):
    print(f"\n{'='*50}")
    print(f"  Grid size: {size}")
    print(f"{'='*50}")
    result = subprocess.run(
        [sys.executable, "benchmark.py", str(size)],
        capture_output=True, text=True,
        cwd="D:\\Resources\\Coding\\snake_arena\\src"
    )
    # print summary line only
    for line in result.stdout.splitlines():
        if "avg_score" in line or "Summary" in line or "seconds" in line or size == 12 or size == 60:
            print(line)
    if result.stderr:
        print(f"  ERROR: {result.stderr.strip()[-200:]}")