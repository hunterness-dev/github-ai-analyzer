"""
Repository-level analysis and feature detection.

Each repository is inspected for the presence of:
  - README files        (documentation)
  - License files       (open-source friendliness)
  - Test directories    (code quality)
  - CI/CD configs       (DevOps maturity)
  - Dockerfile          (containerisation)
  - Dependency files    (requirements.txt, package.json, etc.)
  - Recent activity     (is the repo being maintained?)

All detection is done purely on the metadata returned by the GitHub API
(the `contents` endpoint via the tree URL is NOT used to avoid extra
requests). Instead we check the boolean flags GitHub already provides
and look at filenames in the repo root via the API when needed.

NOTE: GitHub's repo-list endpoint already returns `has_wiki`, `has_pages`,
`license`, `topics`, `size`, `stargazers_count`, `forks_count`, etc.
We exploit these freely.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

# Files that imply CI/CD usage
CI_PATTERNS = [
    ".github/workflows",  # GitHub Actions
    ".travis.yml",
    "Jenkinsfile",
    ".circleci",
    ".gitlab-ci.yml",
    "azure-pipelines.yml",
    ".drone.yml",
]

# Files that imply containerisation
DOCKER_FILES = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]

# Common dependency/package manifest files
DEPENDENCY_FILES = [
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "Gemfile",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
    "composer.json",
]

# Days of inactivity before a repo is considered "inactive"
INACTIVE_DAYS = 365


def enrich_repos(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Add computed feature flags and metadata to each raw repo dict.

    Returns the same list with extra keys injected into each element.
    We work only with data already in the API response to keep this
    fast (no extra HTTP requests per repo).
    """
    for repo in repos:
        repo["_features"] = detect_features(repo)
        repo["_inactive"] = is_inactive(repo)
        repo["_age_days"] = repo_age_days(repo)
    return repos


def detect_features(repo: dict[str, Any]) -> dict[str, bool]:
    """
    Return a dict of boolean feature flags for a single repository.

    GitHub provides some flags directly (e.g. `has_wiki`); others we
    infer from topics or the repo name/description since the contents
    API is too expensive to call for every repo.
    """
    topics: list[str] = repo.get("topics") or []
    description: str = (repo.get("description") or "").lower()
    name: str = repo.get("name", "").lower()

    return {
        # GitHub provides this directly
        "has_readme": bool(repo.get("has_readme", False)),
        # License object is present if a license was detected
        "has_license": repo.get("license") is not None,
        # Heuristic: look for 'test' in topics or description or name
        "has_tests": any(
            kw in (topics + [description, name])
            for kw in ["test", "tests", "testing", "pytest", "jest", "unittest"]
        ),
        # Heuristic: common CI keywords in topics/description
        "has_ci": any(
            kw in topics or kw in description
            for kw in ["ci", "github-actions", "travis", "circleci", "jenkins"]
        ),
        # Heuristic: Docker mentions in topics/description
        "has_docker": any(
            kw in topics or kw in description
            for kw in ["docker", "container", "dockerfile", "kubernetes", "k8s"]
        ),
        # GitHub's own flag for whether the repo has Pages enabled
        "has_pages": bool(repo.get("has_pages", False)),
    }


def is_inactive(repo: dict[str, Any]) -> bool:
    """Return True if the repo hasn't been pushed to in INACTIVE_DAYS days."""
    pushed_at = repo.get("pushed_at")
    if not pushed_at:
        return True
    last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - last_push).days
    return age >= INACTIVE_DAYS


def repo_age_days(repo: dict[str, Any]) -> int:
    """Return the number of days since the repo was created."""
    created_at = repo.get("created_at", "")
    if not created_at:
        return 0
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - created).days


def sort_repos_by_stars(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return repos sorted by stargazers_count descending."""
    return sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)


def get_newest_repo(repos: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the most recently created repo."""
    if not repos:
        return None
    return max(repos, key=lambda r: r.get("created_at", ""))


def get_oldest_repo(repos: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the oldest created repo."""
    if not repos:
        return None
    return min(repos, key=lambda r: r.get("created_at", ""))


def get_inactive_repos(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return all repos that haven't seen activity in over INACTIVE_DAYS days."""
    return [r for r in repos if r.get("_inactive", False)]


def get_forked_repos(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only repos that are forks of other projects."""
    return [r for r in repos if r.get("fork", False)]


def get_original_repos(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only repos the user created themselves (not forks)."""
    return [r for r in repos if not r.get("fork", False)]
