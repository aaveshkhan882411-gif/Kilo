from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class AgentContract(BaseModel):
    id: str
    name: str
    version: str
    purpose: str
    capabilities: List[str]
    allowed_tools: List[str]
    required_permissions: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    context_requirements: List[str]
    memory_policy: str
    safety_policy: str
    execution_policy: str
    verification_policy: str
    failure_policy: str
    audit_policy: str


AGENT_CONTRACTS: Dict[str, AgentContract] = {
    "ai-ceo": AgentContract(
        id="ai-ceo", name="AI CEO", version="1.0.0", purpose="Strategic oversight and decision making",
        capabilities=["strategy", "analysis", "decision"], allowed_tools=["analytics", "crm", "reports"],
        required_permissions=["read_all"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["business_data", "goals"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-business-analyst": AgentContract(
        id="ai-business-analyst", name="AI Business Analyst", version="1.0.0", purpose="Business analysis and insights",
        capabilities=["analysis", "reporting"], allowed_tools=["analytics", "database"],
        required_permissions=["read_analytics"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["business_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-growth-strategist": AgentContract(
        id="ai-growth-strategist", name="AI Growth Strategist", version="1.0.0", purpose="Growth strategy development",
        capabilities=["strategy", "planning"], allowed_tools=["analytics", "crm"],
        required_permissions=["read_analytics", "read_crm"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["business_data", "goals"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-lead-intelligence": AgentContract(
        id="ai-lead-intelligence", name="AI Lead Intelligence", version="1.0.0", purpose="Lead scoring and qualification",
        capabilities=["scoring", "qualification"], allowed_tools=["crm", "leads"],
        required_permissions=["read_leads", "write_leads"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["leads_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-revenue-optimizer": AgentContract(
        id="ai-revenue-optimizer", name="AI Revenue Optimizer", version="1.0.0", purpose="Revenue optimization",
        capabilities=["optimization", "analysis"], allowed_tools=["analytics", "deals"],
        required_permissions=["read_analytics", "read_deals"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["deals_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-sales": AgentContract(
        id="ai-sales", name="AI Sales", version="1.0.0", purpose="Sales automation",
        capabilities=["sales", "communication"], allowed_tools=["crm", "email", "calendar"],
        required_permissions=["read_crm", "write_deals", "send_email"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["deals_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-receptionist": AgentContract(
        id="ai-receptionist", name="AI Receptionist", version="1.0.0", purpose="Front desk and inquiry handling",
        capabilities=["communication", "routing"], allowed_tools=["crm", "email"],
        required_permissions=["read_crm"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["crm_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-support": AgentContract(
        id="ai-support", name="AI Support", version="1.0.0", purpose="Customer support",
        capabilities=["support", "troubleshooting"], allowed_tools=["crm", "email"],
        required_permissions=["read_crm", "read_tickets"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["crm_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-followup": AgentContract(
        id="ai-followup", name="AI Follow-up", version="1.0.0", purpose="Automated follow-up",
        capabilities=["communication", "automation"], allowed_tools=["email", "crm"],
        required_permissions=["read_crm", "send_email"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["crm_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-appointment": AgentContract(
        id="ai-appointment", name="AI Appointment", version="1.0.0", purpose="Appointment scheduling",
        capabilities=["scheduling", "calendar"], allowed_tools=["calendar", "crm"],
        required_permissions=["read_crm", "write_appointments"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["calendar_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-voice": AgentContract(
        id="ai-voice", name="AI Voice", version="1.0.0", purpose="Voice interactions",
        capabilities=["voice", "stt", "tts"], allowed_tools=["voice", "crm"],
        required_permissions=["read_crm"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["crm_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-email": AgentContract(
        id="ai-email", name="AI Email", version="1.0.0", purpose="Email automation",
        capabilities=["email", "communication"], allowed_tools=["email", "crm"],
        required_permissions=["read_crm", "send_email"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["crm_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-whatsapp": AgentContract(
        id="ai-whatsapp", name="AI WhatsApp", version="1.0.0", purpose="WhatsApp messaging",
        capabilities=["whatsapp", "communication"], allowed_tools=["whatsapp", "crm"],
        required_permissions=["read_crm", "send_whatsapp"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["crm_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-crm": AgentContract(
        id="ai-crm", name="AI CRM", version="1.0.0", purpose="CRM management",
        capabilities=["crm", "data"], allowed_tools=["crm"],
        required_permissions=["read_crm", "write_crm"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["crm_data"], memory_policy="long_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-workflow": AgentContract(
        id="ai-workflow", name="AI Workflow", version="1.0.0", purpose="Workflow automation",
        capabilities=["automation", "workflow"], allowed_tools=["workflow", "crm"],
        required_permissions=["read_workflow", "write_workflow"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["workflow_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-marketing-agent": AgentContract(
        id="ai-marketing-agent", name="AI Marketing Agent", version="1.0.0", purpose="Marketing automation",
        capabilities=["marketing", "communication"], allowed_tools=["email", "crm"],
        required_permissions=["read_crm", "send_email"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["crm_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-analytics": AgentContract(
        id="ai-analytics", name="AI Analytics", version="1.0.0", purpose="Data analysis and reporting",
        capabilities=["analytics", "reporting"], allowed_tools=["analytics", "database"],
        required_permissions=["read_analytics"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["analytics_data"], memory_policy="long_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-agent-architect": AgentContract(
        id="ai-agent-architect", name="AI Agent Architect", version="1.0.0", purpose="Agent design and configuration",
        capabilities=["design", "configuration"], allowed_tools=["agents"],
        required_permissions=["read_agents", "write_agents"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["agent_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-autonomous-orchestrator": AgentContract(
        id="ai-autonomous-orchestrator", name="AI Autonomous Orchestrator", version="1.0.0", purpose="Autonomous orchestration",
        capabilities=["orchestration", "automation"], allowed_tools=["workflow", "agents", "crm"],
        required_permissions=["read_all", "write_workflows"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["all_data"], memory_policy="long_term", safety_policy="strict",
        execution_policy="parallel", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
    "ai-review-manager": AgentContract(
        id="ai-review-manager", name="AI Review Manager", version="1.0.0", purpose="Review management",
        capabilities=["reviews", "sentiment"], allowed_tools=["crm", "database"],
        required_permissions=["read_crm", "write_crm"], input_schema={"type": "object"}, output_schema={"type": "object"},
        context_requirements=["crm_data"], memory_policy="short_term", safety_policy="strict",
        execution_policy="sequential", verification_policy="manual", failure_policy="retry", audit_policy="full",
    ),
}
