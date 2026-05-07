from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..parser import Event


class Backend(ABC):
    """所有平台适配器的基类。新平台继承此类并实现两个方法即可接入。"""

    name: str = ""

    @abstractmethod
    def find_log(self, session_id: str = "") -> Path:
        """找到当前活跃的日志文件路径，找不到则抛出 NoActiveSessionError。"""
        ...

    @abstractmethod
    def parse_line(self, line: str) -> Optional[Event]:
        """把一行日志解析成 Event，无法识别则返回 None。"""
        ...
