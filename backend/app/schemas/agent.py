from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


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


class AgentTask(BaseModel):
    task_id: str
    agent_id: str
    org_id: str
    input: Dict[str, Any]
    context: Dict[str, Any]
    permissions: List[str]
    authorization_required: bool = False


class AgentResult(BaseModel):
    task_id: str
    agent_id: str
    status: str
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    outcome_id: Optional[str] = None


class AgentStatus(BaseModel):
    agent_id: str
    name: str
    status: str
    last_executed: Optional[datetime] = None
    success_rate: Optional[float] = None
