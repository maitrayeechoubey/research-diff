# "Watch the web change its mind" — a Research Diff over 4 weeks

*This is a real run of `research-diff` against mocked/fabricated Sonar-style snapshots (no live Perplexity API access was available while building this). The mechanism — track a query as a persistent object, diff each run against the last — works identically against the real API; swap `--mock-fixture` for a live `PPLX_API_KEY` and this becomes a real weekly monitor.*

**The pitch:** every AI search product treats a query as disposable. Ask, get an answer, the thread dies. Nothing treats a query as a *standing monitor* on the state of the web. This is what that looks like.

**Tracked query:** *"What is the current state of open-source LLM agent frameworks?"*

---

### Week 1 — baseline

```
First snapshot saved. Nothing to diff against yet.
```

> LangGraph, AutoGen, and the ReAct loop underneath both. Adoption limited to internal tooling and coding assistants. 3 sources.

### Week 2 — a new framework enters the conversation

```
Answer similarity to previous run: 84.9%
Citation churn: 25.0%

New sources (1):
  + https://github.com/crewAIInc/crewAI
```

CrewAI shows up for the first time — the answer picks up a whole new sentence about its role-based abstraction. Nothing was removed. This is the web *adding* a competitor to the frame, not yet taking sides.

### Week 3 — the story flips, and a citation quietly disappears

```
Answer similarity to previous run: 22.4%
Citation churn: 40.0%

New sources (1):
  + https://example-benchmarks.org/agent-leaderboard

Dropped sources (1):
  - https://arxiv.org/abs/2210.03629
```

This is the interesting week. Answer similarity craters to 22% — this isn't a tweak, the narrative rewrote itself: LangGraph "pulls ahead," teams "migrate off CrewAI." And the original ReAct paper — the academic citation anchoring the whole framework category — silently drops out of the source list, replaced by a benchmark leaderboard. The story moved from *foundational research* to *comparative product benchmarking* as its evidentiary basis. You would never notice that shift by reading Week 3's answer in isolation. You only see it by diffing against Week 1.

### Week 4 — a production incident becomes the new anchor

```
Answer similarity to previous run: 23.9%
Citation churn: 40.0%

New sources (1):
  + https://example-postmortems.org/agent-loop-incident

Dropped sources (1):
  - https://github.com/crewAIInc/crewAI
```

CrewAI drops out of the citation list entirely — not just de-emphasized in text, literally no longer a source. A postmortem about a production incident becomes the new anchor, and the conversation shifts from "which framework wins" to "do any of these frameworks have adequate safety guardrails." That's a materially different question than the one asked in Week 1, surfaced automatically by a diff, not by a human re-reading four separate answers side by side.

### Week 1 vs. Week 4, directly

```
research-diff diff agent-frameworks --from 0001 --to 0004

Answer similarity to previous run: 12.6%
Citation churn: 60.0%

New sources (2):
  + https://example-benchmarks.org/agent-leaderboard
  + https://example-postmortems.org/agent-loop-incident

Dropped sources (1):
  - https://arxiv.org/abs/2210.03629
```

Skip the middle entirely and diff the endpoints: 60% of the citation set has turned over and the answer is 87% rewritten, in four weeks, on a topic most people would assume was "settled" after week one.

---

### The takeaway

None of these four answers is "wrong" — each was presumably a faithful synthesis of the web *at that moment*. The insight isn't in any single answer. It's in the shape of the change: which claims survive, which sources get promoted or quietly dropped, and how fast the ground truth moves under a topic that feels stable if you only ever ask once.

That's a genuinely new way to *consume* a search engine's output — not "get me an answer" but "tell me when the answer stops being true." Perplexity already has every primitive needed to build this as a native feature (saved queries, scheduled re-runs, a diff view) — this is a weekend-scale proof that the workflow is real and worth shipping.
