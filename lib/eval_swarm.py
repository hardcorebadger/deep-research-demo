# Answer the query for each company, provided a pre-selected list of searches for RAG
# Input: query, companies, searches
# Output: company, score, reason

import json
from lib.openai_client import OpenAIClient
from lib.serper_client import SerperClient
from lib.message_factory import system_user_message
from lib.swarm import Swarm

ANSWER_FORMAT = {
    "company": "company name",
    "query": "query",
    "crieria_decomposition": [
        {
            "criteria": "criteria name",
            "score": "score between 0 and 100",
            "reason": "short reason for the score"
        },
        {
            "criteria": "criteria name",
            "score": "score between 0 and 100",
            "reason": "short reason for the score"
        }
    ],
    "final_score": "score between 0 and 100",
    "reason": "short reason for the score",
}

DEFAULT_EVAL_SYSTEM = f"""Your job is to evaluate whether the company meets the condition(s) in the query.
You will be given a company name, a query, and a list of search results.
You will need to evaluate whether the company meets the condition by returning a score between 0 and 100, and a short reason for the score.
Don't over index on the search results, use your own knowledge as well.
Reasoning should be concise as possible and data dense; 10-20 words. Only include data that is relevant to the query. One sentence is enough for the reason.
If a condition is clearly not met, the score should be 0. For less discrete conditions, the score should be between 0 and 100.
Queries may have multiple conditions, if its "and" the final score should be the minimum score of all conditions. If its "or" the final score should be the maximum score of all conditions.
Your answer should be in the following JSON format:
{json.dumps(ANSWER_FORMAT)}
"""

DEFAULT_EVAL_USER = """Company: {company}
Query: {query}
Search results: {rag}

Answer the query based on the search results and your own knowledge.

Answer:"""

class EvalSwarm(Swarm):
    def __init__(self, 
                 llm: OpenAIClient, serper: SerperClient, 
                 eval_system: str = DEFAULT_EVAL_SYSTEM,
                 eval_user: str = DEFAULT_EVAL_USER,
                 max_workers: int = 50,
                 requests_per_second: int = 50
                 ):
        super().__init__(llm, serper, max_workers, requests_per_second)
        self.eval_system = eval_system
        self.eval_user = eval_user

    async def query(self, query: str, company: str, searches: list[str]) -> str:
        rag = ""
        for search in searches:
            search_query = search.format(company=company)
            search_results = await self.serper.search_async(search_query)
            rag += f"{search_query}\n{search_results}\n\n"
        eval_results = await self.llm.chat_completion_async(
            system_user_message(self.eval_system, self.eval_user.format(company=company, query=query, rag=rag)), 
            max_tokens=250, 
            json_response=True
        )
        eval_results['final_score'] = int(eval_results['final_score'])
        print(".", end="", flush=True)
        return eval_results



