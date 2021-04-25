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


class Movie():
    def __init__(self, yaml_path):
        with open(yaml_path, 'r') as yaml_file:
            yaml_dict = yaml.load(yaml_file, Loader=yaml.Loader)
            self.__dict__.update(yaml_dict)

    def to_google_event(self):
        return {
            "start": { "date": self.release_date.isoformat() },
            "end": { "date": self.release_date.isoformat() },
            "summary": self.title,
            "description": self.description,
        }

    def __eq__(self, other):
        if isinstance(other, Movie):
            return self.title        == other.title       \
               and self.description  == other.description \
               and self.release_date == other.release_date
        else:
            self_event = self.to_google_event()
            return self_event["start"]["date"] == other["start"]["date"] \
               and self_event["end"]["date"]   == other["end"]["date"]   \
               and self_event["summary"]       == other["summary"]       \
               and self_event["description"]   == other["description"]


    def __ne__(self, other):
        return not self == other


    def __str__(self):
        return f"{truncate(self.title, 26)} {self.release_date.strftime('%b %d, %Y')}"


def get_movies():
    movies_dir = os.path.join('data', 'movies')
    return [Movie(os.path.join(movies_dir, filename)) for filename in os.listdir(movies_dir)]


def truncate(string, length):
    return string[:(length-3)].ljust(length, ".")


def find(seq, f):
    for item in seq:
        if f(item):
            return item
    return None


def create_google_event(progressTitle, items, existingEvents):
    progress = Progress(
        TextColumn(progressTitle),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn())
    items.sort(key=lambda m: m.release_date)
    with progress:
        for item in progress.track(items):
            event = find(existingEvents, lambda e: e['summary'] == item.title)
            if event == None:
                progress.print(f"[reset]{item}", "[red](Adding)")
                events_service.insert(calendarId=calId, body=item.to_google_event()).execute()
            elif item != event:
                progress.print(f"[reset]{item}", "[yellow](Updating)")
                events_service.update(calendarId=calId, eventId=event["id"], body=item.to_google_event()).execute()
            else:
                progress.print(f"[reset]{item}", "[cyan](Skipping)")


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
