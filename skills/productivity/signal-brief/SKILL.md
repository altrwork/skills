---
name: signal-brief
description: Research AI themes trending on X and Substack, synthesize into a ranked brief by category, and write a dated .md file to raw/signals/. Spawns a subagent to protect the main context window. Requires X_BEARER_TOKEN in environment.
metadata:
  author: altr
  version: "1.1"
---

When this skill is invoked, check prerequisites, then spawn a research subagent that pulls AI signal data from X and Substack, synthesizes a ranked brief, and writes it to `raw/signals/`. All heavy work happens in the subagent — the main context window stays clean. After the subagent finishes, confirm the output file path to the user.

---

# Signal Brief Skill

## Prerequisites

This skill requires `X_BEARER_TOKEN` in the environment. Before spawning the subagent, run:

```bash
echo ${X_BEARER_TOKEN:0:8}
```

If the output is empty or blank, stop and tell the user:

> "X_BEARER_TOKEN is not set. Add it to ~/.claude/settings.json under the `env` key:
> ```json
> { \"env\": { \"X_BEARER_TOKEN\": \"your-bearer-token-here\" } }
> ```
> Then restart Claude Code and run /signal-brief again."

If the token is present, proceed to spawn the subagent.

---

## Spawn the research subagent

Spawn a subagent (claude model, default tools) with the following prompt. Replace `{{TODAY}}` with today's date in YYYY-MM-DD format.

---

**SUBAGENT PROMPT:**

You are a market intelligence agent for altr, an AI automation consultancy. Your job is to research what is trending about AI on X and Substack right now, then synthesize a ranked signal brief and write it to a file.

Today's date: {{TODAY}}
Output file: ./raw/signals/{{TODAY}}-signal-brief.md

The X API Bearer Token is available as the environment variable `$X_BEARER_TOKEN`. Use it directly in curl commands — do not print or log the token value.

Work through these steps in order.

---

### Step 1 — Get worldwide X trends

Call the X Trends API to get current global trends:

```bash
curl -s "https://api.twitter.com/2/trends/by/woeid/1" \
  -H "Authorization: Bearer $X_BEARER_TOKEN"
```

Parse the response. Extract all `trend_name` values. Flag any that relate to:
- **Broad AI:** artificial intelligence, AI, machine learning, LLM, GPT, ChatGPT, Claude, Gemini, deepfake, AI regulation, AI art, AI video
- **AI Tools & Productivity:** Cursor, Copilot, Notion AI, Perplexity, Midjourney, Sora, AI coding, vibe coding
- **AI for Business & Automation:** AI agents, AI automation, workflow, agentic, no-code, AI ROI, AI hiring, AI jobs

Record which trending topics map to which category. If a category has fewer than 1 match, you will supplement with a direct search query in Step 2.

---

### Step 2 — Search X for evidence posts

For each of the 3 categories, find the top 3 themes. Use trending topics from Step 1 where available. Supplement with direct search where needed.

Run one search query per theme (up to 9 searches total). Use this curl pattern — replace `QUERY` with a URL-encoded search string. Always use `max_results=100` and `sort_order=relevancy` to maximise the pool of posts before filtering:

```bash
curl -s "https://api.twitter.com/2/tweets/search/recent?query=QUERY%20lang%3Aen%20-is%3Aretweet%20-crypto%20-NFT%20-DeFi%20-blockchain%20-token&max_results=100&sort_order=relevancy&tweet.fields=text,created_at,public_metrics&expansions=author_id&user.fields=username,name" \
  -H "Authorization: Bearer $X_BEARER_TOKEN"
```

After each search, sort the returned `data[]` by `public_metrics.like_count` descending. Pick the top 2 posts where `like_count >= 50`. If fewer than 2 posts meet the threshold, lower to `like_count >= 10`. If still fewer than 2, take the top 2 by like count regardless and note the low engagement in Raw notes.

Suggested queries per category if trends are sparse (add these as URL-encoded strings in place of QUERY):

**Broad AI:**
- `%22artificial%20intelligence%22%20-crypto%20-NFT%20-DeFi%20-blockchain`
- `%22AI%20regulation%22%20OR%20%22AI%20safety%22%20-crypto%20-NFT`
- `ChatGPT%20OR%20%22OpenAI%22%20-crypto%20-NFT%20-DeFi`

**AI Tools & Productivity:**
- `%22Cursor%22%20%22AI%20coding%22%20-crypto%20-NFT`
- `%22Claude%20Code%22%20OR%20%22Anthropic%22%20-crypto%20-NFT`
- `%22Perplexity%22%20OR%20%22AI%20search%22%20-crypto%20-NFT`

**AI for Business & Automation:**
- `%22AI%20agents%22%20-crypto%20-NFT%20-DeFi%20-blockchain%20-token`
- `%22AI%20automation%22%20OR%20%22workflow%20automation%22%20-crypto%20-NFT`
- `%22AI%20for%20business%22%20OR%20%22enterprise%20AI%22%20-crypto%20-NFT`

The response includes a `data[]` array and an `includes.users[]` array. To construct the post URL, match `data[i].author_id` to `includes.users[j].id` to get the username, then build: `https://x.com/{username}/status/{id}`. Record: like count, post text (truncated to 200 chars if needed), author username, full URL.

---

### Step 3 — Search Substack for AI content

Run 3 WebSearches (one per category) to find recent high-signal Substack posts:

1. `site:substack.com artificial intelligence trends 2026`
2. `site:substack.com AI tools productivity 2026`
3. `site:substack.com AI automation business agents 2026`

For each search, pick the top 2 results. WebFetch each URL and extract: title, author, key argument in 1-2 sentences, URL, publish date if visible.

---

### Step 4 — Synthesize and rank

For each category, rank the 3 themes by signal strength (volume + recency + cross-platform appearance). A theme that appears on both X and Substack ranks higher than one from a single platform.

---

### Step 5 — Write the brief

Write the completed brief to:
`./raw/signals/{{TODAY}}-signal-brief.md`

Use this exact format:

```markdown
---
date: {{TODAY}}
platforms: X, Substack
generated_by: signal-brief skill
status: unreviewed
---

# AI Signal Brief — {{TODAY}}

> Use this brief as exploratory evidence for content planning. Do not publish directly.

---

## Broad AI

### 1. [Theme Name]
**Signal strength:** [High / Medium / Low]
**Platforms:** [X | Substack | Both]
**Pulled:** {{TODAY}}

**Evidence:**
- [Post or article excerpt, 1-2 sentences] — [@username or Author Name]([URL])
- [Post or article excerpt, 1-2 sentences] — [@username or Author Name]([URL])

---

### 2. [Theme Name]
...

### 3. [Theme Name]
...

---

## AI Tools & Productivity

### 1. [Theme Name]
...

### 2. [Theme Name]
...

### 3. [Theme Name]
...

---

## AI for Business & Automation

### 1. [Theme Name]
...

### 2. [Theme Name]
...

### 3. [Theme Name]
...

---

## Raw notes

[Any additional context, anomalies, or things worth flagging that didn't fit a theme slot]
```

After writing the file, confirm: "Signal brief written to raw/signals/{{TODAY}}-signal-brief.md"

---

**END OF SUBAGENT PROMPT**

---

## After the subagent completes

Report to the user:
> "Signal brief ready: `raw/signals/{{TODAY}}-signal-brief.md`"

If the subagent reports an API auth error, tell the user to verify their Bearer Token in `~/.claude/settings.json`.
