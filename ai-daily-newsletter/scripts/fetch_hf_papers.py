#!/usr/bin/env python3
"""Fetch daily papers from HuggingFace via their API.

Uses the public HF daily_papers API endpoint.
Outputs JSON array to stdout.
"""

import json
import sys

import requests

HF_API_URL = "https://huggingface.co/api/daily_papers"


def fetch_papers() -> list[dict]:
    """Fetch papers from HuggingFace daily papers API."""
    results = []
    try:
        resp = requests.get(HF_API_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for item in data:
            paper = item.get("paper", {})
            paper_id = paper.get("id", "")
            title = paper.get("title", "")
            summary = paper.get("summary", "")
            published = paper.get("publishedAt", "")
            upvotes = item.get("paper", {}).get("upvotes", 0)

            if not paper_id or not title:
                continue

            results.append({
                "source": "HuggingFace Papers",
                "category": "research",
                "title": title,
                "url": f"https://huggingface.co/papers/{paper_id}",
                "time": published,
                "summary": summary[:500] if summary else "",
                "heat": str(upvotes) if upvotes else "",
                "github_url": f"https://arxiv.org/abs/{paper_id}",
            })

    except Exception as e:
        print(f"[HF Papers] Error: {e}", file=sys.stderr)

    return results


def main():
    papers = fetch_papers()
    print(f"[HF Papers] Found {len(papers)} papers", file=sys.stderr)
    print(json.dumps(papers, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
