import sys
from memory_management import MemoryManager
import termios, tty
from typing import Annotated, Dict, List, Tuple
from enum import Enum
from biomes import victorian_england, forest
from selection_screen import Biome
from annotated_types import Le
from rich.align import Align
from rich.console import Console
from rich.padding import Padding
from rich.prompt import Prompt
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.console import Group
from rich import box
from npc import NPC
from pydantic import AfterValidator, BaseModel


class Directions(Enum):
    N = 0
    NE = 1
    NW = 2
    S = 3
    SE = 4
    SW = 5


class GameSignal(Enum):
    CONTINUE_GAME = 0
    END_GAME = 1


class GameResult(BaseModel):
    remark: str
    success: bool
    actual_killer: str


class FOCUSED_WINDOW(Enum):
    NPC_SELECTION_SCREEN = 0
    CHAT_PANEL = 1
    ACCUSE_WINDOW = 2


type NPCS = Dict[
    str, NPC
]  ## THIS DATA TYPE IS A REDUNDENCY, CHANGE IT LATER ELSE IT WILL BREAK THINGS
type CHAT_HISTORY = Dict[str, str]

USER_QUESTION_MAX_LEN = 130
METER_INTERVAL = 25


def _multiple_of_25(x: int) -> int:
    if x % 25 != 0:
        raise ValueError("ESCAPE_METER NOT A MULTIPLE OF 25")
    return x


class Gamevariable(BaseModel):
    ESCAPE_METER: Annotated[int, Le(100), AfterValidator(_multiple_of_25)] = 0
    CONVERSATION_COUNT: Annotated[int, Le(9)] = 0


## GLOBAL, MOVE LATER
associated_positions: Dict[Directions, Panel] = dict()


def associate_panels(npcs: NPCS, biome_selected: Biome):
    """Creates test NPC panels with ascii art"""

    biome_dict: Dict[str, str] = dict()
    if biome_selected.name == "victorian_england":
        biome_dict = victorian_england
    elif biome_selected.name == "forest":
        biome_dict = forest

    for npc_name, (k, v), dirs in zip(npcs.keys(), biome_dict.items(), Directions):
        associated_positions[dirs] = Panel(
            Align.center(
                Text(
                    f"{v.strip()}\n" f"{npc_name[:16]} ({dirs.name})",
                ),
            ),
            border_style="white",
            box=box.SQUARE,
            padding=(1, 1),
        )


def assign_chat_histort(chat_history: CHAT_HISTORY, npc_names_list: List[str]):
    for name in npc_names_list:
        chat_history[name] = f"{name}\n\n"


def render_npc_panels(selected: int, is_selected: bool) -> Panel:
    for idx, p in enumerate(associated_positions.values()):
        if idx == selected:
            p.border_style = "dim yellow"
        else:
            p.border_style = "dim white"

    boxes = list(associated_positions.values())

    you = Panel(
        Align.center("YOU"),
        border_style="white",
        box=box.SQUARE,
        height=3,
    )

    rows = Group(
        Columns(
            [
                boxes[2],  # NW
                boxes[0],  # N
                boxes[1],  # NE
            ],
            equal=True,
            expand=True,
        ),
        Align.center(
            you,
            vertical="middle",
        ),
        Columns(
            [
                boxes[5],  # SW
                boxes[4],  # SE
                boxes[3],  # S
            ],
            equal=True,
            expand=True,
        ),
    )

    return Panel(
        rows,
        border_style="red" if is_selected else "white",
        box=box.SQUARE,
        padding=(0, 1),
    )


def render_chat_panel(
    chat_history: CHAT_HISTORY,
    selected_npc_name: str,
    is_selected: bool,
) -> Panel:
    t = Text(chat_history[selected_npc_name], style="red")

    border_style = "bold red" if is_selected else "white"
    return Panel(t, border_style=border_style, box=box.SQUARE, padding=(1, 1))


