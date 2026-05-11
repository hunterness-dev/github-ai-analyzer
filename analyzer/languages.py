"""
Programming language analysis.

GitHub stores the primary language of each repository as a plain string
(e.g. "Python", "JavaScript").  We aggregate these across all repos to
build a frequency/distribution table and identify the developer's
strongest technologies.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def build_language_distribution(repos: list[dict[str, Any]]) -> dict[str, int]:
    """
    Count how many repos use each language.

    Returns a dict like {"Python": 12, "JavaScript": 5, ...} sorted
    by count descending.  Repos with no detected language are skipped.
    """
    languages = [
        repo["language"]
        for repo in repos
        if repo.get("language")  # None / empty string → skip
    ]
    counts = Counter(languages)
    # Sort highest first for display convenience
    return dict(counts.most_common())


def get_top_languages(
    distribution: dict[str, int], top_n: int = 5
) -> list[tuple[str, int]]:
    """
    Return the top-N languages as a list of (language, count) tuples.

    Args:
        distribution: Output of build_language_distribution().
        top_n:        How many languages to return.
    """
    items = list(distribution.items())
    return items[:top_n]


def get_primary_language(distribution: dict[str, int]) -> str | None:
    """Return the single most-used language, or None if no data."""
    if not distribution:
        return None
    return next(iter(distribution))


def language_percentages(distribution: dict[str, int]) -> dict[str, float]:
    """
    Convert raw counts to percentages.

    Useful for pie-chart labels and the terminal dashboard.
    """
    total = sum(distribution.values())
    if total == 0:
        return {}
    return {lang: round(count / total * 100, 1) for lang, count in distribution.items()}


def identify_strongest_technologies(
    repos: list[dict[str, Any]],
    distribution: dict[str, int],
) -> list[str]:
    """
    Identify a developer's strongest technologies by combining:

    1. Language frequency across repos (breadth)
    2. Total stars in repos that use each language (community validation)

    Returns a ranked list of up to 5 technology names.
    """
    # Accumulate stars per language
    stars_per_lang: dict[str, int] = {}
    for repo in repos:
        lang = repo.get("language")
        if not lang:
            continue
        stars = repo.get("stargazers_count", 0)
        stars_per_lang[lang] = stars_per_lang.get(lang, 0) + stars

    total_repos = sum(distribution.values()) or 1
    total_stars = sum(stars_per_lang.values()) or 1

    # Score = 60 % frequency weight + 40 % star weight
    scores: dict[str, float] = {}
    for lang, count in distribution.items():
        freq_score = count / total_repos
        star_score = stars_per_lang.get(lang, 0) / total_stars
        scores[lang] = 0.6 * freq_score + 0.4 * star_score

    ranked = sorted(scores, key=scores.__getitem__, reverse=True)
    return ranked[:5]
