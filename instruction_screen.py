from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def render_instruction_screen(story: str):
    console = Console()

    content = Text()

    content.append("CASE STORY\n", style="bold red")
    content.append(f"{story}\n\n", style="italic white")

    content.append("INVESTIGATION\n", style="bold red")
    content.append(
        "  • Talk with suspects and uncover their secrets\n"
        "  • Ask questions carefully — every detail matters\n"
        "  • NPCs remember your conversations\n\n"
    )

    content.append("ACCUSATION\n", style="bold red")
    content.append(
        "  • After 3 conversations you can accuse a suspect\n"
        "  • Find contradictions before making your choice\n"
        "  • Wrong accusations increase ESCAPE METER by 25%\n\n"
    )

    content.append("OBJECTIVE\n", style="bold red")
    content.append(
        "  • Identify the killer before ESCAPE reaches 100%\n"
        "  • Compare memories and expose the lie\n\n"
    )

    panel = Panel(
        Align.center(content),
        title="[bold red]RECALL[/]",
        subtitle="[dim red]Press Enter to Begin[/]",
        width=100,
        border_style="red",
        padding=(1, 4),
    )

    console.print(Align.center(panel))

if __name__ == "__main__":
    print("RUN game_loop.py")

