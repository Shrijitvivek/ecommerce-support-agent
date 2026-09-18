# E-Commerce Support Agent

An AI-powered customer support agent for e-commerce that can check orders, answer return/refund/replacement policy questions, and remember customer preferences.

The agent uses an LLM with tool calling to decide when it needs information from the order or policy data.

## Features

- **Order Lookup** – Check order status, product, amount, purchase date, and delivery date.
- **Policy Search** – Answer questions about returns, refunds, replacements, damaged items, exceptions, and return shipping.
- **Multi-Tool Calling** – Use multiple tools for a single request when needed.
- **Session Memory** – Remembers information from the current conversation.
- **Persistent Preference Memory** – Remembers whether a customer prefers a refund or replacement.
- **Failure Handling** – Handles unknown orders and unavailable policies without making up information.
- **Agent Trace** – Shows the user request, selected tool, tool input, tool result, and final response.
- **CLI Interface** – Simple terminal-based interaction.

## How It Works

```text
User Request
     ↓
   Agent
     ↓
    LLM
     ↓
Does it need a tool?
   ↙       ↘
 No         Yes
 ↓           ↓
Answer    Select Tool
             ↓
        Tool Execution
             ↓
        Tool Result
             ↓
            LLM
             ↓
        Final Answer

For requests requiring multiple pieces of information, the agent can call more than one tool before giving the final answer.

Example:

Can I return ORD1001?
        ↓
lookup_order
        ↓
Order details
        ↓
search_policy
        ↓
Return policy
        ↓
Final answer
Project Structure
ecommerce-support-agent/
│
├── data/
│   ├── orders.json
│   ├── policy.json
│   └── preferences.json
│
├── tests/
│   └── test_agent.py
│
├── agent.py
├── tools.py
├── memory_store.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
File Responsibilities
File	Purpose
main.py	CLI and conversation history
agent.py	LLM, tool selection, agent loop, and memory
tools.py	Order and policy tools
memory_store.py	Persistent customer preferences
orders.json	Sample order data
policy.json	Sample store policies
preferences.json	Saved customer preferences
test_agent.py	Project tests
Tools
1. Order Lookup
lookup_order(order_id)

Used when the customer asks about a specific order.

Example:

Where is my order ORD1001?

The tool returns information such as:

Order ID
Product
Amount
Status
Purchase date
Delivery date
2. Policy Search
search_policy(query)

Used for questions about store policies.

Example:

How long do I have to return an item?

The tool searches the local policy data for information about:

Returns
Refunds
Replacements
Damaged/defective items
Exceptions
Return shipping
Memory

The project uses two types of memory.

Session Memory

main.py maintains the conversation history.

Example:

User: My order is ORD1001.
Agent: ORD1001 is your Wireless Headphones order.

User: What is my order number?
Agent: Your order number is ORD1001.
Persistent Memory

Customer preferences are stored in:

data/preferences.json

Example:

{
  "user_001": {
    "preferred_resolution": "refund"
  }
}

If a customer says:

I prefer a refund instead of a replacement.

the preference is saved and can be used in future conversations.

Failure Handling

The agent does not invent information when data is unavailable.

Unknown Order
User: Where is my order ORD9999?

Tool result:
order_not_found

Agent:
I couldn't find order ORD9999.
Please double-check the order ID and send it again.
Unknown Policy
User: What is the policy for moon travel?

Tool result:
policy_not_found

Agent:
There's no store policy for moon travel.
Agent Trace

The agent prints a trace for each request:

User request: Where is my order ORD1001?

Tool selected: lookup_order

Tool input: {'order_id': 'ORD1001'}

Tool result: {'success': True, ...}

Final response: Order ORD1001 was delivered...

This helps demonstrate how the LLM selected and used the tools.

Example
E-Commerce Support Agent
Type 'quit' or 'exit' to end the session.

Enter your user ID (e.g. user_001): user_001

You: Can I return ORD1001?

Tool selected: lookup_order
Tool input: {'order_id': 'ORD1001'}

Tool selected: search_policy
Tool input: {'query': 'return window'}

Agent: ORD1001 was delivered on August 30, 2026.
It can be returned within 15 days of delivery,
provided it is unused and in its original packaging.
Technologies
Python
OpenAI Responses API
LLM Tool Calling
JSON
python-dotenv
CLI
Setup
1. Clone the repository
git clone https://github.com/Shrijitvivek/ecommerce-support-agent.git
cd ecommerce-support-agent
2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Configure API key
cp .env.example .env

Add your API key to .env:

OPENAI_API_KEY=your_api_key_here

Do not commit .env to GitHub.

5. Run the application
python main.py
Testing

Run the test suite:

python -m pytest

Basic syntax check:

python -m py_compile agent.py memory_store.py
Sample Data

The project uses local synthetic data for demonstration.

orders.json – Sample customer orders
policy.json – Sample e-commerce policies
preferences.json – Customer preferences

The project does not connect to a real e-commerce platform or real customer database.

Team Project

This project demonstrates the practical implementation of an Agentic AI customer support system using:

LLM reasoning
Tool calling
Agent loops
Session memory
Persistent memory
Failure handling
Structured tool results