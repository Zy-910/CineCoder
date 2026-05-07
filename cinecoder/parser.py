from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Event:
    type: str           # tool_read | tool_write | tool_command | error | message | thinking | turn_end
    detail: str = ""
    tokens_in: int = 0
    tokens_out: int = 0


def parse_line(line: str) -> Optional[Event]:
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None

    t = obj.get("type", "")

    if t == "assistant":
        return _parse_assistant(obj)

    if t == "user":
        return _parse_user(obj)

    if t == "system" and obj.get("subtype") == "turn_duration":
        return Event("turn_end")

    if "error" in obj:
        return Event("error", detail=str(obj["error"])[:80])

    return None


def _parse_assistant(obj: dict) -> Optional[Event]:
    msg = obj.get("message", {})
    content = msg.get("content", [])
    usage = msg.get("usage", {})
    tokens_in = usage.get("input_tokens", 0)
    tokens_out = usage.get("output_tokens", 0)

    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                return _parse_tool(c, tokens_in, tokens_out)

    if tokens_out > 0:
        return Event("thinking", tokens_in=tokens_in, tokens_out=tokens_out)

    return None


def _parse_user(obj: dict) -> Optional[Event]:
    msg = obj.get("message", {})
    content = msg.get("content", "")
    if isinstance(content, str) and content.strip() and not content.startswith("<"):
        return Event("message")
    return None


def _parse_tool(tool: dict, tokens_in: int, tokens_out: int) -> Event:
    name = tool.get("name", "")
    inp = tool.get("input", {})

    if name in ("Read", "Glob", "Grep", "LS"):
        return Event("tool_read", detail=name, tokens_in=tokens_in, tokens_out=tokens_out)

    if name in ("Write", "Edit", "MultiEdit"):
        return Event("tool_write", detail=inp.get("file_path", ""), tokens_in=tokens_in, tokens_out=tokens_out)

    if name == "Bash":
        return Event("tool_command", detail=inp.get("command", "")[:60], tokens_in=tokens_in, tokens_out=tokens_out)

    # 其他工具按读操作计
    return Event("tool_read", detail=name, tokens_in=tokens_in, tokens_out=tokens_out)
