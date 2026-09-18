"""
Main LLM agent that handles user requests,
tool selection, tool execution, and final response.
"""

import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from tools import (
    lookup_order,
    search_policy,
    OPENAI_TOOL_SCHEMAS
)

from memory_store import (
    get_preference,
    save_preference
)


# --------------------------------------------------
# Load environment variables from .env
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Initialize OpenAI client
# --------------------------------------------------

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# --------------------------------------------------
# Function to ask the LLM
# --------------------------------------------------

def ask_llm(user_message, user_id="user_001", history=None):

    # Log the user's request for the agent trace
    print("User request:", user_message)


    # --------------------------------------------------
    # Save user's preferred resolution if mentioned
    # --------------------------------------------------

    if (
        "refund" in user_message.lower()
        and "prefer" in user_message.lower()
    ):
        save_preference(user_id, "refund")

    elif (
        "replacement" in user_message.lower()
        and "prefer" in user_message.lower()
    ):
        save_preference(user_id, "replacement")


    # --------------------------------------------------
    # Get saved customer preference
    # --------------------------------------------------

    preference = get_preference(user_id)

    # Add the saved customer preference to the conversation
    # context if one exists
    if preference:
        preference_message = {
            "role": "system",
            "content": (
                f"The customer's saved preferred resolution "
                f"is: {preference}."
            )
        }
    else:
        preference_message = None


    # --------------------------------------------------
    # Create the first LLM response
    # --------------------------------------------------

    response = client.responses.create(
        model="gpt-5.6-sol",

        # Rules the LLM must follow
        instructions=(
            "You are an e-commerce customer support agent. "
            "Use only information provided by the available tools. "
            "Never invent or guess order details, order status, "
            "return policies, refund policies, or replacement policies. "
            "If a tool fails or cannot find the requested information, "
            "clearly tell the customer that the information "
            "could not be found. "
            "If the request is unrelated to e-commerce support, "
            "politely ask the customer to provide an order ID or ask "
            "about returns, refunds, replacements, or store policies. "
            "Do not call a tool for unrelated requests."
        ),

        # Send conversation history and customer preference
        input=(
            [preference_message] + history
            if preference_message and history
            else [
                preference_message,
                {
                    "role": "user",
                    "content": user_message
                }
            ]
            if preference_message
            else history if history else user_message
        ),

        # Give the LLM access to our tools
        tools=OPENAI_TOOL_SCHEMAS,
    )


    # --------------------------------------------------
    # Agent loop
    #
    # The LLM may:
    # 1. Answer directly
    # 2. Request a tool
    # 3. Request another tool after seeing a result
    #
    # Therefore, we keep processing until the LLM
    # produces a final answer.
    # --------------------------------------------------

    while True:

        # Store outputs from all tool calls
        tool_outputs = []


        # --------------------------------------------------
        # Check everything returned by the LLM
        # --------------------------------------------------

        for item in response.output:

            # We only process function/tool calls here
            if item.type == "function_call":

                # Convert JSON arguments into a Python dictionary
                arguments = json.loads(item.arguments)


                # --------------------------------------------------
                # Tool 1: Order Lookup
                # --------------------------------------------------

                if item.name == "lookup_order":

                    result = lookup_order(
                        arguments["order_id"]
                    )


                # --------------------------------------------------
                # Tool 2: Policy Search
                # --------------------------------------------------

                elif item.name == "search_policy":

                    result = search_policy(
                        arguments["query"]
                    )


                # --------------------------------------------------
                # Unknown tool
                # --------------------------------------------------

                else:

                    result = {
                        "success": False,
                        "error": "unknown_tool",
                        "message": f"Unknown tool: {item.name}"
                    }


                # --------------------------------------------------
                # Print tool trace
                # --------------------------------------------------

                print("Tool selected:", item.name)
                print("Tool input:", arguments)
                print("Tool result:", result)


                # --------------------------------------------------
                # Prepare the tool result for the LLM
                #
                # call_id connects this result to the exact
                # function call made by the LLM.
                # --------------------------------------------------

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }
                )


        # --------------------------------------------------
        # If no tool was requested, the LLM has produced
        # a normal/final answer.
        # --------------------------------------------------

        if not tool_outputs:

            # Get the final answer from the LLM
            final_response = response.output_text

            # Log the final response for the agent trace
            print("Final response:", final_response)

            return final_response


        # --------------------------------------------------
        # Send all tool results back to the LLM
        #
        # previous_response_id tells the API that these
        # tool results belong to the previous response.
        # --------------------------------------------------

        response = client.responses.create(
            model="gpt-5.6-sol",

            previous_response_id=response.id,

            input=tool_outputs,

            tools=OPENAI_TOOL_SCHEMAS,
        )


# --------------------------------------------------
# Run function used by main.py
# --------------------------------------------------

def run(user_id, history, user_message):

    return ask_llm(
        user_message,
        user_id,
        history
    )