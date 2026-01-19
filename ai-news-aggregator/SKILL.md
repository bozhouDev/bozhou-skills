---
name: ai-news-aggregator
description: Automated AI news aggregation from 30+ premium sources (TLDR AI, Ben's Bites, Hugging Face Papers, newsletters, podcasts, and thought leadership blogs). Fetches articles from RSS feeds, APIs, and web pages with incremental updates, deduplication, and automatic Chinese translation. Use when the user wants to (1) sync AI news updates, (2) check for new articles, (3) fetch latest content from configured sources, (4) set up scheduled news aggregation, or (5) mentions keywords like "AI news", "sync articles", "fetch updates", "news aggregator".
---

# AI News Aggregator

Fetch, deduplicate, translate, and aggregate articles from 30+ curated AI and tech sources into Markdown format.

## Quick Start

Run the aggregator manually:

```bash
python3 scripts/scraper.py
```

Output will be saved to `~/Documents/ai-news/updates.md` by default.

## Configuration

### Translation API

The translator uses OpenAI-compatible APIs. Configure via:
- Edit `scripts/translator.py` directly (default values)
- Or set environment variables:
  ```bash
  export TRANSLATION_BASE_URL="https://api.your-provider.com"
  export TRANSLATION_API_KEY="your-api-key"
  export TRANSLATION_MODEL="your-model-name"
  ```

### Sources

All sources are defined in `references/sources.yaml`. The file includes:
- **Type**: `rss`, `api`, or `web`
- **Frequency**: `daily` or `weekly`
- **Parser**: Custom parser name for web sources
- **Additional options**: `min_votes`, `limit`, etc.

To add/remove sources, edit `references/sources.yaml`.

### Output Location

Override default output paths with environment variables:
```bash
export SOURCES_CONFIG="/path/to/sources.yaml"
export STATE_FILE="/path/to/state.json"
export OUTPUT_FILE="/path/to/output.md"
```

## Scheduled Execution

Set up daily automatic execution with `scheduler.py`:

```bash
python3 scripts/scheduler.py
```

**macOS**: Creates a LaunchAgent that runs daily at 9:00 AM.
- Plist saved to `~/Library/LaunchAgents/com.user.ai-news-aggregator.plist`
- Load with: `launchctl load ~/Library/LaunchAgents/com.user.ai-news-aggregator.plist`
- View logs at `/tmp/ai-news-aggregator.log`

**Linux**: Generates cron configuration for daily 9:00 AM execution.
- Add to crontab: `crontab -e`

## How It Works

1. **Fetch**: Scrapes all sources concurrently (RSS, API, web)
2. **Deduplicate**: Compares URL + date hash against state file
3. **Translate**: Sends new article titles to LLM for Chinese translation (cached)
4. **Output**: Appends to Markdown file, grouped by source
5. **State**: Updates seen articles in state file

## Dependencies

Install required packages:
```bash
pip install feedparser requests beautifulsoup4 pyyaml openai
```

## Scripts

- `scraper.py`: Main aggregation script
- `translator.py`: Translation module with caching
- `scheduler.py`: Platform-specific scheduler setup

## State Management

State file (`~/.ai-news-cache/state.json`) tracks:
- Seen articles (URL + date hashes)
- Last run timestamp
- Translation cache (in `~/.ai-news-cache/translations.json`)

Delete state file to re-fetch all articles.
