# database.py
import sqlite3
from datetime import datetime, timedelta
import os

# Absolute path to calendar.db in project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(PROJECT_ROOT, "calendar.db")

def init_db():
    """
    Initialize the SQLite database and create the events table if not exists.
    Schema ensures no duplicate (user, title, date, start_time)
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,          -- add multi-user support
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            UNIQUE(user, title, date, start_time)
        )
    """)
    conn.commit()
    conn.close()


# -------------------------------
# ADD EVENT
# -------------------------------
def add_event(title: str, date: str, start_time: str = None, end_time: str = None, user: str = "user1") -> dict:
    print("DEBUG: Adding event from ==from databse.py:", DB_NAME)
    """
    Adds a new event. Raises sqlite3.IntegrityError if duplicate.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO events (user, title, date, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        """, (user, title, date, start_time, end_time))
        conn.commit()
        event_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Duplicate event: same title/date/start time already exists")
    conn.close()

    return {
        "id": event_id,
        "user": user,
        "title": title,
        "date": date,
        "start_time": start_time,
        "end_time": end_time
    }


# -------------------------------
# UPDATE EVENT
# -------------------------------
def update_event(event_id: int, title: str = None, date: str = None,
                 start_time: str = None, end_time: str = None, user: str = "user1") -> bool:
    """
    Updates an event by ID. Checks duplicates before updating.
    Returns True if updated, False if event not found.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Check if update will violate UNIQUE constraint
    if title or date or start_time:
        # get current values
        cur.execute("SELECT title, date, start_time FROM events WHERE user=? AND id=?", (user, event_id))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False
        cur_title, cur_date, cur_start = row
        new_title = title or cur_title
        new_date = date or cur_date
        new_start = start_time or cur_start
        # check duplicate
        cur.execute("SELECT id FROM events WHERE user=? AND title=? AND date=? AND start_time=? AND id!=?",
                    (user, new_title, new_date, new_start, event_id))
        if cur.fetchone():
            conn.close()
            raise ValueError("Duplicate event would be created with this update")

    # Build dynamic update query
    fields, values = [], []
    if title: fields.append("title=?"); values.append(title)
    if date: fields.append("date=?"); values.append(date)
    if start_time: fields.append("start_time=?"); values.append(start_time)
    if end_time: fields.append("end_time=?"); values.append(end_time)

    if not fields:
        conn.close()
        return False

    values += [user, event_id]
    query = f"UPDATE events SET {', '.join(fields)} WHERE user=? AND id=?"
    cur.execute(query, tuple(values))
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


# -------------------------------
# DELETE EVENT
# -------------------------------
def delete_event(event_id: int, user: str = "user1") -> bool:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE user=? AND id=?", (user, event_id))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def delete_event_by_title(title: str, user: str = "user1") -> bool:
    """
    Delete all events matching a title for a user.
    Returns True if at least one event was deleted.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE user=? AND title=?", (user, title))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def delete_all_events(user: str = None):
    """
    Delete all events from the database.
    If user is provided, only delete events for that user.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if user:
        cursor.execute("DELETE FROM events WHERE user = ?", (user,))
    else:
        cursor.execute("DELETE FROM events")  # delete all events

    conn.commit()
    conn.close()
    return True


# -------------------------------
# LIST ALL, LIST BY DATE/TITLE/NEXT N DAYS
# -------------------------------
def list_all_events(user: str = "user1") -> list:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user, title, date, start_time, end_time
        FROM events
        WHERE user=?
        ORDER BY date ASC, start_time ASC
    """, (user,))
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "user", "title", "date", "start_time", "end_time"], r)) for r in rows]


def list_events_on_date(date: str, user: str = "user1") -> list:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user, title, date, start_time, end_time
        FROM events
        WHERE user=? AND date=?
        ORDER BY start_time ASC
    """, (user, date))
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "user", "title", "date", "start_time", "end_time"], r)) for r in rows]


def list_events_by_title(title: str, user: str = "user1") -> list:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user, title, date, start_time, end_time
        FROM events
        WHERE user=? AND title=?
        ORDER BY date ASC, start_time ASC
    """, (user, title))
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "user", "title", "date", "start_time", "end_time"], r)) for r in rows]


def list_events_next_n_days(n: int, user: str = "user1") -> list:
    """
    Returns all events for the given user within the next `n` days, inclusive.
    Events are ordered by date then start_time.
    """
    today = datetime.today().date()
    end_date = today + timedelta(days=n)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, user, title, date, start_time, end_time
        FROM events
        WHERE user = ?
          AND date(date) >= date(?)
          AND date(date) <= date(?)
        ORDER BY date ASC, start_time ASC
    """, (user, today.isoformat(), end_date.isoformat()))

    rows = cur.fetchall()
    conn.close()

    # Convert rows to list of dicts
    return [
        dict(zip(["id", "user", "title", "date", "start_time", "end_time"], row))
        for row in rows
    ]


# Ensure DB exists
init_db()