def render_accuse_panel(npcn: List[str], selected_accuse: int) -> Panel:
    t = Text(justify="center")
    for idx, npc in enumerate(npcn):
        if selected_accuse == idx:
            t.append(f"{idx + 1}. {npc}\n", style="bold red")
        else:
            t.append(f"{idx + 1}. {npc}\n", style="white")
    return Panel(
        t,
        title="[bold white]Accuse[/]",
        subtitle="[bold white] Up/Down, Press ENTER to ACCUSE [/]",
        border_style="bold red",
        box=box.DOUBLE,
        width=40,
        padding=(1, 2),
    )


def escape_bar(pct: int, width: int = 20) -> Text:
    filled = int(width * pct / 100)
    t = Text()
    t.append("█" * filled, style="bold red")
    t.append("█" * (width - filled), style="dim white")
    t.append(
        f"  {pct}%",
        style="bold red" if pct >= 75 else "bold yellow" if pct >= 50 else "white",
    )
    return t


def render_header(pct: int ) -> Panel:
    t = Text()
    t.append("RECALL", style="bold white")
    t.append("  |  Escape: ", style="dim white")
    t.append_text(escape_bar(pct))
    return Panel(t, box=box.SQUARE, border_style="white", padding=(0, 1))


## Misc
## Move this to termios class
def read_key() -> str:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\033":
            ch += sys.stdin.read(2)  # read [ and D/C
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


## Main game loop


def end_game(game_variable: Gamevariable, accused_npc: str, killer: str) -> GameSignal:
    if accused_npc == killer:
        return GameSignal.END_GAME
    elif game_variable.ESCAPE_METER == 100:
        return GameSignal.END_GAME

    return GameSignal.CONTINUE_GAME


def generate_result(game_variable: Gamevariable, killer: str) -> GameResult:
    result: GameResult = GameResult(remark="", success=True, actual_killer=killer)

    if game_variable.ESCAPE_METER <= 50:
        result.remark = "Good Job"
    elif 50 <= game_variable.ESCAPE_METER < 100:
        result.remark = "Close Call"
    elif game_variable.ESCAPE_METER == 100:
        result.remark = "Criminal Escaped"
        result.success = False

    return result


