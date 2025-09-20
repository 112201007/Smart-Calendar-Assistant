# tools.py
from typing import Dict
import db.database as db

# ============================
# Create: Add Event
# ============================
def add_event_tool(title, date, start_time=None, end_time=None, user="user1"):
    kwargs = {"title": title, "date": date, "user": user}
    if start_time:
        kwargs["start_time"] = start_time
    if end_time:
        kwargs["end_time"] = end_time

    try:
        event = db.add_event(**kwargs)
        output_msg = f"✅ Event added: [ID: {event['id']}] {event['title']} on {event['date']} {event.get('start_time','')}-{event.get('end_time','')}"
        print(output_msg)
        # Return dictionary with 'message' key
        return {"success": True, "message": output_msg, "events": [event]}
    except Exception as e:
        return {"success": False, "message": f"❌ Could not add event: {e}", "events": []}


# ============================
# Read: List Events
# ============================
def list_all_events_tool(user: str = "user1") -> Dict:
    print("DEBUG:===> [[list_all_events_tool]] called with(user):", user)
    events = db.list_all_events(user=user)
    if not events:
        output_msg = "📭 No events found."
        print(output_msg)
        return {"success": True, "message": output_msg}

    lines = [
        f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in events
    ]
    output_msg = "\n".join(lines)
    print(output_msg)
    return {"success": True, "message": output_msg, "events": events}


def list_events_on_date_tool(date: str, user: str = "user1") -> Dict:
    print("DEBUG:===> [[list_events_on_date_tool]] called with(date, user):", date, "==", user)
    events = db.list_events_on_date(date, user=user)
    if not events:
        output_msg = f"📭 No events found on {date}"
        print(output_msg)
        return {"success": True, "message": output_msg}

    lines = [
        f"[{ev['id']}] {ev['title']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in events
    ]
    output_msg = "\n".join(lines)
    print(output_msg)
    return {"success": True, "message": output_msg, "events": events}


def list_events_by_title_tool(title: str, user: str = "user1") -> Dict:
    print("DEBUG:===> [[list_events_by_title_tool]] called with(title, user):", title, "==", user)
    events = db.list_events_by_title(title, user=user)
    if not events:
        output_msg = f"📭 No events found with title '{title}'"
        print(output_msg)
        return {"success": True, "message": output_msg}

    lines = [
        f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in events
    ]
    output_msg = "\n".join(lines)
    print(output_msg)
    return {"success": True, "message": output_msg, "events": events}


def list_events_next_n_days_tool(n, user: str = "user1") -> Dict:
    n = int(n)
    print("DEBUG:===> [[list_events_next_n_days_tool]] called with(n,user):", n, "==", user)
    events = db.list_events_next_n_days(n, user=user)
    if not events:
        output_msg = f"📭 No events in next {n} days"
        print(output_msg)
        return {"success": True, "message": output_msg, "events": []}

    lines = [
        f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in events
    ]
    output_msg = "\n".join(lines)
    print(output_msg)
    return {"success": True, "message": output_msg, "events": events}


def list_events_by_keyword_tool(keyword: str, user: str = "user1") -> Dict:
    print("DEBUG:===> [[list_events_by_keyword_tool]] called with(keyword,user):", keyword, "==", user)
    events = db.list_all_events(user=user)
    filtered = [ev for ev in events if keyword.lower() in ev['title'].lower()]
    
    if not filtered:
        output_msg = f"📭 No events found with keyword '{keyword}'"
        print(output_msg)
        return {"success": True, "message": output_msg, "events": []}
    
    lines = [
        f"[{ev['id']}] {ev['title']} on {ev['date']} {ev['start_time'] or ''}-{ev['end_time'] or ''}"
        for ev in filtered
    ]
    output_msg = "\n".join(lines)
    print(output_msg)
    return {"success": True, "message": output_msg, "events": filtered}


# ============================
# Update: Update Event
# ============================
def update_event_tool(event_id: int, title: str = None, date: str = None,
                      start_time: str = None, end_time: str = None, user: str = "user1") -> Dict:
    print("DEBUG:===> [[update_event_tool]] called with(event_id, title, date, start_time, end_time, user):",
          event_id, "==", title, "==", date, "==", start_time, "==", end_time, "==", user)
    try:
        success = db.update_event(event_id, title, date, start_time, end_time, user=user)
        if success:
            output_msg = f"✅ Event {event_id} updated successfully"
        else:
            output_msg = f"❌ Event {event_id} not found"
    except Exception as e:
        output_msg = f"❌ Could not update event: {e}"

    print(output_msg)
    return {"success": success if 'success' in locals() else False, "message": output_msg}


# ============================
# Delete: Delete Event
# ============================
def delete_event_tool(event_id: int, user: str = "user1") -> Dict:
    print("DEBUG:===> [[delete_event_tool]] called with(event_id,user):", event_id, "==", user)

    success = db.delete_event(event_id, user=user)
    output_msg = f"✅ Event {event_id} deleted successfully" if success else f"❌ Event {event_id} not found"

    print(output_msg)
    return {"success": success, "message": output_msg}

def delete_event_by_title_tool(title: str, user: str = "user1") -> Dict:
    print("DEBUG:===> [[delete_event_by_title_tool]] called with(title,user):", title, "==", user)
    try:
        deleted = db.delete_event_by_title(title, user=user)
        output_msg = f"✅ Event(s) with title '{title}' deleted" if deleted else f"📭 No event found with title '{title}'"
        success = True
    except Exception as e:
        output_msg = f"❌ Could not delete: {e}"
        success = False

    print(output_msg)
    return {"success": success, "message": output_msg}

def delete_all_events_tool(user: str = "user1") -> dict:
    print("DEBUG:===> [[delete_all_events_tool]] called with(user):", user)
    try:
        db.delete_all_events(user=user)
        output_msg = f"All events for {user} deleted successfully."
        success = True
    except Exception as e:
        output_msg = str(e)
        success = False

    print(output_msg)
    return {"success": success, "message": output_msg}

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
