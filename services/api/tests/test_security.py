import httpx
import pytest
import respx

from app.core.http import UpstreamUnavailable, get_json, safe_url


@pytest.mark.parametrize(
    "url",
    [
        "http://geodata.hawaii.gov/x",
        "https://127.0.0.1/x",
        "https://169.254.169.254/",
        "https://geodata.hawaii.gov.evil.test/",
        "https://user:pass@geodata.hawaii.gov/",
        "https://geodata.hawaii.gov:8080/",
        "https://geodata.hawaii.gov/\nfoo",
        "https://geodata.hawaii.gov/foo#x",
    ],
)
def test_unapproved_destinations_rejected(url):
    with pytest.raises(ValueError):
        safe_url(url)


@respx.mock
async def test_redirect_not_followed():
    route = respx.get("https://geodata.hawaii.gov/test").mock(
        return_value=httpx.Response(302, headers={"Location": "http://127.0.0.1/private"})
    )
    with pytest.raises(UpstreamUnavailable):
        await get_json("https://geodata.hawaii.gov/test")
    assert route.call_count == 3
    assert len(respx.calls) == 3


@respx.mock
async def test_size_limit(monkeypatch):
    import app.core.http as module
    from app.core.config import Settings

    monkeypatch.setattr(module, "get_settings", lambda: Settings(max_response_bytes=10))
    respx.get("https://geodata.hawaii.gov/test").mock(
        return_value=httpx.Response(200, json={"data": "long" * 20})
    )
    with pytest.raises(UpstreamUnavailable):
        await get_json("https://geodata.hawaii.gov/test")


@respx.mock
async def test_retries_transient_errors():
    route = respx.get("https://geodata.hawaii.gov/test").mock(
        side_effect=[httpx.Response(503), httpx.Response(200, json={"ok": True})]
    )
    assert await get_json("https://geodata.hawaii.gov/test") == {"ok": True}
    assert route.call_count == 2
