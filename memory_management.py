import random
import io
from typing import Dict, List, Set
import os, dotenv
import cognee
import requests


def get_cognee_api_key():
    dotenv.load_dotenv()
    return os.getenv("COGNEE_API_KEY")


class MemoryManager:
    """Talks with Cognee Cloud."""

    BASE_URL = "https://tenant-c16c2b32-7f8c-4fbe-8fa7-a3b9500601be.aws.cognee.ai"

    def __init__(self) -> None:
        self.npc_datasets_name: Set[str] = set()

    def _validate_dataset(self, dataset: str):
        if dataset not in self.npc_datasets_name:
            raise ValueError(f"Unknown dataset: {dataset}")

    def _headers(self) -> dict:
        api_key = get_cognee_api_key()

        if not api_key:
            raise requests.HTTPError("COGNEE API KEY NOT FOUND")

        return {
            "X-Api-Key": api_key,
        }

    def remember_http_request(
        self,
        remember_text: str,
        dataset_name: str,
    ):
        api_key = get_cognee_api_key()
        files = [
            (
                "data",
                (
                    "memory.txt",
                    io.BytesIO(remember_text.encode()),
                    "text/plain",
                ),
            )
        ]
        
        if not api_key:
            raise requests.HTTPError("COGNEE_API_KEY NOT FOUND")

        payload = {
            "datasetName": dataset_name,
        }

        res = requests.post(
            f"{self.BASE_URL}/api/v1/remember",
            headers={"X-Api-Key": api_key},
            files=files,
            data=payload,
        )

        res.raise_for_status()

    def recall_http_request(
        self,
        user_question: str,
        dataset_name: str,
    ):
        payload = {
            "searchType": "GRAPH_COMPLETION",
            "datasets": [dataset_name],
            "query": user_question,
            "topK": 15,
        }

        headers = self._headers()
        headers["Content-Type"] = "application/json"

        response = requests.post(
            f"{self.BASE_URL}/api/v1/recall",
            headers=headers,
            json=payload,
        )

        response.raise_for_status()

        try:
            return response.json()
        except ValueError:
            return response.text

    async def initialize_memory(self, npc_datasets: Dict[str, str]):
        for npc, memory in npc_datasets.items():
            dataset_name = npc.replace(" ", "_").replace(".", "_") + "_ds"

            self.npc_datasets_name.add(dataset_name)

            self.remember_http_request(
                memory,
                dataset_name,
            )

    async def update_memory(
        self,
        npc_dataset: str,
        to_remember: str,
    ):
        self._validate_dataset(npc_dataset)

        self.remember_http_request(
            to_remember,
            npc_dataset,
        )

    async def recall_memory(
        self,
        npc_dataset: str,
        user_question: str,
    ):
        self._validate_dataset(npc_dataset)

        return self.recall_http_request(
            user_question,
            npc_dataset,
        )

    async def clear_memories(self, npc_dataset: str):
        self._validate_dataset(npc_dataset)
        await cognee.forget(dataset=npc_dataset)

    async def propagate_memories(self, user_question: str):
        """Randomly propagates information between two NPCs."""

        source_dataset, target_dataset = random.sample(
            list(self.npc_datasets_name),
            k=2,
        )

        recalled = await self.recall_memory(
            source_dataset,
            user_question,
        )

        npc_name = source_dataset.removesuffix("_ds")

        await self.update_memory(
            target_dataset,
            f"{npc_name} was questioned about: {recalled}",
        )
