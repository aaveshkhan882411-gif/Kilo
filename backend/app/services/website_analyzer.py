from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx
import ipaddress
from urllib.parse import urlparse
from app.config import settings


class WebsiteAnalyzer:
    BLOCKED_SCHEMES = {"file", "gopher", "ftp"}
    BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}

    def _is_safe_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
        except Exception:
            return False
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.scheme in self.BLOCKED_SCHEMES:
            return False
        hostname = (parsed.hostname or "").lower()
        if hostname in self.BLOCKED_HOSTS:
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                return False
        except ValueError:
            pass
        if any(hostname.endswith(suffix) for suffix in [".local", ".internal", ".lan"]):
            return False
        if hostname in {"metadata.google.internal", "metadata"}:
            return False
        if parsed.port and parsed.port not in {80, 443}:
            return False
        return True

    async def analyze(self, url: str) -> Dict[str, Any]:
        if not self._is_safe_url(url):
            raise ValueError("URL is not allowed for analysis")
        return {
            "url": url,
            "analyzed_at": datetime.utcnow().isoformat(),
            "business_name": None,
            "products": [],
            "services": [],
            "pricing": None,
            "locations": [],
            "contact_methods": [],
            "faqs": [],
            "ctas": [],
            "navigation": [],
            "testimonials": [],
            "structured_data": {},
            "opportunities": [],
            "bottlenecks": [],
            "raw_text_length": 0,
            "page_count": 1,
        }
