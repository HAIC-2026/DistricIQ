"""Small bounded public-data HTTP transport. Never follows redirects or accepts arbitrary hosts."""

import asyncio
import json
import logging
import re
from urllib.parse import urlsplit

import httpx

from app.core.config import get_settings

log = logging.getLogger(__name__)
ALLOWED_HOSTS = frozenset(
    {
        "geoportal.hawaii.gov",
        "geodata.hawaii.gov",
        "files.hawaii.gov",
        "api.census.gov",
        "www.census.gov",
        "dbedt.hawaii.gov",
    }
)


class UpstreamUnavailable(Exception):
    pass


class CensusKeyRejected(UpstreamUnavailable):
    pass


def safe_url(url: str) -> str:
    p = urlsplit(url)
    if (
        p.scheme != "https"
        or p.hostname not in ALLOWED_HOSTS
        or p.port not in (None, 443)
        or p.username
        or p.password
        or p.fragment
        or len(url) > 2048
    ):
        raise ValueError("Destination is not an approved public HTTPS source")
    if re.search(r"[\\\x00-\x20]", url):
        raise ValueError("Invalid URL")
    return url


async def get_json(url: str, params: dict | None = None):
    safe_url(url)
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(20, connect=5), follow_redirects=False, trust_env=False
            ) as client:
                async with client.stream("GET", url, params=params) as r:
                    if (
                        urlsplit(url).hostname == "api.census.gov"
                        and r.status_code == 302
                        and "invalid_key" in r.headers.get("location", "")
                    ):
                        raise CensusKeyRejected(
                            "Census rejected CENSUS_API_KEY. Verify the key and activate it through the Census email link; no data was imported."
                        )
                    if r.status_code in (429, 502, 503, 504):
                        raise UpstreamUnavailable("Transient upstream error")
                    r.raise_for_status()
                    if "json" not in r.headers.get("content-type", "").lower():
                        raise UpstreamUnavailable("Upstream did not return JSON")
                    body = bytearray()
                    async for chunk in r.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > get_settings().max_response_bytes:
                            raise UpstreamUnavailable("Response exceeds size limit")
                    data = json.loads(body)
                    if isinstance(data, dict) and data.get("error"):
                        raise UpstreamUnavailable("Official service returned an error")
                    return data
        except (httpx.HTTPError, ValueError, UpstreamUnavailable) as exc:
            if isinstance(exc, CensusKeyRejected):
                raise CensusKeyRejected(str(exc)) from None
            log.warning(
                "Public source request failed: host=%s attempt=%d type=%s",
                urlsplit(url).hostname,
                attempt + 1,
                type(exc).__name__,
            )
            if attempt == 2:
                raise UpstreamUnavailable("Official source unavailable; try again later") from exc
            await asyncio.sleep(0.2 * 2**attempt)
