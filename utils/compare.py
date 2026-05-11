"""
Side-by-side comparison of two GitHub users.

Presents a Rich table where each row is a metric and the two columns
are the two users' values.  The "winner" (higher value) is highlighted.
"""

from __future__ import annotations

from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_comparison(
    user_a: dict[str, Any],
    stats_a: dict[str, Any],
    scores_a: dict[str, Any],
    user_b: dict[str, Any],
    stats_b: dict[str, Any],
    scores_b: dict[str, Any],
) -> None:
    """
    Print a comparison table for two users side by side.

    Args:
        user_a / user_b:   Raw GitHub user profile dicts.
        stats_a / stats_b: Output of stats.compute_stats().
        scores_a / scores_b: Output of scoring.compute_scores().
    """
    name_a = (user_a.get("name") or user_a.get("login", "User A"))[:18]
    name_b = (user_b.get("name") or user_b.get("login", "User B"))[:18]

    table = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold cyan",
        border_style="cyan",
    )
    table.add_column("Metric", style="dim white", min_width=28)
    table.add_column(name_a, justify="right", min_width=14)
    table.add_column(name_b, justify="right", min_width=14)

    metrics = [
        ("Total Repos",         "total_repos",       stats_a, stats_b),
        ("Original Repos",      "original_repos",     stats_a, stats_b),
        ("Total Stars ⭐",       "total_stars",        stats_a, stats_b),
        ("Total Forks 🍴",       "total_forks",        stats_a, stats_b),
        ("Followers",            "followers",          stats_a, stats_b),
        ("Languages Used",       "language_count",     stats_a, stats_b),
        ("Avg Repo Size (KB)",   "avg_size_kb",        stats_a, stats_b),
        ("Activity Score",       "activity_score",     stats_a, stats_b),
        ("Account Age (days)",   "account_age_days",   stats_a, stats_b),
    ]

    score_metrics = [
        ("Documentation Score",  "documentation_score", scores_a, scores_b),
        ("Consistency Score",    "consistency_score",   scores_a, scores_b),
        ("Complexity Score",     "complexity_score",    scores_a, scores_b),
        ("Overall Score 🏅",     "overall_score",       scores_a, scores_b),
    ]

    def _row(label: str, key: str, da: dict, db: dict) -> None:
        va = da.get(key, 0) or 0
        vb = db.get(key, 0) or 0
        # Highlight the higher value
        if va > vb:
            ca, cb = "bright_green", "white"
        elif vb > va:
            ca, cb = "white", "bright_green"
        else:
            ca, cb = "yellow", "yellow"
        table.add_row(label, f"[{ca}]{va}[/]", f"[{cb}]{vb}[/]")

    table.add_row("[bold]── Statistics ──[/]", "", "")
    for m in metrics:
        _row(*m)

    table.add_row("[bold]── Scores ──[/]", "", "")
    for m in score_metrics:
        _row(*m)

    # Developer level
    level_a = scores_a.get("level", "—")
    level_b = scores_b.get("level", "—")
    level_order = {"Advanced": 3, "Intermediate": 2, "Beginner": 1}
    if level_order.get(level_a, 0) > level_order.get(level_b, 0):
        ca, cb = "bright_green", "white"
    elif level_order.get(level_b, 0) > level_order.get(level_a, 0):
        ca, cb = "white", "bright_green"
    else:
        ca, cb = "yellow", "yellow"
    table.add_row("Developer Level", f"[{ca}]{level_a}[/]", f"[{cb}]{level_b}[/]")

    console.print(
        Panel(
            table,
            title=f"[bold cyan]⚔️  Comparison: {name_a} vs {name_b}[/]",
            border_style="cyan",
        )
    )
