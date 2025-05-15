# Answer the query for each company, provided a pre-selected list of searches for RAG
# Input: query, companies, searches
# Output: company, answer, confidence

from lib.openai_client import OpenAIClient
from lib.serper_client import SerperClient
from lib.message_factory import system_user_message
from lib.swarm import Swarm

DEFAULT_ANSWER_SYSTEM = "Your job is to answer the query about the company.\nYou will be given a company name, a query, and a list of search results.\nYou will need to provide a clear answer to the query and indicate your confidence level.\nYou will need to return a confidence score between 0 and 100, and an answer based on the search results and your own knowledge.\nDon't over index on the search results, use your own knowledge as well.\nAnswer should be concise as possible and data dense; 10-20 words. Only include data that is relevant to the query.\nYour answer should be in JSON format with values company, answer, confidence"
DEFAULT_ANSWER_USER = "Company: {company}\nQuery: {query}\nSearch results: {rag}\n\nAnswer the query based on the search results and your own knowledge.\n\nAnswer:"

class AnswerSwarm(Swarm):
    def __init__(self, 
                 llm: OpenAIClient, serper: SerperClient, 
                 answer_system: str = DEFAULT_ANSWER_SYSTEM,
                 answer_user: str = DEFAULT_ANSWER_USER,
                 max_workers: int = 50,
                 requests_per_second: int = 50
                 ):
        super().__init__(llm, serper, max_workers, requests_per_second)
        self.answer_system = answer_system
        self.answer_user = answer_user

    async def query(self, query: str, company: str, searches: list[str]) -> str:
        rag = ""
        for search in searches:
            search_query = search.format(company=company)
            search_results = await self.serper.search_async(search_query)
            rag += f"{search_query}\n{search_results}\n\n"
        answer_results = await self.llm.chat_completion_async(
            system_user_message(self.answer_system, self.answer_user.format(company=company, query=query, rag=rag)), 
            max_tokens=250, 
            json_response=True
        )
        print(".", end="", flush=True)
        return answer_results 