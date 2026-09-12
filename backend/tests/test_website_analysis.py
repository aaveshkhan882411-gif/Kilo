import pytest
from app.services.website_analyzer import WebsiteAnalyzer


@pytest.mark.asyncio
async def test_domain_validation():
    analyzer = WebsiteAnalyzer()
    assert analyzer._is_safe_url("https://example.com") is True
    assert analyzer._is_safe_url("http://example.com") is True


@pytest.mark.asyncio
async def test_crawl_policy_check():
    analyzer = WebsiteAnalyzer()
    assert analyzer._is_safe_url("https://example.com/robots.txt") is True


@pytest.mark.asyncio
async def test_public_page_discovery():
    analyzer = WebsiteAnalyzer()
    result = await analyzer.analyze("https://example.com")
    assert result["url"] == "https://example.com"
    assert "page_count" in result
