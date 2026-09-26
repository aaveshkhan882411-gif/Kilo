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
async def test_registered_calendar_tool_is_executed():
    from app.agents.tool_registry import tool_registry

    result = await tool_registry.execute(
        agent_id="ai-sales",
        tool="calendar",
        params={
            "action": "list_appointments",
            "limit": 10,
        },
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
    assert result["tool"] == "calendar"
    assert result["action"] == "list_appointments"


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


@pytest.mark.asyncio
async def test_builtin_email_tool_sends_through_email_integration(monkeypatch):
    from app.agents import tool_registry as tool_registry_module
    from app.agents.tool_registry import _email_tool, tool_registry
    from app.integrations.base import IntegrationResult

    class FakeEmailIntegration:
        async def send_email(self, to, subject, body, html=None):
            assert to == "customer@example.com"
            assert subject == "Welcome"
            assert body == "Hello from GrowthAI"
            assert html == "<p>Hello from GrowthAI</p>"

            return IntegrationResult(
                success=True,
                data={"message_id": "test-message-1"},
            )

    monkeypatch.setattr(
        tool_registry_module,
        "EmailIntegration",
        FakeEmailIntegration,
    )

    tool_registry.register("email", _email_tool)

    result = await tool_registry.execute(
        agent_id="ai-email",
        tool="email",
        params={
            "to": "  customer@example.com  ",
            "subject": "  Welcome  ",
            "body": "Hello from GrowthAI",
            "html": "<p>Hello from GrowthAI</p>",
        },
        permissions=["read_crm", "send_email"],
        context={
            "org_id": "org-email-test",
            "user_id": "user-email-test",
            "permissions": ["read_crm", "send_email"],
        },
    )

    assert result["success"] is True
    assert result["status"] == "executed"
    assert result["tool"] == "email"
    assert result["data"]["message_id"] == "test-message-1"


@pytest.mark.asyncio
async def test_builtin_email_tool_rejects_missing_required_parameters():
    from app.agents.tool_registry import _email_tool

    context = {"org_id": "org-email-test"}

    missing_to = await _email_tool(
        {
            "subject": "Hello",
            "body": "Test",
            "_execution_context": context,
        }
    )
    assert missing_to["status"] == "invalid_parameters"

    missing_subject = await _email_tool(
        {
            "to": "customer@example.com",
            "body": "Test",
            "_execution_context": context,
        }
    )
    assert missing_subject["status"] == "invalid_parameters"

    missing_body = await _email_tool(
        {
            "to": "customer@example.com",
            "subject": "Hello",
            "_execution_context": context,
        }
    )
    assert missing_body["status"] == "invalid_parameters"


@pytest.mark.asyncio
async def test_builtin_email_tool_requires_trusted_context():
    from app.agents.tool_registry import _email_tool

    result = await _email_tool(
        {
            "to": "customer@example.com",
            "subject": "Hello",
            "body": "Test",
        }
    )

    assert result["success"] is False
    assert result["status"] == "invalid_execution_context"


@pytest.mark.asyncio
async def test_builtin_email_tool_handles_integration_failure(monkeypatch):
    from app.agents import tool_registry as tool_registry_module
    from app.agents.tool_registry import _email_tool
    from app.integrations.base import IntegrationResult

    class FakeEmailIntegration:
        async def send_email(self, to, subject, body, html=None):
            return IntegrationResult(
                success=False,
                error="NOT_CONFIGURED",
            )

    monkeypatch.setattr(
        tool_registry_module,
        "EmailIntegration",
        FakeEmailIntegration,
    )

    result = await _email_tool(
        {
            "to": "customer@example.com",
            "subject": "Hello",
            "body": "Test",
            "_execution_context": {
                "org_id": "org-email-test",
            },
        }
    )

    assert result["success"] is False
    assert result["status"] == "email_send_failed"
    assert result["tool"] == "email"
    assert result["error"] == "NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_email_tool_requires_send_email_permission():
    from app.agents.tool_registry import tool_registry

    result = await tool_registry.execute(
        agent_id="ai-email",
        tool="email",
        params={
            "to": "customer@example.com",
            "subject": "Hello",
            "body": "Test",
        },
        permissions=["read_crm"],
        context={
            "org_id": "org-email-test",
            "user_id": "user-email-test",
        },
    )

    assert result["success"] is False
    assert result["status"] == "permission_denied"


@pytest.mark.asyncio
async def test_calendar_tool_requires_trusted_execution_context():
    from app.agents.tool_registry import tool_registry

    result = await tool_registry.execute(
        agent_id="ai-sales",
        tool="calendar",
        params={"action": "list_appointments"},
        permissions=[
            "read_crm",
            "write_deals",
            "send_email",
        ],
        context=None,
    )

    assert result["success"] is False
    assert result["status"] == "execution_context_required"


@pytest.mark.asyncio
async def test_calendar_tool_rejects_invalid_action():
    from app.agents.tool_registry import tool_registry

    result = await tool_registry.execute(
        agent_id="ai-sales",
        tool="calendar",
        params={"action": "delete_appointment"},
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
    assert result["status"] == "invalid_tool_action"


@pytest.mark.asyncio
async def test_calendar_tool_rejects_invalid_times():
    from app.agents.tool_registry import tool_registry

    result = await tool_registry.execute(
        agent_id="ai-sales",
        tool="calendar",
        params={
            "action": "create_appointment",
            "title": "Test appointment",
            "start_time": "2026-09-26T15:00:00",
            "end_time": "2026-09-26T14:00:00",
        },
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
    assert result["status"] == "invalid_parameters"
    assert "end_time must be after start_time" in result["error"]


@pytest.mark.asyncio
async def test_calendar_tool_rejects_cross_tenant_attendee():
    from app.agents.tool_registry import _calendar_tool, tool_registry

    tool_registry.register("calendar", _calendar_tool)

    class FakeScalarResult:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

    class FakeOrganizer:
        id = "user-a"

    class FakeDB:
        def __init__(self):
            self.calls = 0

        async def execute(self, query):
            self.calls += 1
            if self.calls == 1:
                return FakeScalarResult(FakeOrganizer())
            return FakeScalarResult(None)

    class FakeSession:
        async def __aenter__(self):
            return FakeDB()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    from unittest.mock import patch

    with patch(
        "app.agents.tool_registry.async_session_factory",
        return_value=FakeSession(),
    ):
        result = await _calendar_tool(
            {
                "_execution_context": {
                    "org_id": "org-a",
                    "user_id": "user-a",
                },
                "action": "create_appointment",
                "title": "Cross tenant test",
                "start_time": "2026-09-26T15:00:00",
                "end_time": "2026-09-26T16:00:00",
                "attendee_id": "contact-from-org-b",
            }
        )

    assert result["success"] is False
    assert result["status"] == "not_found"
    assert result["error"] == "Attendee contact not found"


@pytest.mark.asyncio
async def test_calendar_tool_rejects_cross_tenant_lead():
    from app.agents.tool_registry import _calendar_tool, tool_registry

    tool_registry.register("calendar", _calendar_tool)

    class FakeScalarResult:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

    class FakeOrganizer:
        id = "user-a"

    class FakeDB:
        def __init__(self):
            self.calls = 0

        async def execute(self, query):
            self.calls += 1
            if self.calls == 1:
                return FakeScalarResult(FakeOrganizer())
            return FakeScalarResult(None)

    class FakeSession:
        async def __aenter__(self):
            return FakeDB()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    from unittest.mock import patch

    with patch(
        "app.agents.tool_registry.async_session_factory",
        return_value=FakeSession(),
    ):
        result = await _calendar_tool(
            {
                "_execution_context": {
                    "org_id": "org-a",
                    "user_id": "user-a",
                },
                "action": "create_appointment",
                "title": "Cross tenant lead test",
                "start_time": "2026-09-26T15:00:00",
                "end_time": "2026-09-26T16:00:00",
                "lead_id": "lead-from-org-b",
            }
        )

    assert result["success"] is False
    assert result["status"] == "not_found"
    assert result["error"] == "Lead not found"


@pytest.mark.asyncio
async def test_calendar_tool_creates_appointment_and_audit_log():
    from datetime import datetime
    from unittest.mock import patch

    from app.agents.tool_registry import _calendar_tool, tool_registry
    from app.services.audit_service import AuditService

    tool_registry.register("calendar", _calendar_tool)

    class FakeScalarResult:
        def scalar_one_or_none(self):
            class FakeOrganizer:
                id = "user-a"
            return FakeOrganizer()

    class FakeDB:
        def add(self, obj):
            self.appointment = obj

        async def execute(self, query):
            return FakeScalarResult()

        async def flush(self):
            self.appointment.id = "appointment-test-1"

        async def commit(self):
            pass

        async def refresh(self, obj):
            pass

    class FakeSession:
        async def __aenter__(self):
            self.db = FakeDB()
            return self.db

        async def __aexit__(self, exc_type, exc, tb):
            return False

    audit_calls = []

    async def fake_audit(**kwargs):
        audit_calls.append(kwargs)

    with patch(
        "app.agents.tool_registry.async_session_factory",
        return_value=FakeSession(),
    ), patch.object(
        AuditService,
        "record",
        side_effect=fake_audit,
    ):
        result = await _calendar_tool(
            {
                "_execution_context": {
                    "org_id": "org-a",
                    "user_id": "user-a",
                },
                "action": "create_appointment",
                "title": "Demo call",
                "description": "GrowthAI demo",
                "start_time": "2026-09-26T15:00:00",
                "end_time": "2026-09-26T16:00:00",
                "location": "Online",
            }
        )

    assert result["success"] is True
    assert result["status"] == "executed"
    assert result["tool"] == "calendar"
    assert result["action"] == "create_appointment"

    appointment = result["appointment"]

    assert appointment["id"] == "appointment-test-1"
    assert appointment["org_id"] == "org-a"
    assert appointment["title"] == "Demo call"
    assert appointment["organizer_id"] == "user-a"

    assert len(audit_calls) == 1
    assert audit_calls[0]["org_id"] == "org-a"
    assert audit_calls[0]["user_id"] == "user-a"
    assert audit_calls[0]["action"] == "CREATE"
    assert audit_calls[0]["entity_type"] == "appointment"
    assert audit_calls[0]["entity_id"] == "appointment-test-1"


@pytest.mark.asyncio
async def test_calendar_tool_lists_only_current_tenant_appointments():
    from datetime import datetime
    from unittest.mock import patch

    from app.agents.tool_registry import _calendar_tool, tool_registry

    tool_registry.register("calendar", _calendar_tool)

    class AppointmentRow:
        id = "appointment-org-a"
        title = "Tenant A appointment"
        description = None
        start_time = datetime.fromisoformat("2026-09-26T15:00:00")
        end_time = datetime.fromisoformat("2026-09-26T16:00:00")
        location = None
        organizer_id = "user-a"
        attendee_id = None
        lead_id = None
        status = "scheduled"

    class FakeScalars:
        def all(self):
            return [AppointmentRow()]

    class FakeResult:
        def scalars(self):
            return FakeScalars()

    class FakeDB:
        async def execute(self, query):
            return FakeResult()

    class FakeSession:
        async def __aenter__(self):
            return FakeDB()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    with patch(
        "app.agents.tool_registry.async_session_factory",
        return_value=FakeSession(),
    ):
        result = await _calendar_tool(
            {
                "_execution_context": {
                    "org_id": "org-a",
                    "user_id": "user-a",
                },
                "action": "list_appointments",
                "limit": 20,
            }
        )

    assert result["success"] is True
    assert result["count"] == 1
    assert result["appointments"][0]["id"] == "appointment-org-a"
    assert result["appointments"][0]["title"] == "Tenant A appointment"
