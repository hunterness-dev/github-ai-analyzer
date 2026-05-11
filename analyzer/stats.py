"""
Aggregate statistics computed from a user's repos.

All functions are pure (no network calls) and operate on the list of
repo dicts already enriched by analyzer.repos.enrich_repos().
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from analyzer.repos import get_newest_repo, get_oldest_repo, get_original_repos


def compute_stats(
    user: dict[str, Any],
    repos: list[dict[str, Any]],
    language_distribution: dict[str, int],
) -> dict[str, Any]:
    """
    Build the master statistics dictionary for a GitHub user.

    Args:
        user:                  Raw GitHub user profile dict.
        repos:                 Enriched list of repo dicts.
        language_distribution: {language: repo_count} mapping.

    Returns:
        A flat dict of computed metrics.
    """
    original = get_original_repos(repos)  # exclude forks for most metrics
    total_repos = len(repos)
    original_repos = len(original)
    forked_repos = total_repos - original_repos

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    total_watchers = sum(r.get("watchers_count", 0) for r in repos)
    total_open_issues = sum(r.get("open_issues_count", 0) for r in repos)

    sizes = [r.get("size", 0) for r in repos if r.get("size", 0) > 0]
    avg_size_kb = round(sum(sizes) / len(sizes), 1) if sizes else 0

    most_starred = max(repos, key=lambda r: r.get("stargazers_count", 0), default=None)
    most_forked = max(repos, key=lambda r: r.get("forks_count", 0), default=None)

    newest = get_newest_repo(repos)
    oldest = get_oldest_repo(repos)

    primary_language = next(iter(language_distribution), None) if language_distribution else None

    activity_score = _compute_activity_score(repos)

    return {
        # Counts
        "total_repos": total_repos,
        "original_repos": original_repos,
        "forked_repos": forked_repos,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "total_watchers": total_watchers,
        "total_open_issues": total_open_issues,
        # Size
        "avg_size_kb": avg_size_kb,
        # Notable repos
        "most_starred_repo": most_starred,
        "most_forked_repo": most_forked,
        "newest_repo": newest,
        "oldest_repo": oldest,
        # Languages
        "primary_language": primary_language,
        "language_count": len(language_distribution),
        # Activity
        "activity_score": activity_score,
        # Profile metadata
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "account_age_days": _account_age_days(user),
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _compute_activity_score(repos: list[dict[str, Any]]) -> float:
    """
    Compute an activity score (0–100) based on recent pushes.

    Scoring logic:
      - Each repo pushed within the last 30 days  → +20 pts (capped at 100)
      - Each repo pushed within the last 90 days  → +10 pts
      - Each repo pushed within the last 365 days → +3 pts
      - No recent activity at all                 → 0 pts

    The score is clamped to [0, 100].
    """
    now = datetime.now(timezone.utc)
    score = 0.0

    for repo in repos:
        pushed_at = repo.get("pushed_at")
        if not pushed_at:
            continue
        last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        days_ago = (now - last_push).days

        if days_ago <= 30:
            score += 20
        elif days_ago <= 90:
            score += 10
        elif days_ago <= 365:
            score += 3

    return min(round(score, 1), 100.0)


def _account_age_days(user: dict[str, Any]) -> int:
    """Return how many days ago the GitHub account was created."""
    created_at = user.get("created_at", "")
    if not created_at:
        return 0
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - created).days
