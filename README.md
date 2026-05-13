# 🔍 GitHub Profile Analyzer — Web App

A terminal-styled, interactive web dashboard for analysing any GitHub user's public profile. Enter a username and get an instant breakdown of scores, language distribution, repository stats, and AI-powered developer insights — all in a sleek dark UI built with React 19 and Vite.

![React](https://img.shields.io/badge/React-19-61dafb?logo=react)
![Vite](https://img.shields.io/badge/Vite-8-646cff?logo=vite)
![License](https://img.shields.io/badge/license-MIT-green)

> **Demo mode:** The frontend ships with realistic mock data for `octocat` and `torvalds` so it works out of the box — no backend or API token required. See [Backend Integration](#-backend-integration) to connect a real analysis engine.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Statistics** | Stars, forks, repos, account age — with eased animated number counters |
| 🏆 **Score Cards** | Documentation, Consistency, and Complexity scores rendered as animated SVG circular progress charts |
| 🎯 **Classification** | Beginner / Intermediate / Advanced badge derived from the overall weighted score |
| 🌐 **Language Distribution** | Proportional colour-coded bar with per-language percentage legend |
| 📋 **Repository Table** | Sortable table (name, stars, language, last updated) with alternating row shading |
| 💡 **AI Insights** | Bold-highlighted rendering of AI-generated developer summaries |
| ⌨️ **Typewriter Effect** | Terminal footer animates the overall score result character by character |
| 🖥️ **Terminal Aesthetic** | JetBrains Mono / Fira Code, deep green-on-black palette, blinking cursor |
| 📱 **Responsive** | Fluid grid layout, works on mobile and desktop |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/github-analyzer.git
cd github-analyzer/github-analyzer   # the Vite app lives in the nested folder
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start the dev server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser. Type `octocat` or `torvalds` to see the dashboard with mock data.

### Other scripts

```bash
npm run build     # production build → dist/
npm run preview   # preview the production build locally
npm run lint      # ESLint check
```

---

## 📁 Project Structure

```
github-analyzer/               ← Python CLI (original backend)
│
├── analyzer/                  ← Core analysis modules
│   ├── api.py                 ← GitHub REST API client
│   ├── repos.py               ← Repo feature detection
│   ├── languages.py           ← Language distribution
│   ├── stats.py               ← Aggregate statistics
│   └── scoring.py             ← Scoring + classification
│
├── ollama/
│   └── AI_insights.py         ← Ollama AI insights agent
│
├── utils/
│   ├── display.py             ← Rich terminal output
│   ├── export.py              ← JSON + Markdown export
│   └── compare.py             ← Side-by-side user comparison
│
├── visualizations/
│   └── charts.py              ← matplotlib chart generation
│
├── tests/
│   └── test_analyzer.py       ← Offline pytest unit tests
│
├── main.py                    ← CLI entry point
├── requirements.txt
│
└── github-analyzer/           ← Vite + React web app
    ├── src/
    │   ├── App.jsx            ← Entire UI (components + state + mock data)
    │   ├── main.jsx           ← React root mount
    │   ├── App.css            ← Vite scaffold styles (largely unused by app)
    │   └── index.css          ← Base CSS variables and resets
    │
    ├── public/
    │   ├── favicon.svg
    │   └── icons.svg
    │
    ├── index.html
    ├── vite.config.js
    ├── eslint.config.js
    └── package.json
```

> **Note on nesting:** The web app currently lives inside the repo as `github-analyzer/github-analyzer/`. You may want to move it to the root or a dedicated `web/` folder once the project stabilises.

---

## 🖥️ The Interface

### Landing / Search

A centered terminal prompt prefixed with `$`. Type any GitHub username and press **Enter** or click **Analyze →**. An animated `Analyzing...` indicator appears while the (mock) request resolves.

### Overview Tab

- **Profile header** — avatar, display name, `@handle`, bio, followers / following / repo counts, and a colour-coded classification badge.
- **Stat cards** — four metric tiles (Total Stars, Total Forks, Account Age, Public Repos) with cubic-eased animated counters that increment from zero on load.
- **Score analysis** — three circular SVG progress arcs (Docs, Consistency, Complexity) plus a computed Overall score, all animating from 0.
- **Language distribution** — proportional segmented bar with a dot-legend showing each language and its percentage share.

### Repositories Tab

A fully sortable table of the user's public repos. Click any column header to toggle ascending / descending order. Repo names are styled as green links; stars show a gold ★ icon; rows alternate shading for readability.

### AI Insights Tab

The AI-generated summary renders with bold segments (wrapped in `**...**`) highlighted in green. A model badge (`llama3`) sits alongside the panel header. A left green border frames the text block.

### Terminal Footer

After results load, a typewriter animation in the footer bar spells out the computed overall score in the style of a CLI command output.

---

## 🔌 Backend Integration

The app currently resolves all data from the `MOCK_DATA` object at the top of `App.jsx`. To connect a real backend, replace the mock resolution block in the `analyze()` function:

```js
// App.jsx — inside the analyze() function
// Replace this mock block:
const found = MOCK_DATA[key] || ...;

// With a real fetch:
const res = await fetch(`/api/analyze?username=${username.trim()}`);
if (!res.ok) {
  setError(`User "${username.trim()}" not found.`);
  return;
}
const found = await res.json();
```

### Expected response shape

```json
{
  "profile": {
    "name": "The Octocat",
    "login": "octocat",
    "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
    "bio": "I work @ GitHub.",
    "followers": 14982,
    "following": 9,
    "public_repos": 8
  },
  "languages": { "JavaScript": 45000, "Python": 32000 },
  "scores": { "documentation": 92, "consistency": 78, "complexity": 85 },
  "total_stars": 4291,
  "total_forks": 1834,
  "account_age_years": 15,
  "classification": "Advanced",
  "repos": [
    { "name": "Hello-World", "stargazers_count": 2410, "language": "C", "updated_at": "2025-03-12" }
  ],
  "ai_insights": "This developer has strong documentation habits..."
}
```

### Backend options

**Option A — Python (existing CLI backend)**

Wrap the existing `analyzer/` modules in a FastAPI server:

```bash
pip install fastapi uvicorn
```

```python
# server.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from analyzer.api import GitHubClient
from analyzer.repos import enrich_repos
from analyzer.languages import build_language_distribution
from analyzer.stats import compute_stats
from analyzer.scoring import compute_scores

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["GET"])

@app.get("/api/analyze")
def analyze(username: str):
    client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    user = client.get_user(username)
    repos = enrich_repos(client.get_repos(username))
    lang_dist = build_language_distribution(repos)
    stats = compute_stats(user, repos, lang_dist)
    scores = compute_scores(repos, stats, lang_dist)
    # assemble and return the JSON schema above
```

```bash
uvicorn server:app --reload --port 8000
```

Then update the fetch URL in `App.jsx` to point at `http://localhost:8000`.

**Option B — Vite dev proxy**

To avoid CORS issues in development, add a proxy to `vite.config.js`:

```js
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

Your fetch can then stay as a relative path: `/api/analyze?username=...`.

---

## 🏆 Scoring System

Each score is computed independently by the Python backend on a 0–100 scale.

### Documentation Score
Rewards repos with a README (+2 pts), description (+1 pt), license (+2 pts), GitHub Pages (+1 pt), and topics (+1 pt). Max 7 pts per repo, normalised to 100.

### Consistency Score
Based on repos-per-year relative to account age. Penalised if many repos are inactive (no pushes in 12+ months).

### Complexity Score
Combines language diversity, average repo size, total stars, open issues, and CI/CD & Docker usage ratio.

### Overall Score
```
Overall = Documentation × 0.30 + Consistency × 0.25 + Complexity × 0.25 + Activity × 0.20
```

The frontend currently approximates this as `Docs × 0.30 + Consistency × 0.35 + Complexity × 0.35` (activity is not yet exposed in the API response).

### Developer Classification

| Level | Badge | Criteria |
|-------|-------|----------|
| Advanced | 🟢 Green | Overall ≥ 65 **and** ≥ 15 original repos |
| Intermediate | 🟡 Amber | Overall ≥ 35 **or** ≥ 5 original repos |
| Beginner | 🔴 Red | Everything else |

---

## 🤖 AI Insights

AI summaries are generated by the Python backend using [Ollama](https://ollama.com) (local inference, no API key needed). The frontend renders the returned text with `**bold**` segments highlighted in green.

Each profile receives:

| Output | Description |
|--------|-------------|
| **Profile summary** | Developer style, strengths, and GitHub activity overview |
| **Key strengths** | Highlighted inline within the summary text |
| **Areas to grow** | Actionable improvement suggestions |

The frontend AI panel displays pre-written mock insights when no backend is connected.

---

## 🚢 Deployment

### Build for production

```bash
cd github-analyzer/github-analyzer
npm run build
# Output: dist/
```

### Vercel

```bash
npm install -g vercel
vercel
```

Set the **root directory** to `github-analyzer/github-analyzer` in the Vercel project settings (because the app is nested inside the repo). Framework preset: **Vite**.

### Netlify

In the Netlify UI, configure:

| Setting | Value |
|---------|-------|
| Base directory | `github-analyzer/github-analyzer` |
| Build command | `npm run build` |
| Publish directory | `github-analyzer/github-analyzer/dist` |

### Nginx / static host

This is a pure client-side SPA, so just serve the `dist/` folder and add a catch-all rewrite:

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

---

## 🗺️ Planned

- Live GitHub API integration via the Python backend
- Export analysis as JSON or PDF report
- Compare two GitHub profiles side by side
- Shareable permalink for a pre-loaded profile result
- Recently-viewed profiles in `localStorage`
- Split `App.jsx` into individual component files

---

## 🛠 Extending the App

The entire UI lives in `src/App.jsx`. Each logical section is a self-contained function component — straightforward to extract into separate files as the project grows:

| Component | What it does |
|-----------|-------------|
| `AnimatedNumber` | `requestAnimationFrame` counter with cubic ease-out |
| `CircleScore` | Animated SVG `stroke-dashoffset` progress ring |
| `LanguageBar` | Proportional segmented bar + dot legend |
| `RepoTable` | Client-side sortable table with toggling sort direction |
| `InsightsPanel` | Parses `**bold**` markdown into highlighted spans |
| `Typewriter` | `setInterval` character-reveal with blinking cursor |
| `StatCard` | Metric tile wrapping `AnimatedNumber` |
| `LoadingDots` | Animated ellipsis indicator |

To add a new score dimension, add another `<CircleScore>` in the score analysis block and ensure the backend returns the value under `scores`.

---

## 📄 License

MIT License — see `LICENSE` for details.

---

## 🙏 Acknowledgements

- [GitHub REST API](https://docs.github.com/en/rest)
- [React](https://react.dev/) + [Vite](https://vite.dev/) for the frontend
- [Ollama](https://ollama.com) for local AI inference (backend)
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/) for the terminal font
- Original CLI built with [Rich](https://github.com/Textualize/rich) and [matplotlib](https://matplotlib.org/)