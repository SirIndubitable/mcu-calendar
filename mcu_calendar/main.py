"""
This script adds events to a google users calendar for Movies and TV shows defined in ./data/
"""
import os
from argparse import ArgumentParser
from datetime import date

from .events import TmdbMovie, TmdbShow, YamlMovie, YamlShow
from .google_service_helper import create_service, MockService
from .tmdb_helper import get_mcu_media
from .general_helpers import create_progress, find, truncate

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
EVENTS_SERVICE = None

def get_cal_id():
    """
    Gets the ID of the calender that this script should write to.  This ID should
    belong to the user that logged in from get_google_creds()
    1. From the cal_id.txt file
    2. From GOOGLE_MCU_CALENDAR_ID environment variable
    """
    if os.path.exists('cal_id.txt'):
        with open('cal_id.txt', 'r', encoding='utf-8') as reader:
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


def get_objects_from_yaml(folder_name, factory):
    """
    Loads all of the objects defined in yaml files in ./data/{{folder_name}}
    """
    dir_path = os.path.join('data', folder_name)
    return [factory(os.path.join(dir_path, filename)) for filename in os.listdir(dir_path)]


def get_yaml_movies():
    """
    Gets all Movie objects defined in the yaml files in ./data/movies
    """
    return get_objects_from_yaml('movies', YamlMovie)


def get_yaml_shows():
    """
    Gets all Show objects defined in the yaml files in ./data/shows
    """
    return get_objects_from_yaml('shows', YamlShow)


def event_to_str(event):
    """
    Converts a google event to a string
    """
    start = date.fromisoformat(event['start']['date'])
    return f"{truncate(event['summary'], 36)} {start.strftime('%b %d, %Y')}"


def event_needs_updated(event, item):
    """
    Checks if event needs to be updated.
    It does this by checking if item is a subset of event,
    if it isn't then event needs to be updated
    """
    for (key, value) in item.items():
        if event[key] != value:
            return True
    return False


def _get_shared_property(event, property_name):
    """
    Gets a google api shared extended property
    """
    properties = event.get('extendedProperties')
    if properties is None:
        return None
    shared_properties = properties.get('shared')
    if shared_properties is None:
        return None
    return shared_properties.get(property_name)


def has_matching_key(left, right, key):
    """
    Compares the alphanumeric characters of a given key
    """
    left_val = ''.join(filter(str.isalnum, left.get(key)))
    right_val = ''.join(filter(str.isalnum, right.get(key)))
    return left_val.lower() == right_val.lower()


def create_google_event(progress_title, items, existing_events, force):
    """
    Creates or Updates events if needed on the calendar based on the items objects
    """
    calendar_id = get_cal_id()
    items.sort(key=lambda i: date.fromisoformat(i['start']['date']))
    with create_progress() as progress:
        for item in progress.track(items, description=progress_title):
            event = find(existing_events, lambda e: has_matching_key(e, item, 'summary'))
            if event is None:
                progress.print(f"[reset]{event_to_str(item)}", "[red](Adding)")
                EVENTS_SERVICE.insert(
                    calendarId=calendar_id,
                    body=item).execute()
            else:
                existing_events.remove(event)
                if event_needs_updated(event, item) or force:
                    progress.print(f"[reset]{event_to_str(item)}", "[yellow](Updating)")
                    EVENTS_SERVICE.update(
                        calendarId=calendar_id,
                        eventId=event["id"],
                        body=item).execute()
                else:
                    progress.print(f"[reset]{event_to_str(item)}", "[cyan](Skipping)")


def main():
    """
    Main method that updates the users google calendar
    """
    events = get_google_events()
    (tmdb_movies, tmdb_shows) = get_mcu_media()
    movies = [TmdbMovie(tmdb_movie) for tmdb_movie in tmdb_movies]
    movie_events = [m.to_google_event() for m in movies]

    shows = [TmdbShow(tmdb_show) for tmdb_show in tmdb_shows]
    show_events = [season for show in shows for season in show.to_google_event()]
    create_google_event("[bold]Movies..", movie_events, events, force=args.force)
    create_google_event("[bold]Shows...", show_events, events, force=args.force)
    calendar_id = get_cal_id()
    with create_progress() as progress:
        events.sort(key=lambda i: date.fromisoformat(i['start']['date']))
        for old_event in progress.track(events, description="Stale events"):
            progress.print(f"[reset]{event_to_str(old_event)}", "[red](Deleting)")
            EVENTS_SERVICE.delete_event(calendarId=calendar_id, eventId=old_event["id"])


if __name__ == '__main__':
    parser = ArgumentParser(description='Update a google calendarwith MCU Release info')
    parser.add_argument('--force', action='store_true', help='Force update the existing events')
    parser.add_argument('--dry', action='store_true', help='A dry run where nothing is updated')
    args = parser.parse_args()

    EVENTS_SERVICE = create_service(SCOPES)
    if args.dry:
        EVENTS_SERVICE = MockService(EVENTS_SERVICE)

    main()
