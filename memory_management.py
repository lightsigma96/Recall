from types import FunctionType
import random
from typing import Dict, List, Set
import cognee
from cognee.api.v1.recall.recall import RecallResponse

class MemoryManager:
    """Talks with Memory Handler (currently Cognee)"""

    def __init__(self) -> None:
        ## npc count is 8 always
        self.npc_datasets_name: Set[str] = set()

    def _validate_dataset(self, dataset: str):
        if dataset not in self.npc_datasets_name:
            raise ValueError(f"Unknown dataset: {dataset}")

    async def initialize_memory(self, npc_datasets: Dict[str, str]):
        for npc, initialize_memory in npc_datasets.items():
            self.npc_datasets_name.add(f"{npc}_ds")
            await cognee.remember(initialize_memory, dataset_name=f"{npc}_ds")

    async def update_memory(self, npc_dataset: str, to_remember: str):
        self._validate_dataset(npc_dataset)
        await cognee.remember(to_remember, dataset_name=npc_dataset)

    async def recall_memory(self, npc_dataset: str, user_question : str) -> List[RecallResponse]:
        self._validate_dataset(npc_dataset)
        return await cognee.recall(query_text=user_question, datasets=[npc_dataset])

    async def clear_memories(self, npc_dataset: str):
        await cognee.forget(dataset=npc_dataset)
        pass

    async def propagate_memories(self, user_question : str):
        """The gossip where npcs interact with each other, this function is called once in a while"""
        
        sample_list : List[str] = random.sample(list(self.npc_datasets_name), k=2)

        recalled = await self.recall_memory(sample_list[0],user_question)

        npc_name = sample_list[0].split("_")[0]
        await self.update_memory(sample_list[1], f"{npc_name} was questioned about {recalled}")
    
