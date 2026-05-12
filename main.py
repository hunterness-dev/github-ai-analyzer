#!/usr/bin/env python3
"""
GitHub Profile Analyzer — main entry point.

Usage
-----
  # Analyse a single user
  python main.py torvalds

  # Analyse and export JSON + Markdown report
  python main.py torvalds --export

  # Compare two users side-by-side
  python main.py torvalds --compare gvanrossum

  # Use a GitHub token for higher rate limits (5 000 req/hr vs 60)
  python main.py torvalds --token ghp_your_token_here

  # Skip chart generation (faster, no matplotlib window)
  python main.py torvalds --no-charts

  # Generate AI-powered insights using Ollama
  python main.py torvalds --ai

  # Use a specific Ollama model
  python main.py torvalds --ai --model mistral
"""

import argparse
import sys
import os

from rich.progress import Progress, SpinnerColumn, TextColumn

from analyzer.api import GitHubClient
from analyzer.repos import enrich_repos, get_inactive_repos
from analyzer.languages import (
    build_language_distribution,
    identify_strongest_technologies,
)
from analyzer.stats import compute_stats
from analyzer.scoring import compute_scores

from ollama import OllamaAgent

from utils.display import (
    console,
    print_header,
    print_stats,
    print_languages,
    print_scores,
    print_repo_highlights,
    print_feature_summary,
    print_insights,
    print_chart_paths,
    print_separator,
)
from utils.export import export_json, export_markdown
from utils.compare import print_comparison

from visualizations.charts import (
    plot_language_pie,
    plot_stars_bar,
    plot_repo_timeline,
)


# ---------------------------------------------------------------------------
# Core analysis pipeline
# ---------------------------------------------------------------------------

def analyse_user(client: GitHubClient, username: str) -> tuple[dict, list, dict, dict, dict, list]:
    """
    Run the full analysis pipeline for one GitHub user.

    Returns:
        (user, repos, stats, scores, language_distribution, strongest_techs)
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Fetching profile for [cyan]{username}[/]…", total=None)

        user = client.get_user(username)
        progress.update(task, description=f"Fetching repositories for [cyan]{username}[/]…")

        repos_raw = client.get_repos(username)
        progress.update(task, description="Analysing repositories…")

        repos = enrich_repos(repos_raw)
        lang_dist = build_language_distribution(repos)
        stats = compute_stats(user, repos, lang_dist)
        scores = compute_scores(repos, stats, lang_dist)
        strongest = identify_strongest_technologies(repos, lang_dist)

    return user, repos, stats, scores, lang_dist, strongest


def display_analysis(
    user: dict,
    repos: list,
    stats: dict,
    scores: dict,
    lang_dist: dict,
    strongest: list,
) -> None:
    """Print all dashboard panels to the terminal."""
    username = user.get("login", "")
    print_separator(f" GitHub Profile Analyzer — {username} ")
    print_header(user)
    print_stats(stats)
    print_languages(lang_dist)
    print_scores(scores)
    print_repo_highlights(stats, repos)
    print_feature_summary(repos)
    print_insights(get_inactive_repos(repos), strongest)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="github-analyzer",
        description="Analyse a GitHub user's public profile and repositories.",
    )
    p.add_argument("username", help="GitHub username to analyse")
    p.add_argument(
        "--compare",
        metavar="USERNAME2",
        help="Compare with a second GitHub user",
    )
    p.add_argument(
        "--token",
        metavar="TOKEN",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub personal access token (or set GITHUB_TOKEN env var)",
    )
    p.add_argument(
        "--export",
        action="store_true",
        help="Export analysis to JSON and Markdown files",
    )
    p.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip matplotlib chart generation",
    )
    p.add_argument(
        "--ai",
        action="store_true",
        help="Generate AI-powered insights using Ollama",
    )
    p.add_argument(
        "--model",
        default="llama3",
        help="Ollama model to use (default: llama3)",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()

    client = GitHubClient(token=args.token)

    # ------------------------------------------------------------------
    # Primary user analysis
    # ------------------------------------------------------------------
    try:
        user, repos, stats, scores, lang_dist, strongest = analyse_user(
            client, args.username
        )
    except ValueError as exc:
        console.print(f"[red]Error:[/] {exc}")
        sys.exit(1)
    except RuntimeError as exc:
        console.print(f"[red]API Error:[/] {exc}")
        sys.exit(1)

    display_analysis(user, repos, stats, scores, lang_dist, strongest)

    # ------------------------------------------------------------------
    # Charts
    # ------------------------------------------------------------------
    if not args.no_charts:
        chart_paths = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("Generating charts…", total=None)
            chart_paths.append(plot_language_pie(lang_dist, args.username))
            chart_paths.append(plot_stars_bar(repos, args.username))
            chart_paths.append(plot_repo_timeline(repos, args.username))
        print_chart_paths(chart_paths)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    if args.export:
        json_path = export_json(
            args.username, user, stats, scores, lang_dist, repos
        )
        md_path = export_markdown(
            args.username, user, stats, scores, lang_dist, repos, strongest
        )
        console.print(f"\n[green]✔[/] JSON   → [cyan]{json_path}[/]")
        console.print(f"[green]✔[/] Report → [cyan]{md_path}[/]")

    # ------------------------------------------------------------------
    # AI Insights
    # ------------------------------------------------------------------
    if args.ai:
        agent = OllamaAgent(model=args.model)

        insights = agent.generate_insights(user, stats, scores, lang_dist, strongest)
        console.print(f"\n[bold cyan]🤖 AI Insights:[/]\n{insights}")

        weaknesses = agent.explain_weaknesses(user, stats, scores, lang_dist, strongest)
        console.print(f"\n[bold cyan]⚠️  Weaknesses:[/]\n{weaknesses}")

        if repos:
            top_repo = max(repos, key=lambda r: r.get("stargazers_count", 0))
            top_explained = agent.explain_top_repo(
                user, stats, scores, lang_dist, strongest, top_repo
            )
            console.print(f"\n[bold cyan]⭐️ Top Repo:[/]\n{top_explained}")

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------
    if args.compare:
        try:
            user_b, repos_b, stats_b, scores_b, lang_dist_b, strongest_b = analyse_user(
                client, args.compare
            )
        except (ValueError, RuntimeError) as exc:
            console.print(f"[red]Could not analyse {args.compare}:[/] {exc}")
        else:
            display_analysis(user_b, repos_b, stats_b, scores_b, lang_dist_b, strongest_b)
            print_separator(" Comparison ")
            print_comparison(user, stats, scores, user_b, stats_b, scores_b)

    print_separator()


if __name__ == "__main__":
    main()