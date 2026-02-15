"""Fetch website content and related resources for analysis."""

import requests
from urllib.parse import urljoin, urlparse


DEFAULT_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (compatible; AISearchAnalyzer/1.0; "
    "+https://github.com/ai-search-analyzer)"
)


def fetch_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> requests.Response | None:
    """Fetch a URL and return the response, or None on failure."""
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
        )
        resp.raise_for_status()
        return resp
    except requests.RequestException:
        return None


def fetch_page(url: str) -> dict:
    """Fetch the main page and return parsed content bundle."""
    resp = fetch_url(url)
    if resp is None:
        return {"ok": False, "error": f"Failed to fetch {url}"}

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    result = {
        "ok": True,
        "url": url,
        "final_url": resp.url,
        "base_url": base_url,
        "status_code": resp.status_code,
        "headers": dict(resp.headers),
        "html": resp.text,
    }

    # Fetch robots.txt
    robots_resp = fetch_url(urljoin(base_url, "/robots.txt"), timeout=10)
    result["robots_txt"] = robots_resp.text if robots_resp else None

    # Fetch sitemap.xml
    sitemap_resp = fetch_url(urljoin(base_url, "/sitemap.xml"), timeout=10)
    result["sitemap_xml"] = sitemap_resp.text if sitemap_resp else None

    # Fetch llms.txt (emerging standard for LLM-friendly content)
    llms_resp = fetch_url(urljoin(base_url, "/llms.txt"), timeout=10)
    result["llms_txt"] = llms_resp.text if llms_resp else None

    return result
