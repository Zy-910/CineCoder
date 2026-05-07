from __future__ import annotations
from rich.panel import Panel
from rich.text import Text

from .reveal import RevealEngine
from .state import SessionState


def render_frame(state: SessionState, engine: RevealEngine, frame: int = 0) -> Panel:
    canvas = _build_canvas(engine)
    status = _build_status(state, engine)

    body = Text(no_wrap=True)
    body.append_text(canvas)
    body.append("\n")
    body.append_text(status)

    return Panel(body, title="[bold magenta]CineCoder[/]", border_style="magenta", padding=0)


def _build_canvas(engine: RevealEngine) -> Text:
    w, h = engine.width, engine.height

    # 先建空白网格
    grid: list[list[tuple | None]] = [[None] * w for _ in range(h)]
    for idx, cell in enumerate(engine.cells):
        if engine.visible[idx]:
            x, y = cell["x"], cell["y"]
            if 0 <= y < h and 0 <= x < w:
                grid[y][x] = (cell["char"], tuple(cell["fg"]), tuple(cell["bg"]), cell.get("blink", False))

    text = Text(no_wrap=True)
    for y in range(h):
        for x in range(w):
            c = grid[y][x]
            if c:
                ch, fg, bg, bl = c
                style = f"rgb({fg[0]},{fg[1]},{fg[2]}) on rgb({bg[0]},{bg[1]},{bg[2]})"
                if bl:
                    style += " blink"
                text.append(ch, style=style)
            else:
                text.append(" ")
        if y < h - 1:
            text.append("\n")

    return text


def _build_status(state: SessionState, engine: RevealEngine) -> Text:
    pct = int(engine.progress * 100)
    filled = int(30 * engine.progress)
    bar = "█" * filled + "░" * (30 - filled)

    elapsed = int(state.elapsed)
    m, s = divmod(elapsed, 60)

    t = Text()
    t.append(f" {state.status.upper()} ", style="bold white on blue")
    t.append(f"  [{bar}] {pct}%  ", style="cyan")
    t.append(f"  {m:02d}:{s:02d}  ", style="dim")
    t.append(f"  📖{state.files_read}  ✏️{state.files_written}  🔧{state.bash_commands}", style="dim")
    if state.errors:
        t.append(f"  ⚠️{state.errors}", style="bold red")
    return t
