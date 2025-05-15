import asyncio
from abc import ABC, abstractmethod
from lib.openai_client import OpenAIClient
from lib.serper_client import SerperClient
from collections import deque
from time import time

class RateLimiter:
    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        
    async def acquire(self):
        now = time()
        # Remove old requests outside the time window
        while self.requests and now - self.requests[0] > self.time_window:
            self.requests.popleft()
            
        if len(self.requests) >= self.max_requests:
            # Wait until the oldest request expires
            wait_time = self.requests[0] + self.time_window - now
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                
        self.requests.append(now)

class Swarm(ABC):
    def __init__(self, 
                 llm: OpenAIClient, 
                 serper: SerperClient,
                 max_workers: int = 50,
                 requests_per_second: int = 50
                 ):
        self.llm = llm
        self.serper = serper
        self.max_workers = max_workers
        self.rate_limiter = RateLimiter(requests_per_second, 1.0)

    @abstractmethod
    async def query(self, query: str, company: str, searches: list[str]) -> str:
        """Process a single company query. Must be implemented by subclasses."""
        pass

    async def _worker(self, query: str, searches: list[str], company_queue: asyncio.Queue, result_queue: asyncio.Queue):
        while True:
            try:
                company = await company_queue.get()
                if company is None:  # Poison pill to stop worker
                    break
                
                # Acquire rate limit token before making the request
                await self.rate_limiter.acquire()
                result = await self.query(query, company, searches)
                await result_queue.put(result)
            except Exception as e:
                print(f"Error processing {company}: {e}")
                await result_queue.put(None)
            finally:
                company_queue.task_done()

    async def research(self, query: str, companies: list[str], searches: list[str]) -> list[tuple[str, str, str]]:
        # Create queues for companies and results
        company_queue = asyncio.Queue()
        result_queue = asyncio.Queue()
        
        # Fill the company queue
        for company in companies:
            await company_queue.put(company)
            
        # Add poison pills to stop workers
        for _ in range(self.max_workers):
            await company_queue.put(None)
            
        # Create worker tasks
        workers = [
            asyncio.create_task(self._worker(query, searches, company_queue, result_queue))
            for _ in range(self.max_workers)
        ]
        
        print(f"Starting research: {len(companies)} companies with {self.max_workers} workers")
        
        # Wait for all companies to be processed
        await company_queue.join()
        
        # Cancel any remaining workers
        for worker in workers:
            worker.cancel()
            
        # Collect results
        results = []
        while not result_queue.empty():
            result = await result_queue.get()
            if result is not None:
                results.append(result)
                
        print()  # New line at the end
        return results 