# research-diff

**Track a Perplexity query as a persistent, versioned object — and watch how the web's answer changes over time.**

Perplexity (and every search-grounded LLM today) treats a query as a one-shot event: you ask, you get an answer + citations, the thread ends. But the interesting signal for any fast-moving topic isn't the answer at a single point in time — it's *how the answer and its sources change* as the story develops. Nobody currently treats a search query as a monitored, diffable, versioned artifact.

`research-diff` is a small CLI that does exactly that:

1. **`track`** a query under a name.
2. **`run`** it on a schedule (cron, launchd, GitHub Actions — whatever). Each run is saved as a snapshot.
3. Every run after the first automatically **diffs** against the previous snapshot: which sources were added/dropped, and how much the answer text actually changed (via similarity ratio + unified diff).
4. **`diff`** any two snapshots directly to see how the story evolved across an arbitrary window (e.g. week 1 vs. week 4).

The output is a plain-text digest — short enough to paste straight into a Slack update, a changelog, or a Perplexity Page — that answers "what's new since I last checked?" instead of forcing you to re-read the whole answer and eyeball the source list.

## Why this matters

Three concrete gaps this targets in how people currently use search-grounded LLMs:

- **No persistence across a research arc.** A live news story, an ongoing legal case, or an evolving technical debate gets re-asked from scratch every time — there's no diff-and-notify layer on a saved research object.
- **Citation churn is invisible.** Sources get added and dropped between two queries a week apart and nobody notices unless they compare the two answers side by side by hand.
- **"What changed and why" is a manual chore.** This makes it a one-command digest.

## Install

```bash
git clone <this-repo>
cd research-diff
pip install -e .
```

Zero third-party dependencies — stdlib only (`argparse`, `difflib`, `urllib`, `json`).

## Usage

### Live mode (requires a Perplexity API key)

```bash
export PPLX_API_KEY=your_key_here
research-diff track my-topic --query "What's the latest on <ongoing story>?"
research-diff run my-topic     # run this on a cron; each run diffs against the last
```

### Mock mode (no API key required — this is how the demo below was generated)

```bash
research-diff track agent-frameworks \
  --query "What is the current state of open-source LLM agent frameworks?" \
  --mock-fixture "$(pwd)/fixtures/agent_frameworks"

research-diff run agent-frameworks   # run this 4x to replay 4 canned "weekly" snapshots
```

Mock mode replays canned Sonar-style JSON responses from `fixtures/<topic>/snapshot_N.json` — one per call — so the diff/digest logic is fully demonstrable without live API access. The fixture content in `fixtures/agent_frameworks/` is **fabricated for this demo**; it is not real Perplexity output.

### Commands

| Command | What it does |
|---|---|
| `track <name> --query "..." [--mock-fixture <dir>]` | Start tracking a query |
| `run <name>` | Execute it, save a snapshot, print a digest vs. the previous run |
| `history <name>` | List all snapshot IDs for a tracked query |
| `diff <name> [--from <id>] [--to <id>]` | Diff any two snapshots directly (defaults to the last two) |
| `list` | List all tracked research objects |

Snapshots persist locally under `~/.research-diff/<name>/snapshots/`.

## Example digest output

```
Research Diff: agent-frameworks
Query: What is the current state of open-source LLM agent frameworks?
Snapshot: 0003_20260702T014452Z

Answer similarity to previous run: 22.4%
Citation churn: 40.0%

New sources (1):
  + https://example-benchmarks.org/agent-leaderboard

Dropped sources (1):
  - https://arxiv.org/abs/2210.03629

Answer text changes:
  -Open-source LLM agent frameworks are converging around a handful of patterns...
  +Open-source LLM agent frameworks have started to consolidate around graph-based orchestration...
```

See [`examples/demo_thread.md`](examples/demo_thread.md) for a full 4-week run written up as a shareable thread.

## Architecture

- `research_diff/client.py` — `PerplexityClient` (real Sonar API, needs `PPLX_API_KEY`) and `MockPerplexityClient` (replays fixtures). Both implement the same `search(query) -> SearchResult` interface, so swapping mock for live is a one-line config change (`--mock-fixture` vs. nothing).
- `research_diff/store.py` — local JSON persistence of tracked queries and their snapshot history.
- `research_diff/diff.py` — set-diff on citation URLs + `difflib` similarity ratio and unified diff on answer text.
- `research_diff/digest.py` — rule-based (no LLM call) rendering of a `DiffResult` into a human-readable digest.
- `research_diff/cli.py` — `argparse` CLI wiring it all together.

## What's next if this had API access

- Real Sonar API integration is already wired (`PerplexityClient`) — it just needs a paid key to exercise end-to-end.
- A follow-up "why did this change?" step could re-prompt Perplexity with the two answers and ask it to explain the delta, rather than relying on the rule-based digest.
- A GitHub Action / cron wrapper to auto-post digests to Slack or a Perplexity Page.

## License

MIT
