import pytest

from agents.agent_orchestrator import AgentOrchestrator
from agents.deal_historian import DealHistorian
from services.hindsight_client import Hindsight


@pytest.fixture(autouse=True)
def clean_memory():
    Hindsight._banks.clear()


@pytest.mark.asyncio
async def test_memory_round_trip():
    historian = DealHistorian()
    await historian.store_memory("Deal ID T1: customer uses Salesforce")
    result = await historian.retrieve_history("T1")
    assert result
    assert "Salesforce" in result[0]["content"]


@pytest.mark.asyncio
async def test_orchestrator_routes_all_core_queries():
    historian = DealHistorian()
    await historian.store_memory(
        "Deal ID T1: budget approved, competitor is Acme, "
        "executive sponsor involved, objection pricing is too high"
    )
    orchestrator = AgentOrchestrator()

    assert "deal_id" in await orchestrator.handle_query("brief", "T1")
    assert isinstance(await orchestrator.handle_query("history", "T1"), list)
    assert "risk_level" in await orchestrator.handle_query("risk", "T1")
    assert "response" in await orchestrator.handle_query("objection pricing", "T1")
    assert "patterns" in await orchestrator.handle_query("patterns", "T1")
