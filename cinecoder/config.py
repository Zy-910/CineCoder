from __future__ import annotations
from pathlib import Path

LOG_DIR = Path.home() / ".claude" / "projects"
REVEAL_THRESHOLD = 0.80      # 解锁 80% 才触发猜谜

TEMPLATES_DIR = Path(__file__).parent / "templates"

UNLOCK_WEIGHTS: dict[str, int] = {
    "tool_read":    5,
    "tool_write":   10,
    "tool_command": 15,
    "error":        3,
    "message":      8,
}
