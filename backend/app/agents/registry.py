from typing import List, Dict, Any
from typing import Optional
from app.agents.base import BaseAgent
from app.agents.contracts import AGENT_CONTRACTS, AgentContract
from app.agents.gip import gip_bus, GIPEvent


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        return self._agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        return [{"id": k, "name": v.name} for k, v in self._agents.items()]

    def get_contract(self, agent_id: str) -> Optional[AgentContract]:
        return AGENT_CONTRACTS.get(agent_id)


registry = AgentRegistry()
