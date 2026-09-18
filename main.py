"""
 Application Layer
=============================
CLI entry point. Manages user session, conversation history,
and delegates to the agent for each user turn.

Expected agent interface :
    agent.run(user_id: str, history: list[dict], user_message: str) -> str
"""

from agent import run as agent_run


def main():
    print("E-Commerce Support Agent")
    print("Type 'quit' or 'exit' to end the session.\n")

    user_id = input("Enter your user ID (e.g. user_001): ").strip()
    if not user_id:
        user_id = "guest"

    conversation_history = []

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        conversation_history.append({"role": "user", "content": user_input})

        try:
            response = agent_run(user_id, conversation_history, user_input)
        except Exception as e:
            response = f"Sorry, something went wrong: {e}"

        conversation_history.append({"role": "assistant", "content": response})
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()
