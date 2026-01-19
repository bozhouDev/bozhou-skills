#!/usr/bin/env python3
"""
Translation module using OpenAI-compatible API.
Supports batch translation with caching.
"""

import os
import json
import hashlib
from typing import List, Dict
from pathlib import Path
from openai import OpenAI


class Translator:
    def __init__(
        self,
        base_url: str = "https://api.deepseek.com",
        api_key: str = "sk-729894101a9d4b5bb58c8810336d7849",
        model: str = "deepseek-chat",
        cache_dir: str = "~/.ai-news-cache"
    ):
        """
        Initialize translator with OpenAI-compatible API.

        Args:
            base_url: API base URL (from env or param)
            api_key: API key (from env or param)
            model: Model name (from env or param)
            cache_dir: Cache directory for translations
        """
        self.base_url = base_url or os.getenv("TRANSLATION_BASE_URL")
        self.api_key = api_key or os.getenv("TRANSLATION_API_KEY")
        self.model = model or os.getenv("TRANSLATION_MODEL", "gpt-4o-mini")

        if not self.api_key:
            raise ValueError("API key not provided")

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

        # Cache setup
        self.cache_dir = Path(cache_dir or os.path.expanduser("~/.ai-news-cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "translations.json"
        self._load_cache()

    def _load_cache(self):
        """Load translation cache from disk."""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def _save_cache(self):
        """Save translation cache to disk."""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def _hash_text(self, text: str) -> str:
        """Generate hash for text (cache key)."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def translate(self, text: str, target_lang: str = "Chinese") -> str:
        """
        Translate single text.

        Args:
            text: Text to translate
            target_lang: Target language

        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text

        # Check cache
        cache_key = self._hash_text(text)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Translate via API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following text to {target_lang}. Only output the translation, no explanations."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3
            )

            translated = response.choices[0].message.content.strip()

            # Cache result
            self.cache[cache_key] = translated
            self._save_cache()

            return translated

        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Fallback to original

    def translate_batch(
        self,
        texts: List[str],
        target_lang: str = "Chinese"
    ) -> List[str]:
        """
        Translate multiple texts efficiently.

        Args:
            texts: List of texts to translate
            target_lang: Target language

        Returns:
            List of translated texts
        """
        results = []

        for text in texts:
            results.append(self.translate(text, target_lang))

        return results

    def translate_articles(
        self,
        articles: List[Dict],
        fields: List[str] = ["title"]
    ) -> List[Dict]:
        """
        Translate specific fields in article dictionaries.

        Args:
            articles: List of article dicts
            fields: Fields to translate (e.g., ["title", "description"])

        Returns:
            Articles with translated fields (adds "_zh" suffix)
        """
        for article in articles:
            for field in fields:
                if field in article and article[field]:
                    translated_field = f"{field}_zh"
                    article[translated_field] = self.translate(article[field])

        return articles


if __name__ == "__main__":
    # Test
    translator = Translator()

    test_text = "AI will change the world"
    result = translator.translate(test_text)
    print(f"Original: {test_text}")
    print(f"Translated: {result}")
