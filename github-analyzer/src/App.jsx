import { useState, useEffect, useRef } from "react";

const MOCK_DATA = {
  octocat: {
    profile: { name: "The Octocat", login: "octocat", avatar_url: "https://avatars.githubusercontent.com/u/583231?v=4", bio: "I work @ GitHub. On open source stuff, mostly.", followers: 14982, following: 9, public_repos: 8 },
    languages: { JavaScript: 45000, Python: 32000, TypeScript: 28000, Ruby: 18000, Go: 12000 },
    scores: { documentation: 92, consistency: 78, complexity: 85 },
    total_stars: 4291, total_forks: 1834, account_age_years: 15,
    classification: "Advanced",
    repos: [
      { name: "Hello-World", stargazers_count: 2410, language: "C", updated_at: "2025-03-12" },
      { name: "Spoon-Knife", stargazers_count: 1892, language: "HTML", updated_at: "2025-01-08" },
      { name: "boysenberry-book-club", stargazers_count: 312, language: "Ruby", updated_at: "2024-11-21" },
      { name: "git-consortium", stargazers_count: 188, language: "Python", updated_at: "2024-09-14" },
      { name: "octocat.github.io", stargazers_count: 98, language: null, updated_at: "2024-07-03" },
      { name: "linguist", stargazers_count: 85, language: "Ruby", updated_at: "2024-06-17" },
      { name: "test-repo1", stargazers_count: 21, language: "JavaScript", updated_at: "2023-12-11" },
      { name: "Hello-World-Template", stargazers_count: 7, language: null, updated_at: "2023-08-05" },
    ],
    ai_insights: "**octocat** is a highly experienced GitHub developer with 15 years on the platform. Their portfolio demonstrates exceptional documentation discipline — nearly every repo ships with a README, license, and description — placing them in the top tier for public visibility and open-source best practices.\n\nTheir consistency score reflects steady, sustained contributions without dramatic spikes, which signals a methodical and professional work style. The complexity score of 85 reflects a polyglot background spanning C, Ruby, Python, JavaScript, and HTML.\n\n**Key strengths:** Documentation culture, language versatility, strong community engagement (14k+ followers).\n\n**Areas to grow:** Increasing repo output volume and modernising CI/CD tooling would push the overall score further into elite territory.",
  },
  torvalds: {
    profile: { name: "Linus Torvalds", login: "torvalds", avatar_url: "https://avatars.githubusercontent.com/u/1024025?v=4", bio: "Just a regular programmer :)", followers: 243000, following: 0, public_repos: 6 },
    languages: { C: 980000, Shell: 42000, Python: 18000, Makefile: 9000, Perl: 4000 },
    scores: { documentation: 74, consistency: 62, complexity: 98 },
    total_stars: 218400, total_forks: 58200, account_age_years: 13,
    classification: "Advanced",
    repos: [
      { name: "linux", stargazers_count: 192400, language: "C", updated_at: "2025-05-09" },
      { name: "uemacs", stargazers_count: 2800, language: "C", updated_at: "2024-12-03" },
      { name: "subsurface-for-dirk", stargazers_count: 1900, language: "C", updated_at: "2023-11-14" },
      { name: "test-tlb", stargazers_count: 860, language: "C", updated_at: "2022-07-22" },
      { name: "libdc1394", stargazers_count: 211, language: "C", updated_at: "2021-03-07" },
      { name: "wdm", stargazers_count: 189, language: "C", updated_at: "2020-09-19" },
    ],
    ai_insights: "**torvalds** is in a class of his own — the creator of Linux and Git represents the archetype of deep, singular focus. With only 6 public repos, every project is weighty and impactful, with linux alone accumulating 190k+ stars.\n\nThe complexity score of 98 reflects enormous codebases, multi-decade histories, and global community adoption. The lower documentation and consistency scores are artefacts of a pre-GitHub workflow — Linus primarily operates through mailing lists and patch systems.\n\n**Key strengths:** Unmatched project scale, extreme technical depth, legendary community impact.\n\n**Areas to grow:** GitHub-native documentation and issue tracking would surface more of the incredible work already happening in these repos.",
  }
};

