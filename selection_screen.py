from dataclasses import dataclass
import sys
from typing import List
from typing import List
import sys
from rich.align import Align
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text 
import tty
from pydantic import BaseModel
import termios

VICTORIAN_ASCII = """
     ___________
    |  _______  |
    | |  [=]  | |
    | |  [=]  | |
    |_|_______|_|
   /             \\
  /_______________\\
 |  []    []    [] |
 |__________________|
"""

MODERN_ASCII = """
    |  |  ||  |
    |  |  ||  |
  __|  |__|└──┘
 |  |__|  |
 |________|
 |  []  []|
 |________|
  ‾‾‾‾‾‾‾‾
"""

INDUSTRIAL_ASCII = """
  ||  __  ||
  || |  | ||
  |_-|  |-_|
  |  |__|  |
  |________|
 _|________|_
|_____________|
   ~~canal~~
"""

FOREST_ASCII = """
   /\\   /\\  /\\
  /  \\ /  \\/  \\
 /    X    \\   \\
/____/ \\____\\___\\
  |  [=]  |
  |_______|
  watchtower
"""

class Biome(BaseModel):
    name: str
    description: str
    ascii_art: str
    locations: List[str]

BIOMES: List[Biome] = [
    Biome(
        name="Victorian England",
        description="1800s London. Fog. Gaslit alleys.\nEvery shadow hides a secret.",
        ascii_art=VICTORIAN_ASCII,
        locations=["Manor House", "Dark Alley", "Tavern", "Apothecary", "Church", "Dockyard"]
    ),
    Biome(
        name="Modern City",
        description="Glass towers. Rooftop parties.\nSurveillance everywhere — except where it matters.",
        ascii_art=MODERN_ASCII,
        locations=["Rooftop Party", "Office Building", "Nightclub", "Parking Garage", "Cafe", "Police Station"]
    ),
    Biome(
        name="Industrial Town",
        description="Factory smoke. Canal docks.\nThe workers saw everything. None will talk.",
        ascii_art=INDUSTRIAL_ASCII,
        locations=["Factory Floor", "Foreman Office", "Canal Docks", "Workers Pub", "Warehouse", "Town Square"]
    ),
    Biome(
        name="Forest Wilderness",
        description="Remote trails. Watchtowers.\nOut here, no one calls for help.",
        ascii_art=FOREST_ASCII,
        locations=["Watchtower", "Ranger Cabin", "Forest Clearing", "Old Mill", "Hunting Lodge", "Forest Trail"]
    ),
]

def render_menu(selected_idx: int):
    console = Console()
    boxes: List[Panel] = []

    for idx, biome in enumerate(BIOMES):
        is_selected = idx == selected_idx
        content :Text = Text()
        content.append(biome.ascii_art, style="dim white")
        content.append(biome.description, style="dim white" if not is_selected else "white")

        box = Panel(
            content,
            title=f"[bold red]{biome.name}[/]" if is_selected else f"[dim white]{biome.name}[/]",
            border_style="bold red" if is_selected else "dim white",
            padding=(1, 2)
        )
        boxes.append(box)

    bottom_text = Align.center(
        Text("NAVIGATE USING  ← / →   |   ENTER TO CONFIRM", style="dim white")
    )
    final = Group(Columns(boxes),bottom_text)
    console.print(Panel(final, border_style="white"))


def read_key() -> str:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\033':
            ch += sys.stdin.read(2)  # read [ and D/C
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def biome_selection() -> Biome:
    selected_idx = 0
    sys.stdout.write("\033[H\033[2J")
    sys.stdout.write("\033[?25l")

    while True:
        sys.stdout.write("\033[H")
        sys.stdout.flush()
        render_menu(selected_idx)

        key = read_key()
        if key == "\033[D":    # left arrow
            selected_idx = max(0, selected_idx - 1)
        elif key == "\033[C":  # right arrow
            selected_idx = min(len(BIOMES) - 1, selected_idx + 1)
        elif key in (" ", "\r", "\n"):  # space or enter
            return BIOMES[selected_idx]
        elif key == "\x03":    # ctrl+c to exit
            sys.stdout.write("\033[?25h")  # restore cursor
            sys.exit(0)

if __name__ == "__main__":
    biome_selection()
