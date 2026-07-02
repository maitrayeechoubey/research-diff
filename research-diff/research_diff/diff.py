"""Diffing logic for comparing two snapshots of the same tracked research query."""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field

from .client import SearchResult


@dataclass
class DiffResult:
    added_sources: list[str] = field(default_factory=list)
    removed_sources: list[str] = field(default_factory=list)
    kept_sources: list[str] = field(default_factory=list)
    text_similarity: float = 1.0
    answer_diff_lines: list[str] = field(default_factory=list)

    @property
    def citation_churn_pct(self) -> float:
        total = len(self.added_sources) + len(self.removed_sources) + len(self.kept_sources)
        if total == 0:
            return 0.0
        return round(100 * (len(self.added_sources) + len(self.removed_sources)) / total, 1)

    @property
    def has_changes(self) -> bool:
        return bool(self.added_sources or self.removed_sources) or self.text_similarity < 0.999


def diff_snapshots(old: SearchResult, new: SearchResult) -> DiffResult:
    old_urls = {c.url for c in old.citations}
    new_urls = {c.url for c in new.citations}

    added = sorted(new_urls - old_urls)
    removed = sorted(old_urls - new_urls)
    kept = sorted(old_urls & new_urls)

    matcher = difflib.SequenceMatcher(a=old.answer.split(), b=new.answer.split())
    similarity = round(matcher.ratio(), 3)

    diff_lines = list(
        difflib.unified_diff(
            old.answer.splitlines(),
            new.answer.splitlines(),
            lineterm="",
            fromfile="previous",
            tofile="current",
        )
    )

    return DiffResult(
        added_sources=added,
        removed_sources=removed,
        kept_sources=kept,
        text_similarity=similarity,
        answer_diff_lines=diff_lines,
    )
