from typing import Dict, Any
from app.agents.base import BaseAgent
from app.agents.contracts import AgentContract
from app.agents.registry import registry
from app.agents.gip import gip_bus


class CEOAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-ceo", "AI CEO")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        gip_bus.publish("TASK_STARTED", self.agent_id, task.get("task_id"), {})
        result = await super().execute(task)
        gip_bus.publish("ACTION_COMPLETED", self.agent_id, task.get("task_id"), result)
        return result


class BusinessAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-business-analyst", "AI Business Analyst")


class GrowthStrategistAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-growth-strategist", "AI Growth Strategist")


class LeadIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-lead-intelligence", "AI Lead Intelligence")


class RevenueOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-revenue-optimizer", "AI Revenue Optimizer")


class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-sales", "AI Sales")


class ReceptionistAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-receptionist", "AI Receptionist")


class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-support", "AI Support")


class FollowupAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-followup", "AI Follow-up")


class AppointmentAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-appointment", "AI Appointment")


class VoiceAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-voice", "AI Voice")


class EmailAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-email", "AI Email")


class WhatsAppAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-whatsapp", "AI WhatsApp")


class CRMAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-crm", "AI CRM")


class WorkflowAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-workflow", "AI Workflow")


class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-marketing-agent", "AI Marketing Agent")


class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-analytics", "AI Analytics")


class AgentArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-agent-architect", "AI Agent Architect")


class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-autonomous-orchestrator", "AI Autonomous Orchestrator")


class ReviewManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai-review-manager", "AI Review Manager")


def register_all_agents():
    agents = [
        CEOAgent(), BusinessAnalystAgent(), GrowthStrategistAgent(), LeadIntelligenceAgent(),
        RevenueOptimizerAgent(), SalesAgent(), ReceptionistAgent(), SupportAgent(),
        FollowupAgent(), AppointmentAgent(), VoiceAgent(), EmailAgent(),
        WhatsAppAgent(), CRMAgent(), WorkflowAgent(), MarketingAgent(),
        AnalyticsAgent(), AgentArchitectAgent(), OrchestratorAgent(), ReviewManagerAgent(),
    ]
    for agent in agents:
        registry.register(agent)


register_all_agents()
