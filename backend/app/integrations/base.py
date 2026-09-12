from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from app.config import settings


@dataclass
class IntegrationResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseIntegration(ABC):
    provider: str = "base"

    @abstractmethod
    async def connect(self) -> IntegrationResult:
        pass

    @abstractmethod
    async def health_check(self) -> IntegrationResult:
        pass

    def is_configured(self) -> bool:
        return True
