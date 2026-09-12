from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, AsyncIterator
from datetime import datetime


class AICompletionRequest(BaseModel):
    prompt: str
    agent_id: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = Field(1024, ge=1, le=4096)
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    stream: bool = False
    context: Optional[Dict[str, Any]] = None


class AICompletionResponse(BaseModel):
    text: str
    model: str
    tokens_used: int
    finish_reason: str
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AIStreamChunk(BaseModel):
    chunk: str
    done: bool
