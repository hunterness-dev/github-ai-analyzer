"""
GitHub REST API client.

Handles authentication, rate limiting, pagination, and all HTTP requests
to the GitHub API. This is the only file that talks directly to GitHub.
"""

import time
import requests
from typing import Any, Optional
from rich.console import Console

console = Console()

BASE_URL = "https://api.github.com"


class GitHubClient:
    """
    A thin wrapper around the GitHub REST API.

    Handles:
    - Optional token-based authentication (higher rate limits)
    - Automatic rate-limit detection and waiting
    - Transparent pagination (fetches ALL pages automatically)
    - Clean error messages for common problems
    """

    def __init__(self, token: Optional[str] = None) -> None:
        """
        Args:
            token: Optional GitHub personal access token.
                   Without a token you get 60 req/hr; with one you get 5,000.
        """
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_user(self, username: str) -> dict[str, Any]:
        """Fetch a user's public profile."""
        return self._get(f"/users/{username}")

    def get_repos(self, username: str) -> list[dict[str, Any]]:
        """Fetch ALL public repositories for a user (handles pagination)."""
        return self._get_paginated(f"/users/{username}/repos", params={"per_page": 100})

    def get_rate_limit(self) -> dict[str, Any]:
        """Check remaining API requests."""
        return self._get("/rate_limit")

    # ------------------------------------------------------------------
    # Internal request machinery
    # ------------------------------------------------------------------

    def _get(self, path: str, params: Optional[dict] = None) -> Any:
        """Make a single GET request and return the parsed JSON body."""
        url = BASE_URL + path
        response = self._request_with_retry(url, params=params)
        return response.json()

    def _get_paginated(self, path: str, params: Optional[dict] = None) -> list[Any]:
        """
        Follow GitHub's Link: <next> headers to collect every page.

        GitHub returns at most 100 items per page; a developer with
        hundreds of repos requires multiple requests.
        """
        params = params or {}
        url = BASE_URL + path
        results: list[Any] = []

        while url:
            response = self._request_with_retry(url, params=params)
            results.extend(response.json())

            # Parse the 'next' URL from the Link header (if present)
            url = self._next_page_url(response.headers.get("Link", ""))
            params = {}  # next URL already contains query params

        return results

    def _request_with_retry(self, url: str, params: Optional[dict] = None) -> requests.Response:
        """
        Send a GET request, automatically waiting if rate-limited.

        GitHub returns HTTP 403 or 429 with a `X-RateLimit-Reset` header
        (a Unix timestamp) when you've used up your quota.
        """
        while True:
            response = self.session.get(url, params=params, timeout=15)

            # Rate limit hit — wait until the window resets
            if response.status_code in (403, 429):
                reset_at = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(reset_at - time.time(), 1)
                console.print(f"[yellow]Rate limited. Waiting {wait:.0f}s …[/yellow]")
                time.sleep(wait)
                continue  # retry the same request

            # User not found
            if response.status_code == 404:
                raise ValueError(f"GitHub user/resource not found: {url}")

            # Any other non-2xx response
            if not response.ok:
                raise RuntimeError(
                    f"GitHub API error {response.status_code}: {response.text[:200]}"
                )

            return response

    @staticmethod
    def _next_page_url(link_header: str) -> Optional[str]:
        """
        Parse GitHub's Link header to extract the 'next' URL.

        Example header:
          <https://api.github.com/...?page=2>; rel="next", <...>; rel="last"
        """
        if not link_header:
            return None
        for part in link_header.split(","):
            if 'rel="next"' in part:
                # Extract URL from angle brackets
                return part.split(";")[0].strip().strip("<>")
        return None
