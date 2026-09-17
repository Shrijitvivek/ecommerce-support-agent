"""
Person A - Tools & Data Layer
==============================
This module provides the two required business tools for the
e-commerce customer support agent:

    1. lookup_order(order_id)   -> Order Lookup Tool
    2. search_policy(query)     -> Policy Search Tool


"""

import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ORDERS_PATH = os.path.join(DATA_DIR, "orders.json")
POLICY_PATH = os.path.join(DATA_DIR, "policy.json")

ORDER_ID_PATTERN = re.compile(r"^ORD\d{4,}$", re.IGNORECASE)


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_orders():
    return _load_json(ORDERS_PATH)["orders"]


def _load_policies():
    return _load_json(POLICY_PATH)["policies"]



# Tool 1: Order Lookup

def lookup_order(order_id):
    """
    Look up a single order by its order ID.

    Args:
        order_id (str): e.g. "ORD1002"

    Returns:
        dict: success/data or success/error/message (see module docstring)
    """
    # --- input validation ---
    if order_id is None or not isinstance(order_id, str) or not order_id.strip():
        return {
            "success": False,
            "error": "invalid_input",
            "message": "An order ID is required to look up an order.",
        }

    cleaned_id = order_id.strip().upper()

    if not ORDER_ID_PATTERN.match(cleaned_id):
        return {
            "success": False,
            "error": "invalid_input",
            "message": (
                f"'{order_id}' doesn't look like a valid order ID "
                "(expected format like ORD1002)."
            ),
        }

    # --- lookup ---
    orders = _load_orders()
    for order in orders:
        if order["order_id"].upper() == cleaned_id:
            return {"success": True, "data": order}

    # --- not found: fail gracefully, never invent a status ---
    return {
        "success": False,
        "error": "order_not_found",
        "message": f"No order found with ID '{cleaned_id}'. Please double-check the order ID.",
    }


# Tool 2: Policy Search

def search_policy(query):
    """
    Search the local policy knowledge base for a matching topic.

    Args:
        query (str): free-text topic, e.g. "return window" or "can I get a refund"

    Returns:
        dict: success/data or success/error/message (see module docstring)
    """
    # --- input validation ---
    if query is None or not isinstance(query, str) or not query.strip():
        return {
            "success": False,
            "error": "invalid_input",
            "message": "A topic or question is required to search the policy.",
        }

    q = query.strip().lower()
    policies = _load_policies()

    # simple keyword scoring: count how many of a policy's keywords/title
    # words appear as substrings of the query (or vice versa)
    best_match = None
    best_score = 0
    for policy in policies:
        score = 0
        haystacks = [policy["title"].lower()] + [k.lower() for k in policy["keywords"]]
        for phrase in haystacks:
            if phrase in q or q in phrase:
                score += 1
        if score > best_score:
            best_score = score
            best_match = policy

    if best_match is None or best_score == 0:
        return {
            "success": False,
            "error": "policy_not_found",
            "message": (
                f"I couldn't find policy information matching '{query}'. "
                "Try asking about returns, refunds, replacements, or exceptions."
            ),
        }

    return {
        "success": True,
        "data": {
            "topic_id": best_match["topic_id"],
            "title": best_match["title"],
            "content": best_match["content"],
        },
    }

# OpenAI function-calling schemas (hand these to Person B)

# This is a list of functions that can be called by the LLM
# Responses API tool schemas: name/description/parameters are top-level fields.
OPENAI_TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "lookup_order",
        "description": (
            "Look up a customer order by its order ID to get its status, "
            "purchase date, product, and amount. Use this any time the user "
            "asks about a specific order or its eligibility for return, "
            "instead of guessing the order's status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID, e.g. 'ORD1002'."
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "type": "function",
        "name": "search_policy",
        "description": (
            "Search the store's return/refund/replacement policy for a given "
            "topic or question. Use this any time the user asks about return "
            "windows, refund timing, replacement eligibility, or exceptions, "
            "instead of answering from general knowledge."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The policy topic or question, e.g. 'return window', "
                        "'how long does a refund take', 'can I get a replacement'."
                    )
                }
            },
            "required": ["query"]
        }
    }
]


# Self-test / demo


if __name__ == "__main__":
    print("== Order lookup: valid ==")
    print(json.dumps(lookup_order("ORD1002"), indent=2))

    print("\n== Order lookup: not found ==")
    print(json.dumps(lookup_order("ORD9999"), indent=2))

    print("\n== Order lookup: invalid input ==")
    print(json.dumps(lookup_order(""), indent=2))
    print(json.dumps(lookup_order("banana"), indent=2))

    print("\n== Policy search: return window ==")
    print(json.dumps(search_policy("Can I return my product?"), indent=2))

    print("\n== Policy search: replacement ==")
    print(json.dumps(search_policy("I want a replacement not a refund"), indent=2))

    print("\n== Policy search: not found ==")
    print(json.dumps(search_policy("do you sell gift wrapping"), indent=2))

    print("\n== Policy search: invalid input ==")
    print(json.dumps(search_policy("   "), indent=2))