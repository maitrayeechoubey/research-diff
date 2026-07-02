"""
Interactive demo of research-diff.

Run locally with: streamlit run streamlit_app.py
Deployable as-is to Streamlit Community Cloud (share.streamlit.io) -- no API
key or backend required, since it replays the fixture snapshots.
"""
import difflib
import json
from pathlib import Path

import streamlit as st

from research_diff.client import SearchResult
from research_diff.diff import diff_snapshots

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "agent_frameworks"

st.set_page_config(page_title="research-diff", page_icon="🔎", layout="centered")


@st.cache_data
def load_snapshots():
    paths = sorted(FIXTURE_DIR.glob("snapshot_*.json"))
    return [SearchResult.from_dict(json.loads(p.read_text())) for p in paths]


def render_word_diff(old_text: str, new_text: str) -> str:
    old_words, new_words = old_text.split(), new_text.split()
    matcher = difflib.SequenceMatcher(a=old_words, b=new_words)
    parts = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            parts.append(" ".join(new_words[j1:j2]))
        elif tag in ("delete", "replace"):
            parts.append(
                f'<span style="background-color:#fbdcdc;text-decoration:line-through;">'
                f'{" ".join(old_words[i1:i2])}</span>'
            )
            if tag == "replace":
                parts.append(
                    f'<span style="background-color:#d6f5d6;">{" ".join(new_words[j1:j2])}</span>'
                )
        elif tag == "insert":
            parts.append(
                f'<span style="background-color:#d6f5d6;">{" ".join(new_words[j1:j2])}</span>'
            )
    return " ".join(parts)


snapshots = load_snapshots()
weeks = [f"Week {i + 1}" for i in range(len(snapshots))]

st.title("🔎 research-diff")
st.caption("Track a Perplexity query as a persistent object. Watch how the web's answer changes over time.")
st.info(
    "This demo replays **fabricated** mock snapshots (no live Perplexity API call) to show the "
    "diff/monitor mechanism. Swap in a real `PPLX_API_KEY` in the CLI and this runs against live Sonar output.",
    icon="ℹ️",
)

st.markdown(f"**Tracked query:** _{snapshots[0].query}_")

if "week_idx" not in st.session_state:
    st.session_state.week_idx = 0

col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("⬅ Prev", disabled=st.session_state.week_idx == 0):
        st.session_state.week_idx -= 1
with col3:
    if st.button("Next ➡", disabled=st.session_state.week_idx == len(snapshots) - 1):
        st.session_state.week_idx += 1
with col2:
    st.session_state.week_idx = st.select_slider(
        "Snapshot",
        options=list(range(len(snapshots))),
        value=st.session_state.week_idx,
        format_func=lambda i: weeks[i],
        label_visibility="collapsed",
    )

idx = st.session_state.week_idx
current = snapshots[idx]

st.subheader(weeks[idx])
st.write(current.answer)

st.markdown("**Sources:**")
for c in current.citations:
    st.markdown(f"- [{c.title or c.url}]({c.url})")

if idx > 0:
    previous = snapshots[idx - 1]
    diff = diff_snapshots(previous, current)

    st.divider()
    st.markdown(f"### What changed since {weeks[idx - 1]}")

    m1, m2 = st.columns(2)
    m1.metric("Answer similarity", f"{diff.text_similarity * 100:.1f}%")
    m2.metric("Citation churn", f"{diff.citation_churn_pct}%")

    if diff.added_sources:
        st.markdown("**New sources:**")
        for u in diff.added_sources:
            st.markdown(f"- 🟢 {u}")
    if diff.removed_sources:
        st.markdown("**Dropped sources:**")
        for u in diff.removed_sources:
            st.markdown(f"- 🔴 {u}")

    st.markdown("**Answer text diff:**")
    st.markdown(render_word_diff(previous.answer, current.answer), unsafe_allow_html=True)

st.divider()
st.markdown("### Jump straight to endpoints")
c1, c2 = st.columns(2)
from_idx = c1.selectbox("From", options=list(range(len(snapshots))), format_func=lambda i: weeks[i], index=0)
to_idx = c2.selectbox(
    "To", options=list(range(len(snapshots))), format_func=lambda i: weeks[i], index=len(snapshots) - 1
)

if from_idx != to_idx:
    lo, hi = min(from_idx, to_idx), max(from_idx, to_idx)
    d = diff_snapshots(snapshots[lo], snapshots[hi])
    st.markdown(
        f"**{weeks[lo]} → {weeks[hi]}:** {d.text_similarity * 100:.1f}% answer similarity, "
        f"{d.citation_churn_pct}% citation churn"
    )
    st.markdown(render_word_diff(snapshots[lo].answer, snapshots[hi].answer), unsafe_allow_html=True)

st.divider()
st.caption("CLI + mock client, MIT licensed — github.com/<you>/research-diff")
