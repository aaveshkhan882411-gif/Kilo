from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, to: str, subject: str, body: str):
    from app.services.notification_service import NotificationService
    import asyncio
    return asyncio.run(NotificationService.send_email(to, subject, body))


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_whatsapp_task(self, to: str, message: str):
    return {"status": "sent"}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_lead_task(self, lead_id: str):
    return {"lead_id": lead_id, "status": "processed"}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_appointment_task(self, appointment_id: str):
    return {"appointment_id": appointment_id, "status": "processed"}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_agent_task(self, agent_id: str, task: dict):
    return {"agent_id": agent_id, "status": "executed"}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_workflow_task(self, workflow_id: str, org_id: str):
    from app.services.workflow_execution_service import WorkflowExecutionService
    import asyncio

    if not isinstance(workflow_id, str) or not workflow_id.strip():
        return {
            "success": False,
            "status": "invalid_parameters",
            "workflow_id": workflow_id,
        }

    if not isinstance(org_id, str) or not org_id.strip():
        return {
            "success": False,
            "status": "invalid_execution_context",
            "workflow_id": workflow_id,
        }

    return asyncio.run(
        WorkflowExecutionService.execute(
            workflow_id=workflow_id.strip(),
            context={"org_id": org_id.strip()},
        )
    )


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_analytics_task(self, org_id: str):
    return {"org_id": org_id, "status": "generated"}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_old_data_task(self):
    return {"status": "cleaned"}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def health_check_task(self):
    return {"status": "healthy"}
