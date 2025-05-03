import json
from datetime import datetime
from typing import List, Dict
import csv


def save_articles(articles: List[Dict], format: str = "json"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format == "json":
        filename = f"news_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
    elif format == "csv":
        filename = f"news_{timestamp}.csv"
        if articles:
            keys = articles[0].keys()
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(articles)
    else:
        raise ValueError(f"Formato no soportado: {format}")

    print(f"Artículos guardados en {filename}")