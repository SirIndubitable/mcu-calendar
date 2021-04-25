import datetime
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import yaml
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def get_google_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_cal_id():
    with open('cal_id.txt', 'r') as reader:
        return reader.read().strip()


def get_google_events():
    global service
    global calId
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = events_service.list(calendarId=calId).execute()
    return events_result.get('items', [])


def get_movies():
    movies = []
    for filename in os.listdir(os.path.join('data', 'movies')):
        with open(os.path.join('data', 'movies', filename), 'r') as movie_yaml:
            yaml_movie = yaml.load(movie_yaml, Loader=yaml.Loader)
            movies.append({
                "start": { "date": yaml_movie['release_date'].isoformat() },
                "end": { "date": yaml_movie['release_date'].isoformat() },
                "summary": yaml_movie['title'],
                "description": yaml_movie['description']
            })
    return movies


def truncate(string, length):
    return string[:(length-3)].ljust(length, ".")


def find(f, seq):
    for item in seq:
        if f(item):
            return item
    return None


def format_item(item):
    return f"[reset]{truncate(item['summary'], 26)} {datetime.date.fromisoformat(item['start']['date']).strftime('%b %d, %Y')}"


def create_google_event(progressTitle, items, existingEvents):
    progress = Progress(
        TextColumn(progressTitle),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn())
    items.sort(key=lambda m: m['start']['date'])
    with progress:
        for item in progress.track(items):
            event = find(lambda e: e['summary'] == item['summary'], existingEvents)
            if event == None:
                progress.print(format_item(item), "[red](Adding)")
                events_service.insert(calendarId=calId, body=item).execute()
            elif event["start"]["date"] != item["start"]["date"] \
              or event['description'] != item['description']:
                progress.print(format_item(item), "[yellow](Updating)")
                events_service.update(calendarId=calId, eventId=event["id"], body=item).execute()
            else:
                progress.print(format_item(item), "[cyan](Skipping)")


import time
calId = get_cal_id()
creds = get_google_creds()
events_service = build('calendar', 'v3', credentials=creds).events()
def main():
    global calId
    global events_service
    events = get_google_events()
    create_google_event("Movies...", get_movies(), events)


if __name__ == '__main__':
    main()
