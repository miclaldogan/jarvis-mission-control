import os
import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def _headers(token: Optional[str]) -> Dict[str, str]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _search_total_count(
    client: httpx.AsyncClient, headers: Dict[str, str], q: str
) -> int:
    """
    Use GitHub Search API to get accurate counts for issues and PRs.
    """
    url = f"{GITHUB_API}/search/issues"
    resp = await client.get(url, headers=headers, params={"q": q})

    if resp.status_code != 200:
        raise Exception(f"GitHub search returned {resp.status_code}: {resp.text}")

    data = resp.json()
    if "total_count" not in data:
        raise Exception("Missing 'total_count' in GitHub search response")

    return int(data["total_count"])


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

    # NOTE:
    # GitHub's open_issues_count includes PRs.
    # We use Search API for accurate separation.
    q_issues = f"repo:{repo_full} type:issue state:open"
    q_prs = f"repo:{repo_full} type:pr state:open"

    async with httpx.AsyncClient(timeout=10) as client:
        open_issues = await _search_total_count(client, headers, q_issues)
        open_prs = await _search_total_count(client, headers, q_prs)

    return {
        "open_issues": open_issues,
        "open_prs": open_prs,
    }
