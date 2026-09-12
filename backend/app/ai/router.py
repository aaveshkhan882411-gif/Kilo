from app.ai.gateway import ai_gateway
from app.config import settings


class ModelRouter:
    @staticmethod
    async def complete(prompt: str, agent_id: Optional[str] = None, model: Optional[str] = None, max_tokens: int = 1024, temperature: float = 0.7, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if agent_id:
            from app.ai.prompts import get_prompt
            prompt = get_prompt(agent_id, context or {})
        return await ai_gateway.generate(prompt, model, max_tokens, temperature, context)
