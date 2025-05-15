from anthropic import Anthropic
from termcolor import colored
import json
from typing import Callable



class Agent:
    def __init__(self, model_name: str, api_key: str, system: str, tools: list[dict], funcs: dict[str, Callable], max_iterations: int = 10, temperature: float = 0.0):
        self.model_name = model_name
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key)
        self.system = system
        self.tools = tools
        self.funcMap = self.map_to_tools(tools, funcs)
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.messages = []
        self.input_tokens = 0
        self.output_tokens = 0

    def map_to_tools(self, tools: list[dict], funcs: dict[str, Callable]) -> dict[str, Callable]:
        return {tool["name"]: func for tool, func in zip(tools, funcs)}
    
    def process_tool_call(self, tool_name, tool_input):
        if tool_name in self.funcMap:
            return self.funcMap[tool_name](tool_input)
        else:
            raise ValueError(f"Unexpected tool name: {tool_name}")
    

    def model_call(self, allow_tools: bool = True, max_tokens: int = 5000):
        if allow_tools:
            response = self.client.messages.create(
                model=self.model_name,
                messages=self.messages,
                max_tokens=max_tokens,
                system = self.system,
                tool_choice={"type": "auto"},
                tools=self.tools,
            )
        else:
            response = self.client.messages.create(
                model=self.model_name,
                messages=self.messages,
                max_tokens=max_tokens,
                system = self.system,
            )
        self.input_tokens += response.usage.input_tokens
        self.output_tokens += response.usage.output_tokens
        return response

    def run(self, input):
        # add the user message to history
        self.messages.append({"role":"user", "content":input})

        # run the agent loop
        iter = 0
        while iter < self.max_iterations:

            # run the completion
            response = self.model_call()
            # print(response)
            self.messages.append({"role": "assistant", "content": response.content})

            tool_use = None
            text = None
            for block in response.content:
                match block.type:
                    case "text":
                        text = block
                        
                    case "tool_use":
                        tool_use = block
                        # print(f"Tool: {block.name}({block.input})")
                    case _:
                        raise ValueError(f"Unexpected block type: {block.type}")

            # print(message)

            # check if the model wants to call a function
            if tool_use:
                # if so, get the function info
                function_name = tool_use.name
                function_input = tool_use.input
                if text:
                    print(colored(text.text, "blue"))
                # can replace this with callbacks
                print(colored(f"Using {function_name} with input:\n {json.dumps(function_input, indent=4)}", "yellow"))

                # call the function
                results = self.process_tool_call(function_name, function_input)

                # this is for debug
                print(colored(results, "red"))

                # add the function results to the chat history
                self.messages.append({"role":"user","content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": results,
                    }
                ]})
                # then return to recall the model, +1 iterations
                iter = iter + 1

            # otherwise print the response and get user input
            else:
                print(colored(text.text, "blue"))
                return text

        # when iterations max out, kill the loop

        response = self.model_call(allow_tools=False)
        self.messages.append({"role": "assistant", "content": response.content})
        print(response.content[0].text)
        return response.content
    
    def input_loop(self):
        while True:
            i = input("Enter a query: ")
            if i == "exit":
                break
            self.run(i)

    def get_costs(self, input_cpm: float = 3.0, output_cpm: float = 15.0):
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "input_cost": self.input_tokens * input_cpm / 1000000,
            "output_cost": self.output_tokens * output_cpm / 1000000,
            "cost": self.input_tokens * input_cpm / 1000000 + self.output_tokens * output_cpm / 1000000,
        }
