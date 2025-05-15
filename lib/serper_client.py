import asyncio
import requests
import aiohttp
import os

class SerperClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("Serper API key must be provided either directly or via SERPER_API_KEY environment variable")
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        self.searches = 0

    def search(self, query: str, limit: int = 5, include_urls: bool = False) -> str:
        response = requests.get(f"https://google.serper.dev/search?q={query}", headers=self.headers)
        self.searches += 1
        if response.status_code != 200:
            raise Exception(f"Serper API request failed with status {response.status_code}: {response.text}")
        result = response.json()
        search_context = ""
        if "organic" in result:
            for result in result["organic"][:limit]:  # Use top 10 results
                search_context += f"Title: {result.get('title', '')}\n"
                search_context += f"Snippet: {result.get('snippet', '')}\n"
                if include_urls:
                    search_context += f"URL: {result.get('link', '')}\n"
                search_context += "\n"
        return search_context
    
    async def search_async(self, query: str, limit: int = 5, include_urls: bool = False) -> str:
        async with aiohttp.ClientSession() as session:
            self.searches += 1
            async with session.post(
                "https://google.serper.dev/search",
                headers=self.headers,
                json={"q": query}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Serper API request failed with status {response.status}: {error_text}")
                
                result = await response.json()
                
                # Extract relevant information from search results
                search_context = ""
                if "organic" in result:
                    for result in result["organic"][:limit]:  # Use top 10 results
                        search_context += f"Title: {result.get('title', '')}\n"
                        search_context += f"Snippet: {result.get('snippet', '')}\n"
                        if include_urls:
                            search_context += f"URL: {result.get('link', '')}\n"
                        search_context += "\n"
                
                return search_context
    
    async def search_async_batch(self, queries: list[str], limit: int = 5, include_urls: bool = False) -> list[str]:
        tasks = [self.search_async(query, limit, include_urls) for query in queries]
        results = await asyncio.gather(*tasks)
        paired = list(zip(queries, results))
        formatted = [f"Query: {query}\n\n{result}" for query, result in paired]
        str = "\n\n\n".join(formatted)
        return str
    
    def get_costs(self, cpk: float = 0.3):
        return {
            "searches": self.searches,
            "cost":round(self.searches * cpk / 1000, 4),
        }


