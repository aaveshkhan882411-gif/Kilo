import pytest

from app.agents.registry import registry


def test_agent_registry_exposes_contract_tools():
    contract = registry.get_contract("ai-sales")

    assert contract is not None
    assert "crm" in contract.allowed_tools
    assert "email" in contract.allowed_tools
    assert "calendar" in contract.allowed_tools


def test_agent_registry_rejects_unknown_agent_contract():
    assert registry.get_contract("not-a-real-agent") is None


@pytest.mark.parametrize(
    "agent_id,required_permission",
    [
        ("ai-sales", "send_email"),
        ("ai-followup", "send_email"),
        ("ai-whatsapp", "send_whatsapp"),
        ("ai-crm", "write_crm"),
        ("ai-appointment", "write_appointments"),
    ],
)
def test_agent_contract_declares_required_permission(
    agent_id: str,
    required_permission: str,
):
    contract = registry.get_contract(agent_id)

    assert contract is not None
    assert required_permission in contract.required_permissions


@pytest.mark.asyncio
async def test_registered_tool_executes_through_registry():
    from app.agents.tool_registry import tool_registry

    async def fake_email_tool(params):
        return {
            "success": True,
            "status": "executed",
            "message": f"email prepared for {params['to']}",
        }

    tool_registry.register("email", fake_email_tool)

    result = await tool_registry.execute(
        agent_id="ai-sales",
        tool="email",
        params={"to": "customer@example.com"},
        permissions=[
            "read_crm",
            "write_deals",
            "send_email",
        ],
        context={
            "org_id": "org-1",
            "user_id": "user-1",
        },
    )

    assert result["success"] is True
    assert result["status"] == "executed"
    assert "customer@example.com" in result["message"]


@pytest.mark.asyncio
async def test_allowed_unregistered_tool_is_not_executed():
    from app.agents.tool_registry import tool_registry

    result = await tool_registry.execute(
        agent_id="ai-sales",
        tool="calendar",
        params={},
        permissions=[
            "read_crm",
            "write_deals",
            "send_email",
        ],
        context={
            "org_id": "org-1",
            "user_id": "user-1",
        },
    )

    assert result["success"] is False
    assert result["status"] == "tool_not_registered"


@pytest.mark.asyncio
async def test_registered_tool_still_requires_agent_contract_permissions():
    from app.agents.tool_registry import tool_registry

    async def fake_email_tool(params):
        return {
            "success": True,
            "status": "executed",
        }

    tool_registry.register("email", fake_email_tool)

    result = await tool_registry.execute(
        agent_id="ai-sales",
        tool="email",
        params={"to": "customer@example.com"},
        permissions=["read_crm"],
    )

    assert result["success"] is False
    assert result["status"] == "permission_denied"


@pytest.mark.asyncio
async def test_base_agent_executes_registered_tool():
    from app.agents.base import BaseAgent
    from app.agents.tool_registry import tool_registry

    async def fake_email_tool(params):
        return {
            "success": True,
            "status": "executed",
            "recipient": params["to"],
        }

    tool_registry.register("email", fake_email_tool)

    agent = BaseAgent("ai-sales", "AI Sales")

    result = await agent.execute_tool(
        tool="email",
        params={"to": "customer@example.com"},
        permissions=[
            "read_crm",
            "write_deals",
            "send_email",
        ],
        context={
            "org_id": "org-1",
            "user_id": "user-1",
        },
    )

    assert result["success"] is True
    assert result["status"] == "executed"
    assert result["recipient"] == "customer@example.com"


@pytest.mark.asyncio
async def test_base_agent_cannot_execute_disallowed_tool():
    from app.agents.base import BaseAgent
    from app.agents.tool_registry import tool_registry

    async def fake_database_tool(params):
        return {
            "success": True,
            "status": "executed",
        }

    tool_registry.register("database", fake_database_tool)

    agent = BaseAgent("ai-sales", "AI Sales")

    result = await agent.execute_tool(
        tool="database",
        params={},
        permissions=[
            "read_crm",
            "write_deals",
            "send_email",
        ],
    )

    assert result["success"] is False
    assert result["status"] == "permission_denied"


@pytest.mark.asyncio
async def test_tool_registry_requires_execution_context():
    from app.agents.tool_registry import tool_registry

    async def fake_crm_tool(params):
        return {
            "success": True,
            "status": "executed",
        }

    tool_registry.register("crm", fake_crm_tool)

    result = await tool_registry.execute(
        agent_id="ai-sales",
        tool="crm",
        params={},
        permissions=[
            "read_crm",
            "write_deals",
            "send_email",
        ],
    )

    assert result["success"] is False
    assert result["status"] == "execution_context_required"


@pytest.mark.asyncio
async def test_tool_registry_rejects_missing_tenant_context():
    from app.agents.tool_registry import tool_registry

    async def fake_crm_tool(params):
        return {
            "success": True,
            "status": "executed",
        }

    tool_registry.register("crm", fake_crm_tool)

    result = await tool_registry.execute(
        agent_id="ai-sales",
        tool="crm",
        params={},
        permissions=[
            "read_crm",
            "write_deals",
            "send_email",
        ],
        context={"user_id": "user-1"},
    )

    assert result["success"] is False
    assert result["status"] == "invalid_execution_context"


