import aiohttp
import asyncio
from typing import List, Dict
from datetime import datetime
try:
    from config import SOURCES, API_KEYS
except ImportError:
    from ..config import SOURCES, API_KEYS


class GNewsScraper:
    def __init__(self):
        self.api_key = API_KEYS.get("gnews")
        self.base_url = "https://gnews.io/api/v4/search"

    async def scrape(self, keywords: List[str], language: str = "en", max_articles: int = 10) -> List[Dict]:
        if not self.api_key:
            print("GNews API key no configurada")
            return []

        # GNews tiene un límite máximo de 10 artículos en el plan gratuito
        max_articles = min(max_articles, 10)
        query = " OR ".join(keywords) if keywords else "news"

        params = {
            "q": query,
            "lang": language,
            "max": max_articles,
            "apikey": self.api_key,
            "in": "title,description,content"  # Buscar en estos campos
        }

        print(f"GNews - Realizando búsqueda con parámetros: {params}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"GNews - Artículos encontrados: {len(data.get('articles', []))}")
                        return self._parse_articles(data.get("articles", []))
                    else:
                        error_data = await response.json()
                        print(f"GNews - Error {response.status}: {error_data.get('message', 'Sin mensaje de error')}")
                        return []
        except asyncio.TimeoutError:
            print("GNews - Timeout al conectar con la API")
            return []
        except Exception as e:
            print(f"GNews - Error inesperado: {str(e)}")
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
                "language": article.get("language", "en"),
                "author": article.get("author"),
                "image_url": article.get("image"),
                "scraped_at": datetime.utcnow().isoformat()
            })
        return parsed