const LANG_COLORS = {
  JavaScript: "#f7df1e", TypeScript: "#3178c6", Python: "#3572A5",
  Ruby: "#701516", Go: "#00add8", C: "#555555", "C++": "#f34b7d",
  HTML: "#e34c26", Shell: "#89e051", Rust: "#dea584", Java: "#b07219",
  Kotlin: "#A97BFF", Swift: "#F05138", Perl: "#0298c3", Makefile: "#427819",
};

function getLangColor(lang) {
  return LANG_COLORS[lang] || "#888";
}

function classifyColor(level) {
  if (level === "Advanced") return { bg: "#0f2a1a", text: "#4ade80", border: "#166534" };
  if (level === "Intermediate") return { bg: "#1a1a0a", text: "#facc15", border: "#713f12" };
  return { bg: "#1a0a0a", text: "#f87171", border: "#7f1d1d" };
}

function AnimatedNumber({ value, duration = 1200 }) {
  const [display, setDisplay] = useState(0);
  const start = useRef(0);
  const raf = useRef(null);
  useEffect(() => {
    start.current = Date.now();
    const animate = () => {
      const elapsed = Date.now() - start.current;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(eased * value));
      if (progress < 1) raf.current = requestAnimationFrame(animate);
    };
    raf.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf.current);
  }, [value, duration]);
  return <>{display.toLocaleString()}</>;
}

