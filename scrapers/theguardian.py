import aiohttp
import asyncio
from typing import List, Dict
from datetime import datetime
try:
    from config import SOURCES, API_KEYS
except ImportError:
    from ..config import SOURCES, API_KEYS


class TheGuardianScraper:
    def __init__(self):
        self.api_key = API_KEYS.get("theguardian")
        self.base_url = "https://content.guardianapis.com/search"

    async def scrape(self, keywords: List[str], language: str = "en", max_articles: int = 20, **kwargs) -> List[Dict]:
        if not self.api_key:
            print("The Guardian API key no configurada")
            return []

            # Validación de parámetros avanzados
        if kwargs.get("section"):
            sections = kwargs["section"].split("|")
            if not all(section.isalpha() or section.replace('-', '').isalpha() for section in sections):
                raise ValueError("Las secciones deben contener solo letras y guiones")
            if len(sections) > 5:
                raise ValueError("Máximo 5 secciones permitidas")

        if language != "en":
            print("The Guardian solo soporta idioma inglés")
            return []

        query = " AND ".join(f'"{k}"' for k in keywords) if keywords else ""

        params = {
            "q": query,
            "lang": language,
            "page-size": min(max_articles, 50),  # Máximo 50 artículos por petición
            "api-key": self.api_key,
            "show-fields": "headline,standfirst,body,byline,thumbnail,publication",  # Campos adicionales
            "show-tags": "contributor",
            "order-by": "newest"
        }

        # Parámetros adicionales desde kwargs
        advanced_params = {
            "section": kwargs.get("section"),  # Ej: "technology|business"
            "from-date": kwargs.get("from_date"),  # Formato "YYYY-MM-DD"
            "to-date": kwargs.get("to_date"),
            "reference-type": kwargs.get("ref_type")
        }

        # Agregar solo los parámetros que tengan valor
        params.update({k: v for k, v in advanced_params.items() if v is not None})

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_articles(data.get("response", {}).get("results", []))
                    else:
                        error_data = await response.json()
                        print(f"The Guardian API error {response.status}: {error_data.get('message', 'Sin mensaje')}")
                        return []
        except Exception as e:
            print(f"Error en The Guardian scraper: {str(e)}")
            return []

    def _parse_articles(self, articles: List[Dict]) -> List[Dict]:
        parsed = []
        for article in articles:
            fields = article.get("fields", {})
            parsed.append({
                "title": fields.get("headline", article.get("webTitle")),
                "description": fields.get("standfirst"),
                "content": fields.get("body"),
                "url": article.get("webUrl"),
                "source": "The Guardian",
                "published_at": article.get("webPublicationDate"),
                "language": "en",  # The Guardian solo tiene contenido en inglés
                "author": fields.get("byline") or self._get_first_contributor(article.get("tags", [])),
                "image_url": fields.get("thumbnail"),
                "scraped_at": datetime.utcnow().isoformat()
            })
        return parsed

    def _get_first_contributor(self, tags: List[Dict]) -> str:
        for tag in tags:
            if tag.get("type") == "contributor":
                return tag.get("webTitle", "")
        return ""