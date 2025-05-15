import asyncio
import json
from lib.serper_client import SerperClient
from lib.openai_client import OpenAIClient
from lib.eval_swarm import EvalSwarm
from lib.scraper_client import ScraperClient

class ResearchTools:
    # Schema definitions as class variables
    PARALLEL_WEBSEARCH_SCHEMA = {
        "name": "parallel_websearch",
        "description": "Searches the web for information",
        "input_schema": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "description": "A list of search queries to run",
                    "items": {
                        "type": "string"
                    },
                    "maxItems": 50
                },
            },
            "required": ["queries"]
        }
    }

    COMPANY_WEBSEARCH_SCHEMA = {
        "name": "parallel_company_websearch",
        "description": "Searches all permutations of company names and a queries ie f\"{company_name} {query}\" returning a table of answers",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_names": {
                    "type": "array",
                    "description": "A list of company names to search",
                    "items": {
                        "type": "string"
                    },
                    "maxItems": 50
                },
                "queries": {
                    "type": "array",
                    "description": "A list of search queries to run",
                    "items": {
                        "type": "string"
                    },
                    "maxItems": 50
                },
            },
            "required": ["company_names", "queries"]
        }
    }

    SWARM_RESEARCH_SCHEMA = {
        "name": "swarm_research",
        "description": "Dispatches a swarm of agents to evaluate a query across a list of companies, returning a sorted list of companies by relevance to the query",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",   
                    "description": "The query to evaluate the companies against. This can include multple conditions in one natural language query. For instance \"companies with a 10x higher following on social media than active users, with high average revenue per user and positive net revenue retention rates\""
                },
                "companies": {
                    "type": "array",
                    "description": "A list of companies to research"
                },
                "searches": {
                    "type": "array",
                    "description": "A list of searches required to evaluate the companies against the query. These should be atomic searches. Format them including the company name ie \"{company} net revenue retention rate\" or \"Does {company} have an office in San Antonio\" etc."
                }
            },
            "required": ["query", "companies", "searches"]
        }
    }

    SCRAPE_URL_SCHEMA = {
        "name": "scrape_url",
        "description": "Scrapes and cleans content from a given URL, returning the main content and metadata",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape and extract content from"
                }
            },
            "required": ["url"]
        }
    }

    def __init__(self, openai_api_key, serper_api_key):
        """Initialize the research tools with API clients."""
        self._llm = OpenAIClient(api_key=openai_api_key)
        self._serper = SerperClient(api_key=serper_api_key)
        self._scraper = ScraperClient()
        self.swarm = EvalSwarm(self._llm, self._serper, max_workers=50)

    @property
    def llm(self):
        """Access the OpenAI client for cost tracking."""
        return self._llm

    @property
    def serper(self):
        """Access the Serper client for cost tracking."""
        return self._serper

    @property
    def scraper(self):
        """Access the scraper client."""
        return self._scraper

    def get_schemas_and_functions(self):
        """Returns a tuple of (schemas, functions) where schemas is a list of schema definitions
        and functions is a list of corresponding function references bound to this instance."""
        schemas = [
            self.PARALLEL_WEBSEARCH_SCHEMA,
            # self.COMPANY_WEBSEARCH_SCHEMA,
            self.SWARM_RESEARCH_SCHEMA,
            self.SCRAPE_URL_SCHEMA
        ]
        
        functions = [
            self.parallel_websearch,
            # self.company_websearch,
            self.swarm_research,
            self.scrape_url
        ]
        return schemas, functions

    async def _parallel_websearch_async(self, searches):
        """Internal async method for parallel web search."""
        return await self._serper.search_async_batch(searches, include_urls=True)

    async def _parallel_llm_async(self, messages):
        """Internal async method for parallel LLM calls."""
        return await self._llm.chat_completion_async_batch(messages)

    def parallel_websearch(self, query):
        """Execute parallel web search for the given queries."""
        return asyncio.run(self._parallel_websearch_async(query['queries']))

    def company_websearch(self, query):
        """Execute parallel web search for company-specific queries."""
        queries = [f"{company_name} {search_query}" 
                  for company_name in query['company_names'] 
                  for search_query in query['queries']]
        return asyncio.run(self._parallel_websearch_async(queries))

    def swarm_research(self, query):
        """Execute swarm research for the given query and companies."""
        results = asyncio.run(self.swarm.research(
            query['query'], 
            query['companies'], 
            query['searches']
        ))
        results.sort(key=lambda x: x["final_score"], reverse=True)

        # Format results as a string, only including results with score > 50
        string_result = ""
        for result in results:
            if result["final_score"] > 50:
                string_result += json.dumps(result) + "\n"
        return string_result

    def scrape_url(self, query):
        """Scrape and clean content from a given URL."""
        result = self._scraper.scrape_url(query['url'])
        if "error" in result and result["error"]:
            return json.dumps({"error": result["error"]})
        return json.dumps(result, indent=2)