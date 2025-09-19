#log_convo.py
import json
from datetime import datetime

MEMORY_FILE = "memory.json"

def ensure_memory_exists():
    """Create memory file if it doesn't exist"""
    try:
        with open(MEMORY_FILE, "r") as f:
            pass
    except FileNotFoundError:
        with open(MEMORY_FILE, "w") as f:
            json.dump([], f)

def load_memory():
    ensure_memory_exists()
    try:
        with open(MEMORY_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []

def save_memory(memory: list):
    """Save conversation memory to file"""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_message(role: str, message: str):
    """
    role: 'user' or 'assistant'
    message: text message
    """
    memory = load_memory()
    memory.append({
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "message": message
    })
    save_memory(memory)

def get_history():
    """Return full conversation history"""
    return load_memory()
