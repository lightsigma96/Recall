from dataclasses import dataclass
import sys
from biomes import victorian_england,forest
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

class Biome(BaseModel):
    name: str
    description: str
    ascii_art: str
    locations: List[str]

BIOMES: List[Biome] = [
    Biome(
        name="victorian_england",
        description="1800s London. Fog. Gaslit alleys.\nEvery shadow hides a secret.",
        ascii_art=victorian_england["Dockyard"],
        locations=[
            "Manor House",
            "Dark Alley",
            "Tavern",
            "Apothecary",
            "Church",
            "Dockyard",
            "Theatre",
            "Train Station",
        ],
    ),
    Biome(
        name="forest",
        description="Remote trails. Watchtowers.\nOut here, no one calls for help.",
        ascii_art=forest["Watch_Tower"],
        locations=[
            "Ranger Cabin",
            "Watchtower",
            "Forest Clearing",
            "Old Mill",
            "Hunting Lodge",
            "Forest Trail",
            "Abandoned Mine",
            "Lake House",
        ],
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

    while True:
        print("\033[H\033[2J\033[3J", end="", flush=True)
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
