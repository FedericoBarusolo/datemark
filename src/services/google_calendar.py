from googleapiclient.discovery import build

from models.io_models import Event


def create_calendar_event(creds, event: Event):
    # Build the service
    service = build('calendar', 'v3', credentials=creds)

    # Create event object
    event = {
        'summary': event.title,
        'description': '',
        'start': {
            'dateTime': event.start_time.isoformat(),  # ISO format: '2023-12-01T10:00:00-07:00'
            'timeZone': event.time_zone,
        },
        'end': {
            'dateTime': event.end_time.isoformat(),
            'timeZone': event.time_zone,
        },
        'attendees': "",
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    # Insert the event
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event
