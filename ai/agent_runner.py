import os
import inspect
import re
from ai.tools import TOOL_MAPPING
from logs.log_convo import add_message
import dateparser

from langchain.agents import Tool, initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

# Load env vars
load_dotenv()


def make_tool(name, fn):
    sig = inspect.signature(fn)

    # Tool-specific example usage
    examples = {
        "add_event": "add_event(title='Doctor appointment', date='2025-09-21', start_time='14:00')",
        "list_events_on_date": "list_events_on_date(date='2025-09-21')",
        "remove_event": "remove_event(title='Doctor appointment', date='2025-09-21')",
    }

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

    # Use custom example if available
    example = examples.get(name, "")
    desc = (
        f"Calendar tool: {name.replace('_', ' ')}. "
        f"Required args: {list(sig.parameters.keys())}. "
        f"Example: {example}."
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
    model="gemini-pro",  # switched from gemini-1.5-flash → assignment spec
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


# # agent_runner.py
# import os
# import inspect
# import re
# from ai.tools import TOOL_MAPPING
# from logs.log_convo import add_message
# import dateparser

# from langchain.agents import Tool, initialize_agent, AgentType
# from langchain_google_genai import ChatGoogleGenerativeAI

# from dotenv import load_dotenv

# # Load env vars
# load_dotenv()


# def make_tool(name, fn):
#     sig = inspect.signature(fn)

#     def _wrapper(input_str: str):
#         kwargs_list = []

#         if input_str and "=" in input_str:
#             # Case 1: JSON-like input
#             kwargs = {}
#             for part in input_str.split(","):
#                 if "=" in part:
#                     k, v = part.split("=", 1)
#                     kwargs[k.strip()] = v.strip().strip('"').strip("'")
#             kwargs["user"] = "user1"
#             kwargs_list.append(kwargs)
#         else:
#             # Case 2: raw text fallback (heuristic)
#             events_texts = re.split(r"\band\b|,", input_str)

#             for event_text in events_texts:
#                 event_text = event_text.strip('"').strip("'").strip()
#                 kwargs = {}

#                 # Parse title
#                 kwargs["title"] = event_text

#                 # Parse date using dateparser
#                 parsed_date = dateparser.parse(event_text)
#                 if parsed_date:
#                     kwargs["date"] = parsed_date.strftime("%Y-%m-%d")

#                 # Parse start and end times
#                 time_matches = re.findall(r"(\d{1,2}(:\d{2})?\s?(am|pm)?)", event_text, re.I)
#                 if len(time_matches) == 1:
#                     kwargs["start_time"] = time_matches[0][0]
#                 elif len(time_matches) >= 2:
#                     kwargs["start_time"] = time_matches[0][0]
#                     kwargs["end_time"] = time_matches[1][0]

#                 # Force single-user
#                 kwargs["user"] = "user1"

#                 kwargs_list.append(kwargs)

#         # Call the function for each set of kwargs
#         results = []
#         for kw in kwargs_list:
#             # Keep only valid args from the tool function signature
#             valid_kwargs = {k: v for k, v in kw.items() if k in sig.parameters}
#             valid_kwargs["user"] = "user1"  # enforce single-user
#             results.append(fn(**valid_kwargs))

#         return results if len(results) > 1 else results[0]

#     return Tool(
#         name=name,
#         func=_wrapper,
#         description=(
#             f"Calendar tool: {name.replace('_', ' ')}. "
#             f"Required args: {list(inspect.signature(fn).parameters.keys())}. "
#             f"Always call with explicit args, e.g. title='Meeting', date='2025-09-20', start_time='10:00'."
#         ),
#     )


# # ==============================
# # Run Agent Function
# # ==============================
# def run_agent(user_input: str, user: str = "user1") -> str:
#     """
#     Uses LangChain agent to process natural language commands.
#     Persists conversation to memory.json via log_convo.
#     """
#     add_message("user", user_input)

#     try:
#         result = agent.run(user_input)
#     except Exception as e:
#         result = f"❌ Agent failed: {e}"

#     add_message("assistant", result)
#     return result


# # ==============================
# # Build LangChain Tools
# # ==============================
# lc_tools = [make_tool(name, fn) for name, fn in TOOL_MAPPING.items()]


# # ==============================
# # Initialize Gemini LLM (LangChain wrapper)
# # ==============================
# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     google_api_key=os.getenv("GEMINI_API_KEY"),
#     temperature=0,
# )


# # ==============================
# # Create LangChain Agent
# # ==============================
# agent = initialize_agent(
#     tools=lc_tools,
#     llm=llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
# )
