# 🎬 CineCoder

English | [中文](README.zh-CN.md)

> Turn your Claude Code session into a movie poster guessing game.

CineCoder watches your [Claude Code](https://claude.ai/code) session in real time and progressively reveals a hidden movie poster as you code — every file read, write, and bash command unlocks more of the image. When you're done, guess the film.

---

## How It Works

1. Start a Claude Code session in one terminal
2. Run `cinecoder start` in another terminal
3. Code — each action unlocks a piece of the ASCII movie poster
4. Press `Ctrl+C` to end the session
5. If ≥ 80% of the poster is revealed, you get to guess the movie title

**Unlock weights**

| Action | Cells unlocked |
|--------|---------------|
| Bash command | 15 |
| Write / Edit file | 10 |
| Read / Grep / LS | 5 |
| User message | 8 |
| Error | 3 |

---

## Installation

```bash
git clone https://github.com/Zy-910/CineCoder
cd CineCoder
pip install .
```

Then simply run:

```bash
cinecoder start
```

---

## Usage

```bash
# Auto-detect the most recent Claude Code session
cinecoder start

# Specify a backend (default: claude-code)
cinecoder start --backend claude-code

# Check current session status
cinecoder status
```

---

## Supported Backends

| Backend | Tool | Status |
|---------|------|--------|
| `claude-code` | Claude Code CLI | ✅ Ready |
| `opencode` | OpenCode | 🔜 Planned |
| `codex` | OpenAI Codex CLI | 🔜 Planned |

Adding a new backend requires only two methods — see [`cinecoder/backends/base.py`](cinecoder/backends/base.py).

---

## Requirements

- Python ≥ 3.8
- [Claude Code CLI](https://claude.ai/code)

---

## License

MIT
