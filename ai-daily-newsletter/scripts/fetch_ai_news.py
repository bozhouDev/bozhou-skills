#!/usr/bin/env python3
"""AI Daily Newsletter - Unified news fetcher.

Fetches from 20+ AI sources: RSS feeds, Hacker News, GitHub Trending,
and HuggingFace Papers. Outputs unified JSON to stdout.

Usage:
    python3 fetch_ai_news.py [--hours 24] [--limit 20] [--outdir PATH]
"""

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from time import mktime
from html import unescape

import feedparser
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# AI keyword filter set
# ---------------------------------------------------------------------------
AI_KEYWORDS = re.compile(
    r"\b("
    r"AI|LLM|GPT|Claude|Agent|RAG|DeepSeek|Gemini|Llama|"
    r"Transformer|Diffusion|RLHF|MCP|Anthropic|OpenAI|"
    r"Machine\s*Learning|Deep\s*Learning|Neural\s*Net|"
    r"Foundation\s*Model|Fine[\s-]?tun|Embedding|Vector\s*DB|"
    r"Copilot|Midjourney|Stable\s*Diffusion|ChatGPT|"
    r"Mistral|Qwen|Phi-|Groq|vLLM|GGUF|LoRA|"
    r"Computer\s*Vision|NLP|MLOps|GenAI|Generative"
    r")\b",
    re.IGNORECASE,
)


def matches_ai(text: str) -> bool:
    """Return True if text contains an AI-related keyword."""
    return bool(AI_KEYWORDS.search(text or ""))


# ---------------------------------------------------------------------------
# RSS source registry
# ---------------------------------------------------------------------------
RSS_SOURCES = [
    # --- Tier 1: 主流 AI 媒体 ---
    {
        "url": "https://venturebeat.com/category/ai/feed/",
        "name": "VentureBeat AI",
        "category": "industry",
        "ai_filter": True,
    },
    {
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "name": "TechCrunch AI",
        "category": "industry",
        "ai_filter": True,
    },
    {
        "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "name": "The Verge AI",
        "category": "announcements",
    },
    {
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "name": "MIT Technology Review AI",
        "category": "research",
    },
    {
        "url": "https://artificialintelligence-news.com/feed/",
        "name": "AI News",
        "category": "announcements",
    },
    # --- AI 公司博客 ---
    {
        "url": "https://openai.com/blog/rss.xml",
        "name": "OpenAI Blog",
        "category": "announcements",
    },
    {
        "url": "https://www.anthropic.com/feed.xml",
        "name": "Anthropic",
        "category": "announcements",
    },
    {
        "url": "https://blog.google/technology/ai/rss/",
        "name": "Google AI Blog",
        "category": "announcements",
    },
    {
        "url": "https://deepmind.google/blog/rss.xml",
        "name": "DeepMind Blog",
        "category": "research",
    },
    {
        "url": "https://blogs.microsoft.com/ai/feed/",
        "name": "Microsoft AI Blog",
        "category": "announcements",
    },
    {
        "url": "https://ai.meta.com/blog/rss/",
        "name": "Meta AI Blog",
        "category": "tools",
    },
    # --- AI Newsletters ---
    {
        "url": "https://www.latent.space/feed",
        "name": "Latent Space AINews",
        "category": "industry",
        "filter_prefix": "[AINews]",
    },
    {
        "url": "https://www.interconnects.ai/feed",
        "name": "Interconnects",
        "category": "industry",
    },
    {
        "url": "https://www.oneusefulthing.org/feed",
        "name": "One Useful Thing",
        "category": "announcements",
    },
    {
        "url": "https://chinai.substack.com/feed",
        "name": "ChinAI",
        "category": "policy",
    },
    {
        "url": "https://www.deeplearning.ai/the-batch/feed/",
        "name": "The Batch (Andrew Ng)",
        "category": "industry",
    },
    # --- AI Bloggers ---
    {
        "url": "https://simonwillison.net/atom/everything/",
        "name": "Simon Willison",
        "category": "tools",
    },
    {
        "url": "https://garymarcus.substack.com/feed",
        "name": "Gary Marcus",
        "category": "policy",
    },
    # --- Papers (Arxiv) ---
    {
        "url": "http://export.arxiv.org/rss/cs.AI",
        "name": "Arxiv cs.AI",
        "category": "research",
    },
    {
        "url": "http://export.arxiv.org/rss/cs.LG",
        "name": "Arxiv cs.LG",
        "category": "research",
    },
    # --- Product ---
    {
        "url": "https://www.producthunt.com/feed",
        "name": "Product Hunt",
        "category": "tools",
    },
]


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------
def parse_date(entry) -> datetime | None:
    """Extract datetime from a feedparser entry."""
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime.fromtimestamp(mktime(val), tz=timezone.utc)
            except Exception:
                pass
    return None


