# 🎬 CineCoder

English | [中文](README.zh-CN.md)

> Turn your Claude Code session into a movie poster guessing game.

CineCoder watches your [Claude Code](https://claude.ai/code) session in real time and progressively reveals a hidden movie poster as you code — every file read, write, and bash command unlocks more of the image. When you're done, guess the film.

---

## How It Works

1. Start a Claude Code session (`claude`)
2. Split your terminal right and run `cinecoder start`
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

---

## Usage

The recommended setup is a split terminal — left for Claude Code, right for CineCoder:

```
┌─────────────────────┬─────────────────────┐
│  $ claude           │  $ cinecoder start  │
│                     │                     │
│  (coding here)      │  [poster unlocking] │
│                     │                     │
└─────────────────────┴─────────────────────┘
```

In **Ghostty**: open a session, split right (`Cmd+D`), run `cinecoder start` in the new pane. It auto-detects the Claude Code session on the left.

```bash
cinecoder start                            # auto-detect session
cinecoder start --template godfather       # force a specific poster
cinecoder start --backend claude-code      # specify backend
cinecoder status                           # check active session info
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
