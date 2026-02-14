---
name: sophnet-dailynews
description: Generate a daily, high-signal Markdown news report by scraping a preset source list, filtering and deduplicating items, and writing `NewsReport/YYYY-MM-DD-news-report.md`. Use when the user asks for “daily news”, “tech/news digest”, “today’s links”, “what should I read”, "what happens today", or requests an automated curated report driven by `sources.json` + `cache.json`.
---

# Daily news report (Markdown)

## Quick start

1. Resolve the target date.
   - Accept `YYYY-MM-DD` from the user.
   - Default to local today.
2. Read `sources.json` and `cache.json` **with explicit paths**.
   - Always call the read tool with a `path` field (not `file_path`).
   - Resolve paths relative to this skill's directory (the folder containing this SKILL.md):
     - `read(path="<skill_dir>/sources.json")`
     - `read(path="<skill_dir>/cache.json")`
   - Where `<skill_dir>` is the absolute path to `skills/sophnet-dailynews/` in the current workspace.
3. Collect items in waves (Tier 1 → Tier 2 → Tier 3/browser) until the report has enough **high-quality** items.
4. Write `NewsReport/YYYY-MM-DD-news-report.md`.
5. Update `cache.json` (dedupe + historical stats).

## Files in this skill

- `sources.json`: tiers, batches, URLs, fetch method (`webfetch`/`browser`), extraction hint, enable/disable flags, and quality thresholds.
- `cache.json`: last run metadata, per-source stats, URL/content dedupe caches, and per-day article history.

## Common failure: `web_fetch` → `fetch failed`

This usually means the fetch tool hit one of these:

- a redirect it doesn’t follow (302)
- a method mismatch (some sites don’t like `HEAD`)
- bot protection / CDN quirks
- response too large / slow for the tool limits

This skill is tuned to avoid common failures:

- Prefer **HN RSS** over HTML (`https://news.ycombinator.com/rss`).
- Pin **HuggingFace Papers** to a concrete date URL to avoid redirects:
  - `https://huggingface.co/papers/date/{{date}}`
  - Replace `{{date}}` with the target date (`YYYY-MM-DD`) before fetching.

## Output contract

Produce exactly one Markdown file:

- Path: `NewsReport/YYYY-MM-DD-news-report.md`
- Target: `quality_thresholds.target_items` items (default 20)
- Include only items with `quality_score >= quality_thresholds.min_score_to_include` (default 3)

Each item must include:

- `title`
- `summary` (2–4 sentences, concrete and non-hypey)
- `key_points` (max 3)
- `url` (canonical if possible)
- `source_id`
- `keywords` (2–6)
- `quality_score` (1–5, integer)

## Collection workflow

### 1) Initialize

- Load `sources.json` → treat it as the source of truth.
- Load `cache.json` → use it for dedupe and stats.
- Create `NewsReport/` if missing.
- If `NewsReport/YYYY-MM-DD-news-report.md` already exists, either:
  - regenerate from scratch (preferred), or
  - append only if explicitly requested.

### 2) Fetch in waves (early stop)

Follow the tier order in `sources.json`:

- **Wave A (Tier 1 / batch_a + batch_b)**: high hit-rate sources first.
- If you still have fewer than ~15 included items after filtering, continue.
- **Wave B (Tier 2 / batch_a + batch_b)**: supplemental sources.
- If you still have fewer than `target_items`, continue.
- **Wave C (Tier 3 / browser sources)**: JS-rendered / blocked sources.

Stop fetching when you have:

- at least `target_items` included items, and
- at least `quality_thresholds.early_stop_threshold` total candidates evaluated (default 25), or you have exhausted all enabled sources.

### 3) Extract and normalize

For each enabled source entry:

- Fetch the page content using the configured `fetch_method`:
  - `webfetch`: normal HTTP fetch.
  - `browser`: render with a headless browser when available; otherwise skip with a recorded error.
- Apply the `extract` hint from the source entry (examples: `top_10`, `latest_5`, `latest_issue`, `today_top_5`).
- For each candidate item, normalize:
  - clean title (no site suffix noise)
  - canonical URL (strip tracking params when safe)
  - short summary + key points

**RSS-first rule (important):**

- For RSS sources, **do not** `web_fetch` the item URLs.
- Use the RSS item's title + description/summary as the source of truth.
- If the RSS description is too thin to summarize, either:
  - drop the item, or
  - keep it with a one-sentence, non-speculative summary based only on the RSS description.
- Only fetch item URLs if the source entry explicitly says `extract: fetch_items` (none do by default).

If a `webfetch` attempt fails:

- retry once (respect `fetch_config.webfetch.timeout_ms`)
- then mark the source as failed and continue (do not abort the whole report)

### 4) Filter, score, and dedupe

Apply these rules in order:

1. Reject obvious low-signal items (marketing fluff, generic science, job posts, thin announcements).
2. Score each remaining item (`quality_score` 1–5) with a consistent rubric:
   - 5: deeply useful + specific + actionable/insightful
   - 4: strong signal, worth reading
   - 3: decent, include only if you need more items
   - 1–2: exclude
3. Deduplicate:
   - exact URL match (including `cache.json:url_cache`)
   - near-duplicate title (treat ~80% similarity as duplicate; keep the higher-scored one)
   - optional content hash match (when you have the full text)

### 5) Select and sort

- Keep only items with `quality_score >= min_score_to_include`.
- Sort by `quality_score` descending.
- Break ties by source credibility (Tier 1 > Tier 2 > Tier 3) and recency.
- Take the top `target_items`.

## Markdown template

Use this structure:

```markdown
# Daily News Report (YYYY-MM-DD)

> Sources used: N | Candidates evaluated: M | Included: K
> Generated at: <local timestamp> | Skill: sophnet-dailynews

---

## 1. <Title>

- **Summary**: ...
- **Key Points**:
  1. ...
  2. ...
  3. ...
- **Source**: <source_id> — <url>
- **Keywords**: `k1` `k2` `k3`
- **Score**: 4/5
```

## Cache update rules (`cache.json`)

Update these fields every run:

- `last_run`: date, duration, items_collected, items_published, sources_used
- `source_stats[source_id]`: total_fetches, success_count, avg_items_per_fetch, avg_quality_score, last_fetch, last_success
- `url_cache.entries`: add included URLs (store timestamps; respect `_ttl_hours`)
- `content_hashes.entries`: add hashes when available (respect `_ttl_hours`)
- `article_history[YYYY-MM-DD]`: record the final included item list (at minimum: title + url + source_id + score)

## Editing sources (`sources.json`)

- Disable a flaky/low-quality source by setting `enabled: false` or moving it to `disabled`.
- Prefer fixing extraction hints before adding new sources.
- Keep Tier 1 small and high-signal; use Tier 2 for “fill”.

## Failure handling

- If a source 403s on `webfetch`, try `browser` (if available) or skip and record the error.
- If all enabled sources fail, still write a report header and an explicit “no items” section; do not silently succeed.
