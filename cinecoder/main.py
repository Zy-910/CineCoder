from __future__ import annotations
import queue
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.live import Live

from .backends import get_backend, list_backends
from .backends.base import Backend
from .endgame import run_endgame
from .renderer import render_frame
from .reveal import RevealEngine
from .state import SessionState, pick_template
from .watcher import LogWatcher, NoActiveSessionError

console = Console()

_UNLOCK_TYPES = {"tool_read", "tool_write", "tool_command", "error", "message"}


@click.group()
def cli():
    """CineCoder — 把 Claude Code 会话变成电影海报猜谜。"""


@cli.command()
@click.option("--session", default="", help="指定 session ID 前缀")
@click.option("--template", default="", help="强制指定模板名（跳过随机选择）")
@click.option("--seed", default="", help="强制指定种子（可复现同一海报）")
@click.option("--backend", default="auto", help=f"日志后端: auto / {' / '.join(list_backends())}")
def start(session: str, template: str, seed: str, backend: str) -> None:
    """监听 coding session，实时渲染电影海报。"""
    try:
        b = get_backend(backend)
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)

    try:
        log_file = b.find_log(session)
    except NoActiveSessionError as e:
        console.print(f"[red]❌ {e}[/red]")
        console.print("[dim]请先在另一个终端启动 Claude Code：claude[/dim]")
        sys.exit(1)

    session_id = log_file.stem
    console.print(f"[green]✓[/green] Backend: [cyan]{b.name}[/cyan]  Session: [cyan]{session_id[:12]}…[/cyan]")

    state = SessionState(session_id=session_id, log_path=str(log_file))
    if seed:
        state.seed = seed

    tname = template or pick_template(state.seed)
    if not tname:
        console.print("[red]❌ 没有可用模板，请先生成至少一个模板。[/red]")
        sys.exit(1)

    try:
        engine = RevealEngine(tname, state.seed)
    except FileNotFoundError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)

    state.total_cells = engine.total
    state.template_name = tname

    console.print(
        f"[green]✓[/green] 海报已加载（[cyan]{engine.total}[/cyan] 格），开始编码解锁！"
        "  [dim]Ctrl+C 提前结束[/dim]\n"
    )

    _run_loop(state, engine, log_file, b)


@cli.command()
@click.option("--backend", default="auto", help=f"日志后端: auto / {' / '.join(list_backends())}")
def status(backend: str) -> None:
    """显示当前活跃的 coding session 信息。"""
    try:
        b = get_backend(backend)
        log_file = b.find_log()
        age = time.time() - log_file.stat().st_mtime
        console.print(f"[green]✓[/green] Backend: [cyan]{b.name}[/cyan]  Session: [cyan]{log_file.stem}[/cyan]")
        console.print(f"[dim]  日志：{log_file}[/dim]")
        console.print(f"[dim]  最后活跃：{age:.0f}s 前[/dim]")
    except (NoActiveSessionError, ValueError) as e:
        console.print(f"[yellow]{e}[/yellow]")


# ── 主循环 ───────────────────────────────────────────────


def _run_loop(state: SessionState, engine: RevealEngine, log_file: Path, backend: Backend) -> None:
    eq: queue.Queue = queue.Queue()
    watcher = LogWatcher(log_file, eq)
    watcher.replay_history()

    frame = 0
    try:
        with Live(render_frame(state, engine, frame), refresh_per_second=2, screen=True) as live:
            while True:
                watcher.poll()
                changed = _drain_queue(eq, state, engine, backend)

                if changed:
                    live.update(render_frame(state, engine, frame))

                frame += 1
                time.sleep(0.5)

    except KeyboardInterrupt:
        state.status = "ended"

    run_endgame(state, engine)


def _drain_queue(eq: queue.Queue, state: SessionState, engine: RevealEngine, backend: Backend) -> bool:
    changed = False
    while not eq.empty():
        try:
            line = eq.get_nowait()
        except queue.Empty:
            break

        event = backend.parse_line(line)
        if event is None:
            continue

        if event.type == "tool_read":
            state.files_read += 1
            state.status = "tool_use"
        elif event.type == "tool_write":
            state.files_written += 1
            state.status = "tool_use"
        elif event.type == "tool_command":
            state.bash_commands += 1
            state.status = "tool_use"
        elif event.type == "error":
            state.errors += 1
        elif event.type == "thinking":
            state.input_tokens += event.tokens_in
            state.output_tokens += event.tokens_out
            state.status = "thinking"
        elif event.type == "turn_end":
            state.turn_count += 1
            state.status = "idle"

        if event.type in _UNLOCK_TYPES:
            newly = engine.unlock(event.type)
            state.unlock_count = engine._next
            if newly:
                changed = True

    return changed