@pytest.mark.asyncio
async def test_base_agent_execute_passes_tenant_context_to_tool():
    from app.agents.base import BaseAgent
    from app.agents.tool_registry import tool_registry

    captured = {}

    async def fake_crm_tool(params):
        captured.update(params["_execution_context"])
        return {
            "success": True,
            "status": "executed",
        }

    class TestAgent(BaseAgent):
        async def create_plan(self, context):
            return {
                "plan": ["execute crm"],
                "requested_tool": "crm",
                "parameters": {},
            }

    tool_registry.register("crm", fake_crm_tool)

    agent = TestAgent("ai-sales", "AI Sales")

    result = await agent.execute(
        {
            "task_id": "task-1",
            "input": {},
            "context": {
                "org_id": "org-1",
                "user_id": "user-1",
            },
            "permissions": [
                "read_crm",
                "write_deals",
                "send_email",
            ],
        }
    )

    assert result["status"] == "completed"
    assert captured["org_id"] == "org-1"
    assert captured["user_id"] == "user-1"

@pytest.mark.asyncio
async def test_builtin_crm_tool_lists_only_current_tenant_leads(
    db,
    test_org,
    monkeypatch,
):
    from app.agents import tool_registry as tool_registry_module
    from app.agents.tool_registry import _crm_lead_tool, tool_registry
    from app.models import Lead, Organization
    from tests.conftest import TestingSessionFactory

    monkeypatch.setattr(
        tool_registry_module,
        "async_session_factory",
        TestingSessionFactory,
    )

    tool_registry.register("crm", _crm_lead_tool)

    org_b = Organization(
        name="Other Org",
        slug="other-org",
        plan="standard",
    )
    db.add(org_b)
    await db.commit()
    await db.refresh(org_b)

    lead_a = Lead(
        org_id=test_org.id,
        first_name="Visible",
        last_name="Lead",
        email="visible@example.com",
    )
    lead_b = Lead(
        org_id=org_b.id,
        first_name="Secret",
        last_name="Lead",
        email="secret@example.com",
    )
    db.add_all([lead_a, lead_b])
    await db.commit()

    result = await tool_registry.execute(
        agent_id="ai-crm",
        tool="crm",
        params={"action": "list_leads"},
        permissions=["read_crm", "write_crm"],
        context={"org_id": test_org.id, "user_id": "test-user"},
    )

    assert result["success"] is True
    assert result["action"] == "list_leads"
    assert result["count"] == 1
    assert result["leads"][0]["email"] == "visible@example.com"


@pytest.mark.asyncio
async def test_builtin_crm_tool_cannot_read_cross_tenant_lead(
    db,
    test_org,
    monkeypatch,
):
    from app.agents import tool_registry as tool_registry_module
    from app.agents.tool_registry import _crm_lead_tool, tool_registry
    from app.models import Lead, Organization
    from tests.conftest import TestingSessionFactory

    monkeypatch.setattr(
        tool_registry_module,
        "async_session_factory",
        TestingSessionFactory,
    )

    tool_registry.register("crm", _crm_lead_tool)

    org_b = Organization(
        name="Other Org",
        slug="other-org",
        plan="standard",
    )
    db.add(org_b)
    await db.commit()
    await db.refresh(org_b)

    lead_b = Lead(
        org_id=org_b.id,
        first_name="Secret",
        last_name="Lead",
        email="secret@example.com",
    )
    db.add(lead_b)
    await db.commit()
    await db.refresh(lead_b)

    result = await tool_registry.execute(
        agent_id="ai-crm",
        tool="crm",
        params={
            "action": "get_lead",
            "lead_id": lead_b.id,
        },
        permissions=["read_crm", "write_crm"],
        context={"org_id": test_org.id, "user_id": "test-user"},
    )

    assert result["success"] is False
    assert result["status"] == "not_found"


@pytest.mark.asyncio
async def test_builtin_crm_tool_caps_list_limit(
    db,
    test_org,
    monkeypatch,
):
    from app.agents import tool_registry as tool_registry_module
    from app.agents.tool_registry import _crm_lead_tool, tool_registry
    from app.models import Lead
    from tests.conftest import TestingSessionFactory

    monkeypatch.setattr(
        tool_registry_module,
        "async_session_factory",
        TestingSessionFactory,
    )

    tool_registry.register("crm", _crm_lead_tool)

    leads = [
        Lead(
            org_id=test_org.id,
            first_name=f"Lead{i}",
            last_name="Test",
            email=f"lead{i}@example.com",
        )
        for i in range(60)
    ]

    db.add_all(leads)
    await db.commit()

    result = await tool_registry.execute(
        agent_id="ai-crm",
        tool="crm",
        params={
            "action": "list_leads",
            "limit": 999,
        },
        permissions=["read_crm", "write_crm"],
        context={"org_id": test_org.id, "user_id": "test-user"},
    )

    assert result["success"] is True
    assert result["count"] == 50
    assert len(result["leads"]) == 50
