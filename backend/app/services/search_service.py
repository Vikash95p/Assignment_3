from typing import List, Dict, Any
from duckduckgo_search import DDGS

class SearchService:
    def __init__(self):
        self.ddgs = DDGS()

    def search_web(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        try:
            results = self.ddgs.text(query, max_results=max_results)
            formatted = []
            for r in results:
                formatted.append({
                    "title": r.get('title', ''),
                    "url": r.get('href', ''),
                    "snippet": r.get('body', '')
                })
            return formatted
        except Exception as e:
            print(f"Web search error: {e}")
            return []

search_service = SearchService()
