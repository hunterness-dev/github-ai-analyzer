"""
Terminal dashboard using the Rich library.

All pretty-printing lives here so that the rest of the codebase stays
logic-only.  The dashboard is split into logical panels:

  • Profile header
  • Key statistics grid
  • Language distribution table
  • Scoring panel with progress bars
  • Repository highlights
  • Feature detection summary
  • Extra insights (inactive repos, strongest technologies)
"""

from __future__ import annotations

from typing import Any

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()

# Colour palette
C_ACCENT = "bright_cyan"
C_GOOD = "bright_green"
C_WARN = "yellow"
C_DANGER = "red"
C_DIM = "dim white"
C_BOLD = "bold white"
C_TITLE = "bold bright_cyan"


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def print_header(user: dict[str, Any]) -> None:
    """Print the profile header panel."""
    name = user.get("name") or user.get("login", "Unknown")
    login = user.get("login", "")
    bio = user.get("bio") or "No bio provided."
    location = user.get("location") or "—"
    company = user.get("company") or "—"
    blog = user.get("blog") or "—"
    email = user.get("email") or "—"

    lines = [
        f"[bold bright_white]{name}[/] [dim](@{login})[/]",
        f"[italic]{bio}[/]",
        "",
        f"[{C_DIM}]📍 Location :[/]  {location}",
        f"[{C_DIM}]🏢 Company  :[/]  {company}",
        f"[{C_DIM}]🌐 Website  :[/]  {blog}",
        f"[{C_DIM}]✉  Email    :[/]  {email}",
        f"[{C_DIM}]🔗 GitHub   :[/]  https://github.com/{login}",
    ]
    console.print(
        Panel("\n".join(lines), title="[bold cyan]👤 GitHub Profile[/]", border_style="cyan")
    )


def print_stats(stats: dict[str, Any]) -> None:
    """Print a two-column grid of key statistics."""
    grid = Table.grid(padding=(0, 3))
    grid.add_column(style="dim white", min_width=26)
    grid.add_column(style="bold white", min_width=12)
    grid.add_column(style="dim white", min_width=26)
    grid.add_column(style="bold white", min_width=12)

    def row(label1, val1, label2, val2):
        grid.add_row(label1, str(val1), label2, str(val2))

    row(
        "📦 Total Repos",         stats["total_repos"],
        "⭐ Total Stars",          stats["total_stars"],
    )
    row(
        "🔀 Original Repos",      stats["original_repos"],
        "🍴 Total Forks Received", stats["total_forks"],
    )
    row(
        "💬 Open Issues",         stats["total_open_issues"],
        "👥 Followers",            stats["followers"],
    )
    row(
        "💾 Avg Repo Size (KB)",  stats["avg_size_kb"],
        "🗣  Following",            stats["following"],
    )
    row(
        "🌍 Languages Used",      stats["language_count"],
        "🏆 Primary Language",     stats["primary_language"] or "—",
    )
    row(
        "⚡ Activity Score",       f"{stats['activity_score']}/100",
        "📅 Account Age",          f"{stats['account_age_days']} days",
    )

    # Highlight the most starred repo
    if stats.get("most_starred_repo"):
        r = stats["most_starred_repo"]
        grid.add_row(
            "🌟 Most Starred Repo",
            f"[bright_yellow]{r['name']}[/] ({r['stargazers_count']} ⭐)",
            "", "",
        )

    console.print(
        Panel(grid, title="[bold cyan]📊 Statistics[/]", border_style="cyan")
    )


def print_languages(distribution: dict[str, int]) -> None:
    """Print a table of language usage."""
    if not distribution:
        console.print("[dim]No language data available.[/dim]")
        return

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold cyan")
    table.add_column("Language", style="bold white", min_width=18)
    table.add_column("Repos", justify="right", style="bright_green")
    table.add_column("Distribution", min_width=30)

    total = sum(distribution.values())
    for lang, count in list(distribution.items())[:10]:
        pct = count / total
        bar = "█" * int(pct * 30) + "░" * (30 - int(pct * 30))
        pct_label = f"{pct*100:.1f}%"
        table.add_row(lang, str(count), f"[cyan]{bar}[/] {pct_label}")

    console.print(
        Panel(table, title="[bold cyan]🗂  Language Distribution[/]", border_style="cyan")
    )