async def game(mem_manager : MemoryManager,npcs: Tuple[str, NPCS] | None, biomes_selected: Biome) -> GameResult:
    selected_npc = 0
    selected_screen = FOCUSED_WINDOW.NPC_SELECTION_SCREEN
    console = Console()
    accuse_idx: int = 0
    main_game_layout = Layout()
    chat_history: CHAT_HISTORY = {}
    game_variable: Gamevariable = Gamevariable()

    if npcs:
        npcn: List[str] = [npc for npc in npcs[1].keys()]
    else:
        raise ValueError("NONE PASSED")

    associate_panels(npcs[1], biomes_selected)
    assign_chat_histort(
        chat_history, npcn
    )  ## Handle back-n-forth of npcs, for now only add user question

    main_game_layout.split_column(
        Layout(
            render_header(game_variable.ESCAPE_METER), name="header", size=5
        ),  # fixed height in lines
        Layout(name="lower"),
    )

    main_game_layout["lower"].split_row(
        Layout(render_npc_panels(selected_npc, True), name="npcs", ratio=3),
        Layout(render_chat_panel(chat_history, npcn[selected_npc], False), name="chat",ratio=2),
    )

    CHAT_PANEL_SENTINAL = "C"
    NPC_PANE_SENTINAL = "NPC"

    while True:
        print("\033[H\033[2J\033[3J", end="", flush=True)
        sys.stdout.flush()

        main_game_layout["header"].update(render_header(game_variable.ESCAPE_METER))
        if selected_screen != FOCUSED_WINDOW.ACCUSE_WINDOW:
            console.print(main_game_layout)

        if (
            game_variable.CONVERSATION_COUNT % 3 == 0
            and game_variable.CONVERSATION_COUNT > 0
        ):
            game_variable.CONVERSATION_COUNT = 0
            selected_screen = FOCUSED_WINDOW.ACCUSE_WINDOW
            continue

        if selected_screen == FOCUSED_WINDOW.NPC_SELECTION_SCREEN:

            dir_selected = Prompt.ask(
                f"[red] Enter Direction (Type {CHAT_PANEL_SENTINAL} (in caps) to start conversation with {npcn[selected_npc]} ) [/red]:",
                choices=[
                    "N",
                    "NW",
                    "NE",
                    "S",
                    "SE",
                    "SW",
                    CHAT_PANEL_SENTINAL,
                ],
                default="N",
                case_sensitive=False,
            )

            if dir_selected != CHAT_PANEL_SENTINAL:
                selected_npc = Directions[dir_selected].value
                main_game_layout["npcs"].update(render_npc_panels(selected_npc, True))
                main_game_layout["chat"].update(
                    render_chat_panel(chat_history, npcn[selected_npc], False)
                )
            elif dir_selected == CHAT_PANEL_SENTINAL:
                main_game_layout["npcs"].update(render_npc_panels(selected_npc, False))
                main_game_layout["chat"].update(
                    render_chat_panel(chat_history, npcn[selected_npc], True)
                )
                selected_screen = FOCUSED_WINDOW.CHAT_PANEL

        elif selected_screen == FOCUSED_WINDOW.CHAT_PANEL:

            prompt = Prompt.ask(
                f"[red] Chat (Type { NPC_PANE_SENTINAL } (in caps) to get back to npc selected_screen) [/red]:",
                default=" ",
                case_sensitive=False,
            )

            if prompt == NPC_PANE_SENTINAL:
                selected_screen = FOCUSED_WINDOW.NPC_SELECTION_SCREEN
                main_game_layout["npcs"].update(render_npc_panels(selected_npc, True))
                main_game_layout["chat"].update(
                    render_chat_panel(chat_history, npcn[selected_npc], False)
                )
            else:
                game_variable.CONVERSATION_COUNT += 1
                chat_history[npcn[selected_npc]] += f"\nUSER: {prompt}\n"
                main_game_layout["chat"].update(
                    render_chat_panel(chat_history, npcn[selected_npc], True)
                )
                console.print(main_game_layout)
                console.print(Text(f"{npcn[selected_npc]} is thinking...",style="bold red"))
                answer: str = await npcs[1][npcn[selected_npc]].generate_response(
                    prompt
                )
                await mem_manager.propagate_memories(prompt)
                chat_history[
                    npcn[selected_npc]
                ] += f"\n{npcn[selected_npc]}: {answer}\n"
                main_game_layout["chat"].update(
                    render_chat_panel(chat_history, npcn[selected_npc], True)
                )

        elif selected_screen == FOCUSED_WINDOW.ACCUSE_WINDOW:

            console.print(
                Align.center(
                    render_accuse_panel(npcn, accuse_idx),
                    vertical="middle",
                ),
                height=console.height,
            )

            key = read_key()
            if key == "\033[B":  # down
                accuse_idx = min(accuse_idx + 1, len(npcn) - 1)
            elif key == "\033[A":  # up
                accuse_idx = max(0, accuse_idx - 1)
            elif key in (" ", "\r", "\n"):  # confirm
                selected_screen = FOCUSED_WINDOW.NPC_SELECTION_SCREEN
                game_variable.ESCAPE_METER += 25
                signal: GameSignal = end_game(game_variable, npcn[accuse_idx], npcs[0])

                if signal == GameSignal.END_GAME:
                    console.print(Text("GAME END", style="bold red"))
                    break
                elif signal == GameSignal.CONTINUE_GAME:
                    accuse_idx = 0
                    main_game_layout["npcs"].update(
                        render_npc_panels(selected_npc, True)
                    )
                    main_game_layout["chat"].update(
                        render_chat_panel(chat_history, npcn[selected_npc], False)
                    )

            elif key == "\x03":  # ctrl+c
                sys.stdout.write("\033[?25h")
                sys.exit(0)

    result: GameResult = generate_result(game_variable, npcs[0])
    return result

if __name__ == "__main__":
    print("RUN game_loop.py")
