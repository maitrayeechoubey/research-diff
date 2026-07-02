"""Perplexity Sonar API client, with a mock fallback for demos without an API key."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Citation:
    url: str
    title: str = ""
    snippet: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Citation":
        return cls(url=d["url"], title=d.get("title", ""), snippet=d.get("snippet", ""))

    def to_dict(self) -> dict:
        return {"url": self.url, "title": self.title, "snippet": self.snippet}


@dataclass
class SearchResult:
    query: str
    answer: str
    citations: list[Citation] = field(default_factory=list)
    model: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "SearchResult":
        return cls(
            query=d["query"],
            answer=d["answer"],
            citations=[Citation.from_dict(c) for c in d.get("citations", [])],
            model=d.get("model", ""),
        )

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "answer": self.answer,
            "citations": [c.to_dict() for c in self.citations],
            "model": self.model,
        }


class PerplexityClient:
    """Real Sonar API client. Requires PPLX_API_KEY in the environment."""

    API_URL = "https://api.perplexity.ai/chat/completions"

    def __init__(self, api_key: Optional[str] = None, model: str = "sonar-pro"):
        self.api_key = api_key or os.environ.get("PPLX_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "No PPLX_API_KEY set. Export it, or track this object with --mock-fixture "
                "to run against local fixtures instead."
            )
        self.model = model

    def search(self, query: str) -> SearchResult:
        payload = {"model": self.model, "messages": [{"role": "user", "content": query}]}
        req = urllib.request.Request(
            self.API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Perplexity API error {e.code}: {e.read().decode()}") from e

        answer = data["choices"][0]["message"]["content"]
        citations = [Citation(url=u) for u in data.get("citations", [])]
        return SearchResult(query=query, answer=answer, citations=citations, model=self.model)


class MockPerplexityClient:
    """
    Replays canned Sonar-style responses from fixtures/<topic>/snapshot_N.json,
    one snapshot per call index, so `research-diff run` can simulate a query
    evolving over multiple time points without live API access.
    """

    def __init__(self, fixture_dir: Path):
        self.fixture_dir = Path(fixture_dir)
        if not self.fixture_dir.exists():
            raise RuntimeError(f"Mock fixture directory not found: {fixture_dir}")
        self._snapshots = sorted(self.fixture_dir.glob("snapshot_*.json"))
        if not self._snapshots:
            raise RuntimeError(f"No snapshot_*.json files found in {fixture_dir}")

    def search(self, query: str, call_index: int = 0) -> SearchResult:
        idx = min(call_index, len(self._snapshots) - 1)
        data = json.loads(self._snapshots[idx].read_text())
        result = SearchResult.from_dict(data)
        result.query = query
        return result
