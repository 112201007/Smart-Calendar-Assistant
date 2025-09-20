from flask import Flask, request, jsonify, render_template
from ai.tools import TOOL_MAPPING
from ai.agent_runner import run_agent
from db import database as db

app = Flask(__name__)

# Ensure DB exists
db.init_db()

# -------------------------------
# Home page
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------------
# Run CLI commands
# -------------------------------
@app.route("/run_cli", methods=["POST"])
def run_cli():
    data = request.json
    cmd = data.get("command", "")
    if not cmd:
        return jsonify({"error": "No command provided"}), 400

    import shlex

    parts = shlex.split(cmd)
    tool_name = parts[0] + "_tool"
    args = parts[1:]
    if tool_name in TOOL_MAPPING:
        kwargs = {}
        for a in args:
            if "=" in a:
                k, v = a.split("=", 1)
                kwargs[k] = v.strip("'\"")
        result = TOOL_MAPPING[tool_name](**kwargs)
        return jsonify({"response": result.get("message", str(result))})
    else:
        return jsonify({"response": f"Tool '{tool_name}' not found"})


# -------------------------------
# Run AI agent (natural language)
# -------------------------------
@app.route("/parse_command", methods=["POST"])
def parse_command():
    data = request.json
    text = data.get("text")
    if not text:
        return jsonify({"error": "No command provided"}), 400

    from ai.agent_runner import run_agent
    import json

    try:
        result_str = run_agent(text, user="user_shreya")
        print("Agent output:", result_str)

        # If agent fails, always return generic message
        if "❌ Agent failed:" in result_str:
            return jsonify({"error": "❌ Agent failed"})

        # Try JSON parse
        try:
            parsed_result = json.loads(result_str)
            if isinstance(parsed_result, dict) and "events" in parsed_result:
                event = parsed_result["events"][0] if parsed_result["events"] else {}
                response = {
                    "title": event.get("title", ""),
                    "date": event.get("date", ""),
                    "start_time": event.get("start_time", ""),
                    "end_time": event.get("end_time", ""),
                    "message": event.get("message", "")
                }
            else:
                response = {"message": str(parsed_result)}
        except Exception:
            # fallback to plain text, but only if it didn't fail
            response = {"message": result_str}

        return jsonify(response)

    except Exception:
        # If anything goes wrong in your Flask handler, return generic failure
        return jsonify({"error": "❌ Agent failed"}), 500
