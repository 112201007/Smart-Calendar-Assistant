# Smart Calendar Assistant
A Python-based AI-assisted calendar management system with CLI and web interfaces. Supports event creation, listing, updating, and deletion, along with natural language commands via a LangChain-powered AI agent.

# Folder Structure
```text
Smart-Calendar-Assistant/
│
├── ai/                     # AI-powered workflow
│   ├── test_agent.py        # Entry point for AI conversation
│   ├── agent_runner.py      # Agent logic & LangChain integration
│   └── tools.py             # Calendar tools wrapped for AI agent
│
├── db/                     # Database layer
│   └── database.py          # CRUD operations for events
│
├── logs/                   # Conversation memory
│   └── log_convo.py         # Handles memory.json read/write
│
├── cli/                    # Optional manual CLI commands
│   └── smart_calendar_cli.py
│
├── templates/              # Flask templates (index.html)
│   └── index.html
├── static/                 # CSS/JS for web interface
│   └── style.css
├── calendar.db              # SQLite DB (auto-created)
└── memory.json              # Conversation memory (auto-created)
```


# High-level workflow
```text
User Input
   │
   ├── CLI Input → smart_calendar_cli.py → db/database.py / logs/log_convo.py
   │
   └── AI Input → test_agent.py → agent_runner.py → tools.py → db/database.py → logs/log_convo.py
                        │
                        └─> LangChain Agent + LLM (Gemini)
```

# Memory Storage & Retrieval
- Stored as a JSON list of messages with timestamp, role (user/assistant), and message.
- log_convo.add_message() appends new messages.
- get_history() retrieves full conversation.

# Tool Definition & Registration with LLM
- TOOL_MAPPING maps tool names to functions in tools.py.
- make_tool() wraps each function into a LangChain Tool object with signature inspection and argument parsing.
- All tools are registered with the LangChain agent (initialize_agent) to allow natural language execution.
- Tools: 
```
-Event Creation:
   add_event_tool

-Event Retrieval: 
   list_all_events_tool
   list_events_on_date_tool
   list_events_by_title_tool
   list_events_next_n_days_tool

-Event Modification:
   update_event_tool
   
-Event Deletion:
   delete_event_tool
   delete_event_by_title_tool
   delete_all_events_tool
```


# File Interactions

| File | Description |
|------|-------------|
| **`test_agent.py`** | Entry point for AI-based conversation.<br>Calls `run_agent` from `agent_runner.py`.<br>Ensures DB (`calendar.db`) and memory (`memory.json`) exist on startup. |
| **`agent_runner.py`** | Converts user commands into tool function calls.<br>Wraps each tool from `tools.py` using LangChain Tool.<br>Persists all conversation messages to `memory.json`. |
| **`tools.py`** | Contains all event-related tools (`add_event_tool`, `list_all_events_tool`, etc.).<br>Calls `db/database.py` functions for CRUD operations.<br>Returns structured outputs (success status, messages, event lists). |
| **`database.py`** | Handles low-level SQLite operations: create, read, update, delete events.<br>Ensures uniqueness (`user`, `title`, `date`, `start_time`) to prevent duplicates. |
| **`log_convo.py`** | Manages conversation memory (`memory.json`).<br>Provides helper functions: `add_message()`, `get_history()`, `ensure_memory_exists()`. |
| **`smart_calendar_cli.py`** | Provides manual CLI commands for event management.<br>Logs all commands & outputs to memory. |
| **`app.py`** | Web interface to run AI or CLI commands via HTTP endpoints. Uses index.html. |

- calendar.db and memory.json are auto-created when running test_agent.py or CLI for the first time.
- AI agent uses LangChain Google Generative API (Gemini). Without API key, only CLI commands will work.

# Setup & Installation

1) Clone the repository:
```bash
git clone <repo-url>
cd Smart-Calendar-Assistant
```

2) Create & activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
```

3) Install dependencies:
```bash
pip install -r requirements.txt
```

4) Environment variables:

Create a .env file in the root directory.
Add your Gemini API key for LangChain (for AI agent):

```bash
GEMINI_API_KEY=<YOUR_KEY>
```


# Running the Project
## 1)Web Interface
```bash
flask run
```

## 2)CLI AI Agent (Natural Language)

```bash
python -m ai.test_agent

```
Type your commands in natural language:

Add meeting on 2025-09-25 at 10:00
Show events next 7 days


## 3)Database Commands
```bash
python cli/smart_calendar_cli.py <command>
```
Example:
```bash
python cli/smart_calendar_cli.py add "SE_Project Meeting" 2025-09-25 --start 10:00 --end 11:00
python cli/smart_calendar_cli.py list-all
python cli/smart_calendar_cli.py list-date 2025-09-25
python cli/smart_calendar_cli.py update 1 --title "Updated Meeting"
python cli/smart_calendar_cli.py delete 1
python cli/smart_calendar_cli.py show-memory
```

# Key Features

- **CRUD operations**: Add, list, update, delete events
- **Natural language AI agent**: Commands parsed via LangChain
- **Conversation memory**: All interactions logged to memory.json
- **SQLite persistence**: All events saved in calendar.db

# Future Improvements
- Extend AI tools and CLI to support multi-user events
- Improve tool handling and argument parsing in AI agent
- Enhance natural language understanding for complex queries
- Better AI feedback messages and error handling, formatting.
- Enhanced natural language understanding (multi-event parsing, fuzzy matching) for CLI
- Explore and integrate LangGraph