import aiohttp
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta
try:
    from config import SOURCES, API_KEYS
except ImportError:
    from ..config import SOURCES, API_KEYS


class NewsAPIScraper:
    def __init__(self):
        self.api_key = API_KEYS.get("newsapi")
        self.base_url = "https://newsapi.org/v2/everything"

    async def scrape(self, keywords: List[str], language: str = "es", max_articles: int = 20) -> List[Dict]:
        if not self.api_key:
            return []

        query = " OR ".join(keywords)
        date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        params = {
            "q": query,
            "language": language,
            "from": date_from,
            "sortBy": "publishedAt",
            "pageSize": max_articles,
            "apiKey": self.api_key
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_articles(data.get("articles", []))
                    else:
                        print(f"Error NewsAPI: {response.status}")
                        return []
            except Exception as e:
                print(f"Error en NewsAPI: {str(e)}")
                return []

    def _parse_articles(self, articles: List[Dict]) -> List[Dict]:
        parsed = []
        for article in articles:
            parsed.append({
                "title": article.get("title"),
                "description": article.get("description"),
                "content": article.get("content"),
                "url": article.get("url"),
                "source": article.get("source", {}).get("name"),
                "published_at": article.get("publishedAt"),
                "language": article.get("language"),
                "author": article.get("author"),
                "image_url": article.get("urlToImage"),
                "scraped_at": datetime.utcnow().isoformat()
            })
        return parsed