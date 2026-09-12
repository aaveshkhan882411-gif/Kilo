import pytest
from app.services.website_analyzer import WebsiteAnalyzer


@pytest.mark.asyncio
async def test_ssrf_blocks_localhost():
    analyzer = WebsiteAnalyzer()
    with pytest.raises(ValueError):
        await analyzer.analyze("http://localhost:8000/admin")


@pytest.mark.asyncio
async def test_ssrf_blocks_private_ips():
    analyzer = WebsiteAnalyzer()
    with pytest.raises(ValueError):
        await analyzer.analyze("http://192.168.1.1/secret")
    with pytest.raises(ValueError):
        await analyzer.analyze("http://10.0.0.1/secret")
    with pytest.raises(ValueError):
        await analyzer.analyze("http://172.16.0.1/secret")


@pytest.mark.asyncio
async def test_ssrf_blocks_internal_endpoints():
    analyzer = WebsiteAnalyzer()
    with pytest.raises(ValueError):
        await analyzer.analyze("http://metadata.google.internal/")
    with pytest.raises(ValueError):
        await analyzer.analyze("http://169.254.169.254/latest/meta-data/")


@pytest.mark.asyncio
async def test_ssrf_blocks_file_scheme():
    analyzer = WebsiteAnalyzer()
    with pytest.raises(ValueError):
        await analyzer.analyze("file:///etc/passwd")


@pytest.mark.asyncio
async def test_public_url_accepted():
    analyzer = WebsiteAnalyzer()
    result = await analyzer.analyze("https://example.com")
    assert result["url"] == "https://example.com"
    assert "analyzed_at" in result
