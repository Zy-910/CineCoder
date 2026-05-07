from __future__ import annotations
import hashlib
import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .config import TEMPLATES_DIR


@dataclass
class SessionState:
    session_id: str
    log_path: str

    status: str = "idle"        # idle | thinking | tool_use | ended
    seed: str = ""
    template_name: str = ""

    files_read: int = 0
    files_written: int = 0
    bash_commands: int = 0
    errors: int = 0
    turn_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    unlock_count: int = 0
    total_cells: int = 0

    start_time: float = field(default_factory=time.time)
    def __post_init__(self):
        if not self.seed:
            self.seed = _make_seed(self.session_id)

    @property
    def progress(self) -> float:
        return self.unlock_count / self.total_cells if self.total_cells else 0.0

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time



def _make_seed(session_id: str) -> str:
    raw = f"{session_id}cinecoder"
    return hashlib.sha256(raw.encode()).hexdigest()[:8]


def pick_template(seed: str) -> Optional[str]:
    """根据种子确定性地选一个有内容的模板。"""
    valid = []
    for path in sorted(TEMPLATES_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("cells"):
                valid.append(path.stem)
        except Exception:
            pass

    if not valid:
        return None

    rng = random.Random(int(seed, 16))
    return rng.choice(valid)
