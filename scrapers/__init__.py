from importlib import import_module
import sys
from pathlib import Path

# Solo necesario si se ejecuta este archivo directamente
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent))

try:
    from config import SOURCES, API_KEYS
except ImportError:
    from ..config import SOURCES, API_KEYS


def get_all_scrapers():
    """
    Factory function que devuelve todas las instancias de scrapers configuradas
    """
    scrapers = []

    # NewsAPI Scraper
    if SOURCES.get("newsapi") and API_KEYS.get("newsapi"):
        try:
            from .newsapi import NewsAPIScraper
            scrapers.append(NewsAPIScraper())
            print("NewsAPI scraper cargado correctamente")
        except ImportError as e:
            print(f"Error al cargar NewsAPI scraper: {str(e)}")

    # RSS Scraper
    if SOURCES.get("rss"):
        try:
            from .generic_rss import GenericRSSScraper
            scrapers.append(GenericRSSScraper())
            print("RSS scraper cargado correctamente")
        except ImportError as e:
            print(f"Error al cargar RSS scraper: {str(e)}")

    # GNews Scraper
    if SOURCES.get("gnews") and API_KEYS.get("gnews"):
        try:
            from .gnews import GNewsScraper
            scrapers.append(GNewsScraper())
            print("GNews scraper cargado correctamente")
        except ImportError as e:
            print(f"Error al cargar GNews scraper: {str(e)}")

    if SOURCES.get("theguardian") and API_KEYS.get("theguardian"):
        try:
            from .theguardian import TheGuardianScraper
            scrapers.append(TheGuardianScraper())
            print("The Guardian scraper cargado correctamente")
        except ImportError as e:
            print(f"Error al cargar The Guardian scraper: {str(e)}")

    # Verificar que al menos un scraper se cargó
    if not scrapers:
        print("¡Advertencia! No se cargó ningún scraper. Verifica tu configuración.")

    return scrapers