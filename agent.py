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
    response = client.responses.create( # generate response
        model = "gpt-5.6-sol",
        input = user_message,
        tools = OPENAI_TOOL_SCHEMAS,
        
    )
    return response.output_text # return response as text