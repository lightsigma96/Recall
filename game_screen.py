import sys
from typing import Annotated, Dict, List
from enum import Enum
from annotated_types import Le
from rich.console import Console
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
    E = 3
    W = 4
    S = 5
    SE = 6
    SW = 7

class FOCUSED_WINDOW(Enum):
    NPC_SELECTION_SCREEN = 0
    CHAT_PANEL = 1

type NPCS = Dict[str, NPC]
type CHAT_HISTORY = Dict[str, str]

USER_QUESTION_MAX_LEN = 130
MAX_ACCUSE = 3
ACCUSE_UNLOCK = 3
METER_INTERVAL = 25

def _multiple_of_25(x: int) -> int:
    if x % 25 != 0:
        raise ValueError("ESCAPE_METER NOT A MULTIPLE OF 25")
    return x

class Gamevariable(BaseModel):
    ESCAPE_METER: Annotated[int, Le(100), AfterValidator(_multiple_of_25)] = 0
    ACCUSE_READY: bool = False
    CONVERSATION_COUNT: Annotated[int, Le(9)] = 0

associated_positions: Dict[Directions, Panel] = dict()

def associate_panels(npc_names_list: List[str]):
    """Creates Panel AND Assign Their positions"""
    for idx, (name, dirs) in enumerate(zip(npc_names_list, Directions)):
        associated_positions[dirs] = Panel(
            Text(f"{name} ({Directions(idx).name})"),
            border_style="white",
            box=box.SQUARE,
            padding=(1, 1),
        )

def assign_chat_histort(chat_history : CHAT_HISTORY,npc_names_list : List[str]):
    for  name in npc_names_list:
        chat_history[name] = f"{name}\n\n"

## Layouts
npcn = [
    "Lord Ashton",
    "Margaret",
    "Barkeep Tom",
    "Sailor Pete",
    "Insp. Grey",
    "Dr. Whitmore",
    "Sister Anne",
    "Dock Foreman",
]

def render_npc_panels(selected: int, is_selected: bool) -> Panel:
    for p in associated_positions.values():
        p.border_style = "dim white"
    associated_positions[Directions(selected)].border_style = "bold yellow"

    boxes = [p for _, p in associated_positions.items()]
    boxes.insert(
        4,
        Panel(
            Text("YOU", justify="center", style="bold white"),
            border_style="white",
            box=box.SQUARE,
            padding=(1, 2),
        ),
    )
    border_style: str = "white"
    if is_selected:
        border_style = "red"
    return Panel(
        Group(
            Columns(boxes[0:3], equal=True, expand=True),
            Columns(boxes[3:6], equal=True, expand=True),
            Columns(boxes[6:9], equal=True, expand=True),
        ),
        border_style=border_style,
        box=box.SQUARE,
        padding=(0, 1),
    )


def render_chat_panel(
    chat_history : CHAT_HISTORY,
    selected_npc_name : str,
    is_selected: bool,
) -> Panel:
    t = Text(chat_history[selected_npc_name], style="red")
    
    border_style = "bold red" if is_selected else "white"
    return Panel(t, border_style=border_style, box=box.SQUARE, padding=(1, 1))

def render_header(header : Panel):
    pass
## Main game loop

def game(npcs: NPCS | None):
    selected_npc = 0
    selected_screen = FOCUSED_WINDOW.NPC_SELECTION_SCREEN
    console = Console()
    layout = Layout()
    chat_history : CHAT_HISTORY = {}
    game_variable : Gamevariable = Gamevariable()

    associate_panels(npcn)
    assign_chat_histort(chat_history,npcn) ## Handle back-n-forth of npcs, for now only add user question

    layout.split_column(
        Layout(Panel(Text("HI")), name="header", size=5),  # fixed height in lines
        Layout(name="lower"),
    )

    layout["lower"].split_row(
                Layout(render_npc_panels(selected_npc, True), name="npcs"),
                Layout(render_chat_panel(chat_history,npcn[selected_npc], False), name="chat"),
    )

    CHAT_PANEL_SENTINAL = "CHAT"
    NPC_PANE_SENTINAL = "NPC"

    console.print(layout)
    while True:
        sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")
        sys.stdout.flush()

        if game_variable.CONVERSATION_COUNT % 3 == 0:
            game_variable.ACCUSE_READY = True
            # block and go to accuse screen (pop up screen), from there set accuse false and escape meter
        
        if selected_screen == FOCUSED_WINDOW.NPC_SELECTION_SCREEN:
            layout["npcs"].update(render_npc_panels(selected_npc, True))
            layout["chat"].update(render_chat_panel(chat_history,npcn[selected_npc], False))

            console.print(layout)

            dir_selected = Prompt.ask(
                f"[red] Enter Direction (Type {CHAT_PANEL_SENTINAL} (in caps) to start conversation with {npcn[selected_npc]} ) [/red]:",
                choices=["N", "NW", "NE", "S", "SE", "SW", "E", "W", f"{ CHAT_PANEL_SENTINAL }"],
                default="N",
                case_sensitive=False,
            )
            
            if dir_selected != CHAT_PANEL_SENTINAL:
                selected_npc = Directions[dir_selected].value

            if dir_selected == CHAT_PANEL_SENTINAL:
                selected_screen = FOCUSED_WINDOW.CHAT_PANEL

        elif selected_screen == FOCUSED_WINDOW.CHAT_PANEL:
            layout["npcs"].update(render_npc_panels(selected_npc, False))
            layout["chat"].update(render_chat_panel(chat_history,npcn[selected_npc], True))

            console.print(layout)

            prompt = Prompt.ask(
                f"[red] Chat (Type { NPC_PANE_SENTINAL } (in caps) to get back to npc selected_screen) [/red]:", default=" ", case_sensitive=False
            )
            chat_history[npcn[selected_npc]] += f"\nUSER: {prompt}\n"
            game_variable.CONVERSATION_COUNT += 1
            if prompt == NPC_PANE_SENTINAL:
                selected_screen = FOCUSED_WINDOW.NPC_SELECTION_SCREEN


if __name__ == "__main__":
    game(None)
