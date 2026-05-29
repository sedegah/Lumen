import time
from dataclasses import dataclass, field
from typing import Optional

import requests


# Mimic a real browser to avoid bot-blocking
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

DEFAULT_TIMEOUT = 15  # seconds


@dataclass
class FetchResult:
    """Result of an HTTP fetch operation."""

    url: str
    final_url: str = ""
    status_code: int = 0
    html: str = ""
    load_time: float = 0.0
    error: Optional[str] = None
    headers: dict = field(default_factory=dict)
    ok: bool = False


def normalize_url(url: str) -> str:
    """Ensure the URL has a scheme prefix."""
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def fetch_page(url: str, timeout: int = DEFAULT_TIMEOUT) -> FetchResult:
    """
    Fetch a web page and return the result with metadata.

    Args:
        url: The URL to fetch (will be normalized if no scheme).
        timeout: Request timeout in seconds.

    Returns:
        FetchResult with HTML content, status, timing, and error info.
    """
    url = normalize_url(url)
    if not url:
        return FetchResult(url="", error="Empty URL provided.")

    result = FetchResult(url=url)

    try:
        start = time.perf_counter()
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )
        elapsed = time.perf_counter() - start

        result.final_url = response.url
        result.status_code = response.status_code
        result.load_time = round(elapsed, 2)
        result.headers = dict(response.headers)

        # Force UTF-8 if encoding detection fails
        response.encoding = response.apparent_encoding or "utf-8"
        result.html = response.text
        result.ok = response.ok

        if not response.ok:
            result.error = f"HTTP {response.status_code}: {response.reason}"

    except requests.exceptions.ConnectionError:
        result.error = f"Connection failed: Could not reach {url}"
    except requests.exceptions.Timeout:
        result.error = f"Timeout: Server did not respond within {timeout}s"
    except requests.exceptions.TooManyRedirects:
        result.error = "Too many redirects. The URL may be misconfigured."
    except requests.exceptions.MissingSchema:
        result.error = f"Invalid URL format: {url}"
    except requests.exceptions.RequestException as e:
        result.error = f"Request failed: {e}"

    return result
