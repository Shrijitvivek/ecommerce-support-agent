# E-Commerce Support Agent

A command-line customer support agent that uses an LLM (via the OpenAI API) with tool-calling to answer questions about orders and store policy, and to remember a customer's preferred resolution (refund vs. replacement) across turns.

## Features

- **Order lookup** — Look up order status, product, amount, and delivery date by order ID (e.g. `ORD1002`).
- **Policy search** — Answer questions about returns, refunds, replacements, exceptions, damaged/defective items, and return shipping using a local policy knowledge base.
- **Preference memory** — Detects when a customer states a preferred resolution ("I prefer a refund" / "I prefer a replacement") and saves it to `data/preferences.json` so future responses take it into account.
- **Agentic tool loop** — The agent calls tools as needed (including multiple rounds) until it has enough information to give a final answer.
- **Simple CLI** — Chat with the agent directly from the terminal, with conversation history maintained for the session.

## Project Structure

```
.
├── main.py               # CLI entry point — manages session & conversation history
├── agent.py               # Core agent loop — LLM calls, tool dispatch, preference handling
├── tools.py                # Business tools + OPENAI_TOOL_SCHEMAS: lookup_order, search_policy
├── memory_store.py    # Reads/writes customer preferences
├── data/
│   ├── orders.json         # Sample order records
│   ├── policy.json          # Sample return/refund/replacement policy KB
│   └── preferences.json  # Saved customer preferences (updated at runtime)
├── tests/
│   └── test_agent.py       # (placeholder for agent tests)
├── requirements.txt
└── .env.example
```

## Requirements

- Python 3.9+
- An OpenAI API key
- An OpenAI model available on your account that supports the Responses API and tool calling (e.g. `gpt-4o`)

## Setup

1. **Clone the repo and install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   > Note: `requirements.txt` is currently empty in this repo — install at least `openai` and `python-dotenv`:
   > ```bash
   > pip install openai python-dotenv
   > ```

2. **Configure your API key:**

   Copy `.env.example` to `.env` and fill in your key:

   ```bash
   cp .env.example .env
   ```

   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Set a valid model name.**

   `agent.py` calls `client.responses.create(model="gpt-5.6-sol", ...)` in two places. `gpt-5.6-sol` is a placeholder and is not a real OpenAI model — replace it with a model your API key has access to (e.g. `gpt-4o`), or every request will fail with an invalid-model error.

## Usage

Run the CLI:

```bash
python main.py
```

You'll be prompted for a user ID (e.g. `user_001`), then you can chat with the agent. Type `quit` or `exit` to end the session.

### Example

```
E-Commerce Support Agent
Type 'quit' or 'exit' to end the session.

Enter your user ID (e.g. user_001): user_001
You: What's the status of order ORD1002?
Agent: Order ORD1002 (Smart Watch) has shipped and is on its way. Delivery date isn't confirmed yet.

You: Can I get a refund if it arrives damaged?
Agent: Yes — damaged or defective items can be reported within 30 days of delivery for a free replacement or full refund, regardless of the standard 15-day return window.

You: I prefer a refund over a replacement.
Agent: Got it, I've noted that you prefer a refund for future resolutions.
```

## How It Works

1. `main.py` reads user input and passes the running conversation history to `agent.run()`.
2. `agent.py`:
   - Checks the message for a stated preference ("prefer refund" / "prefer replacement") and saves it via `memory_store.save_preference`.
   - Loads any previously saved preference and injects it as a system message for context.
   - Sends the conversation to the LLM along with `tools.OPENAI_TOOL_SCHEMAS`, which describes the available tools to the model.
   - If the model requests a tool call, dispatches it to `lookup_order` or `search_policy`, sends the result back to the model (via `previous_response_id`), and repeats until the model returns a final text answer.
3. `tools.py` implements the two tools against the local JSON data files in `data/`, always returning a `{"success": bool, ...}` shaped dict so the agent can fail gracefully instead of inventing information. It also defines `OPENAI_TOOL_SCHEMAS`, the OpenAI Responses API tool schemas describing `lookup_order` and `search_policy` to the model — this is what `agent.py` imports.
4. `memory_store.py` persists per-user preferences to `data/preferences.json`.

## Tool Schemas

`tools.py` exports `OPENAI_TOOL_SCHEMAS`, a list of two function-tool definitions in the OpenAI Responses API format:

```python
OPENAI_TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "lookup_order",
        "description": "Look up an order by its order ID ...",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "..."}
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_policy",
        "description": "Search the store's return/refund/replacement policy ...",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "..."}
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
]
```

`agent.py` passes this list as the `tools` argument on every `client.responses.create(...)` call, and dispatches any `function_call` the model returns to the matching Python function in `tools.py`.

## Data

The `data/` directory contains sample/demo data only:

- **`orders.json`** — six sample orders across three customers with varying statuses (delivered, shipped, processing, cancelled).
- **`policy.json`** — a small keyword-searchable knowledge base covering return windows, refunds, replacements, exceptions, damaged/defective items, and return shipping costs.
- **`preferences.json`** — starts with one sample preference and is updated as users interact with the agent.



