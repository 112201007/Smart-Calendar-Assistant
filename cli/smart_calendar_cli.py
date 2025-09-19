# smart_calendar_cli.py
import click
import db.database as db
import logs.log_convo as log_convo
from datetime import datetime

# Load previous conversation memory - ensures memory.json is read once when the CLI starts
conversation_memory = log_convo.get_history()


# ==========================================================
# Utility validators
# ==========================================================
def validate_date(ctx, param, value):
    if value is None:
        return None
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise click.BadParameter("Date must be in YYYY-MM-DD format")


def validate_time(ctx, param, value):
    if value is None:
        return None
    try:
        datetime.strptime(value, "%H:%M")
        return value
    except ValueError:
        raise click.BadParameter("Time must be in HH:MM (24-hour) format")


def validate_time_range(start_time, end_time):
    if start_time and end_time:
        t1 = datetime.strptime(start_time, "%H:%M")
        t2 = datetime.strptime(end_time, "%H:%M")
        if t1 > t2:
            raise click.BadParameter("Start time must be earlier than or equal to end time")


# ==========================================================
# CLI Group
# ==========================================================
@click.group()
def cli():
    """Smart Calendar CLI"""
    pass


# ==========================================================
# Helper function to log CLI commands and outputs
# ==========================================================
def log_cli(user_input: str, output_msg: str):
    log_convo.add_message("user", user_input)
    log_convo.add_message("assistant", output_msg)


# ==========================================================
# CREATE
# ==========================================================
@cli.command()
@click.argument("title")
@click.argument("date", callback=validate_date)
@click.option("--start", "start_time", callback=validate_time, default=None, help="Start time HH:MM")
@click.option("--end", "end_time", callback=validate_time, default=None, help="End time HH:MM")
@click.option("--user", default="user_shreya", help="Username for multi-user support")
def add(title, date, start_time, end_time, user):
    """Add a new event"""
    user_cmd = f"add {title} {date} --start {start_time} --end {end_time}"
    try:
        if not title.strip():
            raise click.BadParameter("Title cannot be empty")
        validate_time_range(start_time, end_time)

        event = db.add_event(title, date, start_time, end_time, user=user)
        output_msg = f"✅ Event added: [ID: {event['id']}] {event['title']} on {event['date']} {event['start_time'] or ''}-{event['end_time'] or ''}"
        click.echo(output_msg)
        log_cli(user_cmd, output_msg)
    except Exception as e:
        error_msg = f"❌ Could not add event: {e}"
        click.echo(error_msg)
        log_cli(user_cmd, error_msg)


# ==========================================================
# READ COMMANDS
# ==========================================================
@cli.command("list-all")
@click.option("--user", default="user_shreya", help="Username for multi-user support")
def list_all(user):
    user_cmd = "list-all"
    events = db.list_all_events(user=user)
    if not events:
        output_msg = "📭 No events found."
        click.echo(output_msg)
    else:
        output_lines = []
        for ev in events:
            line = f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
            click.echo(line)
            output_lines.append(line)
        output_msg = "\n".join(output_lines)
    log_cli(user_cmd, output_msg)


@cli.command("list-date")
@click.argument("date", callback=validate_date)
@click.option("--user", default="user_shreya", help="Username for multi-user support")
def list_on_date(date, user):
    user_cmd = f"list-date {date}"
    events = db.list_events_on_date(date, user=user)
    if not events:
        output_msg = f"📭 No events on {date}"
        click.echo(output_msg)
    else:
        output_lines = []
        for ev in events:
            line = f"[{ev['id']}] {ev['title']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
            click.echo(line)
            output_lines.append(line)
        output_msg = "\n".join(output_lines)
    log_cli(user_cmd, output_msg)


@cli.command("list-title")
@click.argument("title")
@click.option("--user", default="user_shreya", help="Username for multi-user support")
def list_by_title(title, user):
    user_cmd = f"list-title {title}"
    events = db.list_events_by_title(title, user=user)
    if not events:
        output_msg = f"📭 No events with title '{title}'"
        click.echo(output_msg)
    else:
        output_lines = []
        for ev in events:
            line = f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
            click.echo(line)
            output_lines.append(line)
        output_msg = "\n".join(output_lines)
    log_cli(user_cmd, output_msg)


@cli.command("list-next")
@click.argument("n", type=int)
@click.option("--user", default="user_shreya", help="Username for multi-user support")
def list_next(n, user):
    user_cmd = f"list-next {n}"
    if n <= 0:
        output_msg = "❌ Number of days must be positive"
        click.echo(output_msg)
        log_cli(user_cmd, output_msg)
        return

    events = db.list_events_next_n_days(n, user=user)
    if not events:
        output_msg = f"📭 No events in next {n} days."
        click.echo(output_msg)
    else:
        output_lines = []
        for ev in events:
            line = f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
            click.echo(line)
            output_lines.append(line)
        output_msg = "\n".join(output_lines)
    log_cli(user_cmd, output_msg)


# ==========================================================
# UPDATE
# ==========================================================
@cli.command()
@click.argument("event_id", type=int)
@click.option("--title", default=None, help="New title")
@click.option("--date", callback=validate_date, default=None, help="New date (YYYY-MM-DD)")
@click.option("--start", "start_time", callback=validate_time, default=None, help="New start time (HH:MM)")
@click.option("--end", "end_time", callback=validate_time, default=None, help="New end time (HH:MM)")
@click.option("--user", default="user_shreya", help="Username for multi-user support")
def update(event_id, title, date, start_time, end_time, user):
    user_cmd = f"update {event_id} --title {title} --date {date} --start {start_time} --end {end_time}"
    try:
        if title is not None and not title.strip():
            raise click.BadParameter("Title cannot be empty")
        validate_time_range(start_time, end_time)

        success = db.update_event(event_id, title, date, start_time, end_time, user=user)
        if success:
            output_msg = "✅ Event updated successfully."
        else:
            output_msg = "❌ Event not found."
        click.echo(output_msg)
    except Exception as e:
        output_msg = f"❌ Could not update event: {e}"
        click.echo(output_msg)
    log_cli(user_cmd, output_msg)


# ==========================================================
# DELETE
# ==========================================================
@cli.command()
@click.argument("event_id", type=int)
@click.option("--user", default="user_shreya", help="Username for multi-user support")
def delete(event_id, user):
    user_cmd = f"delete {event_id}"
    success = db.delete_event(event_id, user=user)
    if success:
        output_msg = f"✅ Event {event_id} deleted."
    else:
        output_msg = "❌ Event not found."
    click.echo(output_msg)
    log_cli(user_cmd, output_msg)


# ==========================================================
# SHOW CONVERSATION MEMORY
# ==========================================================
@cli.command("show-memory")
def show_memory():
    """Show last 10 conversation messages"""
    history = log_convo.get_history()
    if not history:
        click.echo("📭 No conversation history yet.")
        return
    for msg in history[-10:]:  # last 10 messages
        click.echo(f"[{msg['timestamp']}] {msg['role']}: {msg['message']}")


# ==========================================================
# AI NATURAL LANGUAGE COMMAND (LangChain agent)
# ==========================================================
@cli.command("ai")
@click.argument("user_input")
@click.option("--user", default="user_shreya", help="Username for multi-user support")
def ai_command_cli(user_input, user):
    """Send a natural language command to the LangChain AI agent"""
    from ai.agent_runner import run_agent

    output = run_agent(user_input, user=user)
    click.echo(output)


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    cli()
