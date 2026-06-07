# SnakeArena

基于 PyGame 的贪吃蛇游戏，支持人类操控与多种 AI 控制器，并提供评估不同算法性能的批量测试脚本

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)![Pygame|90](https://img.shields.io/badge/Pygame-2.0%2B-green)

---

### 基本功能

- 经典贪吃蛇核心玩法
- 内置多种模块化的控制器，接口清晰易加新：
	- `HumanController`：人类键盘操作
	- `DrunkController`：随机选择可行方向
	- `GreedyController`：选择最靠近食物的可行方向
	- `BFSController`：BFS 寻路策略
- 提供展示游戏进程的【渲染模式】与可用于批量测试的【无头模式】
- 【测试脚本】导出 JSON / CSV 文件，可统计 AI 算法的平均分、每步计算耗时等数据

---

### 项目结构

```
snake_arena/
├── assets/
│   └── fonts/
│       └── T.ttf
├── results/                    # 测试结果文件
│   ├── benchmark_*.csv
│   └── benchmark_*.json
├── src/
│   ├── benchmark.py            # 【测试脚本】入口
│   ├── config.py               # 全局配置（窗口大小、帧率等）
│   ├── controller.py           # 控制器基类及多种具体控制器算法
│   ├── game.py                 # 游戏逻辑（蛇更新、食物更新、碰撞检测等）
│   ├── main.py                 # 【渲染模式】入口
│   ├── runner.py               # 单局游戏运行函数
│   ├── snake.py                # 蛇类（身体位置分布等）
│   └── ui.py                   # 绘图函数（网格、蛇、食物、文字等）
└── README.md
```

---

### 测试脚本

对多种控制器进行批量无头测试，统计平均分、每步耗时等数据

```
SnakeArena/src/benchmark.py
```

输出示例：

```text
Running DrunkController... (100 games)
[Drunk]   #001   score:    2.0   steps:   5010   avg_compute_time_ms:  0.002   max_steps_reached: False
[Drunk]   #002   score:    4.0   steps:   4653   avg_compute_time_ms:  0.002   max_steps_reached: False
...
[Drunk]   #100   score:    3.0   steps:   4551   avg_compute_time_ms:  0.003   max_steps_reached: False

Running GreedyController... (100 games)
[Greedy]  #001   score:   53.0   steps:   1162   avg_compute_time_ms:  0.005   max_steps_reached: False
[Greedy]  #002   score:   59.0   steps:   1415   avg_compute_time_ms:  0.005   max_steps_reached: False
...
[Greedy]  #100   score:   51.0   steps:   1108   avg_compute_time_ms:  0.004   max_steps_reached: False

Running BFSController... (100 games)
[BFS]     #001   score:  115.0   steps:   2548   avg_compute_time_ms:  0.251   max_steps_reached: False
[BFS]     #002   score:  103.0   steps:   2625   avg_compute_time_ms:  0.285   max_steps_reached: False
...
[BFS]     #100   score:  153.0   steps:   3712   avg_compute_time_ms:  0.319   max_steps_reached: False

Benchmark results saved to "results\benchmark_20260512_195202.json" and "results\benchmark_20260512_195202.csv"

=== Summary ===
Drunk      | avg_score:    3.7 | max_score:   7 | avg_compute_time_ms:  0.002
Greedy     | avg_score:   41.9 | max_score:  77 | avg_compute_time_ms:  0.004
BFS        | avg_score:  102.6 | max_score: 177 | avg_compute_time_ms:  0.299
```

结果文件包含每局详细记录（随机种子、分数、步数等），以及控制器汇总统计。

可通过编辑 `benchmark.py` 中的配置自定义测试脚本：

- `NUM_GAMES_PER_CONTROLLER`：每个控制器运行的局数
- `MAX_STEPS`：单局最大步数（中断死循环）
- `SEED_OFFSET`：随机种子平移
- `RESULTS_DIR`：结果文件目录
- `CONTROLLERS`：待测试控制器列表

---

### 模块化控制器的开发

所有控制器需继承 `controller.py` 中的 `Controller` 类并定义 `react(self, game_state, events)` 函数：

```python
class MyController(Controller):
    def react(self, game_state, events):
        # game_state 定义详见 game.py
        # events 为 Pygame 事件列表（无头模式下为空列表）
        # 返回移动方向 (dr, dc) \in \{(1,0), (-1,0), (0,1), (0,-1)\}
        return (0, 1)
```
完成后就即可选择自己的控制器操控贪吃蛇

`Controller` 类中也给出了若干辅助函数，如：
- `get_valid_dir(self, game_state)`：返回所有可行方向的列表
- `bold_react(self, game_state, target)`：从可行方向中返回最靠近 `target` 的方向

---

### 配置说明

在 `config.py` 中可以调整：

- `GRID_SIZE`：网格边长
- `LOGIC_FPS`：逻辑帧率
- `RENDER_FPS`：渲染帧率
- `INITIAL_LEN`：初始蛇长

> 无头模式下 `LOGIC_FPS` 不生效，游戏以最快速度运行。

---

### 开发日志

#### v1.0.0_2026-06-07
- 加入初始菜单
- 统一调整视觉风格

#### v0.3.1_2026-06-05
- 加入 `LookaheadController`, `WanderController`, `LookaheadController`
    - 对 `FloodFillController` 的 `warn_rate` 参数进行测试，加入 `FloodFill_Report.md`

#### v0.3.0_2026-06-04
- 更新 `BFSController`
    - 加入了 "shuffle_once", "per_node", "rotate", "no_shuffle" 四种 tie_breaker 策略参数
    - 对策略进行评估，加入 `BFS_Benchmark_Report.md`
- 加入 `AStarController`, `FloodFillController`, `LookaheadController`
    - 对 `FloodFillController` 的 `warn_rate` 参数进行测试，加入 `FloodFill_Report.md`


#### v0.2.1_2026-05-14
- 更新 UI，加入信息栏

#### v0.2.0_2026-05-12
- 优化数据结构，加入 `GameState`，`GameResult` 等数据结构类
- 优化逻辑架构，加入 `run_game` 函数实现游戏进程的封装
- 实现批量测试脚本 `benchmark.py`

#### v0.1.1_2026-04-23
- 加入 `BFSController`

#### v0.1.0_2026-04-22 
- 单人游戏基本逻辑架构
- 实现模块化 `Controller`，加入`HumanController`，`DrunkController`，`GreedyController`
- 实现基于 Pygame 的游戏渲染界面