# ---------------------------------------------------------------------------
# RSS fetcher
# ---------------------------------------------------------------------------
def fetch_rss(source: dict, cutoff: datetime, limit: int) -> list[dict]:
    """Fetch a single RSS source and return entries within the time window."""
    url = source["url"]
    results = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if len(results) >= limit:
                break

            title = entry.get("title", "No Title")

            # Optional prefix filter (e.g. Latent Space [AINews])
            prefix = source.get("filter_prefix")
            if prefix and not title.startswith(prefix):
                continue

            # Optional AI keyword filter
            if source.get("ai_filter"):
                text = f"{title} {entry.get('summary', '')}"
                if not matches_ai(text):
                    continue

            pub_date = parse_date(entry)
            if pub_date and pub_date < cutoff:
                continue

            summary_raw = entry.get("summary", "") or ""
            # Strip HTML tags from summary
            summary = BeautifulSoup(summary_raw, "html.parser").get_text()[:500]

            results.append({
                "source": source["name"],
                "category": source["category"],
                "title": unescape(title),
                "url": entry.get("link", ""),
                "time": pub_date.isoformat() if pub_date else "",
                "summary": summary,
            })
    except Exception as e:
        print(f"[RSS] Error fetching {source['name']} ({url}): {e}", file=sys.stderr)
    return results


# ---------------------------------------------------------------------------
# GitHub Trending
# ---------------------------------------------------------------------------
def fetch_readme(repo_path: str) -> str:
    """Fetch README text for a GitHub repo (first 1000 chars). Returns empty string on failure."""
    headers = {"User-Agent": "Mozilla/5.0 AI-Daily-Newsletter/1.0"}
    for branch in ("main", "master"):
        try:
            url = f"https://raw.githubusercontent.com/{repo_path}/{branch}/README.md"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.text[:1000]
        except Exception:
            pass
    return ""


