from research_diff.client import Citation, SearchResult
from research_diff.diff import diff_snapshots
from research_diff.digest import render_digest


def make_result(answer: str, urls: list[str]) -> SearchResult:
    return SearchResult(query="q", answer=answer, citations=[Citation(url=u) for u in urls])


def test_no_changes():
    old = make_result("same answer", ["https://a.com", "https://b.com"])
    new = make_result("same answer", ["https://a.com", "https://b.com"])
    diff = diff_snapshots(old, new)
    assert not diff.has_changes
    assert diff.citation_churn_pct == 0.0


def test_added_and_removed_sources():
    old = make_result("answer one", ["https://a.com", "https://b.com"])
    new = make_result("answer one", ["https://a.com", "https://c.com"])
    diff = diff_snapshots(old, new)
    assert diff.added_sources == ["https://c.com"]
    assert diff.removed_sources == ["https://b.com"]
    assert diff.kept_sources == ["https://a.com"]
    assert diff.citation_churn_pct == 66.7


def test_text_similarity_drops_on_rewrite():
    old = make_result("the sky is blue today", ["https://a.com"])
    new = make_result("the ocean is deep and cold", ["https://a.com"])
    diff = diff_snapshots(old, new)
    assert diff.text_similarity < 0.5
    assert diff.has_changes


def test_digest_reports_no_change():
    old = make_result("same", ["https://a.com"])
    new = make_result("same", ["https://a.com"])
    diff = diff_snapshots(old, new)
    text = render_digest("demo", "q", "20260101T000000Z", diff)
    assert "No material change" in text


def test_digest_lists_new_and_dropped_sources():
    old = make_result("answer", ["https://a.com", "https://b.com"])
    new = make_result("answer", ["https://a.com", "https://c.com"])
    diff = diff_snapshots(old, new)
    text = render_digest("demo", "q", "20260101T000000Z", diff)
    assert "+ https://c.com" in text
    assert "- https://b.com" in text
