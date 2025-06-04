from ics import Calendar, Event
from datetime import datetime

def add_event_to_calendar(calendar_path, event_name, start_time, end_time):
    calendar = Calendar()
    try:
        with open(calendar_path, 'r', encoding='utf-8') as calendar_file:
            calendar = Calendar(calendar_file.read())
    except FileNotFoundError:
        pass

    event = Event()
    event.name = event_name
    event.begin = start_time
    event.end = end_time
    calendar.events.add(event)

    with open(calendar_path, 'w', encoding='utf-8') as calendar_file:
        calendar_file.writelines(calendar)

    return True
