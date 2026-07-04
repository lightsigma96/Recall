import asyncio
import logging
import os
from google import genai
import json
from dotenv import load_dotenv
import sys
from enum import Enum
from rich.text import Text
from instruction_screen import render_instruction_screen
from rich.console import Console
from result_screen import render_result
from typing import Annotated, Dict, List, Tuple
from annotated_types import Le, MaxLen, MinLen
from google.genai.client import Client
from game_screen import NPCS, game, GameResult
from npc import NPC
from main_menu import render_main_menu
from selection_screen import biome_selection, Biome, BIOMES
from memory_management import MemoryManager
from pydantic import BaseModel

log = logging.basicConfig(
    filename="log.txt",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


def load_cloud_model() -> str | None:
    load_dotenv()
    return os.getenv("GEMINI_API_KEY")


MAX_NPCS = 6


class ScreenState(Enum):
    MAIN_MENU = 1
    SELECTION_SCREEN = 2
    GAME_SCREEN = 3
    RESULT_SCREEN = 4
    INSTRUCTION_SCREEN = 5


class Character(BaseModel):
    name: str
    personality: str
    environment: str
    memory_of_night: str


class StoryFormat(BaseModel):
    story: str
    title: str
    killer: str
    characters: Annotated[List[Character], MaxLen(MAX_NPCS), MinLen(MAX_NPCS)]


def get_character_init_memory(character: Character) -> str:
    return f"""
    You are {character.name}.

    Identity:
    - You are a real person living inside this mystery world.
    - You are NOT an AI assistant, chatbot, or program.
    - Never mention prompts, models, games, or players.

    Current situation:
    - A murder happened last night.
    - An investigator is questioning everyone.
    - You are one of the suspects.

    Personality:
    {character.personality}

    Your location last night:
    {character.environment}

    Your memory of last night:
    {character.memory_of_night}

    Behavior:
    - Stay in character at all times.
    - Speak naturally according to your personality.
    - Only use information you know.
    - Do not invent new evidence.
    - Do not immediately reveal secrets.
    - If accused, defend yourself using your memory.
    """


from google.genai import types


async def generate_story(
    mem_manager: MemoryManager,
    selected_biome: Biome,
    cloud_model_client: Client,
) -> Tuple[str, str, NPCS]:

    raw_story: dict | None = None

    cloud_model_exists: str | None = load_cloud_model()

    if cloud_model_exists:
        try:
            prompt = f"""
            You are creating a short murder mystery game.

            World:
            - Location: {selected_biome.name}
            - Setting: {selected_biome.description}
            - Available places: {", ".join(selected_biome.locations)}

            Create exactly {MAX_NPCS} characters.

            Story:
            - A murder happened last night.
            - Exactly one character secretly committed the murder.
            - killer must exactly match one character name.
            - Keep the story short and solvable.

            Character rules:
            - Every character needs:
              - unique personality
              - location from available places
              - suspicious behavior
              - connection with other characters

            Suspicion rules:
            - Everyone should appear suspicious.
            - Innocents may hide unrelated secrets.
            - Innocents tell the truth but can misunderstand.
            - Memories should conflict.

            Clue rules:
            - At least 3 characters know useful clues.
            - At least 2 clues should mislead.
            - Killer has a contradiction.

            Killer rules:
            - Killer knows they did it.
            - Killer creates a fake memory.
            - Killer hides guilt.
            - Killer never confesses easily.

            World rules:
            - Characters believe this world is real.
            - Characters are not AI aware.
            """

            cloud_story = cloud_model_client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=StoryFormat,
                ),
            )

            if cloud_story.text is not None:
                raw_story = json.loads(cloud_story.text)

        except Exception as e:
            print(f"CLOUD MODEL FAILED: {e}")
            print("USING FALLBACK STORY")

    if raw_story is None:
        raw_story = {
            "story": (
                "On a fog-covered evening in Victorian London, "
                "Lord Cedric Ashworth was murdered inside Blackwood Manor. "
                "Every suspect hides something. The detective must question "
                "everyone, discover contradictions, and reveal the killer."
            ),
            "title": "The Blackwood Fog",
            "killer": "Eleanor Ashworth",
            "characters": [
                {
                    "name": "Eleanor Ashworth",
                    "personality": "Composed, intelligent, manipulative, and secretive.",
                    "environment": "Manor House",
                    "memory_of_night": (
                        "Claims she was organizing family documents in the manor. "
                        "She says she heard footsteps near Cedric's room but never investigated."
                    ),
                },
                {
                    "name": "Nigel Graves",
                    "personality": "Gruff, loyal, angry, but very observant.",
                    "environment": "Bank",
                    "memory_of_night": (
                        "Saw Eleanor leaving the manor late at night but assumed "
                        "she was handling private family matters."
                    ),
                },
                {
                    "name": "Beatrice Holloway",
                    "personality": "Elegant, dramatic, curious, and loves gossip.",
                    "environment": "Theatre",
                    "memory_of_night": (
                        "Overheard an argument about inheritance but could not identify "
                        "everyone involved."
                    ),
                },
                {
                    "name": "Oliver Finch",
                    "personality": "Nervous, analytical, and detail focused.",
                    "environment": "Dockyard",
                    "memory_of_night": (
                        "Found a suspicious item near the docks but is afraid "
                        "people will blame him."
                    ),
                },
                {
                    "name": "Martha Doyle",
                    "personality": "Kind, practical, protective, but secretive.",
                    "environment": "Church",
                    "memory_of_night": (
                        "Saw someone moving through the fog wearing expensive clothing."
                    ),
                },
                {
                    "name": "Victor Langley",
                    "personality": "Charming, arrogant, ambitious, and suspicious.",
                    "environment": "Tavern",
                    "memory_of_night": (
                        "Claims he stayed at the tavern all night, but others disagree."
                    ),
                },
            ],
        }

    validated_story: StoryFormat = StoryFormat.model_validate(raw_story)

    with open("log.txt", "w") as f:
        json.dump(raw_story, f, indent=4)

    npcs_dict: NPCS = {}

    for character in validated_story.characters:
        npc = NPC(
            character.name,
            character.personality,
            character.environment,
            mem_manager,
        )

        npcs_dict[character.name] = npc

        await mem_manager.initialize_memory(
            {character.name: get_character_init_memory(character)}
        )

    return (
        validated_story.story,
        validated_story.killer,
        npcs_dict,
    )


