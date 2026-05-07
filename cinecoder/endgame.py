from __future__ import annotations
import difflib
import sys
import time

from rich.console import Console

from .config import REVEAL_THRESHOLD
from .reveal import RevealEngine
from .state import SessionState

console = Console()

_RST = "\033[0m"

# (col, fall_delay, char) — delay staggers when each piece appears
_PARTICLES = [
    (2,  0, '~'),  (9,  2, '·'),  (16, 0, '-'),  (24, 3, '~'),
    (33, 1, '·'),  (41, 0, '~'),  (48, 2, '-'),   (55, 1, '·'),
    (60, 0, '~'),  (5,  4, '-'),  (12, 1, '~'),   (20, 2, '·'),
    (29, 0, '-'),  (37, 3, '~'),  (44, 0, '·'),   (51, 2, '-'),
    (57, 1, '~'),  (7,  3, '·'),  (27, 4, '-'),   (52, 0, '~'),
]

_H = 9       # canvas height
_CROW = 4    # row where "Congratulations!" sits
_CCOL = 5    # left padding


def _hue_rgb(hue: int) -> tuple:
    h = (hue % 360) / 60
    x = int(255 * (1 - abs(h % 2 - 1)))
    if h < 1: return (255, x, 0)
    if h < 2: return (x, 255, 0)
    if h < 3: return (0, 255, x)
    if h < 4: return (0, x, 255)
    if h < 5: return (x, 0, 255)
    return (255, 0, x)


def run_endgame(state: SessionState, engine: RevealEngine) -> None:
    _full_reveal(engine)

    if engine.progress < REVEAL_THRESHOLD:
        pct = int(engine.progress * 100)
        console.print(f"\n[dim]解锁进度 {pct}%，不足 80%，继续编码再来猜吧。[/dim]")
        _show_stats(state, engine)
        return

    _run_guess(state, engine)


def _full_reveal(engine: RevealEngine) -> None:
    engine.unlock_all()
    console.print("\n[bold yellow]🎬 Session 结束，海报完整揭晓...[/bold yellow]")
    time.sleep(0.8)


def _run_guess(state: SessionState, engine: RevealEngine) -> None:
    console.print("\n" + "─" * 52)
    console.print(f"[bold cyan]🎬 {engine.question}[/bold cyan]  （直接回车跳过）")

    try:
        answer = input(">>> ").strip()
    except (EOFError, KeyboardInterrupt):
        answer = ""

    if not answer:
        console.print(f"\n[dim]答案是：[bold]{engine.title}[/bold][/dim]")
    elif _is_correct(answer, engine):
        _celebrate(engine)
    else:
        console.print(f"\n[yellow]差一点！答案是：[bold]{engine.title}[/bold][/yellow]")
        if engine.quote:
            console.print(f'[dim italic]"{engine.quote}"[/dim italic]')

    if engine.insight:
        console.print(f"\n[cyan italic]{engine.insight}[/cyan italic]")

    _show_stats(state, engine)


def _is_correct(answer: str, engine: RevealEngine) -> bool:
    answer_l = answer.lower().strip()
    for candidate in [engine.title] + engine.aliases:
        if answer_l == candidate.lower().strip():
            return True
        ratio = difflib.SequenceMatcher(None, answer_l, candidate.lower()).ratio()
        if ratio >= 0.8:
            return True
    return False


def _celebrate(engine: RevealEngine) -> None:
    _confetti_fall()
    if engine.quote:
        console.print(f'\n[bold green]"[italic]{engine.quote}[/italic]"[/bold green]')


def _make_congrats(congrats: str, frame: int) -> str:
    return "".join(
        f"\033[1;38;2;{_hue_rgb(ci * 22 + frame * 18)[0]};{_hue_rgb(ci * 22 + frame * 18)[1]};{_hue_rgb(ci * 22 + frame * 18)[2]}m{ch}{_RST}"
        for ci, ch in enumerate(congrats)
    )


def _confetti_fall() -> None:
    congrats = "Congratulations!"

    sys.stdout.write("\033[?25l")  # hide cursor
    sys.stdout.write("\n" * _H)

    # Phase 1: particles fall
    for frame in range(_H + 5):
        congrats_colored = _make_congrats(congrats, frame)
        sys.stdout.write(f"\033[{_H}A")

        canvas = [[' '] * 64 for _ in range(_H)]
        for col, delay, ch in _PARTICLES:
            row = frame - delay
            if 0 <= row < _H and row != _CROW:
                canvas[row][col] = ch

        for row in range(_H):
            if row == _CROW:
                sys.stdout.write(f"\r\033[2K{' ' * _CCOL}{congrats_colored}\n")
            else:
                out = ""
                for ci, ch in enumerate(canvas[row]):
                    if ch != ' ':
                        r, g, b = _hue_rgb(ci * 17 + frame * 28)
                        out += f"\033[1;38;2;{r};{g};{b}m{ch}{_RST}"
                    else:
                        out += ' '
                sys.stdout.write(f"\r\033[2K{out}\n")

        sys.stdout.flush()
        time.sleep(0.12)

    # Phase 2: rainbow wave loops on congrats line only
    rows_below = _H - _CROW - 1
    deadline = time.time() + 4.0
    frame = _H + 5
    while time.time() < deadline:
        congrats_colored = _make_congrats(congrats, frame)
        sys.stdout.write(f"\033[{rows_below + 1}A")
        sys.stdout.write(f"\r\033[2K{' ' * _CCOL}{congrats_colored}\n")
        sys.stdout.write(f"\033[{rows_below}B")
        sys.stdout.flush()
        time.sleep(0.06)
        frame += 1

    sys.stdout.write("\033[?25h")  # restore cursor
    sys.stdout.flush()
    print()


def _show_stats(state: SessionState, engine: RevealEngine) -> None:
    m, s = divmod(int(state.elapsed), 60)
    console.print("\n[dim]─── 编码统计 " + "─" * 38 + "[/dim]")
    console.print(f"[dim]  海报：{engine.title}  │  解锁：{int(engine.progress*100)}%[/dim]")
    console.print(f"[dim]  时长：{m:02d}:{s:02d}  │  轮次：{state.turn_count}[/dim]")
    console.print(f"[dim]  读取：{state.files_read}  写入：{state.files_written}  命令：{state.bash_commands}  错误：{state.errors}[/dim]")
    console.print(f"[dim]  Tokens：{state.input_tokens} in / {state.output_tokens} out[/dim]")
