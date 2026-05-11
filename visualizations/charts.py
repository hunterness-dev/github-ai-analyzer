"""
Chart generation using matplotlib.

Three charts are produced and saved to the charts_output/ directory:
  1. language_pie.png   – language distribution pie chart
  2. stars_bar.png      – stars per repository (top 10)
  3. timeline.png       – repository creation timeline (growth over time)

All functions accept pre-computed data and write PNG files; they do NOT
perform any network calls.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import matplotlib
matplotlib.use("Agg")  # headless backend — no display required
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

OUTPUT_DIR = "charts_output"


def ensure_output_dir() -> None:
    """Create the output directory if it doesn't already exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Chart 1: Language distribution pie
# ---------------------------------------------------------------------------

def plot_language_pie(
    distribution: dict[str, int],
    username: str,
) -> str:
    """
    Save a pie chart of language usage to {OUTPUT_DIR}/language_pie.png.

    Args:
        distribution: {language: repo_count} (already sorted by count).
        username:     GitHub username (used in the title).

    Returns:
        Absolute path to the saved image.
    """
    ensure_output_dir()
    path = os.path.join(OUTPUT_DIR, f"{username}_language_pie.png")

    if not distribution:
        return _placeholder(path, "No language data")

    # Keep the top-6 languages; group the rest as "Other"
    items = list(distribution.items())
    top = items[:6]
    rest = items[6:]

    labels = [lang for lang, _ in top]
    sizes = [count for _, count in top]

    if rest:
        labels.append("Other")
        sizes.append(sum(count for _, count in rest))

    colours = plt.cm.Set3.colors[: len(labels)]  # type: ignore[attr-defined]

    fig, ax = plt.subplots(figsize=(7, 5), facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        colors=colours,
        startangle=140,
        pctdistance=0.82,
        wedgeprops={"edgecolor": "#1a1a2e", "linewidth": 1.5},
    )

    for text in texts + autotexts:
        text.set_color("white")
        text.set_fontsize(9)

    ax.set_title(
        f"{username}'s Language Distribution",
        color="white",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()
    return path


# ---------------------------------------------------------------------------
# Chart 2: Stars per repository (horizontal bar)
# ---------------------------------------------------------------------------

def plot_stars_bar(repos: list[dict[str, Any]], username: str) -> str:
    """
    Save a horizontal bar chart of stars per repo to {OUTPUT_DIR}/stars_bar.png.

    Shows the top 10 repos by star count.
    """
    ensure_output_dir()
    path = os.path.join(OUTPUT_DIR, f"{username}_stars_bar.png")

    starred = [r for r in repos if r.get("stargazers_count", 0) > 0]
    if not starred:
        return _placeholder(path, "No starred repos")

    top10 = sorted(starred, key=lambda r: r["stargazers_count"], reverse=True)[:10]
    names = [r["name"][:25] for r in top10]
    stars = [r["stargazers_count"] for r in top10]

    # Reverse so highest-star repo is at the top of the chart
    names = names[::-1]
    stars = stars[::-1]

    fig, ax = plt.subplots(figsize=(8, max(4, len(names) * 0.6)), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")

    bars = ax.barh(names, stars, color="#e94560", edgecolor="#1a1a2e", height=0.6)

    # Add value labels at the end of each bar
    for bar, val in zip(bars, stars):
        ax.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height() / 2,
            str(val),
            va="center",
            color="white",
            fontsize=8,
        )

    ax.set_title(f"{username}'s Top Starred Repos", color="white", fontsize=13, fontweight="bold")
    ax.set_xlabel("Stars", color="#aaaaaa")
    ax.tick_params(colors="white")
    ax.spines[:].set_edgecolor("#444")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()
    return path


# ---------------------------------------------------------------------------
# Chart 3: Repository creation timeline
# ---------------------------------------------------------------------------

def plot_repo_timeline(repos: list[dict[str, Any]], username: str) -> str:
    """
    Save a line chart showing cumulative repos over time to
    {OUTPUT_DIR}/timeline.png.

    The x-axis shows calendar years; y-axis shows the running total of
    public repositories at that point in time.
    """
    ensure_output_dir()
    path = os.path.join(OUTPUT_DIR, f"{username}_timeline.png")

    dated = [r for r in repos if r.get("created_at")]
    if not dated:
        return _placeholder(path, "No dated repos")

    # Sort repos by creation date
    dated.sort(key=lambda r: r["created_at"])

    dates = [datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")) for r in dated]
    cumulative = list(range(1, len(dates) + 1))

    fig, ax = plt.subplots(figsize=(9, 4), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")

    ax.plot(dates, cumulative, color="#0f3460", linewidth=2, zorder=2)
    ax.fill_between(dates, cumulative, alpha=0.25, color="#e94560", zorder=1)
    ax.scatter(dates, cumulative, color="#e94560", s=25, zorder=3)

    ax.set_title(f"{username}'s Repository Growth", color="white", fontsize=13, fontweight="bold")
    ax.set_ylabel("Total Repos", color="#aaaaaa")
    ax.set_xlabel("Year", color="#aaaaaa")
    ax.tick_params(colors="white")
    ax.spines[:].set_edgecolor("#444")
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()
    return path


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _placeholder(path: str, message: str) -> str:
    """Save a simple 'no data' placeholder chart."""
    fig, ax = plt.subplots(figsize=(5, 3), facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    ax.text(0.5, 0.5, message, ha="center", va="center", color="gray", fontsize=12)
    ax.axis("off")
    plt.savefig(path, dpi=100, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()
    return path
