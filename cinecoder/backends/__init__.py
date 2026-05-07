from __future__ import annotations
from .base import Backend
from .claude_code import ClaudeCodeBackend

# 新平台：在这里注册，key 即 --backend 参数值
_REGISTRY: dict[str, type[Backend]] = {
    "claude-code": ClaudeCodeBackend,
    # "opencode":  OpenCodeBackend,
    # "codex":     CodexBackend,
}


def get_backend(name: str = "auto") -> Backend:
    if name == "auto":
        return ClaudeCodeBackend()
    if name not in _REGISTRY:
        available = ", ".join(_REGISTRY.keys())
        raise ValueError(f"未知后端: {name}，可用: {available}")
    return _REGISTRY[name]()


def list_backends() -> list[str]:
    return list(_REGISTRY.keys())
