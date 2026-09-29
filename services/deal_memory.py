from services.hindsight_client import Hindsight

client = Hindsight()
BANK_ID = "deal-oracle"


async def retain_memory(content, metadata=None):
    return client.retain(
        bank_id=BANK_ID,
        content=content,
        metadata=metadata or {},
    )


async def recall_memory(query, top_k=5):
    return client.recall(
        bank_id=BANK_ID,
        query=query,
        top_k=top_k,
    )
