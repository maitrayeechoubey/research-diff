"""Rule-based digest rendering for a DiffResult. No LLM call needed to summarize what changed."""
from __future__ import annotations

from .diff import DiffResult


def render_digest(name: str, query: str, timestamp: str, diff: DiffResult) -> str:
    lines = [f"Research Diff: {name}", f"Query: {query}", f"Snapshot: {timestamp}", ""]

    if not diff.has_changes:
        lines.append("No material change since last run.")
        return "\n".join(lines) + "\n"

    lines.append(f"Answer similarity to previous run: {diff.text_similarity * 100:.1f}%")
    lines.append(f"Citation churn: {diff.citation_churn_pct}%")
    lines.append("")

    if diff.added_sources:
        lines.append(f"New sources ({len(diff.added_sources)}):")
        for url in diff.added_sources:
            lines.append(f"  + {url}")
        lines.append("")

    if diff.removed_sources:
        lines.append(f"Dropped sources ({len(diff.removed_sources)}):")
        for url in diff.removed_sources:
            lines.append(f"  - {url}")
        lines.append("")

    if diff.text_similarity < 0.999:
        lines.append("Answer text changes:")
        for line in diff.answer_diff_lines:
            if line.startswith(("+++", "---", "@@")):
                continue
            if line.startswith("+") or line.startswith("-"):
                lines.append(f"  {line}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
