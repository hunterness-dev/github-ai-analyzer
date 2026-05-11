"""
Export analysis results to JSON and Markdown.

Both formats are written to the current working directory.
File names include the GitHub username for easy identification.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any


def export_json(
    username: str,
    user: dict[str, Any],
    stats: dict[str, Any],
    scores: dict[str, Any],
    language_distribution: dict[str, int],
    repos: list[dict[str, Any]],
) -> str:
    """
    Write a comprehensive JSON report and return the file path.

    The JSON is human-readable (indented) and includes a timestamp so
    multiple runs don't overwrite each other (if you rename them).
    """
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "profile": {
            "name": user.get("name"),
            "bio": user.get("bio"),
            "location": user.get("location"),
            "company": user.get("company"),
            "blog": user.get("blog"),
            "email": user.get("email"),
            "public_repos": user.get("public_repos"),
            "followers": user.get("followers"),
            "following": user.get("following"),
            "created_at": user.get("created_at"),
        },
        "statistics": _sanitise(stats),
        "scores": scores,
        "language_distribution": language_distribution,
        "repositories": [
            {
                "name": r.get("name"),
                "description": r.get("description"),
                "language": r.get("language"),
                "stars": r.get("stargazers_count", 0),
                "forks": r.get("forks_count", 0),
                "size_kb": r.get("size", 0),
                "fork": r.get("fork", False),
                "created_at": r.get("created_at"),
                "pushed_at": r.get("pushed_at"),
                "url": r.get("html_url"),
                "topics": r.get("topics", []),
                "features": r.get("_features", {}),
                "inactive": r.get("_inactive", False),
            }
            for r in repos
        ],
    }

    path = f"{username}_analysis.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str)
    return path


def export_markdown(
    username: str,
    user: dict[str, Any],
    stats: dict[str, Any],
    scores: dict[str, Any],
    language_distribution: dict[str, int],
    repos: list[dict[str, Any]],
    strongest_techs: list[str],
) -> str:
    """
    Write a Markdown report and return the file path.

    The report is structured like a developer portfolio summary card —
    useful for sharing or pasting into a GitHub README.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    name = user.get("name") or username
    bio = user.get("bio") or "—"

    top_langs = list(language_distribution.items())[:5]
    lang_rows = "\n".join(
        f"| {lang} | {count} |" for lang, count in top_langs
    )

    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:5]
    repo_rows = "\n".join(
        f"| [{r['name']}]({r.get('html_url', '#')}) | {r.get('stargazers_count', 0)} | "
        f"{r.get('language') or '—'} | {(r.get('description') or '—')[:60]} |"
        for r in top_repos
    )

    inactive_repos = [r for r in repos if r.get("_inactive")]
    inactive_str = (
        ", ".join(f"`{r['name']}`" for r in inactive_repos[:8])
        + (" …" if len(inactive_repos) > 8 else "")
        if inactive_repos
        else "_All repos are active!_"
    )

    md = f"""# 🔍 GitHub Profile Analysis: {name}

> Generated on {now} by [GitHub Profile Analyzer](https://github.com/)

## 👤 Profile

| | |
|---|---|
| **Username** | [@{username}](https://github.com/{username}) |
| **Bio** | {bio} |
| **Location** | {user.get("location") or "—"} |
| **Company** | {user.get("company") or "—"} |
| **Website** | {user.get("blog") or "—"} |
| **Followers** | {stats.get("followers", 0)} |
| **Following** | {stats.get("following", 0)} |

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total Repositories | {stats["total_repos"]} |
| Original Repos | {stats["original_repos"]} |
| Forked Repos | {stats["forked_repos"]} |
| Total Stars Earned | ⭐ {stats["total_stars"]} |
| Total Forks Received | 🍴 {stats["total_forks"]} |
| Open Issues | {stats["total_open_issues"]} |
| Average Repo Size | {stats["avg_size_kb"]} KB |
| Languages Used | {stats["language_count"]} |
| Primary Language | {stats["primary_language"] or "—"} |
| Activity Score | {stats["activity_score"]} / 100 |
| Account Age | {stats["account_age_days"]} days |

---

## 🏆 Scores

| Dimension | Score |
|-----------|-------|
| 📝 Documentation | {scores["documentation_score"]:.0f} / 100 |
| 🔄 Consistency | {scores["consistency_score"]:.0f} / 100 |
| 🧩 Complexity | {scores["complexity_score"]:.0f} / 100 |
| 🏅 **Overall** | **{scores["overall_score"]:.0f} / 100** |

**Developer Level:** `{scores["level"]}`

---

## 🗂 Language Distribution (top 5)

| Language | Repos |
|----------|-------|
{lang_rows}

---

## 🌟 Top Repositories

| Repository | Stars | Language | Description |
|------------|-------|----------|-------------|
{repo_rows}

---

## 💪 Strongest Technologies

{" · ".join(f"`{t}`" for t in strongest_techs) or "—"}

---

## 💤 Inactive Repositories (> 1 year)

{inactive_str}

---

_Analysis performed with GitHub Profile Analyzer._
"""

    path = f"{username}_report.md"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(md)
    return path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sanitise(data: dict[str, Any]) -> dict[str, Any]:
    """
    Remove non-serialisable values (nested dicts from repo objects)
    so json.dump doesn't fail on the stats dict.
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict) and "name" in value:
            # It's a repo object — summarise it
            result[key] = {
                "name": value.get("name"),
                "stars": value.get("stargazers_count", 0),
                "url": value.get("html_url"),
            }
        else:
            result[key] = value
    return result
