import os
import httpx
from typing import Dict
import logging

logger = logging.getLogger(__name__)


async def fetch_github() -> Dict[str, any]:
    """
    Fetch GitHub repository stats and return normalized GitHubContext.

    Reads from environment:
    - GITHUB_OWNER: repository owner (required)
    - GITHUB_REPO: repository name (required)
    - GITHUB_TOKEN: optional personal access token for higher rate limits

    Returns:
        {"open_issues": <int>, "open_prs": <int>}

    Raises:
        Exception: On HTTP error, missing env vars, or parse error.
    """
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")

    if not owner or not repo:
        raise Exception("Missing required env vars: GITHUB_OWNER, GITHUB_REPO")

    headers = {
        "Accept": "application/vnd.github.v3+json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=10) as client:
        # Fetch repo info for open issues count
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        repo_resp = await client.get(repo_url, headers=headers)

        if repo_resp.status_code != 200:
            raise Exception(
                f"GitHub API (repo) returned {repo_resp.status_code}: {repo_resp.text}"
            )

        try:
            repo_data = repo_resp.json()
            open_issues_count = repo_data.get("open_issues_count")

            if open_issues_count is None:
                raise Exception("Missing 'open_issues_count' in GitHub API response")

        except ValueError as e:
            raise Exception(f"Failed to parse GitHub repo response: {e}")

        # Fetch open PRs count
        open_prs_count = 0
        try:
            prs_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            prs_params = {"state": "open", "per_page": 1}  # Only fetch 1 to get total count from header
            prs_resp = await client.get(prs_url, headers=headers, params=prs_params)

            if prs_resp.status_code == 200:
                # GitHub returns Link header with pagination info
                link_header = prs_resp.headers.get("link", "")
                if "last" in link_header:
                    # Extract last page number from link header
                    import re
                    match = re.search(r"page=(\d+)>; rel=\"last\"", link_header)
                    if match:
                        open_prs_count = int(match.group(1))
                else:
                    # If no link header, just count the returned items (should be 0 or 1)
                    open_prs_count = len(prs_resp.json())
        except Exception as e:
            logger.warning(f"Failed to fetch GitHub PRs count: {e}")
            # Don't fail the entire request if PR count fails; default to 0

        return {
            "open_issues": open_issues_count,
            "open_prs": open_prs_count,
        }

