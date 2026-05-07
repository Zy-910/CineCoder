from __future__ import annotations
import json
import random
from pathlib import Path

from .config import TEMPLATES_DIR, UNLOCK_WEIGHTS


class RevealEngine:
    def __init__(self, template_name: str, seed: str):
        path = TEMPLATES_DIR / f"{template_name}.json"
        if not path.exists():
            raise FileNotFoundError(f"模板不存在: {path}")

        data = json.loads(path.read_text(encoding="utf-8"))
        self._meta = data
        self.cells: list[dict] = data["cells"]
        self.total = len(self.cells)

        # 用种子打乱解锁顺序，同一 session 顺序固定
        order = list(range(self.total))
        random.Random(int(seed, 16)).shuffle(order)
        self._order = order
        self._next = 0

        self.visible = [False] * self.total

    # ── 公开接口 ──────────────────────────────────────────

    def unlock(self, event_type: str) -> list[int]:
        """按事件类型解锁若干字符，返回新解锁的索引列表。"""
        count = UNLOCK_WEIGHTS.get(event_type, 1)
        end = min(self._next + count, self.total)
        newly = self._order[self._next:end]
        for idx in newly:
            self.visible[idx] = True
        self._next = end
        return newly

    def unlock_all(self) -> list[int]:
        """解锁全部剩余字符（session 结束时调用）。"""
        remaining = self._order[self._next:]
        for idx in remaining:
            self.visible[idx] = True
        self._next = self.total
        return remaining

    @property
    def progress(self) -> float:
        return self._next / self.total if self.total else 0.0

    # ── 模板元数据 ────────────────────────────────────────

    @property
    def title(self) -> str:
        return self._meta.get("title", "")

    @property
    def aliases(self) -> list[str]:
        return self._meta.get("aliases", [])

    @property
    def quote(self) -> str:
        return self._meta.get("quote", "")

    @property
    def width(self) -> int:
        return self._meta.get("width", 80)

    @property
    def height(self) -> int:
        return self._meta.get("height", 40)
