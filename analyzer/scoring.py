"""
Developer scoring system.

Produces four independent scores (each 0–100) and a human-readable
classification: Beginner / Intermediate / Advanced.

Score dimensions
----------------
1. Documentation Score
   Rewards READMEs, licenses, descriptions, and GitHub Pages.

2. Consistency Score
   Rewards regular repo creation / updates over time.

3. Project Complexity Score
   Rewards large repos, many languages, issues, and CI/CD usage.

4. Overall Score
   Weighted average of the three dimensions above plus activity.
"""

from __future__ import annotations

import math
from typing import Any

from analyzer.repos import get_original_repos


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_scores(
    repos: list[dict[str, Any]],
    stats: dict[str, Any],
    language_distribution: dict[str, int],
) -> dict[str, Any]:
    """
    Calculate all scores and developer classification.

    Args:
        repos:                 Enriched repo list.
        stats:                 Output of stats.compute_stats().
        language_distribution: {language: count} mapping.

    Returns:
        Dict with individual scores, overall score, and level.
    """
    docs_score = _documentation_score(repos)
    consistency_score = _consistency_score(repos, stats)
    complexity_score = _complexity_score(repos, stats, language_distribution)

    # Weighted overall: documentation matters most for a public portfolio
    overall = round(
        docs_score * 0.30
        + consistency_score * 0.25
        + complexity_score * 0.25
        + min(stats.get("activity_score", 0), 100) * 0.20,
        1,
    )

    level = _classify_level(overall, stats)

    return {
        "documentation_score": docs_score,
        "consistency_score": consistency_score,
        "complexity_score": complexity_score,
        "overall_score": overall,
        "level": level,
    }


def _classify_level(overall: float, stats: dict[str, Any]) -> str:
    """
    Map an overall score + repo count to a developer level label.

    Thresholds (arbitrary but reasonable):
      Advanced     → score ≥ 65 AND original repos ≥ 15
      Intermediate → score ≥ 35 OR original repos ≥ 5
      Beginner     → everything else
    """
    original = stats.get("original_repos", 0)

    if overall >= 65 and original >= 15:
        return "Advanced"
    if overall >= 35 or original >= 5:
        return "Intermediate"
    return "Beginner"


# ---------------------------------------------------------------------------
# Individual score calculators
# ---------------------------------------------------------------------------

def _documentation_score(repos: list[dict[str, Any]]) -> float:
    """
    Score based on how well repos are documented.

    Criteria (per original repo):
      - Has README          → +2 pts
      - Has description     → +1 pt
      - Has license         → +2 pts
      - Has GitHub Pages    → +1 pt
      - Has topics/tags     → +1 pt

    Max raw score = 7 per repo.  Normalised to 0–100.
    """
    originals = get_original_repos(repos)
    if not originals:
        return 0.0

    total = 0
    for repo in originals:
        features = repo.get("_features", {})
        total += 2 if features.get("has_readme") else 0
        total += 1 if repo.get("description") else 0
        total += 2 if features.get("has_license") else 0
        total += 1 if features.get("has_pages") else 0
        total += 1 if repo.get("topics") else 0

    max_possible = len(originals) * 7
    return round(total / max_possible * 100, 1)


def _consistency_score(repos: list[dict[str, Any]], stats: dict[str, Any]) -> float:
    """
    Score based on sustained activity over the account lifetime.

    We compute repos-per-year.  Anything above 10 repos/year
    earns a full score; we scale linearly below that.
    """
    age_days = stats.get("account_age_days", 1)
    if age_days < 1:
        age_days = 1

    total_repos = stats.get("total_repos", 0)
    repos_per_year = total_repos / (age_days / 365)

    # Cap at 10 repos/year for a full score
    raw = min(repos_per_year / 10, 1.0)
    score = round(raw * 100, 1)

    # Bonus: subtract points if most repos are inactive
    inactive_count = sum(1 for r in repos if r.get("_inactive", False))
    if total_repos > 0:
        inactive_ratio = inactive_count / total_repos
        score = max(0.0, score - inactive_ratio * 20)

    return min(round(score, 1), 100.0)


def _complexity_score(
    repos: list[dict[str, Any]],
    stats: dict[str, Any],
    language_distribution: dict[str, int],
) -> float:
    """
    Score based on the sophistication and diversity of projects.

    Sub-metrics (each normalised to 0–1):
      1. Language diversity  → more langs = higher score (cap 10)
      2. Average repo size   → bigger is more complex (cap 5 000 KB)
      3. Total stars         → community recognition (cap 500)
      4. Open issues         → active projects attract issues (cap 200)
      5. CI/Docker usage     → advanced tooling (% of repos)
    """
    lang_score = min(len(language_distribution) / 10, 1.0)

    avg_size = stats.get("avg_size_kb", 0)
    size_score = min(avg_size / 5000, 1.0)

    total_stars = stats.get("total_stars", 0)
    star_score = min(total_stars / 500, 1.0)

    open_issues = stats.get("total_open_issues", 0)
    issues_score = min(open_issues / 200, 1.0)

    originals = get_original_repos(repos)
    if originals:
        ci_ratio = sum(
            1 for r in originals if r.get("_features", {}).get("has_ci")
        ) / len(originals)
        docker_ratio = sum(
            1 for r in originals if r.get("_features", {}).get("has_docker")
        ) / len(originals)
        tooling_score = (ci_ratio + docker_ratio) / 2
    else:
        tooling_score = 0.0

    combined = (
        lang_score * 0.25
        + size_score * 0.20
        + star_score * 0.30
        + issues_score * 0.10
        + tooling_score * 0.15
    )
    return round(combined * 100, 1)
