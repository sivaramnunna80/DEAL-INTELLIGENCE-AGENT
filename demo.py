import asyncio

from agents.agent_orchestrator import AgentOrchestrator
from agents.deal_historian import DealHistorian


async def main():
    historian = DealHistorian()
    await historian.store_memory(
        "Deal ID DL001: Acme Health uses Salesforce. "
        "Budget approved in Q4. HubSpot is primary competitor. "
        "Sarah Johnson is champion. Executive sponsor is involved."
    )
    await historian.store_memory(
        "Deal ID DL001: Customer objection: pricing is too high. "
        "ROI justification was requested."
    )

    orchestrator = AgentOrchestrator()

    for query in ("brief", "history", "risk", "objection pricing is too high"):
        result = await orchestrator.handle_query(query, "DL001")
        print(f"\n=== {query.upper()} ===")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
