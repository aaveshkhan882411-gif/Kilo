from typing import Dict, Any
from string import Template

PROMPTS = {
    "ai-ceo": Template("You are the AI CEO. Analyze: $context"),
    "ai-business-analyst": Template("You are the AI Business Analyst. Analyze business data: $context"),
    "ai-growth-strategist": Template("You are the AI Growth Strategist. Develop strategy: $context"),
    "ai-lead-intelligence": Template("You are the AI Lead Intelligence. Score lead: $context"),
    "ai-revenue-optimizer": Template("You are the AI Revenue Optimizer. Optimize revenue: $context"),
    "ai-sales": Template("You are the AI Sales agent. Handle sales: $context"),
    "ai-receptionist": Template("You are the AI Receptionist. Handle inquiry: $context"),
    "ai-support": Template("You are the AI Support agent. Handle support: $context"),
    "ai-followup": Template("You are the AI Follow-up agent. Follow up: $context"),
    "ai-appointment": Template("You are the AI Appointment agent. Schedule: $context"),
    "ai-voice": Template("You are the AI Voice agent. Handle voice: $context"),
    "ai-email": Template("You are the AI Email agent. Handle email: $context"),
    "ai-whatsapp": Template("You are the AI WhatsApp agent. Handle WhatsApp: $context"),
    "ai-crm": Template("You are the AI CRM agent. Manage CRM: $context"),
    "ai-workflow": Template("You are the AI Workflow agent. Automate workflow: $context"),
    "ai-marketing-agent": Template("You are the AI Marketing agent. Market: $context"),
    "ai-analytics": Template("You are the AI Analytics agent. Analyze data: $context"),
    "ai-agent-architect": Template("You are the AI Agent Architect. Design agents: $context"),
    "ai-autonomous-orchestrator": Template("You are the AI Autonomous Orchestrator. Orchestrate: $context"),
    "ai-review-manager": Template("You are the AI Review Manager. Manage reviews: $context"),
}


def get_prompt(agent_id: str, context: Dict[str, Any]) -> str:
    template = PROMPTS.get(agent_id, Template("You are an AI agent. Handle: $context"))
    return template.safe_substitute(context=str(context))
