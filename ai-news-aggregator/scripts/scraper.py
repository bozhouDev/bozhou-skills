#!/usr/bin/env python3
"""
AI News Aggregator - Main scraper script.
Fetches articles from multiple sources, deduplicates, translates, and outputs to Markdown.
"""

import os
import sys
import json
import hashlib
import yaml
import feedparser
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Add script directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from translator import Translator


class NewsAggregator:
    def __init__(
        self,
        sources_config: str,
        state_file: str,
        output_file: str,
        max_workers: int = 5
    ):
        """
        Initialize the news aggregator.

        Args:
            sources_config: Path to sources.yaml
            state_file: Path to state.json (for deduplication)
            output_file: Path to output Markdown file
            max_workers: Max concurrent threads for fetching
        """
        self.sources_config = Path(sources_config)
        self.state_file = Path(state_file)
        self.output_file = Path(output_file)
        self.max_workers = max_workers

        # Load sources
        with open(self.sources_config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.sources = config.get('sources', [])

        # Load state (seen articles)
        self.state = self._load_state()

        # Initialize translator
        self.translator = Translator()

    def _load_state(self) -> Dict:
        """Load state from disk."""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"seen": {}, "last_run": None}

    def _save_state(self):
        """Save state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)

    def _article_hash(self, url: str, date: str = None) -> str:
        """Generate unique hash for article (URL + date)."""
        key = f"{url}:{date or ''}"
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    def _is_seen(self, article: Dict) -> bool:
        """Check if article has been seen before."""
        article_id = self._article_hash(
            article.get('url', ''),
            article.get('date', '')
        )
        return article_id in self.state.get('seen', {})

    def _mark_seen(self, article: Dict):
        """Mark article as seen."""
        article_id = self._article_hash(
            article.get('url', ''),
            article.get('date', '')
        )
        if 'seen' not in self.state:
            self.state['seen'] = {}
        self.state['seen'][article_id] = {
            'url': article.get('url'),
            'title': article.get('title'),
            'date': article.get('date'),
            'timestamp': datetime.now().isoformat()
        }

    def fetch_rss(self, source: Dict) -> List[Dict]:
        """Fetch articles from RSS feed."""
        articles = []
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries:
                article = {
                    'source': source['name'],
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'date': entry.get('published', ''),
                    'description': entry.get('summary', '')[:200]
                }
                articles.append(article)
        except Exception as e:
            print(f"Error fetching RSS {source['name']}: {e}")

        return articles

    def fetch_web(self, source: Dict) -> List[Dict]:
        """Fetch articles from web pages (basic implementation)."""
        articles = []
        parser = source.get('parser', 'generic_web')

        try:
            response = requests.get(source['url'], timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Parser-specific logic
            if parser == 'hackernews_web':
                articles = self._parse_hackernews(soup, source)
            elif parser == 'huggingface_web':
                articles = self._parse_huggingface(soup, source)
            elif parser == 'paulgraham_web':
                articles = self._parse_paulgraham(soup, source)
            else:
                # Generic parser: find article titles and links
                articles = self._parse_generic(soup, source)

        except Exception as e:
            print(f"Error fetching web {source['name']}: {e}")

        return articles

    def _parse_hackernews(self, soup: BeautifulSoup, source: Dict) -> List[Dict]:
        """Parse Hacker News front page."""
        articles = []
        limit = source.get('limit', 8)

        # Find story rows
        storylinks = soup.select('.titleline > a')[:limit]

        for link in storylinks:
            articles.append({
                'source': source['name'],
                'title': link.get_text(strip=True),
                'url': link.get('href', ''),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': ''
            })

        return articles

    def _parse_huggingface(self, soup: BeautifulSoup, source: Dict) -> List[Dict]:
        """Parse Hugging Face Papers page."""
        articles = []
        min_votes = source.get('min_votes', 20)

        # This is a placeholder - actual implementation depends on HF's HTML structure
        # Would need to inspect page and extract paper cards with vote counts
        # For now, return empty to avoid errors
        print(f"Note: {source['name']} parser needs custom implementation")

        return articles

    def _parse_paulgraham(self, soup: BeautifulSoup, source: Dict) -> List[Dict]:
        """Parse Paul Graham essays page."""
        articles = []

        # Find essay links (typically in a table or list)
        links = soup.select('table a[href$=".html"]')

        for link in links[:10]:  # Latest 10
            href = link.get('href', '')
            if href:
                full_url = f"https://paulgraham.com/{href}"
                articles.append({
                    'source': source['name'],
                    'title': link.get_text(strip=True),
                    'url': full_url,
                    'date': '',
                    'description': ''
                })

        return articles

    def _parse_generic(self, soup: BeautifulSoup, source: Dict) -> List[Dict]:
        """Generic parser for article-style sites."""
        articles = []

        # Try common article selectors
        selectors = [
            'article h2 a',
            'article h3 a',
            '.post-title a',
            '.entry-title a',
            'h2.title a'
        ]

        for selector in selectors:
            links = soup.select(selector)
            if links:
                for link in links[:10]:
                    articles.append({
                        'source': source['name'],
                        'title': link.get_text(strip=True),
                        'url': link.get('href', ''),
                        'date': '',
                        'description': ''
                    })
                break

        return articles

    def fetch_api(self, source: Dict) -> List[Dict]:
        """Fetch articles from API endpoints."""
        articles = []
        parser = source.get('parser', 'generic_api')

        try:
            response = requests.get(source['url'], timeout=10)
            response.raise_for_status()
            data = response.json()

            if parser == 'tldr_api':
                # Parse TLDR AI API response
                for item in data.get('items', []):
                    articles.append({
                        'source': source['name'],
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'date': item.get('date', ''),
                        'description': item.get('description', '')[:200]
                    })

        except Exception as e:
            print(f"Error fetching API {source['name']}: {e}")

        return articles

    def fetch_source(self, source: Dict) -> List[Dict]:
        """Fetch articles from a single source."""
        print(f"Fetching: {source['name']} ({source['type']})")

        source_type = source.get('type', 'web')

        if source_type == 'rss':
            return self.fetch_rss(source)
        elif source_type == 'web':
            return self.fetch_web(source)
        elif source_type == 'api':
            return self.fetch_api(source)
        else:
            print(f"Unknown type: {source_type}")
            return []

    def fetch_all(self) -> List[Dict]:
        """Fetch articles from all sources concurrently."""
        all_articles = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_source = {
                executor.submit(self.fetch_source, source): source
                for source in self.sources
            }

            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                except Exception as e:
                    print(f"Error processing {source['name']}: {e}")

        return all_articles

    def filter_new_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter out articles that have been seen before."""
        new_articles = [a for a in articles if not self._is_seen(a)]
        print(f"New articles: {len(new_articles)} / {len(articles)}")
        return new_articles

    def translate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Translate article titles to Chinese."""
        print("Translating titles...")
        return self.translator.translate_articles(articles, fields=['title'])

    def generate_markdown(self, articles: List[Dict]) -> str:
        """Generate Markdown output."""
        # Group by source
        by_source = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(article)

        # Generate markdown
        lines = [
            f"# AI News Update - {datetime.now().strftime('%Y-%m-%d')}",
            "",
            f"Total: {len(articles)} new articles",
            ""
        ]

        for source, items in sorted(by_source.items()):
            lines.append(f"## {source} ({len(items)})")
            lines.append("")

            for item in items:
                title = item.get('title', 'No title')
                title_zh = item.get('title_zh', '')
                url = item.get('url', '')
                date = item.get('date', '')

                lines.append(f"- [{title}]({url})")
                if title_zh:
                    lines.append(f"  - **中文**: {title_zh}")
                if date:
                    lines.append(f"  - **Date**: {date}")
                lines.append("")

        return "\n".join(lines)

    def save_output(self, content: str):
        """Save Markdown output."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        # Append mode for incremental updates
        mode = 'a' if self.output_file.exists() else 'w'

        with open(self.output_file, mode, encoding='utf-8') as f:
            f.write(content + "\n\n---\n\n")

        print(f"Output saved to: {self.output_file}")

    def run(self):
        """Main execution flow."""
        print("=== AI News Aggregator ===")
        print(f"Sources: {len(self.sources)}")

        # 1. Fetch all articles
        all_articles = self.fetch_all()
        print(f"Total fetched: {len(all_articles)}")

        # 2. Filter new articles
        new_articles = self.filter_new_articles(all_articles)

        if not new_articles:
            print("No new articles found.")
            return

        # 3. Translate titles
        translated_articles = self.translate_articles(new_articles)

        # 4. Generate Markdown
        markdown = self.generate_markdown(translated_articles)

        # 5. Save output
        self.save_output(markdown)

        # 6. Mark articles as seen
        for article in translated_articles:
            self._mark_seen(article)

        # 7. Save state
        self.state['last_run'] = datetime.now().isoformat()
        self._save_state()

        print("✅ Done!")


def main():
    """CLI entry point."""
    # Paths (relative to script location)
    base_dir = script_dir.parent
    sources_config = base_dir / 'references' / 'sources.yaml'
    state_file = Path.home() / '.ai-news-cache' / 'state.json'
    output_file = Path.home() / 'Documents' / 'ai-news' / 'updates.md'

    # Override with env vars if provided
    sources_config = Path(os.getenv('SOURCES_CONFIG', sources_config))
    state_file = Path(os.getenv('STATE_FILE', state_file))
    output_file = Path(os.getenv('OUTPUT_FILE', output_file))

    # Run aggregator
    aggregator = NewsAggregator(
        sources_config=sources_config,
        state_file=state_file,
        output_file=output_file
    )

    aggregator.run()


if __name__ == "__main__":
    main()
