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

type NPCS = Dict[str,NPC]

USER_QUESTION_MAX_LEN = 130
MAX_ACCUSE = 3
ACCUSE_UNLOCK = 3
METER_INTERVAL = 25

def _multiple_of_25(x : int) -> int:
    if x % 25 != 0:
        raise ValueError("ESCAPE_METER NOT A MULTIPLE OF 25")
    return x

class Gamevariable(BaseModel):
    ESCAPE_METER: Annotated[int, Le(100), AfterValidator(_multiple_of_25)] = 0
    ACCUSE_READY: bool = False
    CONVERSATION_COUNT: Annotated[int, Le(9)] = 0 

associated_positions : Dict[Directions,Panel] = dict()

def associate_panels(npc_names_list : List[str]):
    '''Creates Panel AND Assign Their positions'''
    for idx, (name, dirs) in enumerate(zip(npc_names_list,Directions)):
        associated_positions[dirs] = Panel(Text(f"{name} ({Directions(idx).name})"),border_style="white",box=box.SQUARE,padding=(1,1))

## Layouts
npcn = [
    "Lord Ashton", "Margaret", "Barkeep Tom",
    "Sailor Pete", "Insp. Grey",
    "Dr. Whitmore", "Sister Anne", "Dock Foreman",
]

def render_npc_panels(console: Console, selected: int, is_selected : bool):
    for p in associated_positions.values():
        p.border_style = "dim white"
    associated_positions[Directions(selected)].border_style = "bold yellow"

    boxes = [p for _, p in associated_positions.items()]
    boxes.insert(4, Panel(Text("YOU", justify="center", style="bold white"),
                          border_style="white", box=box.SQUARE, padding=(1, 2)))
    border_style : str = "white"
    if is_selected:
        border_style = "red"
    console.print(Panel(
        Group(
            Columns(boxes[0:3], equal=True, expand=True),
            Columns(boxes[3:6], equal=True, expand=True),
            Columns(boxes[6:9], equal=True, expand=True),
        ),
        border_style=border_style, box=box.SQUARE, padding=(0, 1),width=80,height= 40
    ))

def render_chat_panel(console : Console, selected_character : str, is_selected : bool):
    border_style : str = "white"
    if is_selected:
        border_style = "red"
    console.print(Panel(Text(selected_character), border_style=border_style, box=box.SQUARE, padding=(0, 1),width=20,height= 40))


def render_game(console : Console, selected_npc : int, selected_character : str ,which_selected:FOCUSED_WINDOW): 
    if which_selected == FOCUSED_WINDOW.NPC_SELECTION_SCREEN:
        render_npc_panels(console, selected_npc,True)

    render_npc_panels(console, selected_npc,False)

    if which_selected == FOCUSED_WINDOW.CHAT_PANEL:
        render_chat_panel(console,selected_character,True)

    render_chat_panel(console,selected_character,False)

def game(npcs: NPCS | None):
    selected_npc = 0          
    selected_screen = FOCUSED_WINDOW.NPC_SELECTION_SCREEN
    console = Console()

    npc_panel : Panel

    associate_panels(npcn)

    sys.stdout.write("\033[H\033[2J")
    sys.stdout.write("\033[?25l")
    while True:
        sys.stdout.write("\033[H")
        sys.stdout.flush()

        render_game(console,selected_npc,'h',selected_screen)

        if selected_screen == FOCUSED_WINDOW.NPC_SELECTION_SCREEN:
            dir_selected = Prompt.ask("[red] Enter Direction [/red]:", choices=["N", "NW", "NE","S","SE","SW","E","W"], default="N",case_sensitive=False)
                        
            selected_npc = Directions[dir_selected].value
            selected_screen = FOCUSED_WINDOW.CHAT_PANEL


if __name__ == "__main__":
    game(None)
