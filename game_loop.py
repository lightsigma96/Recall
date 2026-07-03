import asyncio
import logging
import os
from google import genai
import json
from dotenv import load_dotenv
import sys
from enum import Enum
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


MAX_NPCS = 8


class ScreenState(Enum):
    MAIN_MENU = 1
    SELECTION_SCREEN = 2
    GAME_SCREEN = 3
    RESULT_SCREEN = 4


class Character(BaseModel):
    name: str
    personality: str
    environment: str


class StoryFormat(BaseModel):
    story: str
    title: str
    killer: str
    characters: Annotated[List[Character], MaxLen(MAX_NPCS), MinLen(MAX_NPCS)]


def get_character_init_memory(character: Character) -> str:
    return (
        f"Name: {character.name}. "
        f"Personality: {character.personality}. "
        f"Location: {character.environment}."
    )


from google.genai import types


async def generate_story(
    mem_manager: MemoryManager, selected_biome: Biome, cloud_model_client: Client
) -> Tuple[str,NPCS]:

    # prompt = f"""
    #    You are a murder mystery game designer.
    #
    #        A crime has occurred in: {selected_biome.name}
    #        Setting: {selected_biome.description}
    #        Available locations: {", ".join(selected_biome.locations)}
    #
    #        Rules:
    #        - Exactly 8 characters, one of them is the killer
    #        - killer field must exactly match one character's name
    #        - Each character's environment must be one of the available locations
    #        - Characters should have conflicting memories of the night
    #        - The killer's personality should not be obviously guilty
    #    """
    #
    #    raw_story = cloud_model_client.models.generate_content(
    #        model="gemini-2.0-flash-lite",
    #        contents=prompt,
    #        config=types.GenerateContentConfig(
    #            response_mime_type="application/json",
    #            response_schema=StoryFormat,
    #        ),
    #    )

    # sample story
    raw_story = {
    "story": "On a fog-covered evening in Victorian London, the wealthy Ashworth family gathered at Blackwood Manor to celebrate the retirement of Lord Cedric Ashworth. The night was filled with old rivalries, whispered conversations, and secrets buried beneath years of family politics. Near midnight, the manor bell rang unexpectedly, followed by a scream echoing through the halls. Lord Cedric was discovered murdered, and the storm outside trapped everyone within the surrounding estate grounds. The nearby buildings became isolated pockets of suspicion — the tavern held rumors, the church held confessions, the dockyard hid dealings, and the manor concealed old betrayals. Each person knows fragments of the truth: some saw suspicious movements, some overheard arguments, and others hide their own crimes. The detective must question everyone, connect memories, and reveal who killed Lord Cedric.",
    "title": "The Blackwood Fog",
    "killer": "Eleanor Ashworth",
    "characters": [
        {
            "name": "Eleanor Ashworth",
            "personality": "Composed, intelligent, manipulative, and obsessed with preserving the Ashworth legacy.",
            "environment": "Manor House",
        },
        {
            "name": "Nigel Graves",
            "personality": "Gruff, loyal, easily irritated, but notices details others ignore.",
            "environment": "Dark Alley",
        },
        {
            "name": "Beatrice Holloway",
            "personality": "Elegant, gossip-loving, curious, and skilled at uncovering secrets.",
            "environment": "Theatre",
        },
        {
            "name": "Oliver Finch",
            "personality": "Nervous, analytical, intelligent, and easily frightened.",
            "environment": "Apothecary",
        },
        {
            "name": "Martha Doyle",
            "personality": "Kind, practical, hardworking, and protective of ordinary townsfolk.",
            "environment": "Tavern",
        },
        {
            "name": "Victor Langley",
            "personality": "Charming, ambitious, arrogant, and always hiding his true intentions.",
            "environment": "Dockyard",
        },
        {
            "name": "Samuel Brooks",
            "personality": "Quiet, disciplined, suspicious, and loyal to his duty.",
            "environment": "Church",
        },
        {
            "name": "Clara Whitmore",
            "personality": "Cheerful, empathetic, observant, and able to read people's emotions.",
            "environment": "Train Station",
        },
    ],
}
    # if raw_story.text
    if raw_story:
        # validated_story = StoryFormat.model_validate_json(raw_story)
        validated_story = StoryFormat.model_validate(raw_story)
    else:
        raise ValueError("STORY COULD NOT BE GENERATED BY AI")

    npcs_dict: NPCS = dict()
    for character in validated_story.characters:
        npc = NPC(
            character.name, character.personality, character.environment, mem_manager
        )
        npcs_dict[character.name] = npc
        im = get_character_init_memory(character)
        await mem_manager.initialize_memory({character.name: im})

    return  validated_story.killer ,npcs_dict

async def main():
    mem_manager: MemoryManager = MemoryManager()
    screen_state: ScreenState = ScreenState.MAIN_MENU
    load_dotenv()

    game_result: GameResult = GameResult(remark="",success=False,actual_killer="")
    cloud_model = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    # It is accessed, type checker problem
    npcs: Tuple[str, NPCS] | None = None

    while True:
        sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")
        sys.stdout.flush()

        if screen_state == ScreenState.MAIN_MENU:
            render_main_menu()
            x: str = input()
            if len(x.strip()) == 0:
                screen_state = ScreenState.SELECTION_SCREEN

        elif screen_state == ScreenState.SELECTION_SCREEN:
            selected_biome: Biome = biome_selection()
            npcs = await generate_story(mem_manager, selected_biome, cloud_model)
            screen_state = ScreenState.GAME_SCREEN

        elif screen_state == ScreenState.GAME_SCREEN:
            game_result = await game(npcs)
            screen_state = ScreenState.RESULT_SCREEN

        elif screen_state == ScreenState.RESULT_SCREEN:
            render_result(game_result.actual_killer,game_result.success,game_result.remark)
            break

if __name__ == "__main__":
    asyncio.run(main())
