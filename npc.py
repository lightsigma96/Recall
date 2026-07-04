from typing import List
from cognee.api.v1.recall.recall import RecallResponse
import requests
from memory_management import MemoryManager
from pydantic import BaseModel
import os, dotenv

def load_local_model():
    dotenv.load_dotenv()
    return os.getenv("LLM_MODEL")

# types
class llm_call_format(BaseModel):
    response: str
    summary: str


class NPC:
    def __init__(
        self,
        name: str,
        personality: str,
        environment: str,
        memory_manager: MemoryManager,
    ):
        """Personalities should be constant"""
        self.mem_manager = memory_manager
        self.name = name
        self.personality: str = personality
        self.environment: str = environment
        self.dataset_name = f"{name.replace(' ', '_').replace('.', '_')}_ds"

        self.answer_format = {
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "summary": {"type": "string"},
            },
            "required": ["response", "summary"],
        }

    def _sanitize_name(self, name: str) -> str:
        return name.replace(" ", "_").replace(".", "_")

    def _llm_call(self, npc_recall, user_question: str):
        local_model : str | None = load_local_model()
        if not local_model:
            local_model = "gemma3:4b"

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": local_model,
                    "prompt": f"""
                        You are roleplaying a murder mystery suspect.

                        Core rules:
                        - Never break character.
                        - DO NOT EVER SAY YOU ARE ChatGPT OR ANY AI ASSISTANT.
                        - Answer only as the character.
                        - Keep responses short and natural.

                        World rules:
                        - A murder happened last night.
                        - An investigator is questioning you.
                        - You are one of the suspects.

                        Memory:
                        These are YOUR memories and past experiences:
                        {npc_recall}

                        Conversation rules:
                        - Use your memory to answer the investigator.
                        - Stay consistent with previous answers.
                        - Do not invent new evidence or events.
                        - If you do not remember something, say so.
                        - Do not reveal information unrelated to the question.

                        If you are guilty:
                        - Never confess directly.
                        - Maintain your fake story.
                        - Hide contradictions when possible.
                        - Become nervous or defensive when pressured.

                        If you are innocent:
                        - Tell what you remember.
                        - You can be confused, scared, or suspicious.

                        Investigator question:
                        {user_question}

                        Reply as your character:
                    """,
                    "format": self.answer_format,
                    "stream": False,
                },
            )
            answer = response.json()
            return llm_call_format.model_validate_json(answer["response"])

        except Exception as e:
            raise requests.HTTPError("Error occurred during model generation.") from e

    async def generate_response(self, user_question: str) -> str:

        npc_recall = self.mem_manager.recall_http_request(
            user_question, self._sanitize_name(f"{self.name}_ds")
        )
        # npc_recall: List[RecallResponse] = await self.mem_manager.recall_memory(
        #    self._sanitize_name(f"{self.name}_ds"), user_question
        # )

        llm_answer = self._llm_call(npc_recall, user_question)

        await self.mem_manager.update_memory(
            self._sanitize_name(f"{self.name}_ds"), llm_answer.summary
        )
        return llm_answer.response


if __name__ == "__main__":
    print("RUN game_loop.py")
