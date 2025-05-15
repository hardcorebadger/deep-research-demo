import asyncio
import json
import time
import os
from dotenv import load_dotenv
from lib.openai_client import OpenAIClient
from lib.agent import Agent
from lib.serper_client import SerperClient
from lib.message_factory import system_user_message, zero_shot_message
from lib.eval_swarm import EvalSwarm
from lib.portfolio import Portfolio
from lib.research_tools import ResearchTools

# Load environment variables from .env file if it exists
load_dotenv()

# Get API keys from environment variables
ex_model_name = "claude-3-7-sonnet-20250219"
ex_api_key = os.environ.get("ANTHROPIC_API_KEY")
if not ex_api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

framework = """
# Efficient Company Research Framework

## 1. Define Precise Criteria
- Extract specific measurable parameters from request
- Set clear thresholds for qualification
- Disambiguate any vague terms

## 2. Generate Comprehensive Candidate Pool
- Leverage existing knowledge to identify initial candidates
- Conduct broad discovery searches across industries
- Compile a working list of 20-50 companies with high potential
- Document this initial candidate pool

(Think out loud - at this point you should write out your thoughts and the initial candidate pool)

## 3. Execute Targeted Research
- Gather specific data for each criterion for all candidates
- Triangulate information from multiple sources
- Document data sources and confidence levels
- Note where information is unavailable or incomplete

## 4. Evaluate Against Criteria
- Apply strict qualification filters to all candidates
- Rank companies by degree of criteria match
- Document specific reasons for inclusion or exclusion
- Identify partial matches worth noting

## 5. Present Results
- List all qualifying companies with ticker symbols
- Score each company based on criteria fit (1-10)
- Include key supporting data points for each qualifier
- Organize by relevance to original request
- Identify any notable patterns or insights
"""
framework_old = """
# Overview

1. Before dispatching the swarm, think to yourself about the query, and come up with a list of 20-50 companies that are probable candidates. Write this out loud along with your reasoning.
2. If required, run a swarm research to evaluate the companies against the criteria. (Some queries are easy enough to evaluate without a swarm)
3. Evaluate the results, and return a list of companies that fit the criteria.

"""
ex_system_old = f"""
You are a deep research agent focused on finding public companies that meet the user's criteria.

Tools:
- parallel_websearch: Searches the web for information
- swarm_research: Dispatches a swarm of agents to evaluate a query across a list of companies, returning a sorted list of companies by relevance to the query

Usage:
- Use parallel_websearch to search the web for broad information, typically in discovery
- Use swarm_research to evaluate a query across a list of companies

Final results must be public companies trading on a major exchange. Include the symbol.
Your answers should be exhaustive as possible. Use the following framework:

{framework_old}

Show your work as you go, thinking out loud. Do not wait until the end to show your work.
"""

new_system = """
You are a deep research agent focused on finding public companies that meet the user's criteria.

Research Tools:
- parallel_websearch: Searches the web for information (max 50 queries at a time)
- swarm_research: Dispatches a swarm of agents to evaluate a query across a list of companies, returning a sorted list of companies by relevance to the query

Portfolio Tools:
- add_companies: Adds a list of companies to the portfolio
- remove_companies: Removes a list of companies from the portfolio
- get_portfolio: Returns the current portfolio
- change_weight: Changes the weight of a company in the portfolio
- weight_by: Weights the portfolio by the given metric

The user can see the portfolio in the UI next to you. Instead of writing out the portfolio, you can use the Portfolio Tools to add, remove, and change the weight of companies in the portfolio.
"""


portfolio = Portfolio()
research_tools = ResearchTools(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    serper_api_key=os.environ.get("SERPER_API_KEY")
)

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is required")
if not os.environ.get("SERPER_API_KEY"):
    raise ValueError("SERPER_API_KEY environment variable is required")

portfolio_schemas, portfolio_functions = portfolio.get_schemas_and_functions()
research_tools_schemas, research_tools_functions = research_tools.get_schemas_and_functions()

agent = Agent(
    ex_model_name, 
    ex_api_key, 
    new_system, 
    [*research_tools_schemas, *portfolio_schemas], 
    [*research_tools_functions, *portfolio_functions]
)

# t = time.time()
# agent.input_loop()
# # agent.inpt("companies whose CEO has a podcast")
# print(f"Agent costs: ${round(agent.get_costs()['cost'], 4)}")
# print(f"LLM costs: ${round(research_tools.llm.get_costs()['cost'], 4)}")
# print(f"Serper costs: ${round(research_tools.serper.get_costs()['cost'], 4)}")
# print(f"Total time: {round(time.time() - t, 2)}s")
# print(f"Total costs: ${round(agent.get_costs()['cost'] + research_tools.serper.get_costs()['cost'] + research_tools.llm.get_costs()['cost'], 4)}")
