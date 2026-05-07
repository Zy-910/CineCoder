from __future__ import annotations
import queue
from pathlib import Path


class NoActiveSessionError(Exception):
    pass


class LogWatcher:
    """平台无关的日志文件尾读器。"""

    def __init__(self, log_file: Path, event_queue: queue.Queue):
        self.log_file = log_file
        self.queue = event_queue
        self._position = 0

    def replay_history(self) -> None:
        """启动前先回放文件内已有的历史行。"""
        try:
            with open(self.log_file, encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.queue.put(line)
                self._position = f.tell()
        except OSError:
            pass

    def poll(self) -> None:
        """读取自上次位置以来的新行，放入队列。"""
        try:
            with open(self.log_file, encoding="utf-8", errors="replace") as f:
                f.seek(self._position)
                for line in f:
                    line = line.strip()
                    if line:
                        self.queue.put(line)
                self._position = f.tell()
        except OSError:
            pass
