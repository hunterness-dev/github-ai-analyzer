import ollama


class OllamaAgent:
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.client = ollama.Client(host=base_url)

    # ---------------------------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------------------------

    def generate_insights(
        self,
        user: dict,
        stats: dict,
        scores: dict,
        lang_dist: dict,
        strongest: list,
    ) -> str:
        """Generate a summary or README-style insight depending on overall score."""
        prompt = self._build_prompt(user, stats, scores, lang_dist, strongest)
        return self._chat(prompt, fallback="Error generating insights")

    def explain_top_repo(
        self,
        user: dict,
        stats: dict,
        scores: dict,
        lang_dist: dict,
        strongest: list,
        top_repo: dict,
    ) -> str:
        """Explain why the developer's top repository stands out."""
        prompt = f"""
You are a developer profile analyst. Explain why this developer's top repository
is their best one, based on the stats below.

{self._stats_block(user, stats, scores, lang_dist, strongest)}
Top repository : {top_repo.get('name')}
Description    : {top_repo.get('description', 'N/A')}
Stars          : {top_repo.get('stargazers_count', 0)}
Language       : {top_repo.get('language', 'N/A')}

Focus on what makes this repo stand out compared to the others.
""".strip()
        return self._chat(prompt, fallback="Error explaining top repository")

    def explain_weaknesses(
        self,
        user: dict,
        stats: dict,
        scores: dict,
        lang_dist: dict,
        strongest: list,
    ) -> str:
        """Identify the main weaknesses in the developer's profile."""
        prompt = f"""
You are a developer profile analyst. Identify the main weaknesses in this
developer's GitHub profile and give specific, actionable suggestions.

{self._stats_block(user, stats, scores, lang_dist, strongest)}
""".strip()
        return self._chat(prompt, fallback="Error explaining weaknesses")
    
    def explain_strengths(
        self,
        user: dict,
        stats: dict,
        scores: dict,
        lang_dist: dict,
        strongest: list,
    ) -> str:
        """Identify the main strengths in the developer's profile."""
        prompt = f"""
You are a developer profile analyst. Identify the main strengths in this
developer's GitHub profile and give specific, actionable suggestions.

{self._stats_block(user, stats, scores, lang_dist, strongest)}
""".strip()
        return self._chat(prompt, fallback="Error explaining strengths")

    # ---------------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------------

    def _chat(self, prompt: str, fallback: str = "Error") -> str:
        """Send a prompt to Ollama and return the response text."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response["message"]["content"]
        except ollama.ResponseError as e:
            return f"{fallback}: {e}"

    def _build_prompt(
        self,
        user: dict,
        stats: dict,
        scores: dict,
        lang_dist: dict,
        strongest: list,
    ) -> str:
        """Route to README or summary prompt based on overall score."""
        if scores.get("overall_score", 0) >= 80:
            return self._readme_prompt(user, stats, scores, lang_dist, strongest)
        return self._summary_prompt(user, stats, scores, lang_dist, strongest)

    def _stats_block(
        self,
        user: dict,
        stats: dict,
        scores: dict,
        lang_dist: dict,
        strongest: list,
    ) -> str:
        """Shared stats block used across prompts."""
        return f"""
Username             : {user.get('login')}
Total repos          : {stats.get('total_repos')}
Total stars          : {stats.get('total_stars')}
Top languages        : {list(lang_dist.keys())[:5]}
Strongest techs      : {strongest}
Overall score        : {scores.get('overall_score')} / 100
Level                : {scores.get('level')}
Documentation score  : {scores.get('documentation_score')}
Consistency score    : {scores.get('consistency_score')}
Complexity score     : {scores.get('complexity_score')}
""".strip()

    def _summary_prompt(
        self,
        user: dict,
        stats: dict,
        scores: dict,
        lang_dist: dict,
        strongest: list,
    ) -> str:
        return f"""
You are a developer profile analyst. Write a short, honest summary of this
developer's profile in 3–5 sentences. Be specific, not generic.

{self._stats_block(user, stats, scores, lang_dist, strongest)}
""".strip()

    def _readme_prompt(
        self,
        user: dict,
        stats: dict,
        scores: dict,
        lang_dist: dict,
        strongest: list,
    ) -> str:
        return f"""
You are a developer profile analyst. Write a README-style summary of this
developer's profile with sections: "About Me", "Skills", and "GitHub Highlights".
Be specific, not generic.

{self._stats_block(user, stats, scores, lang_dist, strongest)}
""".strip()