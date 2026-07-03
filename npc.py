from typing import List
from cognee.api.v1.recall.recall import RecallResponse
import requests
from memory_management import MemoryManager
from pydantic import BaseModel

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

    def _sanitize_name(self,name: str) -> str:
        return name.replace(" ", "_").replace(".", "_")

    def _llm_call(self, npc_recall, user_question: str):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma3:4b",
                    "prompt": f"""
            You are {self.name}.

            Personality:
            {self.personality}
            
            Relevant memories:
            {npc_recall}

            Player asks:
            {user_question}

            Answer only as {self.name}. Do not break character. Only use the memories above. If you don't know something, say so naturally.
            Return ONLY valid JSON with this exact structure:
            {{
                "response": "<your reply>",
                "summary": "<one sentence summarizing this conversation>"
            }}
            Do not output any other text.
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
        
        npc_recall = self.mem_manager.recall_http_request(user_question,self._sanitize_name(f"{self.name}_ds"))
        #npc_recall: List[RecallResponse] = await self.mem_manager.recall_memory(
        #    self._sanitize_name(f"{self.name}_ds"), user_question
        #)

        llm_answer = self._llm_call(npc_recall, user_question)

        await self.mem_manager.update_memory(self._sanitize_name(f"{self.name}_ds"), llm_answer.summary)
        return llm_answer.response
