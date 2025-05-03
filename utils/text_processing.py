from typing import List, Dict
import re


def contains_keywords(text_or_dict, keywords: List[str]) -> bool:
    if isinstance(text_or_dict, str):
        text = text_or_dict
    elif isinstance(text_or_dict, dict):
        text = " ".join([str(v) for v in text_or_dict.values() if v])
    else:
        return False

    text = text.lower()
    for keyword in keywords:
        if re.search(rf"\b{re.escape(keyword.lower())}\b", text):
            return True
    return False


def filter_by_keywords(articles: List[Dict], keywords: List[str]) -> List[Dict]:
    return [article for article in articles if contains_keywords(article, keywords)]