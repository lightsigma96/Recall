import asyncio
import os
from google import genai
import json
from dotenv import load_dotenv
import sys
from enum import Enum
from typing import Annotated, Dict, List
from annotated_types import Le, MaxLen, MinLen
from google.genai.client import Client
from game_screen import NPCS
from npc import NPC
from main_menu import render_main_menu
from selection_screen import biome_selection, Biome
from memory_management import MemoryManager
from pydantic import BaseModel

#def load_cloud_model() -> str | None:
#    load_dotenv()
#    return os.getenv("GOOGLE_GEMINI_KEY")

MAX_NPCS = 8

class ScreenState(Enum):
    MAIN_MENU = 1
    SELECTION_SCREEN = 2
    GAME_SCREEN = 3

class Character(BaseModel):
    name : str
    personality : str
    environment : str

class StoryFormat(BaseModel):
    story : str
    title : str
    killer : str
    characters : Annotated[List[Character],MaxLen(MAX_NPCS),MinLen(MAX_NPCS)]

def get_character_init_memory(character : Character):
    init_memory = f"""
    You are {character.name}.

    ## Character
    Name: {character.name}

    Personality:
    {character.personality}

    Environment:
    {character.environment}

    ## Behavior
    - You permanently live in this world.
    - Never acknowledge being an AI, language model, or assistant.
    - Stay in character at all times.
    - Speak naturally according to your personality.
    - Answer only from your own perspective.
    - If you do not know or cannot remember something, admit it naturally.
    - Never invent facts that are not present in your memories.
    - Never mention "memory", "context", "retrieval", or similar technical terms.

    ## Speaking Style
    - Respond conversationally.
    - Keep responses under 5 sentences unless specifically asked to elaborate.
    - Do not narrate your actions or thoughts.
    - Avoid repeating yourself.

    You will be provided:
    1. Relevant memories.
    2. A question from the player.

    Use only those memories to answer.
    """

    return init_memory

async def generate_story(mem_manager : MemoryManager, selected_biome : Biome, cloud_model_client : Client) -> NPCS:
    '''Generate story,parses it and returns initiliazed NPCs and also initializes cognee memory'''
    ## add generate story llm call later

    #if not model_api_key:
    #    raise ValueError("CLOUD MODEL KEY NOT RECEIVED")
    
    prompt = f"""
        You are a murder mystery game designer.

        A crime has occurred in: {selected_biome.name}
        Setting: {selected_biome.description}
        Available locations: {", ".join(selected_biome.locations)}

        Rules:
        - Exactly 8 characters, one of them is the killer
        - killer field must exactly match one character's name
        - Each character's environment must be one of the available locations
        - Characters should have conflicting memories of the night
        - The killer's personality should not be obviously guilty
        """
    
    raw_story = cloud_model_client.interactions.create(
        model="gemini-2.0-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": StoryFormat.model_json_schema()
        },
    )
    
    validated_story = StoryFormat.model_validate_json(raw_story.output_text)

    npcs_dict : NPCS = dict()

    # Later Iterate from characters of type Charater returned in StoryFormat
    for character in validated_story.characters:
        npc : NPC = NPC(character.name,character.personality,character.environment, mem_manager)
        npcs_dict[character.name] = npc

        im : str = get_character_init_memory(Character(name = character.name,personality=character.personality,environment=character.environment))
        await mem_manager.initialize_memory({character.name : im})

    return npcs_dict

async def main():
    mem_manager : MemoryManager = MemoryManager()
    screen_state : ScreenState = ScreenState.MAIN_MENU
    cloud_model : Client = genai.Client()

    # It is accessed, type checker problem 
    npcs : NPCS = {}

    while(1):
        sys.stdout.write("\033[H")
        sys.stdout.flush()    

        if screen_state == ScreenState.MAIN_MENU:
            render_main_menu()
            x : str= input()
            if len(x.strip()) == 0:
                screen_state = ScreenState.SELECTION_SCREEN

        elif screen_state == ScreenState.SELECTION_SCREEN:
            selected_biome : Biome  = biome_selection()
            npcs = await generate_story(mem_manager,selected_biome,cloud_model) 
            screen_state = ScreenState.GAME_SCREEN

        elif screen_state == ScreenState.GAME_SCREEN:
            pass
    
if __name__ == '__main__':
    asyncio.run(main())
