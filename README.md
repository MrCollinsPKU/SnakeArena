# SnakeArena

基于 PyGame 的贪吃蛇游戏，支持人类操控与多种 AI 控制器，并提供评估不同算法性能的批量测试脚本

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)![Pygame|90](https://img.shields.io/badge/Pygame-2.0%2B-green)

### 安装依赖

项目需要 2.0 版本以上的 PyGame 库

```bash

# 安装依赖：pygame>=2.0
pip install -r requirements.txt 

# 渲染模式
python src/main.py

# 测试脚本（测试内容需在源代码中自行配置）
python src/benchmark.py

```

---

### 基本功能

- 经典贪吃蛇核心玩法
- 内置多种模块化的控制器，接口清晰易加新：
	- `HumanController`：人类键盘操作
	- `DrunkController`：随机选择可行方向
	- `GreedyController`：选择最靠近食物的可行方向
	- `BFSController`：BFS 寻路策略
    - `AStarController`：A* 寻路策略
    - `FloodFillController`: 加入 Flood-fill 安全限制的 BFS 寻路策略
    - `LoodAheadController`: 失败的项目——贪吃蛇不适合 Look-ahead 算法
    - `WanderController`: 总是走向最早上一次访问的格子，在不同大小的场地下表现不稳定
- 提供展示游戏进程的【渲染模式】与可用于批量测试的【无头模式】
- 【测试脚本】导出 JSON / CSV 文件，可统计 AI 算法的平均分、每步计算耗时等数据

---

### 项目结构

```
snake_arena/

├── assets/
│   └── fonts/
│       └── *.ttf
├── docs/
│   ├── algo_explanation/       # 算法思路（AI生成）
│   │   └── *.md                
│   └── report/                 # 结果报告（AI生成）
│       └── *.md                
├── results/                    # 测试结果文件
│   ├── benchmark_*.csv         
│   └── benchmark_*.json
├── src/
│   ├── benchmark.py            # 【测试脚本】入口
│   ├── controller.py           # 控制器基类及多种具体控制器算法
│   ├── game.py                 # 游戏逻辑（蛇更新、食物更新、碰撞检测等）
│   ├── main.py                 # 【渲染模式】入口
│   ├── run_all_sizes.py        # 针对 WanderController 在不同场地大小下表现的特别测试脚本
│   ├── runner.py               # 单局游戏运行函数
│   ├── snake.py                # 蛇类（身体位置分布等）
│   └── ui.py                   # 绘图函数（网格、蛇、食物、文字等）
├── LICENSE
├── play.bat                    # 双击即开始的【渲染模式】入口
└── README.md
```

---

### 渲染模式
带有 GUI 的贪吃蛇游戏，可在初始菜单选择游戏参数

``` bash
python src/main.py
```

或者双击运行项目根目录中的 `play.bat`

可以选择 Human 控制器，自行游玩；也可以选择其他自动控制器，观察结果

### 测试脚本

对多种控制器进行批量无头测试，统计平均分、每步耗时等数据

``` bash
python src/benchmark.py
```

控制台输出示例：

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

同时脚本会将结果文件（*.json, *.csv）保存在 `SnakeArena/results` 目录下

结果文件包含每局详细记录（随机种子、分数、步数等），以及控制器汇总统计。

可通过编辑 `benchmark.py` 中的配置自定义测试脚本：

- `NUM_GAMES_PER_CONTROLLER`：每个控制器运行的局数
- `MAX_STEPS`：单局最大步数（中断死循环）
- `SEED_OFFSET`：随机种子平移
- `RESULTS_DIR`：结果文件目录
- `CONTROLLERS`：待测试控制器列表

---

### 模块化控制器的开发

所有控制器需继承 `controller.py` 中的 `Controller` 类并定义 `react(self, game_state, events)` 函数

通过 `self.params` 定义控制器实例化时需要的参数，便可以在【渲染模式】的初始菜单中选择参数并传参

```python
class MyController(Controller):
    params = [
    {"key": "para_1", "label": "Para_1", "type": "choice",
        "options": ["A", "B", "C", "D"]},
    ]
    def __init__(self, para_1):
        pass

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

### 开发日志

#### v1.0.1_2026-06-14
- 完善 `play.bat`, `LICENSE`, `requirements.txt`
- 修改 `ui.py` 的一些运行逻辑

#### v1.0.0_2026-06-07
- 加入初始菜单
- 统一调整视觉风格

#### v0.3.1_2026-06-05
- 加入 `WanderController`
    - 对其在不同场地大小下的表现进行测试，加入 `Wander_Benchmark.md`

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

---

### AI 工具声明

本项目利用接入 DeepseekAPI 的 Reasonix AI 代码工具完成了：
- Lookahead 等复杂算法的样例
- 蛇类数据结构的设计
- 测试脚本的撰写
- 代码的工程规范化
- 算法解释文档及结果报告的撰写