import pytest
from app.agents.contracts import AGENT_CONTRACTS, AgentContract
from app.agents.registry import registry


def test_all_agents_registered():
    assert len(AGENT_CONTRACTS) == 20
    expected_ids = [
        "ai-ceo", "ai-business-analyst", "ai-growth-strategist", "ai-lead-intelligence",
        "ai-revenue-optimizer", "ai-sales", "ai-receptionist", "ai-support",
        "ai-followup", "ai-appointment", "ai-voice", "ai-email",
        "ai-whatsapp", "ai-crm", "ai-workflow", "ai-marketing-agent",
        "ai-analytics", "ai-agent-architect", "ai-autonomous-orchestrator", "ai-review-manager",
    ]
    for agent_id in expected_ids:
        assert agent_id in AGENT_CONTRACTS


def test_agent_contracts_valid():
    for agent_id, contract in AGENT_CONTRACTS.items():
        assert isinstance(contract, AgentContract)
        assert contract.id == agent_id
        assert contract.name
        assert contract.version
        assert contract.purpose
        assert len(contract.capabilities) > 0
        assert len(contract.allowed_tools) > 0
        assert len(contract.required_permissions) > 0


def test_agent_registry_has_all_agents():
    agents = registry.list_agents()
    assert len(agents) == 20
