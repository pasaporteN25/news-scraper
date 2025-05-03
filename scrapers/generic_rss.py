import feedparser
import asyncio
from typing import List, Dict
from datetime import datetime
from utils.text_processing import contains_keywords

# Fuentes RSS de noticias internacionales
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",  # BBC Mundo
    "https://www.elmundo.es/rss/",  # El Mundo
    "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml",  # NY Times
    "https://rss.lemonde.fr/c/205/f/3050/index.rss",  # Le Monde
    "https://www.spiegel.de/international/index.rss",  # Der Spiegel
    "https://www.theguardian.com/world/rss",  # The Guardian
    "https://www.japantimes.co.jp/feed/topstories/",  # Japan Times
    "http://www.chinadaily.com.cn/rss/world_rss.xml"  # China Daily
]


class GenericRSSScraper:
    async def scrape(self, keywords: List[str], language: str = "es", max_articles: int = 20) -> List[Dict]:
        tasks = [self._scrape_feed(feed, keywords, max_articles) for feed in RSS_FEEDS]
        results = await asyncio.gather(*tasks)
        return [article for sublist in results for article in sublist]

    async def _scrape_feed(self, feed_url: str, keywords: List[str], max_articles: int) -> List[Dict]:
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)

        articles = []
        for entry in feed.entries[:max_articles]:
            if contains_keywords(entry, keywords):
                articles.append({
                    "title": entry.get("title"),
                    "description": entry.get("description"),
                    "url": entry.get("link"),
                    "published_at": entry.get("published"),
                    "source": feed.feed.get("title"),
                    "language": self._detect_language(entry),
                    "scraped_at": datetime.utcnow().isoformat()
                })
        return articles

    def _detect_language(self, entry) -> str:
        # Implementación básica - mejorar con detección real
        if "elmundo" in entry.get("link", ""):
            return "es"
        elif "bbc.co.uk" in entry.get("link", ""):
            return "en"
        # Añadir más detecciones según sea necesario
        return "en"