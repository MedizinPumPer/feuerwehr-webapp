from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import pytz
import logging

# Google Calendar API Einstellungen
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = '/var/www/feuerwehr-webapp/static/service_account.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)

# Zeitzone definieren
berlin_tz = pytz.timezone('Europe/Berlin')

def is_time_slot_available(calendar_id, start_time, end_time):
    # Zeiten in UTC konvertieren
    start_time_utc = start_time.astimezone(pytz.utc)
    end_time_utc = end_time.astimezone(pytz.utc)
    
    logging.debug(f"Checking availability from {start_time.isoformat()} to {end_time.isoformat()} (UTC: {start_time_utc.isoformat()} to {end_time_utc.isoformat()})")
    
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_time_utc.isoformat(),
        timeMax=end_time_utc.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    logging.debug(f"Found events: {format(events)}")
    
    for event in events:
        event_start = event['start'].get('dateTime')
        event_end = event['end'].get('dateTime')
        logging.debug(f"Event Start: {event_start}, Event End: {event_end}")

        # Konvertiere Eventzeiten in UTC
        event_start_dt = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
        event_end_dt = datetime.fromisoformat(event_end.replace("Z", "+00:00"))

        # Prüfe auf Überlappung
        if (start_time_utc < event_end_dt and end_time_utc > event_start_dt):
            logging.debug(f"Conflict with event: {event['summary']}")
            return False

    return True

def add_event_to_google_calendar(calendar_id, event_name, start_time, end_time, multi_day=False):
    # Zeiten in Berlin-Zeitzone umwandeln
    start_time = berlin_tz.localize(start_time)
    end_time = berlin_tz.localize(end_time)
    
    if multi_day:
        current_start = start_time
        current_end = start_time.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)
        links = []
        while current_start < end_time:
            if is_time_slot_available(calendar_id, current_start, current_end):
                event = {
                    'summary': event_name,
                    'start': {
                        'dateTime': current_start.isoformat(),
                        'timeZone': 'Europe/Berlin',
                    },
                    'end': {
                        'dateTime': current_end.isoformat(),
                        'timeZone': 'Europe/Berlin',
                    },
                }
                event = service.events().insert(calendarId=calendar_id, body=event).execute()
                links.append(event.get('htmlLink'))
            current_start = current_start + timedelta(days=1)
            current_start = current_start.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
            current_end = current_start.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)
            logging.debug('Start: ' + format(current_start))
            logging.debug('End: ' + format(current_end))
        if links:
            return links, None
        else:
            return None, "Der gewünschte Zeitraum ist bereits gebucht."
    else:
        if not is_time_slot_available(calendar_id, start_time, end_time):
            return None, "Der gewünschte Zeitraum ist bereits gebucht."
        
        event = {
            'summary': event_name,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Europe/Berlin',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Europe/Berlin',
            },
        }
        
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return event.get('htmlLink'), None
