### SnakeArena

### 基本架构
- `main.py`：带图形界面的主函数，串联游戏元素与流程
- `ui.py`：界面图形文件
- `config`：基本参数文件
- `Snake` 类：用于蛇的生成、移动与碰撞判定，储存当前位置和蛇身构成（使用双端队列）
- `Game` 类：单人游戏的场景，负责生成蛇与食物、接收 `Controller` 每一帧的操作并在场景上演算
- `Controller` 类：含 `HumanController`、`DrunkController`、`GreedyController` 等，提供用户操作的接口与各种 AI 算法的封装

### 日志

#### 2026-04-22 SnakeArena_v0.1

完成单人游戏的基本架构，并加入三种 `Controller`
- `HumanController`：接收用户的上下左右键操作；不允许转向当前方向的相反方向
- `DrunkController`：随机选取不会在下一步死亡的操作（可行操作）；都会死亡则认命
- `GreedyController`：总是尽可能朝向食物行动（在可行操作中选取与食物方向向量点积最大的操作）

#### 2026-05-12 SnakeArena_v0.2

