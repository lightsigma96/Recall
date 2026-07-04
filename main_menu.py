from rich.console import Console
from rich.align import Align
from rich.panel import Panel
from rich.text import Text

console = Console()

RECALL_ART = """
▓▒░░▒▓█▓▒░░░░      ▄▄▒▓█▓▒▒▒▒▒▓█▓   ▄▄▒▓█▓▒▒▒▒▒▓█▓   ▄▄▒▓█▓▒▒▒▄▄    █▓▒▓▓            █▓▒▓▓           
███░▒▓██▓▒░▒▒▒░  ▄▓▓░▒▓██▓▒░▒▒▒▒▒ ▄██░▒▓██▓▒░▒▒▒▒▒  █░░▒▓█░░▒▓▓▓▓▄  ▓▓▓▓▒            ▓▓▓▓▒           
█▓▓▓░     ░▓▓▓▓░ █▒▒▒░▀    ░▓▓▓▓░ █▓▓▓░▀    ░▓▓▓▓░ █▒▒░░▀   ▀░▒▒▒▒▌ █▒▒▒░            █▒▒▒░           
▓▒▒▒░    ▐▓███▓▀ ▓░░░░▄▄▄  ▒████░ ▓▒▒▒░     ▒████░ ▓▓▓▒░     ▒░░░░░ ▓░░░░            ▓░░░░           
▒░░░▒▄▄▄▄███▓▀   ▒░░░▒░▒▓  ▀▀▀▀▀▀ ▒░░░▒     ▀▀▀▀▀▀ ▒██▓▒▄▄▄▄▄▓░░░░▒ ▒░░░▒            ▒░░░▒           
░░░░▒▒▓▓███▒▓▓▄  ░▒▒▒▓     ▄▄▄▄▄▄ ░░░░▓     ▄▄▄▄▄▄ ░▓▓█▓▓▓▓▒▒▒▒▒▒▒▓ ░▒▒▒▓     ▄▄▄▄▄▄ ░▒▒▒▓     ▄▄▄▄▄▄
░▒▒▒█    ▀█▒▓▓▓█ ░▓▓▓█     █▒▒▒▒█ ░▒▒▒░     █▒▒▒▒█ ░▒▒▓█     █▓▓▓▓█ ░▓▓▓█     █▒▒▒▒█ ░▓▓▓█     █▒▒▒▒█
▒▓▓▓▓     ▓░░▒▒▓ ▀▓▒▒▒█▄▄▄▄▓░░░░▓ ▀▓▓▓▓█▄▄▄▄▓░░░░▓ ▒░░░▓     ▓▒▒▒▒▓ ▀▓▒▒▒█▄▄▄▄▓░░░░▓ ▀▓▒▒▒█▄▄▄▄▓░░░░▓
▓▓▓▓▓     ▒░▒▒▒▓   ▀▀▓▓▓▒▒▒░░░░░▒   ▀▀▓▓▓▒▒▒░░░░░▒ ▓░░░▒     ▒░░░░▒   ▀▀▓▓▓▒▒▒░░░░░▒   ▀▀▓▓▓▒▒▒░░░░░▒"""

def render_title():
    t = Text(RECALL_ART)
    t.stylize("bold white", 0, len(RECALL_ART)//2)
    t.stylize("bold red", len(RECALL_ART)//3, len(RECALL_ART)//3 + len(RECALL_ART)//6)
    console.print(t)
    console.print("\n")
    console.print(
        "  A N   A I   M Y S T E R Y   G A M E",
        style="dim white"
    )

def render_description():

    console = Console()

    desc = Text()
    desc.append("\n  A crime has been committed.\n", style="bold white")
    desc.append("  The truth is buried in the memories of those who\n", style="bold white")
    desc.append("  were there — but no two remember it the same way.\n", style="bold white")
    desc.append("\n  Question the witnesses. Find the contradictions.\n", style="dim white")
    desc.append("  Every conversation leaves a trace.\n", style="dim white")
    desc.append("  Every lie has a shape.\n", style="dim white")
    desc.append("\n  The criminal is already planning their escape.\n", style="bold red")
    desc.append("  You are the only one who can stop them.\n", style="bold red")
    desc.append("\n  But be careful — the longer you take,\n", style="dim red")
    desc.append("  the further they run.\n", style="dim red")
    desc.append("\n")

    console.print(Panel(
        Align.left(desc),
        border_style="dim white",
        padding=(0, 1)
    ))
    console.print(
    Align.center(Text("[ PRESS ENTER TO BEGIN ]", style="white")),
    )


def render_main_menu():
    render_title()
    render_description()


if __name__ == "__main__":
    print("RUN game_loop.py")

