import os
import inspect
import re
from ai.tools import TOOL_MAPPING
from logs.log_convo import add_message
import dateparser
import datetime
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load env vars
load_dotenv()


def make_tool(name, fn):
    sig = inspect.signature(fn)

    def _wrapper(input_str: str):
        kwargs_list = []

        if input_str and "=" in input_str:
            # Case 1: structured input like title=Meeting, date=2025-09-21
            kwargs = {}
            for part in input_str.split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    kwargs[k.strip()] = v.strip().strip('"').strip("'")
            kwargs["user"] = "user1"
            kwargs_list.append(kwargs)
        else:
            # Case 2: raw text fallback (heuristic)
            events_texts = re.split(r"\band\b|,", input_str)

            for event_text in events_texts:
                event_text = event_text.strip('"').strip("'").strip()
                kwargs = {}

                # Parse title
                kwargs["title"] = event_text

                # Parse date using dateparser
                parsed_date = dateparser.parse(event_text)
                if parsed_date:
                    kwargs["date"] = parsed_date.strftime("%Y-%m-%d")

                # Parse times (start_time / end_time)
                time_matches = [m[0] for m in re.findall(r"(\d{1,2}(:\d{2})?\s?(am|pm)?)", event_text, re.I)]
                if len(time_matches) == 1:
                    kwargs["start_time"] = time_matches[0]
                elif len(time_matches) >= 2:
                    kwargs["start_time"] = time_matches[0]
                    kwargs["end_time"] = time_matches[1]

                # Force single-user
                kwargs["user"] = "user1"

                kwargs_list.append(kwargs)

        # Call the function for each set of kwargs
        results = []
        for kw in kwargs_list:
            # Keep only valid args from the tool function signature
            valid_kwargs = {k: v for k, v in kw.items() if k in sig.parameters}
            valid_kwargs["user"] = "user1"  # enforce single-user
            results.append(fn(**valid_kwargs))

        return results if len(results) > 1 else results[0]
    # # Tool-specific example usage
    # examples = {
    #     "add_event": "add_event(title='Doctor appointment', date='2025-09-21', start_time='14:00')",
    #     "list_events_on_date": "list_events_on_date(date='2025-09-21')",
    #     "remove_event": "remove_event(title='Doctor appointment', date='2025-09-21')",
    # }
    # # Use custom example if available
    # example = examples.get(name, "")

    # desc = (
    #     f"Calendar tool: {name.replace('_', ' ')}. "
    #     f"Required args: {list(sig.parameters.keys())}. "
    #     f"Always return arguments in this exact format: "
    #     f"title='...', date='YYYY-MM-DD', start_time='HH:MM', user='user1'. "
    #     f"Example: {example}."
    # )

    # Tool-specific structured examples
    structured_examples = {
        "add_event": "add_event(title='Doctor appointment', date='2025-09-21', start_time='14:00')",
        "list_events_on_date": "list_events_on_date(date='2025-09-21')",
        "remove_event": "remove_event(title='Doctor appointment', date='2025-09-21')",
    }

    # Natural-language examples
    nl_examples = [
        "set a meeting day after tomorrow at 5 PM",
        "set a meeting for discussing logistics after 2 hours"
    ]

    # Get current date/time
    today_str = datetime.date.today().isoformat()
    current_time_str = datetime.datetime.now().strftime("%H:%M")

    # Use custom example if available
    example = structured_examples.get(name, "")

    desc = (
        f"Calendar tool: {name.replace('_', ' ')}. "
        f"Required args: {list(sig.parameters.keys())}. "
        f"Always return arguments in this exact format: "
        f"title='...', date='YYYY-MM-DD', start_time='HH:MM' (optional), end_time='HH:MM' (optional), user='username'(optional, specify who is adding the meeting)'. "
        f"Use today's date ({today_str}) and current time ({current_time_str}) as reference "
        f"for relative expressions. "
        f"Structured example: {example}. "
        f"Natural-language examples: {nl_examples[0]}, {nl_examples[1]}."
    )
    return Tool(
        name=name,
        func=_wrapper,
        description=desc,
    )


# ==============================
# Run Agent Function
# ==============================
def run_agent(user_input: str, user: str = "user1") -> str:
    """
    Uses LangChain agent to process natural language commands.
    Persists conversation to memory.json via log_convo.
    """
    add_message("user", user_input)

    try:
        result = agent.run(user_input)
    except Exception as e:
        result = f"❌ Agent failed: {e}"

    add_message("assistant", result)
    return result


# ==============================
# Build LangChain Tools
# ==============================
lc_tools = [make_tool(name, fn) for name, fn in TOOL_MAPPING.items()]


# ==============================
# Initialize Gemini LLM (LangChain wrapper)
# ==============================
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # switched from gemini-1.5-flash → assignment spec,
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0,
)


# ==============================
# Create LangChain Agent
# ==============================
agent = initialize_agent(
    tools=lc_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
