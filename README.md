# 🔍 GitHub Profile Analyzer

A clean, production-quality CLI tool that analyses any GitHub user's public profile and repositories, then generates rich statistics, scores, and visual charts — all in your terminal.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Statistics** | Stars, forks, repos, languages, activity score, account age |
| 🏆 **Scoring** | Documentation, Consistency, Complexity scores (0–100 each) |
| 🎯 **Classification** | Beginner / Intermediate / Advanced developer level |
| 🔍 **Feature Detection** | README, license, tests, CI/CD, Docker, GitHub Pages |
| 💡 **Insights** | Inactive repos, strongest technologies |
| 📈 **Charts** | Language pie chart, stars bar chart, repo growth timeline |
| 📤 **Export** | JSON data file and Markdown report |
| ⚔️  **Compare** | Side-by-side comparison of two GitHub users |

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-username/github-analyzer.git
cd github-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run it

```bash
# Analyse any GitHub user
python main.py torvalds

# Export results to JSON + Markdown
python main.py torvalds --export

# Compare two users
python main.py torvalds --compare gvanrossum

# Skip chart generation
python main.py torvalds --no-charts
```

### 4. (Optional) Set a GitHub token

Without a token you get **60 API requests/hour**. With one you get **5 000**.

```bash
# Option A — environment variable (recommended)
export GITHUB_TOKEN=ghp_your_token_here
python main.py torvalds

# Option B — CLI flag
python main.py torvalds --token ghp_your_token_here
```

Get a token at: https://github.com/settings/tokens (no scopes needed for public data)

---

## 📁 Project Structure

```
github-analyzer/
│
├── analyzer/           # Core analysis modules (no I/O)
│   ├── api.py          # GitHub REST API client (requests, pagination, rate limits)
│   ├── repos.py        # Repository feature detection and enrichment
│   ├── languages.py    # Language distribution and strongest tech analysis
│   ├── stats.py        # Aggregate statistics computation
│   └── scoring.py      # Scoring system and developer classification
│
├── visualizations/
│   └── charts.py       # matplotlib chart generation (3 charts)
│
├── utils/
│   ├── display.py      # Rich terminal dashboard (all pretty-printing)
│   ├── export.py       # JSON and Markdown export
│   └── compare.py      # Side-by-side user comparison
│
├── tests/
│   └── test_analyzer.py  # Pytest unit tests (no network calls)
│
├── charts_output/      # Generated charts saved here (auto-created)
│
├── main.py             # CLI entry point
├── requirements.txt
└── README.md
```

---

## 📊 Statistics Computed

- Total / original / forked repository counts
- Total stars earned across all repos
- Total forks received
- Average repository size
- Most starred and most forked repository
- Newest and oldest repository
- Open issues count
- Language distribution (top languages with percentages)
- Activity score (0–100, based on recent push dates)
- Account age in days

---

## 🏆 Scoring System

Each score is independently calculated on a 0–100 scale.

### Documentation Score
Rewards repos that have:
- ✅ README file (+2 pts per repo)
- ✅ Description (+1 pt)
- ✅ License (+2 pts)
- ✅ GitHub Pages (+1 pt)
- ✅ Topics/tags (+1 pt)

### Consistency Score
Based on repos-per-year relative to account age.
Penalised if many repos are inactive (no pushes in 12+ months).

### Project Complexity Score
Combines:
- Language diversity (how many different languages used)
- Average repository size
- Total stars (community validation)
- Open issues (active projects attract issues)
- CI/CD and Docker usage ratio

### Overall Score
Weighted average: `Documentation × 0.30 + Consistency × 0.25 + Complexity × 0.25 + Activity × 0.20`

### Developer Level
| Level | Criteria |
|-------|----------|
| 🟢 Advanced | Overall ≥ 65 AND ≥ 15 original repos |
| 🟡 Intermediate | Overall ≥ 35 OR ≥ 5 original repos |
| 🔴 Beginner | Everything else |

---

## 📈 Charts

Three PNG charts are generated in `charts_output/`:

| Chart | Description |
|-------|-------------|
| `{username}_language_pie.png` | Pie chart of language distribution |
| `{username}_stars_bar.png` | Horizontal bar chart: top 10 repos by stars |
| `{username}_timeline.png` | Line chart: cumulative repo count over time |

---

## 🔍 Feature Detection

Detected using GitHub API metadata (topics, license object, boolean flags):

| Feature | Detection Method |
|---------|-----------------|
| README | `has_readme` flag from API |
| License | `license` object presence |
| Tests | Topics/description containing `test`, `pytest`, `jest`, etc. |
| CI/CD | Topics/description containing `ci`, `github-actions`, `travis`, etc. |
| Docker | Topics/description containing `docker`, `container`, etc. |
| GitHub Pages | `has_pages` flag from API |

> **Note:** For more accurate feature detection (checking actual file trees), add a GitHub token and optionally extend `analyzer/repos.py` to call the contents API per repo.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

All tests are fully offline (no network calls — all data is mocked).

---

## ⚙️ CLI Reference

```
usage: python main.py [-h] [--compare USERNAME2] [--token TOKEN] [--export] [--no-charts] username

positional arguments:
  username              GitHub username to analyse

options:
  -h, --help            Show this help message and exit
  --compare USERNAME2   Compare with a second GitHub user
  --token TOKEN         GitHub personal access token (or GITHUB_TOKEN env var)
  --export              Export analysis to JSON and Markdown files
  --no-charts           Skip matplotlib chart generation (faster)
```

---

## 📤 Export Formats

### JSON (`{username}_analysis.json`)
Complete machine-readable snapshot including all stats, scores, language distribution, and per-repo data.

### Markdown (`{username}_report.md`)
Human-readable summary card with tables — paste directly into a GitHub README or share with others.

---

## 🔑 Rate Limits

| Mode | Requests/Hour |
|------|--------------|
| No token | 60 |
| With token | 5,000 |

The tool automatically detects rate limit responses and waits for the reset window before retrying. You'll see a yellow notice in the terminal if this happens.

---

## 🛠 Extending the Project

The modular architecture makes it easy to add features:

- **New stat** → add to `analyzer/stats.py`
- **New score dimension** → add to `analyzer/scoring.py`
- **New chart** → add to `visualizations/charts.py`
- **New export format** → add to `utils/export.py`
- **New display panel** → add to `utils/display.py`

---

## 📄 License

MIT License — see `LICENSE` for details.

---

## 🙏 Acknowledgements

- [GitHub REST API](https://docs.github.com/en/rest)
- [Rich](https://github.com/Textualize/rich) for the beautiful terminal output
- [matplotlib](https://matplotlib.org/) for the charts
