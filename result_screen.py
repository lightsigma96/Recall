from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

RECALL_ART = """
                    ▓▒░░▒▓█▓▒░░░░      ▄▄▒▓█▓▒▒▒▒▒▓█▓   ▄▄▒▓█▓▒▒▒▒▒▓█▓   ▄▄▒▓█▓▒▒▒▄▄    █▓▒▓▓            █▓▒▓▓           
                    ███░▒▓██▓▒░▒▒▒░  ▄▓▓░▒▓██▓▒░▒▒▒▒▒ ▄██░▒▓██▓▒░▒▒▒▒▒  █░░▒▓█░░▒▓▓▓▓▄  ▓▓▓▓▒            ▓▓▓▓▒           
                    █▓▓▓░     ░▓▓▓▓░ █▒▒▒░▀    ░▓▓▓▓░ █▓▓▓░▀    ░▓▓▓▓░ █▒▒░░▀   ▀░▒▒▒▒▌ █▒▒▒░            █▒▒▒░           
                    ▓▒▒▒░    ▐▓███▓▀ ▓░░░░▄▄▄  ▒████░ ▓▒▒▒░     ▒████░ ▓▓▓▒░     ▒░░░░░ ▓░░░░            ▓░░░░           
                    ▒░░░▒▄▄▄▄███▓▀   ▒░░░▒░▒▓  ▀▀▀▀▀▀ ▒░░░▒     ▀▀▀▀▀▀ ▒██▓▒▄▄▄▄▄▓░░░░▒ ▒░░░▒            ▒░░░▒           
                    ░░░░▒▒▓▓███▒▓▓▄  ░▒▒▒▓     ▄▄▄▄▄▄ ░░░░▓     ▄▄▄▄▄▄ ░▓▓█▓▓▓▓▒▒▒▒▒▒▒▓ ░▒▒▒▓     ▄▄▄▄▄▄ ░▒▒▒▓     ▄▄▄▄▄▄
                    ░▒▒▒█    ▀█▒▓▓▓█ ░▓▓▓█     █▒▒▒▒█ ░▒▒▒░     █▒▒▒▒█ ░▒▒▓█     █▓▓▓▓█ ░▓▓▓█     █▒▒▒▒█ ░▓▓▓█     █▒▒▒▒█
                    ▒▓▓▓▓     ▓░░▒▒▓ ▀▓▒▒▒█▄▄▄▄▓░░░░▓ ▀▓▓▓▓█▄▄▄▄▓░░░░▓ ▒░░░▓     ▓▒▒▒▒▓ ▀▓▒▒▒█▄▄▄▄▓░░░░▓ ▀▓▒▒▒█▄▄▄▄▓░░░░▓
                    ▓▓▓▓▓     ▒░▒▒▒▓   ▀▀▓▓▓▒▒▒░░░░░▒   ▀▀▓▓▓▒▒▒░░░░░▒ ▓░░░▒     ▒░░░░▒   ▀▀▓▓▓▒▒▒░░░░░▒   ▀▀▓▓▓▒▒▒░░░░░▒
"""


def render_title(console : Console):
    t = Text(RECALL_ART)
    t.stylize("bold white", 0, len(RECALL_ART) // 2)
    t.stylize(
        "bold red", len(RECALL_ART) // 3, len(RECALL_ART) // 3 + len(RECALL_ART) // 6
    )
    console.print(Align.center(t))
    console.print(
        Align.center(
            "                   A N   A I   M Y S T E R Y   G A M E", style="dim white"
        )
    )


def render_result(killer: str, completion_status: bool, remark: str):
    console : Console = Console()

    verdict: str = "CRIMINAL CAUGHT" if completion_status else "CRIMINAL ESCAPED"

    frame: str = f"""

              ╔════════════════════════ CASE REPORT ════════════════════════╗


                         KLLER         :  {killer}

                         VERDICT       :  {verdict}

                         REMARK        :  {remark} 


             ╚══════════════════════════════════════════════════════════════╝
"""

    render_title(console)
    console.print(
        Align.center(
            Text(frame, style="red"),
            vertical="middle",
        )
    )


if __name__ == "__main__":
    print("RUN game_loop.py")

