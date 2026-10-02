

def test_send_whatsapp_task_uses_real_integration(monkeypatch):
    from app.workers.tasks import send_whatsapp_task
    from app.integrations.base import IntegrationResult

    calls = {}

    async def fake_send_message(self, to, message):
        calls["to"] = to
        calls["message"] = message

        return IntegrationResult(
            success=True,
            data={"message_id": "wamid.worker-test"},
        )

    monkeypatch.setattr(
        "app.integrations.whatsapp.WhatsAppIntegration.send_message",
        fake_send_message,
    )

    result = send_whatsapp_task.run(
        "+1234567890",
        "Hello from worker",
    )

    assert result == {
        "success": True,
        "data": {
            "message_id": "wamid.worker-test",
        },
        "error": None,
    }

    assert calls == {
        "to": "+1234567890",
        "message": "Hello from worker",
    }
