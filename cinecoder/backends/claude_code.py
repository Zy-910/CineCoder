from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional

from .base import Backend
from ..config import LOG_DIR
from ..parser import Event, parse_line
from ..watcher import NoActiveSessionError


def _log_dirs() -> list[Path]:
    """返回所有可能存放 Claude Code 日志的目录。"""
    dirs = [LOG_DIR]

    if sys.platform == "linux":
        # WSL：Claude Code 可能装在 Windows 侧，日志在 /mnt/c/Users/*/
        try:
            proc_version = Path("/proc/version").read_text().lower()
            if "microsoft" in proc_version:
                mnt = Path("/mnt/c/Users")
                if mnt.exists():
                    for user_dir in mnt.iterdir():
                        win_log = user_dir / ".claude" / "projects"
                        if win_log.exists():
                            dirs.append(win_log)
        except OSError:
            pass

    return dirs


class ClaudeCodeBackend(Backend):
    """适配 Claude Code CLI，支持 Linux / macOS / Windows / WSL。"""

    name = "claude-code"

    def find_log(self, session_id: str = "") -> Path:
        candidates: list[Path] = []
        for d in _log_dirs():
            candidates.extend(d.glob("**/*.jsonl"))

        if not candidates:
            raise NoActiveSessionError("未找到任何 Claude Code 日志，请先启动 claude")

        if session_id:
            matched = [f for f in candidates if session_id in f.name]
            if matched:
                return max(matched, key=lambda f: f.stat().st_mtime)

        return max(candidates, key=lambda f: f.stat().st_mtime)

    def parse_line(self, line: str) -> Optional[Event]:
        return parse_line(line)
