"""
Main LLM agent that handles user requests , tool selection , and final response
"""

import os 
import json 
from dotenv import load_dotenv
from openai import OpenAI 
from tools import lookup_order, search_policy , OPENAI_TOOL_SCHEMAS

load_dotenv() # load environment variables

# initialize openai
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

# function to ask LLM
def ask_llm(user_message):

    response = client.responses.create( # create response
        model="gpt-5.6-sol",
        input=user_message, # user message
        tools=OPENAI_TOOL_SCHEMAS, # tools
    )

    for item in response.output: # iterate over output

        if item.type == "function_call": 

            arguments = json.loads(item.arguments) # parse arguments

            if item.name == "lookup_order":
                result = lookup_order(arguments["order_id"])

            elif item.name == "search_policy":
                result = search_policy(arguments["query"])

            else:
                result = {
                    "success": False,
                    "error": "unknown_tool",
                    "message": f"Unknown tool: {item.name}"
                }

            print("Tool selected:", item.name)
            print("Tool result:", result)

            tool_response = client.responses.create( # create response
                model="gpt-5.6-sol",
                previous_response_id=response.id,
                input=[
                    {
                        "type": "function_call_output", # function call output
                        "call_id": item.call_id, # call id
                        "output": json.dumps(result), # output
                    },
                ],
            )

            return tool_response.output_text # return tool response

    return response.output_text # return response