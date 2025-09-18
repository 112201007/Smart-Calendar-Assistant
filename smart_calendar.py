import click
import database as db
from datetime import datetime

# ==========================================================
# Validators
# ==========================================================
def validate_date(ctx, param, value):
    """Ensure date is in YYYY-MM-DD format."""
    if value is None:
        return None
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise click.BadParameter("Date must be in YYYY-MM-DD format")


def validate_time(ctx, param, value):
    """Ensure time is in HH:MM 24-hour format."""
    if value is None:
        return None
    try:
        datetime.strptime(value, "%H:%M")
        return value
    except ValueError:
        raise click.BadParameter("Time must be in HH:MM (24-hour) format")


def validate_time_range(start_time, end_time):
    """Ensure start_time <= end_time if both are provided."""
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
    """Smart Calendar Assistant CLI"""
    pass


# ==========================================================
# CREATE
# ==========================================================
@cli.command()
@click.argument("title")
@click.argument("date", callback=validate_date)
@click.option("--start", "start_time", callback=validate_time, default=None, help="Start time in HH:MM format")
@click.option("--end", "end_time", callback=validate_time, default=None, help="End time in HH:MM format")
def add(title, date, start_time, end_time):
    """
    Add a new event.
    Title and date are required. Start/end time optional.
    """
    try:
        # sanity checks
        if not title.strip():
            raise click.BadParameter("Title cannot be empty")
        validate_time_range(start_time, end_time)

        event = db.add_event(title, date, start_time, end_time)

        # Nicely formatted output
        click.echo(f"✅ Event added: [ID: {event['id']}] {event['title']} on {event['date']} "
                   f"{event['start_time'] or '--'}-{event['end_time'] or '--'}")
    except Exception as e:
        click.echo(f"❌ Could not add event: {e}")


# ==========================================================
# READ
# ==========================================================
@cli.command("list-all")
def list_all():
    events = db.list_all_events()
    if not events:
        click.echo("📭 No events found.")
    else:
        for ev in events:
            click.echo(f"[{ev['id']}] {ev['title']} on {ev['date']} "
                       f"{ev['start_time'] or ''}-{ev['end_time'] or ''}")


@cli.command("list-date")
@click.argument("date", callback=validate_date)
def list_on_date(date):
    events = db.list_events_on_date(date)
    if not events:
        click.echo(f"📭 No events on {date}")
    else:
        for ev in events:
            click.echo(f"[{ev['id']}] {ev['title']} {ev['start_time'] or ''}-{ev['end_time'] or ''}")


@cli.command("list-title")
@click.argument("title")
def list_by_title(title):
    events = db.list_events_by_title(title)
    if not events:
        click.echo(f"📭 No events with title '{title}'")
    else:
        for ev in events:
            click.echo(f"[{ev['id']}] {ev['title']} on {ev['date']} "
                       f"{ev['start_time'] or ''}-{ev['end_time'] or ''}")


@cli.command("list-next")
@click.argument("n", type=int)
def list_next(n):
    if n <= 0:
        click.echo("❌ Number of days must be positive")
        return
    events = db.list_events_next_n_days(n)
    if not events:
        click.echo(f"📭 No events in next {n} days.")
    else:
        for ev in events:
            click.echo(f"[{ev['id']}] {ev['title']} on {ev['date']} "
                       f"{ev['start_time'] or ''}-{ev['end_time'] or ''}")


# ==========================================================
# UPDATE
# ==========================================================
@cli.command()
@click.argument("event_id", type=int)
@click.option("--title", default=None, help="New title")
@click.option("--date", callback=validate_date, default=None, help="New date (YYYY-MM-DD)")
@click.option("--start", "start_time", callback=validate_time, default=None, help="New start time (HH:MM)")
@click.option("--end", "end_time", callback=validate_time, default=None, help="New end time (HH:MM)")
def update(event_id, title, date, start_time, end_time):
    """Update an event by ID"""
    try:
        # Check for empty title
        if title is not None and not title.strip():
            raise click.BadParameter("Title cannot be empty")

        # Fetch current event
        existing_events = db.list_all_events()
        current_event = next((ev for ev in existing_events if ev["id"] == event_id), None)
        if not current_event:
            click.echo("❌ Event not found.")
            return

        # Determine new start and end times
        new_start = start_time or current_event.get("start_time")
        new_end = end_time or current_event.get("end_time")

        # Validate time range
        if new_start and new_end:
            t1 = datetime.strptime(new_start, "%H:%M")
            t2 = datetime.strptime(new_end, "%H:%M")
            if t1 > t2:
                raise click.BadParameter("Start time must be earlier than or equal to end time")

        # Call DB update
        success = db.update_event(event_id, title, date, start_time, end_time)
        if success:
            click.echo("✅ Event updated successfully.")
        else:
            click.echo("❌ Event not found.")
    except Exception as e:
        click.echo(f"❌ Could not update event: {e}")

# ==========================================================
# DELETE
# ==========================================================
@cli.command()
@click.argument("event_id", type=int)
def delete(event_id):
    success = db.delete_event(event_id)
    if success:
        click.echo(f"✅ Event {event_id} deleted.")
    else:
        click.echo("❌ Event not found.")


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    cli()