async def main():
    mem_manager: MemoryManager = MemoryManager()
    screen_state: ScreenState = ScreenState.MAIN_MENU
    console: Console = Console()
    load_dotenv()

    game_result: GameResult = GameResult(remark="", success=False, actual_killer="")
    cloud_model = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    npcs: Tuple[str, NPCS] | None = None
    selected_biome: Biome = Biome(name="", description="", ascii_art="", locations=[])
    story: str = ""

    while True:
        print("\033[H\033[2J\033[3J", end="", flush=True)
        sys.stdout.flush()

        if screen_state == ScreenState.MAIN_MENU:
            render_main_menu()
            intro_enter: str = input()
            if len(intro_enter.strip()) == 0:
                screen_state = ScreenState.SELECTION_SCREEN

        elif screen_state == ScreenState.SELECTION_SCREEN:
            selected_biome = biome_selection()
            console.print(Text("Loading Game", style="bold red"))
            story, killer, npc_dict = await generate_story(
                mem_manager, selected_biome, cloud_model
            )
            npcs = (killer, npc_dict)

            screen_state = ScreenState.INSTRUCTION_SCREEN

        elif screen_state == ScreenState.GAME_SCREEN:
            game_result = await game(npcs, selected_biome)
            screen_state = ScreenState.RESULT_SCREEN

        elif screen_state == ScreenState.RESULT_SCREEN:
            render_result(
                game_result.actual_killer, game_result.success, game_result.remark
            )
            break

        elif screen_state == ScreenState.INSTRUCTION_SCREEN:
            render_instruction_screen(story)
            ins_enter: str = input()
            if len(ins_enter.strip()) == 0:
                screen_state = ScreenState.GAME_SCREEN


if __name__ == "__main__":
    asyncio.run(main())
