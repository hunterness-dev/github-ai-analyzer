# Sample Output — `python main.py torvalds`

```
━━━━━━━━━━━━━━━━━━━━━ GitHub Profile Analyzer — torvalds ━━━━━━━━━━━━━━━━━━━━━

╭─────────────────────── 👤 GitHub Profile ────────────────────────╮
│ Linus Torvalds (@torvalds)                                        │
│ Linux kernel developer                                            │
│                                                                   │
│ 📍 Location :  Portland, OR                                       │
│ 🏢 Company  :  Linux Foundation                                   │
│ 🌐 Website  :  —                                                  │
│ ✉  Email    :  —                                                  │
│ 🔗 GitHub   :  https://github.com/torvalds                        │
╰───────────────────────────────────────────────────────────────────╯

╭────────────────────────── 📊 Statistics ──────────────────────────╮
│ 📦 Total Repos          7      ⭐ Total Stars        199,201      │
│ 🔀 Original Repos       5      🍴 Total Forks         56,430      │
│ 💬 Open Issues          0      👥 Followers          225,671      │
│ 💾 Avg Repo Size (KB) 857,482  🗣  Following              0       │
│ 🌍 Languages Used       3      🏆 Primary Language    C          │
│ ⚡ Activity Score    73/100    📅 Account Age         5,110 days  │
│ 🌟 Most Starred Repo  linux (196,431 ⭐)                          │
╰───────────────────────────────────────────────────────────────────╯

╭──────────────────── 🗂  Language Distribution ────────────────────╮
│  C               █████████████████████████░░░░░ 71.4%  5 repos   │
│  Python          ████████░░░░░░░░░░░░░░░░░░░░░  14.3%  1 repo    │
│  C++             ████████░░░░░░░░░░░░░░░░░░░░░  14.3%  1 repo    │
╰───────────────────────────────────────────────────────────────────╯

╭──────────────────────── 🏆 Scores ────────────────────────────────╮
│   Developer Level:    Advanced                                    │
╰───────────────────────────────────────────────────────────────────╯
╭─────────────────────── 📈 Score Breakdown ────────────────────────╮
│  📝 Documentation  ████████████░░░░░░░░░░░░░░░░░░    42/100      │
│  🔄 Consistency    ████████████████████████████░░    94/100      │
│  🧩 Complexity     ████████████████████████████████  98/100      │
│  🏅 Overall        ████████████████████████░░░░░░░   78/100      │
╰───────────────────────────────────────────────────────────────────╯

╭──────── 🌟 Most Starred ────────╮╭──── 🆕 Newest Repo ───╮╭─ 👴 Oldest Repo ──╮
│ linux                           ││ uemacs               ││ linux              │
│ Linux kernel source tree        ││ My personal version  ││ Linux kernel       │
│ ⭐ 196431  | C  | Updated:2026  ││ ⭐ 2,291 | C         ││ ⭐ 196431 | C      │
╰─────────────────────────────────╯╰──────────────────────╯╰────────────────────╯

╭──────────────────── 🔍 Feature Detection ─────────────────────────╮
│  📖 Has README    5   ██████████████████░░  86%  ✅               │
│  ⚖️  Has License  4   ███████████████░░░░░  71%  ✅               │
│  🧪 Has Tests     0   ░░░░░░░░░░░░░░░░░░░░   0%  ❌               │
│  ⚙️  Has CI/CD    0   ░░░░░░░░░░░░░░░░░░░░   0%  ❌               │
│  🐳 Has Docker    0   ░░░░░░░░░░░░░░░░░░░░   0%  ❌               │
│  🌐 Has Pages     0   ░░░░░░░░░░░░░░░░░░░░   0%  ❌               │
╰───────────────────────────────────────────────────────────────────╯

╭─────────────────────────── 💡 Insights ───────────────────────────╮
│ 💪 Strongest Technologies:                                        │
│    1. C    2. Python    3. C++                                    │
│                                                                   │
│ 💤 Inactive Repos (>1 year): All repos active!                    │
╰───────────────────────────────────────────────────────────────────╯

╭────────────────── 📊 Charts Saved ────────────────────────────────╮
│  → charts_output/torvalds_language_pie.png                        │
│  → charts_output/torvalds_stars_bar.png                           │
│  → charts_output/torvalds_timeline.png                            │
╰───────────────────────────────────────────────────────────────────╯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## With `--export` flag

Two additional files are written:
- `torvalds_analysis.json`  — full machine-readable data
- `torvalds_report.md`      — human-readable Markdown summary card

## With `--compare gvanrossum`

```
╭──────── ⚔️  Comparison: Linus Torvalds vs Guido van Rossum ────────╮
│  Metric                   Linus Torvalds   Guido van Rossum        │
│ ── Statistics ──                                                    │
│  Total Repos                          7                 69         │
│  Original Repos                       5                 51         │
│  Total Stars ⭐               199,201              5,842           │
│  Total Forks 🍴                56,430              1,230           │
│  Followers                    225,671             10,491           │
│  Languages Used                     3                  9           │
│  Avg Repo Size (KB)           857,482              5,230           │
│  Activity Score                    73                 42           │
│ ── Scores ──                                                        │
│  Documentation Score               42                 65           │
│  Consistency Score                 94                 71           │
│  Complexity Score                  98                 52           │
│  Overall Score 🏅                  78                 58           │
│  Developer Level             Advanced           Advanced           │
╰────────────────────────────────────────────────────────────────────╯
```