def fetch_github_trending(limit: int) -> list[dict]:
    """Scrape GitHub Trending, fetch README for AI candidates, filter by README content."""
    candidates = []
    try:
        resp = requests.get(
            "https://github.com/trending",
            params={"since": "daily"},
            headers={"User-Agent": "Mozilla/5.0 AI-Daily-Newsletter/1.0"},
            timeout=15,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for article in soup.select("article.Box-row"):
            h2 = article.select_one("h2 a")
            if not h2:
                continue
            repo_path = h2.get("href", "").strip("/")
            repo_url = f"https://github.com/{repo_path}"
            repo_name = repo_path.split("/")[-1] if "/" in repo_path else repo_path

            p = article.select_one("p")
            desc = p.get_text(strip=True) if p else ""

            lang_span = article.select_one("[itemprop='programmingLanguage']")
            lang = lang_span.get_text(strip=True) if lang_span else ""

            stars_links = article.select("a.Link--muted")
            stars = stars_links[0].get_text(strip=True).replace(",", "") if stars_links else ""

            # 初步过滤：名字或描述命中 AI 关键词
            if not matches_ai(f"{repo_name} {desc}"):
                continue

            candidates.append({
                "repo_path": repo_path,
                "repo_url": repo_url,
                "desc": desc,
                "lang": lang,
                "stars": stars,
            })
    except Exception as e:
        print(f"[GitHub] Error fetching trending page: {e}", file=sys.stderr)
        return []

    # 并发抓取 README，二次验证 AI 相关性
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_repo = {
            executor.submit(fetch_readme, c["repo_path"]): c for c in candidates
        }
        for future in concurrent.futures.as_completed(future_to_repo):
            c = future_to_repo[future]
            readme = future.result()
            combined = f"{c['repo_path']} {c['desc']} {readme}"
            if not matches_ai(combined):
                print(f"  [GitHub] SKIP {c['repo_path']} (README 不含 AI 关键词)", file=sys.stderr)
                continue

            # 取 README 前 500 字作为 summary 补充
            readme_snippet = readme[:500].strip() if readme else ""

            results.append({
                "source": "GitHub Trending",
                "category": "tools",
                "title": c["repo_path"],
                "url": c["repo_url"],
                "time": datetime.now(timezone.utc).isoformat(),
                "summary": c["desc"],
                "readme": readme_snippet,
                "github_url": c["repo_url"],
                "lang": c["lang"],
                "stars": c["stars"],
            })

            if len(results) >= limit:
                break

    return results


# ---------------------------------------------------------------------------
# HuggingFace Papers (via subprocess)
# ---------------------------------------------------------------------------
def fetch_hf_papers(limit: int) -> list[dict]:
    """Run fetch_hf_papers.py as a subprocess and parse its JSON output."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "fetch_hf_papers.py")

    if not os.path.exists(script_path):
        print("[HF] fetch_hf_papers.py not found, skipping", file=sys.stderr)
        return []

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"[HF] fetch_hf_papers.py failed: {result.stderr}", file=sys.stderr)
            return []

        papers = json.loads(result.stdout)
        return papers[:limit]
    except subprocess.TimeoutExpired:
        print("[HF] fetch_hf_papers.py timed out", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[HF] Error running fetch_hf_papers.py: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AI Daily Newsletter - News Fetcher")
    parser.add_argument("--hours", type=int, default=24, help="Time window in hours (default: 24)")
    parser.add_argument("--limit", type=int, default=20, help="Max entries per source (default: 20)")
    parser.add_argument("--outdir", type=str, help="Save JSON to directory instead of stdout")
    args = parser.parse_args()

    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    all_entries = []
    source_count = 0

    # --- Phase 1: Concurrent RSS fetch ---
    print(f"[INFO] Fetching {len(RSS_SOURCES)} RSS sources (window: {args.hours}h)...", file=sys.stderr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_rss, src, cutoff, args.limit): src["name"]
            for src in RSS_SOURCES
        }
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                entries = future.result()
                if entries:
                    source_count += 1
                    all_entries.extend(entries)
                    print(f"  [RSS] {name}: {len(entries)} entries", file=sys.stderr)
                else:
                    print(f"  [RSS] {name}: 0 entries", file=sys.stderr)
            except Exception as e:
                print(f"  [RSS] {name}: error - {e}", file=sys.stderr)

    # --- Phase 2: GitHub, HF (concurrent) ---
    print("[INFO] Fetching GitHub Trending, HF Papers...", file=sys.stderr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        gh_future = executor.submit(fetch_github_trending, args.limit)
        hf_future = executor.submit(fetch_hf_papers, args.limit)

        for name, future in [("GitHub", gh_future), ("HF Papers", hf_future)]:
            try:
                entries = future.result()
                if entries:
                    source_count += 1
                    all_entries.extend(entries)
                    print(f"  [{name}] {len(entries)} entries", file=sys.stderr)
                else:
                    print(f"  [{name}] 0 entries", file=sys.stderr)
            except Exception as e:
                print(f"  [{name}] error - {e}", file=sys.stderr)

    # --- Sort by time descending ---
    def sort_key(entry):
        t = entry.get("time", "")
        if not t:
            return ""
        return t

    all_entries.sort(key=sort_key, reverse=True)

    # --- Output ---
    output = json.dumps(all_entries, ensure_ascii=False, indent=2)
    stats = f"[DONE] {source_count} sources | {len(all_entries)} entries"
    print(stats, file=sys.stderr)

    if args.outdir:
        os.makedirs(args.outdir, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        filepath = os.path.join(args.outdir, f"ai-news-{date_str}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[SAVED] {filepath}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
