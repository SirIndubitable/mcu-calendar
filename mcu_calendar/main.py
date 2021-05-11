"""
This script adds events to a google users calendar for Movies and TV shows defined in ./data/
"""
import argparse
import os
from google.api_core.client_options import ClientOptions
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

from events import Movie, Show

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
EVENTS_SERVICE = None


def update_creds_token(creds):
    """
    Updates the token.json containing the login token so that when testing
    it is not required to login constantly
    """
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


def get_local_creds():
    """
    Gets the google Credentials object in this order:
    1. Automatically created token.json
    2. credentials.json file created from https://console.cloud.google.com/
    """
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                update_creds_token(creds)
                return creds
            except RefreshError:
                pass

    # This is the credentials file that is created from making a project with an
    # OAuth 2.0 Client ID from
    if os.path.exists('credentials.json'):
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file='credentials.json',
            scopes=SCOPES)
        creds = flow.run_console(access_type='offline', include_granted_scopes='true')
        update_creds_token(creds)
        return creds

    raise RuntimeError("Could not load local credentials, add a credentials.json "
                       "file from https://console.cloud.google.com/")


def get_cal_id():
    """
    Gets the ID of the calender that this script should write to.  This ID should
    belong to the user that logged in from get_google_creds()
    1. From the cal_id.txt file
    2. From GOOGLE_MCU_CALENDAR_ID environment variable
    """
    if os.path.exists('cal_id.txt'):
        with open('cal_id.txt', 'r') as reader:
            return reader.read().strip()
    if 'GOOGLE_MCU_CALENDAR_ID' in os.environ:
        return os.environ['GOOGLE_MCU_CALENDAR_ID']

    # This would normally be secret, but this project is so people can add this calendar
    # to their calendars, and this information is on the iCal url, so why hide it?
    return "unofficial.mcu.calendar@gmail.com"


def get_google_events():
    """
    Gets all of the events currently on the calender from get_cal_id()
    """
    events_result = EVENTS_SERVICE.list(calendarId=get_cal_id()).execute()
    return events_result.get('items', [])

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


def find(seq, predicate):
    """
    Finds the first element in seq that predicate return true for
    """
    for item in seq:
        if predicate(item):
            return item
    return None


def create_google_event(progress_title, items, existing_events, force):
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
            elif item != event or force:
                progress.print(f"[reset]{item}", "[yellow](Updating)")
                EVENTS_SERVICE.update(
                    calendarId=calendar_id,
                    eventId=event["id"],
                    body=item.to_google_event()).execute()
            else:
                progress.print(f"[reset]{item}", "[cyan](Skipping)")


class MockService():
    """
    A service that doesn't allow post requests to update the calendar data, but still allows
    get requests so that the code can run properly
    """
    def __init__(self, realService):
        self.real_service = realService

    # Disable unused argument and missing doc string because these are required to match the methods
    # That they are Mocking out
    # pylint: disable=unused-argument,missing-docstring
    def list(self, **kwargs):
        return self.real_service.list(**kwargs)

    def update(self, **kwargs):
        return self

    def insert(self, **kwargs):
        return self

    def execute(self):
        pass


def main():
    """
    Main method that updates the users google calendar
    """
    events = get_google_events()
    create_google_event("[bold]Movies..", get_movies(), events, force=args.force)
    create_google_event("[bold]Shows...", get_shows(), events, force=args.force)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update a google calendarwith MCU Release info')
    parser.add_argument('--force', action='store_true', help='Force update the existing events')
    parser.add_argument('--dry', action='store_true', help='A dry run where nothing is updated')
    args = parser.parse_args()

    token_path = os.path.join(os.environ.get("HOME"), "secrets", "service_token.json")
    if os.path.exists(token_path):
        EVENTS_SERVICE = build(
            serviceName= 'calendar',
            version= 'v3',
            client_options=ClientOptions(credentials_file=token_path, scopes=SCOPES)).events()
    else:
        EVENTS_SERVICE = build(
            serviceName= 'calendar',
            version= 'v3',
            credentials= get_local_creds()).events()

    if args.dry:
        EVENTS_SERVICE = MockService(EVENTS_SERVICE)

    main()
