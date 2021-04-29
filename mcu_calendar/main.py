"""
This script adds events to a google users calendar for Movies and TV shows defined in ./data/
"""
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
    """
    Updates the token.json containing the login token so that when testing
    it is not required to login constantly
    """
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


def get_google_creds():
    """
    Gets the google Credentials object in this order:
    1. Automatically created token.json
    2. credentials.json file created from https://console.cloud.google.com/
    3. Environment variables containing the token information
    """
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            update_creds_token(creds)
            return creds

    # This is the credentials file that is created from making a project with an
    # OAuth 2.0 Client ID from
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
    """
    Gets the ID of the calender that this script should write to.  This ID should
    belong to the user that logged in from get_google_creds()
    1. From the cal_id.txt file
    2. From GOOGLE_MCU_CALENDAR_ID environment variable
    3. The primary user calendar
    """
    if os.path.exists('cal_id.txt'):
        with open('cal_id.txt', 'r') as reader:
            return reader.read().strip()
    if 'GOOGLE_MCU_CALENDAR_ID' in os.environ:
        return os.environ['GOOGLE_MCU_CALENDAR_ID']
    return 'primary'


def get_google_events():
    """
    Gets all of the events currently on the calender from get_cal_id()
    """
    events_result = EVENTS_SERVICE.list(calendarId=get_cal_id()).execute()
    return events_result.get('items', [])


class GoogleMediaEvent():
    """
    Base class for a google event that is defined in yaml
    """
    def to_google_event(self):
        """
        Converts this object to a google calendar api event
        https://developers.google.com/calendar/v3/reference/events#resource
        """

    def sort_val(self):
        """
        Gets the value that this object should be sorted by
        """

    def __ne__(self, other):
        return not self == other


class Movie(GoogleMediaEvent):
    """
    The event that describes a movie release date
    """
    def __init__(self, title, description, release_date):
        self.title = title
        self.description = description
        self.release_date = release_date

    @staticmethod
    def from_yaml(yaml_path):
        """
        Factory method to create a Movie object from yaml
        """
        with open(yaml_path, 'r') as yaml_file:
            yaml_data = yaml.load(yaml_file, Loader=yaml.Loader)
        return Movie(**yaml_data)

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
        self_event = self.to_google_event()
        return self_event["start"]["date"] == other["start"]["date"] \
           and self_event["end"]["date"]   == other["end"]["date"]   \
           and self_event["summary"]       == other["summary"]       \
           and self_event["description"]   == other["description"]

    def __str__(self):
        return f"{truncate(self.title, 26)} {self.release_date.strftime('%b %d, %Y')}"


class Show(GoogleMediaEvent):
    """
    The event that describes a show start date and how many weeks it runs for
    """
    def __init__(self, title, start_date, weeks):
        self.title = title
        self.start_date = start_date
        self.weeks = weeks

    @staticmethod
    def from_yaml(yaml_path):
        """
        Factory method to create a Show object from yaml
        """
        with open(yaml_path, 'r') as yaml_file:
            yaml_data = yaml.load(yaml_file, Loader=yaml.Loader)
        return Show(**yaml_data)

    def _rfc5545_weekday(self):
        _recurrence_weekday = [ "MO", "TU", "WE", "TH", "FR", "SA", "SU" ]
        return _recurrence_weekday[self.start_date.weekday()]

    def to_google_event(self):
        return {
            "summary": self.title,
            "start": { "date": self.start_date.isoformat() },
            "end": { "date": (self.start_date + datetime.timedelta(days=1)).isoformat() },
            "recurrence": [
                f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT={self.weeks};BYDAY={self._rfc5545_weekday()}"
            ],
        }

    def sort_val(self):
        return self.start_date

    def __eq__(self, other):
        if isinstance(other, Show):
            return self.title      == other.title      \
               and self.start_date == other.start_date \
               and self.weeks      == other.weeks
        self_event = self.to_google_event()
        return self_event["summary"]       == other["summary"]       \
           and self_event["start"]["date"] == other["start"]["date"] \
           and self_event["end"]["date"]   == other["end"]["date"]   \
           and self_event["recurrence"]    == other["recurrence"]

    def __str__(self):
        return f"{truncate(self.title, 26)} {self.start_date.strftime('%b %d, %Y')}"

def get_objects_from_data(folder_name, factory):
    """
    Loads all of the objects defined in yaml files in ./data/{{folder_name}}
    """
    dir_path = os.path.join('data', folder_name)
    return [factory(os.path.join(dir_path, filename)) for filename in os.listdir(dir_path)]


def get_movies():
    """
    Gets all Movie objects defined in the yaml files in ./data/movies
    """
    return get_objects_from_data('movies', Movie.from_yaml)


def get_shows():
    """
    Gets all Show objects defined in the yaml files in ./data/shows
    """
    return get_objects_from_data('shows', Show.from_yaml)


def truncate(string, length):
    """
    Truncates a string to a given length with "..." at the end if needed
    """
    return string[:(length-3)].ljust(length, ".")


def find(seq, predicate):
    """
    Finds the first element in seq that predicate return true for
    """
    for item in seq:
        if predicate(item):
            return item
    return None


def create_google_event(progress_title, items, existing_events):
    """
    Creates or Updates events if needed on the calendar based on the items objects
    """
    calendar_id = get_cal_id()
    progress = Progress(
        TextColumn(progress_title),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn())
    items.sort(key=lambda i: i.sort_val())
    with progress:
        for item in progress.track(items):
            event = find(existing_events, lambda e: 'summary' in e and e['summary'] == item.title)
            if event is None:
                progress.print(f"[reset]{item}", "[red](Adding)")
                EVENTS_SERVICE.insert(calendarId=calendar_id, body=item.to_google_event()).execute()
            elif item != event:
                progress.print(f"[reset]{item}", "[yellow](Updating)")
                EVENTS_SERVICE.update(
                    calendarId=calendar_id,
                    eventId=event["id"],
                    body=item.to_google_event()).execute()
            else:
                progress.print(f"[reset]{item}", "[cyan](Skipping)")



def main():
    """
    Main method that updates the users google calendar
    """
    global EVENTS_SERVICE
    EVENTS_SERVICE = build('calendar', 'v3', credentials=get_google_creds()).events()
    events = get_google_events()
    create_google_event("[bold]Movies..", get_movies(), events)
    create_google_event("[bold]Shows...", get_shows(), events)


if __name__ == '__main__':
    main()
