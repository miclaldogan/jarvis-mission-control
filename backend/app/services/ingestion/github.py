import asyncio
import logging
import os
import re
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

import httpx

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def _headers(token: Optional[str]) -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        # GitHub API guidance: always send a User-Agent.
        "User-Agent": "jarvis-mission-control",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _parse_last_page_from_link(link_header: str) -> Optional[int]:
    """Parse GitHub REST pagination Link header for rel="last".

    We request pulls with per_page=1 so the last page number equals the total count.
    """

    if not link_header:
        return None

    for part in link_header.split(","):
        if 'rel="last"' not in part:
            continue
        match = re.search(r"<([^>]+)>", part)
        if not match:
            return None
        url = match.group(1)
        page = parse_qs(urlparse(url).query).get("page", [None])[0]
        try:
            return int(page) if page is not None else None
        except Exception:
            return None

    return None


async def _get_with_retries(
    client: httpx.AsyncClient,
    url: str,
    *,
    headers: Dict[str, str],
    params: Optional[Dict[str, Any]] = None,
    max_attempts: int = 3,
) -> httpx.Response:
    last_exc: Optional[BaseException] = None

    for attempt in range(1, max_attempts + 1):
        try:
            resp = await client.get(url, headers=headers, params=params)
        except httpx.RequestError as exc:
            last_exc = exc
            if attempt >= max_attempts:
                raise
            await asyncio.sleep(0.4 * attempt)
            continue

        if resp.status_code in (502, 503, 504, 429):
            if attempt >= max_attempts:
                resp.raise_for_status()
            await asyncio.sleep(0.4 * attempt)
            continue

        # Some 403s are temporary (secondary rate limits) and may include Retry-After.
        if resp.status_code == 403 and resp.headers.get("Retry-After"):
            if attempt >= max_attempts:
                resp.raise_for_status()
            try:
                wait_s = float(resp.headers.get("Retry-After") or "0")
            except Exception:
                wait_s = 0
            await asyncio.sleep(max(0.4 * attempt, min(wait_s, 5.0)))
            continue

        if resp.status_code >= 400:
            # Raise with response context; caller will mark source failed.
            raise Exception(f"GitHub API returned {resp.status_code}: {resp.text}")

        return resp

    # Should be unreachable.
    if last_exc:
        raise last_exc
    raise Exception("GitHub API request failed")


async def fetch_github() -> Dict[str, Any]:
    """
    Fetch GitHub repository stats and return normalized GitHubContext.

    Env vars:
    - GITHUB_OWNER (required)
    - GITHUB_REPO (required)
    - GITHUB_TOKEN (optional; increases rate limit)

    Returns:
        {"open_issues": <int>, "open_prs": <int>}
    """
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")

    if not owner or not repo:
        raise Exception("Missing required env vars: GITHUB_OWNER, GITHUB_REPO")

    headers = _headers(token)
    repo_full = f"{owner}/{repo}"

    repo_url = f"{GITHUB_API}/repos/{repo_full}"
    pulls_url = f"{GITHUB_API}/repos/{repo_full}/pulls"

    # We avoid GitHub Search API because it's more prone to secondary rate limiting
    # and intermittent failures in classroom/demo environments.
    timeout = httpx.Timeout(10.0, connect=5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        repo_resp = await _get_with_retries(client, repo_url, headers=headers)
        repo_data = repo_resp.json()
        if "open_issues_count" not in repo_data:
            raise Exception("Missing 'open_issues_count' in GitHub repo response")

        open_issues_count = int(repo_data["open_issues_count"])

        pulls_resp = await _get_with_retries(
            client,
            pulls_url,
            headers=headers,
            params={"state": "open", "per_page": 1, "page": 1},
        )
        last_page = _parse_last_page_from_link(pulls_resp.headers.get("Link", ""))
        if last_page is not None:
            open_prs = last_page
        else:
            # With per_page=1, body is [] or [..] for 0/1 PR.
            body = pulls_resp.json()
            open_prs = len(body) if isinstance(body, list) else 0

        # open_issues_count includes PRs; derive issues-only count.
        open_issues = max(open_issues_count - open_prs, 0)

    return {
        "open_issues": open_issues,
        "open_prs": open_prs,
    }
