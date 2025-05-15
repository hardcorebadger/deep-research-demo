import asyncio
import json
from openai import AsyncOpenAI, OpenAI

class OpenAIClient:
    def __init__(self, api_key: str):
        self.sync = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.input_tokens = 0
        self.output_tokens = 0
        
    def chat_completion(self, messages: list[dict], model: str = "gpt-4o-mini", temperature: float = 0.0, max_tokens: int = 1000, json_response: bool = False) -> str:
        response = self.sync.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"} if json_response else None
        )
        self.input_tokens += response.usage.prompt_tokens
        self.output_tokens += response.usage.completion_tokens
        return response.choices[0].message.content if not json_response else json.loads(response.choices[0].message.content)
    
    
    async def chat_completion_async(self, messages: list[dict], model: str = "gpt-4o-mini", temperature: float = 0.0, max_tokens: int = 1000, json_response: bool = False) -> str:
        response = await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"} if json_response else None
        )
        self.input_tokens += response.usage.prompt_tokens
        self.output_tokens += response.usage.completion_tokens
        return response.choices[0].message.content if not json_response else json.loads(response.choices[0].message.content)
    
    async def chat_completion_async_batch(self, messages: list[list[dict]], model: str = "gpt-4o-mini", temperature: float = 0.0, json_response: bool = False) -> list[str]:
        tasks = [self.chat_completion_async(message, model, temperature, json_response=json_response) for message in messages]
        return await asyncio.gather(*tasks)
    
    def get_costs(self, input_cpm: float = 0.30, output_cpm: float = 1.20):
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "input_cost": round(self.input_tokens * input_cpm / 1000000, 4),
            "output_cost": round(self.output_tokens * output_cpm / 1000000, 4),
            "cost": round((self.input_tokens * input_cpm + self.output_tokens * output_cpm) / 1000000, 4)
        }
        