def print_scores(scores: dict[str, Any]) -> None:
    """Print the scoring panel with progress bars."""
    level = scores["level"]
    level_colour = {
        "Advanced": C_GOOD,
        "Intermediate": C_ACCENT,
        "Beginner": C_WARN,
    }.get(level, "white")

    # Build progress bars manually using Rich markup
    table = Table.grid(padding=(0, 2))
    table.add_column(min_width=26, style="dim white")
    table.add_column(min_width=34)
    table.add_column(min_width=7, style="bold white", justify="right")

    score_items = [
        ("📝 Documentation", scores["documentation_score"]),
        ("🔄 Consistency",   scores["consistency_score"]),
        ("🧩 Complexity",    scores["complexity_score"]),
        ("🏅 Overall",       scores["overall_score"]),
    ]

    for label, score in score_items:
        filled = int(score / 100 * 30)
        empty = 30 - filled
        colour = _score_colour(score)
        bar = f"[{colour}]{'█' * filled}[/][dim]{'░' * empty}[/]"
        table.add_row(label, bar, f"[{colour}]{score:.0f}/100[/]")

    level_line = Text.assemble(
        "\n  Developer Level:  ",
        (f"  {level}  ", f"bold {level_colour} on grey23"),
    )

    console.print(
        Panel(
            Text.assemble(level_line, "\n"),
            title="[bold cyan]🏆 Scores[/]",
            border_style="cyan",
        )
    )
    # Print bars inside the panel (Rich limitation: assemble table separately)
    console.print(
        Panel(table, title="[bold cyan]📈 Score Breakdown[/]", border_style="blue")
    )


def print_repo_highlights(stats: dict[str, Any], repos: list[dict[str, Any]]) -> None:
    """Print newest / oldest / most-starred repo cards."""
    cards = []
    for title, repo in [
        ("🌟 Most Starred", stats.get("most_starred_repo")),
        ("🆕 Newest Repo",  stats.get("newest_repo")),
        ("👴 Oldest Repo",  stats.get("oldest_repo")),
    ]:
        if repo:
            desc = repo.get("description") or "No description."
            lang = repo.get("language") or "—"
            stars = repo.get("stargazers_count", 0)
            pushed = (repo.get("pushed_at") or "?")[:10]
            content = (
                f"[bold white]{repo['name']}[/]\n"
                f"[dim]{desc[:60]}[/]\n"
                f"[cyan]⭐ {stars}[/]  [dim]|[/]  [yellow]{lang}[/]  [dim]| Updated: {pushed}[/]"
            )
            cards.append(Panel(content, title=f"[cyan]{title}[/]", border_style="blue", width=38))

    if cards:
        console.print(Columns(cards, equal=True, expand=True))


def print_feature_summary(repos: list[dict[str, Any]]) -> None:
    """Print a summary table of feature detection across all repos."""
    total = len(repos)
    if total == 0:
        return

    feature_map = {
        "📖 Has README":      "has_readme",
        "⚖️  Has License":    "has_license",
        "🧪 Has Tests":       "has_tests",
        "⚙️  Has CI/CD":      "has_ci",
        "🐳 Has Docker":      "has_docker",
        "🌐 Has Pages":       "has_pages",
    }

    table = Table(box=box.SIMPLE_HEAD, header_style="bold cyan")
    table.add_column("Feature", style="white", min_width=20)
    table.add_column("Repos", justify="right")
    table.add_column("Coverage", min_width=26)
    table.add_column("Status")

    for label, key in feature_map.items():
        count = sum(1 for r in repos if r.get("_features", {}).get(key))
        pct = count / total
        bar = "█" * int(pct * 20) + "░" * (20 - int(pct * 20))
        colour = C_GOOD if pct >= 0.5 else (C_WARN if pct >= 0.25 else C_DANGER)
        status = "✅" if pct >= 0.5 else ("⚠️" if pct >= 0.25 else "❌")
        table.add_row(
            label,
            str(count),
            f"[{colour}]{bar}[/] {pct*100:.0f}%",
            status,
        )

    console.print(
        Panel(table, title="[bold cyan]🔍 Feature Detection[/]", border_style="cyan")
    )


def print_insights(
    inactive_repos: list[dict[str, Any]],
    strongest_techs: list[str],
) -> None:
    """Print extra insights: inactive repos and strongest technologies."""
    lines = []

    if strongest_techs:
        tech_str = "  ".join(
            f"[bright_cyan]{i+1}. {t}[/]" for i, t in enumerate(strongest_techs)
        )
        lines.append(f"[bold]💪 Strongest Technologies:[/]\n   {tech_str}")

    if inactive_repos:
        names = ", ".join(r["name"] for r in inactive_repos[:8])
        lines.append(
            f"\n[bold]💤 Inactive Repos (>1 year)[/] [{C_WARN}]({len(inactive_repos)} total)[/]:\n"
            f"   [dim]{names}{'…' if len(inactive_repos) > 8 else ''}[/]"
        )
    else:
        lines.append("\n[bold]💤 Inactive Repos:[/] [bright_green]All repos active![/]")

    console.print(
        Panel("\n".join(lines), title="[bold cyan]💡 Insights[/]", border_style="cyan")
    )


def print_chart_paths(paths: list[str]) -> None:
    """Tell the user where their charts were saved."""
    if not paths:
        return
    items = "\n".join(f"  [dim]→[/] [cyan]{p}[/]" for p in paths)
    console.print(
        Panel(items, title="[bold cyan]📊 Charts Saved[/]", border_style="blue")
    )


def print_separator(title: str = "") -> None:
    console.rule(f"[bold cyan]{title}[/]" if title else "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_colour(score: float) -> str:
    if score >= 70:
        return C_GOOD
    if score >= 40:
        return C_ACCENT
    if score >= 20:
        return C_WARN
    return C_DANGER
