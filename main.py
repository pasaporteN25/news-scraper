import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from scrapers import get_all_scrapers
from utils.text_processing import filter_by_keywords
from utils.storage import save_articles


async def scrape_all_sources(
        keywords: Optional[List[str]] = None,
        language: str = "es",
        max_articles: int = 20,
        active_sources: Optional[List[str]] = None,
        **kwargs  # Acepta parámetros adicionales para fuentes específicas
) -> List[Dict]:
    """
    Función principal modificada para aceptar parámetros desde la GUI

    Args:
        keywords: Lista de palabras clave (si None, usa las de config.py)
        language: Código de idioma (ej. 'es', 'en')
        max_articles: Máximo de artículos por fuente
        active_sources: Lista de fuentes a usar (si None, usa todas)
    """
    if keywords is None:
        from config import KEYWORDS
        keywords = KEYWORDS

    if active_sources is None:
        from config import SOURCES
        active_sources = [k for k, v in SOURCES.items() if v]

    scrapers = get_all_scrapers()

    # Filtrar scrapers por fuentes activas si se especificó
    if active_sources:
        scrapers = [s for s in scrapers if type(s).__name__.lower().replace('scraper', '') in active_sources]

    tasks = []

    for scraper in scrapers:
        task = asyncio.create_task(
            scraper.scrape(
                keywords=keywords,
                language=language,
                max_articles=max_articles,
                **{k: v for k, v in kwargs.items() if k in scraper.__class__.__name__.lower()}
            )
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Manejar errores y aplanar resultados
    articles = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Error en {type(scrapers[i]).__name__}: {str(result)}")
        elif isinstance(result, list):
            articles.extend(result)

    # Filtrado adicional por palabras clave
    filtered_articles = filter_by_keywords(articles, keywords)

    return filtered_articles


def run_as_script():
    """Función mantenida para compatibilidad con ejecución por CLI"""
    print("Iniciando scraping de noticias...")
    start_time = datetime.now()

    articles = asyncio.run(scrape_all_sources())

    # Guardar resultados
    save_articles(articles)

    end_time = datetime.now()
    print(f"\nScraping completado en {end_time - start_time}")
    print(f"Total de artículos encontrados: {len(articles)}")
    print("Artículos guardados en la base de datos/archivo")


# Al final de main.py, reemplaza el if __name__ == "__main__" con:
if __name__ == "__main__":
    try:
        from gui import NewsScraperApp
        app = NewsScraperApp()
        app.run()
    except ImportError as e:
        print("Modo GUI no disponible, ejecutando en modo consola...")
        run_as_script()