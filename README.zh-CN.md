# 🎬 CineCoder

[English](README.md) | 中文

> 把你的 Claude Code 会话变成电影海报猜谜游戏。

CineCoder 实时监听你的 [Claude Code](https://claude.ai/code) 会话，随着你的编码操作逐步揭开一张隐藏的电影海报——每次读写文件、执行命令都会解锁更多画面。结束时，猜猜这是哪部电影。

---

## 玩法

1. 启动 Claude Code 会话（`claude`）
2. 向右分屏，运行 `cinecoder start`
3. 正常写代码——每个操作解锁一块 ASCII 电影海报
4. 按 `Ctrl+C` 结束会话
5. 若已解锁 ≥ 80%，你将有机会猜电影名

**解锁权重**

| 操作 | 解锁格数 |
|------|----------|
| Bash 命令 | 15 |
| 写文件 / 编辑文件 | 10 |
| 读文件 / Grep / LS | 5 |
| 用户发送消息 | 8 |
| 发生错误 | 3 |

---

## 安装

```bash
git clone https://github.com/Zy-910/CineCoder
cd CineCoder
pip install .
```

---

## 使用

推荐使用分屏布局——左边跑 Claude Code，右边跑 CineCoder：

```
┌─────────────────────┬─────────────────────┐
│  $ claude           │  $ cinecoder start  │
│                     │                     │
│  （在这里写代码）    │  [海报逐渐解锁中]   │
│                     │                     │
└─────────────────────┴─────────────────────┘
```

在 **Ghostty** 中：启动会话后向右分屏（`Cmd+D`），在新 pane 里运行 `cinecoder start`，它会自动识别左侧的 Claude Code 会话。

```bash
cinecoder start                            # 自动检测会话
cinecoder start --template godfather       # 强制指定海报
cinecoder start --backend claude-code      # 指定后端
cinecoder status                           # 查看当前会话信息
```

---

## 支持的后端

| 后端 | 工具 | 状态 |
|------|------|------|
| `claude-code` | Claude Code CLI | ✅ 已支持 |
| `opencode` | OpenCode | 🔜 计划中 |
| `codex` | OpenAI Codex CLI | 🔜 计划中 |

新增后端只需实现两个方法，参考 [`cinecoder/backends/base.py`](cinecoder/backends/base.py)。

---

## 依赖

- Python ≥ 3.8
- [Claude Code CLI](https://claude.ai/code)

---

## 开源协议

MIT
