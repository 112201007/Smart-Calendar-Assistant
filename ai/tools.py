# tools.py
from typing import Dict
import db.database as db

# ============================
# Create: Add Event
# ============================
def add_event_tool(title, date, start_time=None, end_time=None, user="user_shreya"):
    try:
        event = db.add_event(title, date, start_time, end_time, user=user)
        return {
            "success": True,
            "message": f"✅ Event added: {event['title']} on {event['date']} {event.get('start_time') or ''}-{event.get('end_time') or ''}",
            "events": [event]
        }
    except Exception as e:
        return {"success": False, "message": f"❌ Could not add event: {e}", "events": []}

# ============================
# Read: List Events
# ============================
def list_all_events_tool(user: str = "user_shreya") -> Dict:
    events = db.list_all_events(user=user)
    if not events:
        return {"success": True, "message": "📭 No events found."}

    lines = [
        f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in events
    ]
    return {"success": True, "message": "\n".join(lines), "events": events}

def list_events_on_date_tool(date: str, user: str = "user_shreya") -> Dict:
    events = db.list_events_on_date(date, user=user)
    if not events:
        return {"success": True, "message": f"📭 No events found on {date}"}

    lines = [
        f"[{ev['id']}] {ev['title']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in events
    ]
    return {"success": True, "message": "\n".join(lines), "events": events}

def list_events_by_title_tool(title: str, user: str = "user_shreya") -> Dict:
    events = db.list_events_by_title(title, user=user)
    if not events:
        return {"success": True, "message": f"📭 No events found with title '{title}'"}

    lines = [
        f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in events
    ]
    return {"success": True, "message": "\n".join(lines), "events": events}

def list_events_next_n_days_tool(n: int, user: str = "user_shreya") -> Dict:
    events = db.list_events_next_n_days(n, user=user)
    if not events:
        return {"success": True, "events": [], "message": f"📭 No events in next {n} days"}
    lines = [
        f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in events
    ]
    return {"success": True, "events": events, "message": "\n".join(lines)}

def list_events_by_keyword_tool(keyword: str, user: str = "user_shreya") -> Dict:
    """
    Returns all events whose title contains the given keyword.
    """
    events = db.list_all_events(user=user)
    filtered = [ev for ev in events if keyword.lower() in ev['title'].lower()]
    
    if not filtered:
        return {"success": True, "message": f"📭 No events found with keyword '{keyword}'", "events": []}
    
    lines = [
        f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in filtered
    ]
    return {"success": True, "message": "\n".join(lines), "events": filtered}

# ============================
# Update: Update Event
# ============================
def update_event_tool(event_id: int, title: str = None, date: str = None,
                      start_time: str = None, end_time: str = None, user: str = "user_shreya") -> Dict:
    try:
        success = db.update_event(event_id, title, date, start_time, end_time, user=user)
        if success:
            return {"success": True, "message": f"✅ Event {event_id} updated successfully"}
        else:
            return {"success": False, "message": f"❌ Event {event_id} not found"}
    except Exception as e:
        return {"success": False, "message": f"❌ Could not update event: {e}"}

# ============================
# Delete: Delete Event
# ============================
def delete_event_tool(event_id: int, user: str = "user_shreya") -> Dict:
    success = db.delete_event(event_id, user=user)
    if success:
        return {"success": True, "message": f"✅ Event {event_id} deleted successfully"}
    else:
        return {"success": False, "message": f"❌ Event {event_id} not found"}

def delete_event_by_title_tool(title: str, user: str = "user_shreya") -> Dict:
    try:
        deleted = db.delete_event_by_title(title, user=user)
        if deleted:
            return {"success": True, "message": f"✅ Event(s) with title '{title}' deleted"}
        else:
            return {"success": False, "message": f"📭 No event found with title '{title}'"}
    except Exception as e:
        return {"success": False, "message": f"❌ Could not delete: {e}"}

def delete_all_events_tool(user: str = "user_shreya") -> dict:
    try:
        db.delete_all_events(user=user)
        return {"success": True, "message": f"All events for {user} deleted successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ============================
# TOOL MAPPING
# ============================
TOOL_MAPPING = {
    "add_event_tool": add_event_tool,
    "list_all_events_tool": list_all_events_tool,
    "list_events_on_date_tool": list_events_on_date_tool,
    "list_events_by_title_tool": list_events_by_title_tool,
    "list_events_next_n_days_tool": list_events_next_n_days_tool,
    "delete_all_events_tool": delete_all_events_tool,
    "update_event_tool": update_event_tool,
    "delete_event_tool": delete_event_tool,
    "delete_event_by_title_tool": delete_event_by_title_tool,
    "list_events_by_keyword_tool": list_events_by_keyword_tool
}
