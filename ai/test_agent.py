# test_agent.py
from ai.agent_runner import run_agent
from db import database as db
from logs import log_convo


def main():
    print("🗓️ Smart Calendar Agent (type 'exit' to quit)")
    user = "user1"  # default username

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Assistant: Goodbye! 👋")
            break

        # Pass input to agent
        response = run_agent(user_input, user=user)
        print(f"Assistant: {response}\n")


if __name__ == "__main__":
    db.init_db()                        # ensure calendar.db exists
    log_convo.ensure_memory_exists()    # ensure memory.json exists
    main()
