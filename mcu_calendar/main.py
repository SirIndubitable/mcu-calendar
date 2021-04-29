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


def update_creds_token(creds):
    with open('token.json', 'w') as token:
       token.write(creds.to_json())


def get_google_creds():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if creds.valid:
            return creds
        elif creds.expired and creds.refresh_token:
            creds.refresh(Request())
            update_creds_token(creds)
            return creds

    # This is the credentials file that is created from making a project with an 
    # OAuth 2.0 Client ID from https://console.cloud.google.com/
    if os.path.exists('credentials.json'):
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file='credentials.json',
            scopes=SCOPES)
        creds = flow.run_console(access_type='offline', include_granted_scopes='true')
        update_creds_token(creds)
        return creds

    # Lastly if there is no credentials.json override.  We should use the environment variables
    # this is what the CI pipeline should end up using
    info = {
        "token": os.environ.get("GOOGLE_API_TOKEN"),
        "refresh_token": os.environ.get("GOOGLE_API_REFRESH_TOKEN"),
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "quota_project_id":"yaml-mcu-calendar-311822"
    }

    creds = Credentials.from_authorized_user_info(info, scopes=SCOPES)
    creds.refresh(Request())
    return creds


def get_cal_id():
    # The actual mcu calendar uses it's "primary" calendar
    # Though we have two options to override this for testing purposes
    if os.path.exists('cal_id.txt'):
        with open('cal_id.txt', 'r') as reader:
            return reader.read().strip()
    if 'GOOGLE_MCU_CALENDAR_ID' in os.environ:
        return os.environ['GOOGLE_MCU_CALENDAR_ID']
    return 'primary'


def get_google_events():
    global service
    global calId
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = events_service.list(calendarId=calId).execute()
    return events_result.get('items', [])


class GoogleMediaEvent(object):
    def __init__(self, args):
        if isinstance(args, str):
            with open(args, 'r') as yaml_file:
                yaml_dict = yaml.load(yaml_file, Loader=yaml.Loader)
                self.__init__(yaml_dict)
        if isinstance(args, dict):
            self.__dict__.update(args)

    def to_google_event(self):
        pass

    def sort_val(self):
        pass

    def __ne__(self, other):
        return not self == other


class Movie(GoogleMediaEvent):
    sort_key = "release_date"

    def to_google_event(self):
        return {
            "start": { "date": self.release_date.isoformat() },
            "end": { "date": self.release_date.isoformat() },
            "summary": self.title,
            "description": self.description,
        }

    def sort_val(self):
        return self.release_date

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

    def __str__(self):
        return f"{truncate(self.title, 26)} {self.release_date.strftime('%b %d, %Y')}"


class Show(GoogleMediaEvent):
    def _rfc5545_weekday(self):
        _recurrence_weekday = [ "MO", "TU", "WE", "TH", "FR", "SA", "SU" ]
        return _recurrence_weekday[self.start_date.weekday()]

    def to_google_event(self):
        return {
            "summary": self.title,
            "start": { "date": self.start_date.isoformat() },
            "end": { "date": (self.start_date + datetime.timedelta(days=1)).isoformat() },
            "recurrence": [f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT={self.weeks};BYDAY={self._rfc5545_weekday()}"],
        }

    def sort_val(self):
        return self.start_date

    def __eq__(self, other):
        if isinstance(other, Show):
            return self.title      == other.title      \
               and self.start_date == other.start_date \
               and self.weeks      == other.weeks
        else:
            self_event = self.to_google_event()
            return self_event["summary"]       == other["summary"]       \
               and self_event["start"]["date"] == other["start"]["date"] \
               and self_event["end"]["date"]   == other["end"]["date"]   \
               and self_event["recurrence"]    == other["recurrence"]

    def __str__(self):
        return f"{truncate(self.title, 26)} {self.start_date.strftime('%b %d, %Y')}"


def get_movies():
    movies_dir = os.path.join('data', 'movies')
    return [Movie(os.path.join(movies_dir, filename)) for filename in os.listdir(movies_dir)]


def get_shows():
    shows_dir = os.path.join('data', 'shows')
    return [Show(os.path.join(shows_dir, filename)) for filename in os.listdir(shows_dir)]


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
    items.sort(key=lambda i: i.sort_val())
    with progress:
        for item in progress.track(items):
            event = find(existingEvents, lambda e: 'summary' in e and e['summary'] == item.title)
            if event == None:
                progress.print(f"[reset]{item}", "[red](Adding)")
                events_service.insert(calendarId=calId, body=item.to_google_event()).execute()
            elif item != event:
                progress.print(f"[reset]{item}", "[yellow](Updating)")
                events_service.update(calendarId=calId, eventId=event["id"], body=item.to_google_event()).execute()
            else:
                progress.print(f"[reset]{item}", "[cyan](Skipping)")


calId = get_cal_id()
events_service = build('calendar', 'v3', credentials=get_google_creds()).events()

def main():
    events = get_google_events()
    create_google_event("[bold]Movies..", get_movies(), events)
    create_google_event("[bold]Shows...", get_shows(), events)


if __name__ == '__main__':
    main()
