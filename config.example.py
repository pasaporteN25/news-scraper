# Ejemplo de configuración - Renombrar a config.py y completar

# Palabras Clave por defecto
KEYWORDS = ["ejemplo", "palabra clave"]

# Idioma por defecto (código ISO 639-1)
LANGUAGE = "es"

# Máximo de artículos por fuente
MAX_ARTICLES_PER_SOURCE = 20

# Fuentes activas por defecto
SOURCES = {
    "newsapi": True,
    "gnews": True,
    "rss": True,
    "theguardian": True,
    "mediastack": False
}

# API Keys (obtener en los servicios correspondientes)
API_KEYS = {
    "newsapi": "TU_API_KEY_AQUI",      # https://newsapi.org
    "gnews": "TU_API_KEY_AQUI",        # https://gnews.io
    "theguardian": "TU_API_KEY_AQUI",  # https://open-platform.theguardian.com
    # Agregar otras keys según necesites
}