function CircleScore({ score, label, color }) {
  const r = 36, cx = 44, cy = 44, circumference = 2 * Math.PI * r;
  const [animScore, setAnimScore] = useState(0);
  useEffect(() => {
    let frame;
    const start = Date.now();
    const animate = () => {
      const t = Math.min((Date.now() - start) / 1000, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setAnimScore(Math.round(eased * score));
      if (t < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [score]);
  const offset = circumference - (animScore / 100) * circumference;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
      <svg width="88" height="88" viewBox="0 0 88 88" aria-hidden="true">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1e2a1e" strokeWidth="6" />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 44 44)"
          style={{ transition: "stroke-dashoffset 0.05s linear" }} />
        <text x={cx} y={cy + 1} textAnchor="middle" dominantBaseline="middle"
          fill={color} fontSize="15" fontWeight="600" fontFamily="monospace">{animScore}</text>
      </svg>
      <span style={{ fontSize: 11, color: "#6b7280", letterSpacing: "0.08em", textTransform: "uppercase", fontFamily: "monospace" }}>{label}</span>
    </div>
  );
}

function LanguageBar({ languages }) {
  const total = Object.values(languages).reduce((a, b) => a + b, 0);
  const sorted = Object.entries(languages).sort((a, b) => b[1] - a[1]).slice(0, 8);
  return (
    <div>
      <div style={{ display: "flex", height: 10, borderRadius: 5, overflow: "hidden", marginBottom: 14, gap: 1 }}>
        {sorted.map(([lang, count]) => (
          <div key={lang} title={`${lang}: ${((count / total) * 100).toFixed(1)}%`}
            style={{ width: `${(count / total) * 100}%`, background: getLangColor(lang), minWidth: 2 }} />
        ))}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px 16px" }}>
        {sorted.map(([lang, count]) => (
          <div key={lang} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: getLangColor(lang), display: "inline-block" }} />
            <span style={{ fontSize: 12, color: "#9ca3af", fontFamily: "monospace" }}>{lang}</span>
            <span style={{ fontSize: 12, color: "#6b7280", fontFamily: "monospace" }}>{((count / total) * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function RepoTable({ repos }) {
  const [sort, setSort] = useState({ key: "stargazers_count", dir: -1 });
  const sorted = [...repos].sort((a, b) => {
    const av = a[sort.key] ?? "";
    const bv = b[sort.key] ?? "";
    return av < bv ? sort.dir : av > bv ? -sort.dir : 0;
  });
  const toggleSort = (key) => setSort(s => ({ key, dir: s.key === key ? -s.dir : -1 }));
  const arrow = (key) => sort.key === key ? (sort.dir === -1 ? " ↓" : " ↑") : "";
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, fontFamily: "monospace" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #1f2e1f" }}>
            {[["name", "Repository"], ["stargazers_count", "Stars"], ["language", "Language"], ["updated_at", "Updated"]].map(([k, label]) => (
              <th key={k} onClick={() => toggleSort(k)} style={{ textAlign: "left", padding: "8px 12px", color: "#4b5563", fontSize: 11, letterSpacing: "0.06em", textTransform: "uppercase", cursor: "pointer", whiteSpace: "nowrap", userSelect: "none" }}>
                {label}{arrow(k)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((repo, i) => (
            <tr key={repo.name} style={{ borderBottom: "1px solid #111a11", background: i % 2 === 0 ? "transparent" : "rgba(0,255,0,0.015)" }}>
              <td style={{ padding: "9px 12px", color: "#86efac", fontWeight: 500 }}>
                <a href={`https://github.com/octocat/${repo.name}`} style={{ color: "#86efac", textDecoration: "none" }} onClick={e => { e.preventDefault(); }}>
                  {repo.name}
                </a>
              </td>
              <td style={{ padding: "9px 12px", color: "#f0fdf4" }}>
                <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <span style={{ color: "#facc15" }}>★</span> {(repo.stargazers_count ?? 0).toLocaleString()}
                </span>
              </td>
              <td style={{ padding: "9px 12px" }}>
                {repo.language ? (
                  <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span style={{ width: 8, height: 8, borderRadius: "50%", background: getLangColor(repo.language), display: "inline-block" }} />
                    <span style={{ color: "#d1fae5" }}>{repo.language}</span>
                  </span>
                ) : <span style={{ color: "#374151" }}>—</span>}
              </td>
              <td style={{ padding: "9px 12px", color: "#6b7280" }}>
                {repo.updated_at ? new Date(repo.updated_at).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }) : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function InsightsPanel({ text }) {
  const lines = text.split("\n");
  return (
    <div style={{ fontFamily: "monospace", fontSize: 13, lineHeight: 1.8, color: "#9ca3af" }}>
      {lines.map((line, i) => {
        const parts = line.split(/(\*\*[^*]+\*\*)/g);
        return (
          <p key={i} style={{ margin: "0 0 8px" }}>
            {parts.map((p, j) =>
              p.startsWith("**") && p.endsWith("**")
                ? <span key={j} style={{ color: "#86efac", fontWeight: 600 }}>{p.slice(2, -2)}</span>
                : p
            )}
          </p>
        );
      })}
    </div>
  );
}

function Typewriter({ text, speed = 18 }) {
  const [shown, setShown] = useState("");
  useEffect(() => {
    setShown("");
    let i = 0;
    const iv = setInterval(() => {
      setShown(text.slice(0, ++i));
      if (i >= text.length) clearInterval(iv);
    }, speed);
    return () => clearInterval(iv);
  }, [text]);
  return <span style={{ fontFamily: "monospace", color: "#4ade80" }}>{shown}<span style={{ animation: "blink 1s step-end infinite" }}>_</span></span>;
}

function StatCard({ icon, label, value, sub }) {
  return (
    <div style={{ background: "#0a0f0a", border: "1px solid #1a2a1a", borderRadius: 10, padding: "14px 16px", display: "flex", flexDirection: "column", gap: 4 }}>
      <span style={{ fontSize: 20 }}>{icon}</span>
      <span style={{ fontSize: 11, color: "#4b5563", letterSpacing: "0.06em", textTransform: "uppercase", fontFamily: "monospace", marginTop: 4 }}>{label}</span>
      <span style={{ fontSize: 22, fontWeight: 700, color: "#f0fdf4", fontFamily: "monospace", letterSpacing: "-0.02em" }}>
        <AnimatedNumber value={typeof value === "number" ? value : parseInt(value)} />
        {sub && <span style={{ fontSize: 12, color: "#6b7280", marginLeft: 4 }}>{sub}</span>}
      </span>
    </div>
  );
}

function LoadingDots() {
  const [dots, setDots] = useState(".");
  useEffect(() => {
    const iv = setInterval(() => setDots(d => d.length >= 3 ? "." : d + "."), 400);
    return () => clearInterval(iv);
  }, []);
  return <span style={{ fontFamily: "monospace", color: "#4ade80", fontSize: 14 }}>Analyzing{dots}</span>;
}

export default function GitHubAnalyzer() {
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  const inputRef = useRef(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const analyze = async () => {
    if (!username.trim()) return;
    setLoading(true);
    setError("");
    setData(null);
    await new Promise(r => setTimeout(r, 1800));
    const key = username.trim().toLowerCase();
    const found = MOCK_DATA[key] || (Object.keys(MOCK_DATA).find(k => k.includes(key)) && MOCK_DATA[Object.keys(MOCK_DATA).find(k => k.includes(key))]);
    if (found) {
      setData(found);
      setActiveTab("overview");
    } else {
      setError(`User "${username.trim()}" not found. Try "octocat" or "torvalds".`);
    }
    setLoading(false);
  };

  const reset = () => { setData(null); setError(""); setUsername(""); setTimeout(() => inputRef.current?.focus(), 50); };
  const badge = data ? classifyColor(data.classification) : null;

  return (
    <div style={{ minHeight: "100vh", background: "#050a05", color: "#f0fdf4", fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace", padding: "0" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        @keyframes blink { 0%, 100% { opacity: 1 } 50% { opacity: 0 } }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(16px) } to { opacity: 1; transform: none } }
        @keyframes scanline { 0% { transform: translateY(-100%) } 100% { transform: translateY(100vh) } }
        .fade-up { animation: fadeUp 0.5s ease both; }
        .tab-btn { background: none; border: none; cursor: pointer; padding: 8px 16px; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; font-family: inherit; transition: all 0.15s; }
        .tab-btn:hover { color: #86efac; }
        .analyze-btn { background: #052305; border: 1px solid #166534; color: #4ade80; padding: 0 24px; height: 44px; font-size: 13px; font-family: inherit; letter-spacing: 0.08em; border-radius: 8px; cursor: pointer; transition: all 0.2s; text-transform: uppercase; }
        .analyze-btn:hover { background: #0a3a0a; border-color: #22c55e; }
        .analyze-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .gh-input { background: #0a0f0a; border: 1px solid #1a2a1a; color: #f0fdf4; padding: 0 16px; height: 44px; font-size: 14px; font-family: inherit; border-radius: 8px; outline: none; transition: border-color 0.2s; width: 100%; }
        .gh-input:focus { border-color: #166534; }
        .gh-input::placeholder { color: #374151; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #050a05; }
        ::-webkit-scrollbar-thumb { background: #1a2a1a; border-radius: 2px; }
      `}</style>

      <div style={{ maxWidth: 860, margin: "0 auto", padding: "0 20px 60px" }}>
        {/* Header */}
        <div style={{ padding: "32px 0 28px", borderBottom: "1px solid #0f1f0f" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 4 }}>
            <span style={{ fontSize: 18, fontWeight: 700, color: "#4ade80", letterSpacing: "-0.02em" }}>github</span>
            <span style={{ color: "#1a2a1a", fontSize: 18 }}>/</span>
            <span style={{ fontSize: 18, fontWeight: 700, color: "#86efac", letterSpacing: "-0.02em" }}>analyzer</span>
            <span style={{ fontSize: 10, background: "#0f2a1a", color: "#22c55e", border: "1px solid #166534", padding: "2px 8px", borderRadius: 4, marginLeft: 4, letterSpacing: "0.1em" }}>v2.1.0</span>
          </div>
          <p style={{ fontSize: 12, color: "#374151", margin: 0, letterSpacing: "0.04em" }}>
            $ profile analysis · scoring · ai insights · language distribution
          </p>
        </div>

        {/* Search */}
        <div style={{ padding: "28px 0 24px" }}>
          <div style={{ display: "flex", gap: 10, maxWidth: 520 }}>
            <div style={{ flex: 1, position: "relative" }}>
              <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "#374151", fontSize: 14, pointerEvents: "none" }}>$</span>
              <input ref={inputRef} className="gh-input" style={{ paddingLeft: 28 }}
                value={username} onChange={e => setUsername(e.target.value)} placeholder="github username"
                onKeyDown={e => e.key === "Enter" && !loading && analyze()} />
            </div>
            <button className="analyze-btn" onClick={analyze} disabled={loading || !username.trim()}>
              {loading ? "..." : "Analyze →"}
            </button>
            {data && <button className="analyze-btn" onClick={reset} style={{ background: "none", borderColor: "#1a2a1a", color: "#4b5563" }}>Reset</button>}
          </div>
          {error && (
            <div style={{ marginTop: 12, padding: "10px 14px", background: "#1a0505", border: "1px solid #7f1d1d", borderRadius: 8, fontSize: 13, color: "#f87171" }}>
              ⚠ {error}
            </div>
          )}
          {loading && (
            <div style={{ marginTop: 14, fontSize: 13, color: "#374151" }}>
              <LoadingDots />
            </div>
          )}
        </div>

        {/* Results */}
        {data && (
          <div className="fade-up">
            {/* Profile Header */}
            <div style={{ display: "flex", alignItems: "flex-start", gap: 20, padding: "20px 0 24px", borderBottom: "1px solid #0f1f0f" }}>
              <img src={data.profile.avatar_url} alt={data.profile.name} style={{ width: 72, height: 72, borderRadius: "50%", border: "2px solid #1a2a1a", flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 20, fontWeight: 700, color: "#f0fdf4", letterSpacing: "-0.02em" }}>{data.profile.name}</span>
                  <span style={{ fontSize: 13, color: "#4b5563" }}>@{data.profile.login}</span>
                  <span style={{ fontSize: 11, padding: "3px 10px", borderRadius: 6, fontWeight: 600, letterSpacing: "0.06em", background: badge.bg, color: badge.text, border: `1px solid ${badge.border}` }}>
                    {data.classification}
                  </span>
                </div>
                {data.profile.bio && <p style={{ fontSize: 13, color: "#6b7280", margin: "6px 0 10px", lineHeight: 1.5 }}>{data.profile.bio}</p>}
                <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
                  {[
                    ["followers", data.profile.followers.toLocaleString()],
                    ["following", data.profile.following.toLocaleString()],
                    ["repos", data.profile.public_repos],
                  ].map(([k, v]) => (
                    <span key={k} style={{ fontSize: 12, color: "#6b7280" }}>
                      <span style={{ color: "#f0fdf4", fontWeight: 600 }}>{v}</span> {k}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div style={{ display: "flex", gap: 0, borderBottom: "1px solid #0f1f0f", marginBottom: 24 }}>
              {[["overview", "Overview"], ["repos", "Repositories"], ["insights", "AI Insights"]].map(([id, label]) => (
                <button key={id} className="tab-btn" onClick={() => setActiveTab(id)}
                  style={{ color: activeTab === id ? "#4ade80" : "#374151", borderBottom: activeTab === id ? "2px solid #4ade80" : "2px solid transparent", marginBottom: -1 }}>
                  {label}
                </button>
              ))}
            </div>

            {/* Overview Tab */}
            {activeTab === "overview" && (
              <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
                {/* Stat cards */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 10 }}>
                  <StatCard icon="⭐" label="Total Stars" value={data.total_stars} />
                  <StatCard icon="🍴" label="Total Forks" value={data.total_forks} />
                  <StatCard icon="📅" label="Account Age" value={data.account_age_years} sub="yrs" />
                  <StatCard icon="📦" label="Public Repos" value={data.profile.public_repos} />
                </div>

                {/* Scores */}
                <div style={{ background: "#0a0f0a", border: "1px solid #1a2a1a", borderRadius: 10, padding: "20px 24px" }}>
                  <p style={{ fontSize: 11, color: "#4b5563", letterSpacing: "0.08em", textTransform: "uppercase", margin: "0 0 16px" }}>Score Analysis</p>
                  <div style={{ display: "flex", justifyContent: "space-around", flexWrap: "wrap", gap: 16 }}>
                    <CircleScore score={data.scores.documentation} label="Docs" color="#4ade80" />
                    <CircleScore score={data.scores.consistency} label="Consistency" color="#60a5fa" />
                    <CircleScore score={data.scores.complexity} label="Complexity" color="#a78bfa" />
                    <CircleScore score={Math.round(data.scores.documentation * 0.3 + data.scores.consistency * 0.35 + data.scores.complexity * 0.35)} label="Overall" color="#fb923c" />
                  </div>
                </div>

                {/* Languages */}
                <div style={{ background: "#0a0f0a", border: "1px solid #1a2a1a", borderRadius: 10, padding: "20px 24px" }}>
                  <p style={{ fontSize: 11, color: "#4b5563", letterSpacing: "0.08em", textTransform: "uppercase", margin: "0 0 14px" }}>Language Distribution</p>
                  <LanguageBar languages={data.languages} />
                </div>
              </div>
            )}

            {/* Repos Tab */}
            {activeTab === "repos" && (
              <div style={{ background: "#0a0f0a", border: "1px solid #1a2a1a", borderRadius: 10, overflow: "hidden" }}>
                <div style={{ padding: "14px 16px", borderBottom: "1px solid #0f1f0f" }}>
                  <span style={{ fontSize: 11, color: "#4b5563", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                    {data.repos.length} repositories · click column headers to sort
                  </span>
                </div>
                <RepoTable repos={data.repos} />
              </div>
            )}

            {/* AI Insights Tab */}
            {activeTab === "insights" && (
              <div style={{ background: "#0a0f0a", border: "1px solid #1a2a1a", borderRadius: 10, padding: "20px 24px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
                  <span style={{ fontSize: 11, color: "#4b5563", letterSpacing: "0.08em", textTransform: "uppercase" }}>AI Insights</span>
                  <span style={{ fontSize: 10, background: "#0f1a2a", color: "#60a5fa", border: "1px solid #1e3a5f", padding: "2px 8px", borderRadius: 4 }}>llama3</span>
                </div>
                <div style={{ borderLeft: "2px solid #166534", paddingLeft: 16 }}>
                  <InsightsPanel text={data.ai_insights} />
                </div>
              </div>
            )}

            {/* Terminal footer */}
            <div style={{ marginTop: 32, padding: "12px 16px", background: "#070c07", border: "1px solid #0f1f0f", borderRadius: 8, fontSize: 11, color: "#1f3f1f", fontFamily: "monospace" }}>
              $ github-analyzer {data.profile.login} --export --ai ·{" "}
              <span style={{ color: "#166534" }}>analysis complete</span> ·{" "}
              <Typewriter text={`overall score: ${Math.round(data.scores.documentation * 0.3 + data.scores.consistency * 0.35 + data.scores.complexity * 0.35)}/100`} speed={30} />
            </div>
          </div>
        )}

        {!data && !loading && !error && (
          <div style={{ paddingTop: 40, color: "#1a2a1a", fontSize: 13, lineHeight: 2, fontFamily: "monospace" }}>
            <div>$ # Try: octocat · torvalds</div>
            <div>$ # Enter a username above and press Enter</div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span>$</span>
              <span style={{ color: "#4ade80", animation: "blink 1s step-end infinite" }}>_</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}