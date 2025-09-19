from flask import Flask, render_template, request, jsonify
import subprocess
from ai.agent_runner import run_agent

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run_ai", methods=["POST"])
def run_ai():
    data = request.json
    user_input = data.get("query", "")
    result = run_agent(user_input)
    return jsonify({"response": result})

@app.route("/run_cli", methods=["POST"])
def run_cli():
    data = request.json
    command = data.get("command", "")
    try:
        result = subprocess.check_output(
            ["python", "cli/smart_calendar_cli.py"] + command.split(),
            stderr=subprocess.STDOUT,
            text=True
        )
    except subprocess.CalledProcessError as e:
        result = e.output
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(debug=True)
