"""
Unit tests for the GitHub Profile Analyzer.

Run with:
    pytest tests/ -v

No network calls are made — all data is mocked.
"""

import pytest
from analyzer.languages import (
    build_language_distribution,
    get_primary_language,
    language_percentages,
    identify_strongest_technologies,
)
from analyzer.repos import (
    detect_features,
    is_inactive,
    get_inactive_repos,
    get_original_repos,
    get_forked_repos,
)
from analyzer.stats import compute_stats, _compute_activity_score
from analyzer.scoring import compute_scores, _classify_level


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_repo(
    name="test-repo",
    language="Python",
    stars=10,
    forks=2,
    size=500,
    fork=False,
    description="A test repo",
    pushed_at="2024-01-01T00:00:00Z",
    created_at="2022-01-01T00:00:00Z",
    license=None,
    topics=None,
    has_readme=True,
    has_pages=False,
    open_issues_count=0,
    watchers_count=0,
) -> dict:
    return {
        "name": name,
        "language": language,
        "stargazers_count": stars,
        "forks_count": forks,
        "size": size,
        "fork": fork,
        "description": description,
        "pushed_at": pushed_at,
        "created_at": created_at,
        "license": license,
        "topics": topics or [],
        "has_readme": has_readme,
        "has_pages": has_pages,
        "open_issues_count": open_issues_count,
        "watchers_count": watchers_count,
        "_features": {},
        "_inactive": False,
        "_age_days": 365,
    }


def _make_user(login="testuser", followers=50, following=20, created_at="2020-01-01T00:00:00Z") -> dict:
    return {
        "login": login,
        "name": "Test User",
        "followers": followers,
        "following": following,
        "created_at": created_at,
        "public_repos": 10,
    }


# ---------------------------------------------------------------------------
# Language tests
# ---------------------------------------------------------------------------

class TestLanguages:
    def test_build_distribution_counts_correctly(self):
        repos = [
            _make_repo(language="Python"),
            _make_repo(language="Python"),
            _make_repo(language="JavaScript"),
            _make_repo(language=None),  # should be ignored
        ]
        dist = build_language_distribution(repos)
        assert dist == {"Python": 2, "JavaScript": 1}

    def test_primary_language_is_first(self):
        dist = {"Python": 5, "Go": 2}
        assert get_primary_language(dist) == "Python"

    def test_primary_language_none_on_empty(self):
        assert get_primary_language({}) is None

    def test_percentages_sum_to_100(self):
        dist = {"Python": 3, "Go": 1}
        pcts = language_percentages(dist)
        assert abs(sum(pcts.values()) - 100.0) < 0.1

    def test_identify_strongest_returns_up_to_5(self):
        repos = [_make_repo(language=lang, stars=i) for i, lang in enumerate(
            ["Python", "Go", "Rust", "Java", "C++", "TypeScript"]
        )]
        dist = build_language_distribution(repos)
        strongest = identify_strongest_technologies(repos, dist)
        assert len(strongest) <= 5


# ---------------------------------------------------------------------------
# Repo feature detection tests
# ---------------------------------------------------------------------------

class TestRepoFeatures:
    def test_has_license_true_when_license_present(self):
        repo = _make_repo(license={"key": "mit", "name": "MIT License"})
        features = detect_features(repo)
        assert features["has_license"] is True

    def test_has_license_false_when_none(self):
        repo = _make_repo(license=None)
        features = detect_features(repo)
        assert features["has_license"] is False

    def test_has_tests_detected_from_topics(self):
        repo = _make_repo(topics=["python", "pytest", "testing"])
        features = detect_features(repo)
        assert features["has_tests"] is True

    def test_has_ci_detected_from_topics(self):
        repo = _make_repo(topics=["github-actions", "ci"])
        features = detect_features(repo)
        assert features["has_ci"] is True

    def test_inactive_repo_old_push(self):
        repo = _make_repo(pushed_at="2020-01-01T00:00:00Z")
        assert is_inactive(repo) is True

    def test_active_repo_recent_push(self):
        repo = _make_repo(pushed_at="2026-05-01T00:00:00Z")
        assert is_inactive(repo) is False

    def test_get_original_repos_excludes_forks(self):
        repos = [
            _make_repo(name="original", fork=False),
            _make_repo(name="forked", fork=True),
        ]
        originals = get_original_repos(repos)
        assert len(originals) == 1
        assert originals[0]["name"] == "original"

    def test_get_forked_repos(self):
        repos = [
            _make_repo(name="a", fork=False),
            _make_repo(name="b", fork=True),
            _make_repo(name="c", fork=True),
        ]
        forks = get_forked_repos(repos)
        assert len(forks) == 2


# ---------------------------------------------------------------------------
# Stats tests
# ---------------------------------------------------------------------------

class TestStats:
    def test_total_stars_aggregated(self):
        repos = [_make_repo(stars=10), _make_repo(stars=20)]
        user = _make_user()
        lang_dist = {"Python": 2}
        stats = compute_stats(user, repos, lang_dist)
        assert stats["total_stars"] == 30

    def test_activity_score_capped_at_100(self):
        # 10 repos all pushed within 30 days → 10 * 20 = 200, capped at 100
        repos = [_make_repo(pushed_at="2026-05-01T00:00:00Z") for _ in range(10)]
        score = _compute_activity_score(repos)
        assert score == 100.0

    def test_activity_score_zero_for_no_activity(self):
        repos = [_make_repo(pushed_at="2018-01-01T00:00:00Z")]
        score = _compute_activity_score(repos)
        assert score == 0.0


# ---------------------------------------------------------------------------
# Scoring tests
# ---------------------------------------------------------------------------

class TestScoring:
    def test_classify_level_advanced(self):
        stats = {"original_repos": 20}
        assert _classify_level(80.0, stats) == "Advanced"

    def test_classify_level_intermediate(self):
        stats = {"original_repos": 6}
        assert _classify_level(10.0, stats) == "Intermediate"

    def test_classify_level_beginner(self):
        stats = {"original_repos": 1}
        assert _classify_level(5.0, stats) == "Beginner"

    def test_compute_scores_returns_expected_keys(self):
        repos = [_make_repo()]
        repos[0]["_features"] = detect_features(repos[0])
        repos[0]["_inactive"] = False
        user = _make_user()
        lang_dist = {"Python": 1}
        stats = compute_stats(user, repos, lang_dist)
        scores = compute_scores(repos, stats, lang_dist)
        for key in ["documentation_score", "consistency_score", "complexity_score", "overall_score", "level"]:
            assert key in scores

    def test_scores_in_valid_range(self):
        repos = [_make_repo() for _ in range(5)]
        for repo in repos:
            repo["_features"] = detect_features(repo)
            repo["_inactive"] = False
        user = _make_user()
        lang_dist = {"Python": 5}
        stats = compute_stats(user, repos, lang_dist)
        scores = compute_scores(repos, stats, lang_dist)
        for key in ["documentation_score", "consistency_score", "complexity_score", "overall_score"]:
            assert 0 <= scores[key] <= 100, f"{key} out of range: {scores[key]}"
