import os
import logging
from typing import Dict, Any, Optional
import requests
from urllib.parse import urlparse

class ScraperClient:
    def __init__(self, api_key: str = None):
        """Initialize the scraper client with Firecrawl API key."""
        self.api_key = api_key or os.environ.get("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("Firecrawl API key must be provided either directly or via FIRECRAWL_API_KEY environment variable")
        
        self.base_url = "https://api.firecrawl.dev/v0"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a URL using Firecrawl API and return cleaned content along with metadata.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dict containing:
            - content: Cleaned main content in markdown format
            - title: Page title
            - metadata: Additional metadata
            - error: Error message if any
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return {"error": "Invalid URL format"}

            # Make request to Firecrawl API
            response = requests.post(
                f"{self.base_url}/scrape",
                headers=self.headers,
                json={
                    "url": url,
                    "pageOptions": {
                        "onlyMainContent": True,  # Ignore navs, footers, etc.
                        "includeMetadata": True   # Get title and other metadata
                    }
                }
            )
            
            if response.status_code != 200:
                error_msg = f"Firecrawl API request failed with status {response.status_code}: {response.text}"
                logging.error(f"Error scraping URL {url}: {error_msg}")
                return {
                    "error": error_msg,
                    "metadata": {
                        "url": url,
                        "status_code": response.status_code
                    }
                }

            result = response.json()
            
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown error from Firecrawl API")
                logging.error(f"Error from Firecrawl API for URL {url}: {error_msg}")
                return {
                    "error": error_msg,
                    "metadata": {
                        "url": url
                    }
                }

            # Extract data from Firecrawl response
            data = result.get("data", {})
            return {
                "content": data.get("markdown", ""),
                "title": data.get("metadata", {}).get("title", ""),
                "metadata": {
                    "url": url,
                    "source_url": data.get("metadata", {}).get("sourceURL", url),
                    "description": data.get("metadata", {}).get("description", ""),
                    "language": data.get("metadata", {}).get("language"),
                    "status_code": response.status_code
                },
                "error": None
            }

        except requests.RequestException as e:
            error_msg = f"Failed to fetch URL: {str(e)}"
            logging.error(f"Error fetching URL {url}: {error_msg}")
            return {
                "error": error_msg,
                "metadata": {
                    "url": url,
                    "error_type": type(e).__name__,
                    "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
                }
            }
        except Exception as e:
            error_msg = f"Error processing content: {str(e)}"
            logging.error(f"Error processing URL {url}: {error_msg}")
            return {
                "error": error_msg,
                "metadata": {
                    "url": url,
                    "error_type": type(e).__name__
                }
            }

    async def scrape_url_async(self, url: str) -> Dict[str, Any]:
        """Async version of scrape_url."""
        # Since requests is synchronous, we'll run it in a thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.scrape_url, url) 