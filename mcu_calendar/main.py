"""
This script adds events to a google users calendar for Movies and TV shows defined in ./data/
"""
import os
from argparse import ArgumentParser
from datetime import date, datetime

from .events import Movie, Show
from .google_service_helper import create_service, MockService
from .imdb_helper import get_mcu_media
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
        with open('cal_id.txt', 'r', encoding='UTF-8') as reader:
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
    return get_objects_from_yaml('movies', Movie.from_yaml)


def get_yaml_shows():
    """
    Gets all Show objects defined in the yaml files in ./data/shows
    """
    return get_objects_from_yaml('shows', Show.from_yaml)


def event_to_str(event):
    """
    Converts a google event to a string
    """
    return f"{truncate(event['summary'], 36)} {date.fromisoformat(event['start']['date']).strftime('%b %d, %Y')}"


def event_needs_updated(event, item):
    for (key, value) in item.items():
        if event[key] != value:
            print(key)
            return True
    return False


def create_google_event(progress_title, items, existing_events, force):
    """
    Creates or Updates events if needed on the calendar based on the items objects
    """
    calendar_id = get_cal_id()
    items.sort(key=lambda i: date.fromisoformat(i['start']['date']))
    with create_progress() as progress:
        for item in progress.track(items, description=progress_title):
            event = find(existing_events, lambda e: 'summary' in e and e['summary'] == item['summary'])
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
    yaml_movies = get_yaml_movies()
    yaml_shows = get_yaml_shows()
    (imdb_movies, imdb_shows) = get_mcu_media([movie.title for movie in yaml_movies], [show.title for show in yaml_shows])
    for imdb_movie in imdb_movies:
        yaml_movies.append(Movie({
            "title": imdb_movie['title'],
            "release_date": imdb_movie['releaseDate'],
            "description": f"https://www.imdb.com/title/{imdb_movie['id']}"
        }))
    for imdb_show in imdb_shows:
        yaml_show = find(yaml_shows, lambda s: s.title == imdb_show['title'])
        if yaml_show is None:
            yaml_show = Show({
                "title": imdb_show['title'],
                "seasons": [],
                "description": f"https://www.imdb.com/title/{imdb_show['imDbId']}"
            })
            yaml_shows.append(yaml_show)
        season = imdb_show['episodes'][0]
        yaml_show.data['seasons'].append({
            "num": season['seasonNumber'],
            "start_date": datetime.strptime(season['released'], "%d %b. %Y").date().isoformat(),
            "weeks": len(imdb_show['episodes'])})

    movies = [m.to_google_event() for m in yaml_movies]
    shows = [season for show in yaml_shows for season in show.to_google_event()]
    create_google_event("[bold]Movies..", movies, events, force=args.force)
    create_google_event("[bold]Shows...", shows, events, force=args.force)
    calendar_id = get_cal_id()
    with create_progress() as progress:
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
