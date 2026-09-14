import os
import json
from openai import OpenAI
from pprint import pprint
from dotenv import load_dotenv

from functions import solve_quadratic, get_weather, complex_to_json

# Load environment variables
load_dotenv()

# Initialize OpenAI client pointing to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# Define custom tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "solve_quadratic",
            "description": "Use this function to solve quadratic equation ax^2 + bx + c = 0",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "first constant a",
                    },
                    "b": {
                        "type": "number",
                        "description": "second constant b",
                    },
                    "c": {
                        "type": "number",
                        "description": "third constant c",
                    },
                },
                "required": ["a", "b", "c"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Use this function to get the current weather in a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "name of the city, e.g. Prague",
                    },
                },
                "required": ["city"],
            },
        },
    },
]

available_functions = {
    "solve_quadratic": solve_quadratic,
    "get_weather": get_weather,
}


# Function to process messages and handle function calls
def get_completion_from_messages(messages, model="google/gemma-4-31b-it"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,  # Custom tools
        tool_choice="auto",  # Allow AI to decide if a tool should be called
    )

    response_message = response.choices[0].message

    print("First response:", response_message)

    if response_message.tool_calls:
        # Find the tool call content
        tool_call = response_message.tool_calls[0]

        # Extract tool name and arguments
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        tool_id = tool_call.id

        # Call the function
        function_to_call = available_functions[function_name]
        function_response = function_to_call(**function_args)

        messages.append(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": tool_id,
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": json.dumps(function_args),
                        },
                    }
                ],
            }
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_id,
                "name": function_name,
                "content": json.dumps(function_response, default=complex_to_json),
            }
        )

        # Second call to get final response based on function output
        second_response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        final_answer = second_response.choices[0].message

        print("Second response:", final_answer)
        return final_answer

    return "No relevant function call found."


# Example usage
messages = [
    {"role": "system", "content": "You are a living calculator, return just result numbers with summary no explanation how you compute it."},
    {"role": "user", "content": "solve quadratic equation ax^2 + bx + c = 0 with a = 1 b = 2 c = 3"},
    #{"role": "system", "content": "You are a weather forecaster."},
    #{"role": "user", "content": "Tell me weather in Praha"}
]

response = get_completion_from_messages(messages)
print("--- Full response: ---")
pprint(response)
print("--- Response text: ---")
print(response.content)
