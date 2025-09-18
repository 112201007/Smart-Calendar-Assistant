import sqlite3
from datetime import datetime, timedelta

DB_NAME = "calendar.db"

def init_db():
    """
    Initialize the SQLite database and create the events table if not exists.
    Schema ensures that no two events can have the same (user, title, date, start_time).
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,         -- stored as YYYY-MM-DD
            start_time TEXT,            -- stored as HH:MM (optional)
            end_time TEXT,              -- stored as HH:MM (optional)
            UNIQUE(user, title, date, start_time)  -- prevents duplicates
        )
    """)
    conn.commit()
    conn.close()


def add_event(title: str, date: str, start_time: str = None, end_time: str = None, user: str = "user_shreya") -> dict:
    """
    Adds a new event for the user.
    Allows multiple events at the same time, but not with the same title+date+start_time.
    Raises ValueError if duplicate.
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


def list_all_events(user: str = "user_shreya") -> list:
    """
    Returns all events for the given user, ordered by date and start_time.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user, title, date, start_time, end_time
        FROM events
        WHERE user = ?
        ORDER BY date ASC, 
                 CASE WHEN start_time IS NULL THEN '00:00' ELSE start_time END ASC
    """, (user,))
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "user", "title", "date", "start_time", "end_time"], row)) for row in rows]


def list_events_on_date(date: str, user: str = "user_shreya") -> list:
    """Returns all events for the user on a given date."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user, title, date, start_time, end_time
        FROM events
        WHERE user = ? AND date = ?
        ORDER BY CASE WHEN start_time IS NULL THEN '00:00' ELSE start_time END ASC
    """, (user, date))
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "user", "title", "date", "start_time", "end_time"], row)) for row in rows]


def list_events_by_title(title: str, user: str = "user_shreya") -> list:
    """Returns all events for the user with the given title."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user, title, date, start_time, end_time
        FROM events
        WHERE user = ? AND title = ?
        ORDER BY date ASC,
                 CASE WHEN start_time IS NULL THEN '00:00' ELSE start_time END ASC
    """, (user, title))
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "user", "title", "date", "start_time", "end_time"], row)) for row in rows]


def list_events_next_n_days(n: int, user: str = "user_shreya") -> list:
    """Returns all events for the user in the next n days (inclusive)."""
    today = datetime.today().date()
    end_date = today + timedelta(days=n)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user, title, date, start_time, end_time
        FROM events
        WHERE user = ? AND DATE(date) <= DATE(?)
        ORDER BY date ASC,
                 CASE WHEN start_time IS NULL THEN '00:00' ELSE start_time END ASC
    """, (user, str(end_date)))
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "user", "title", "date", "start_time", "end_time"], row)) for row in rows]

def update_event(event_id: int, title: str = None, date: str = None, start_time: str = None, end_time: str = None, user: str = "user_shreya") -> bool:
    """
    Updates an event for the user by ID.
    Only provided fields will be updated.
    """
    # Fetch current event
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT start_time, end_time FROM events WHERE user = ? AND id = ?", (user, event_id))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False

    current_start, current_end = row

    # Determine final start/end
    new_start = start_time or current_start
    new_end = end_time or current_end

    # Validate time range
    if new_start and new_end:
        t1 = datetime.strptime(new_start, "%H:%M")
        t2 = datetime.strptime(new_end, "%H:%M")
        if t1 > t2:
            conn.close()
            raise ValueError("Start time must be earlier than or equal to end time")

    # Build dynamic query
    fields = []
    values = []
    if title: fields.append("title = ?"); values.append(title)
    if date: fields.append("date = ?"); values.append(date)
    if start_time: fields.append("start_time = ?"); values.append(start_time)
    if end_time: fields.append("end_time = ?"); values.append(end_time)

    if not fields:
        conn.close()
        return False

    values.extend([user, event_id])
    query = f"UPDATE events SET {', '.join(fields)} WHERE user = ? AND id = ?"
    cur.execute(query, tuple(values))
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated

def delete_event(event_id: int, user: str = "user_shreya") -> bool:
    """Deletes an event for the user by ID."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE user = ? AND id = ?", (user, event_id))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


# Ensure DB is initialized
init_db()
