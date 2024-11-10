"""
Calendars objects that sync data to a google Calendar
"""

from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence

from .events import GoogleMediaEvent, Movie, Show
from .helpers import create_progress, truncate


# pylint: disable=too-few-public-methods
class YamlCalendar:
    """
    Uses Yaml data to sync calendar information
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        name: str,
        cal_id: str,
        movie_dirs: List[Path],
        show_dirs: List[Path],
        google_service: Any,
    ) -> None:
        self.name = name
        self.cal_id = cal_id
        self.movie_dirs = movie_dirs
        self.show_dirs = show_dirs
        self.google_service = google_service

    @staticmethod
    def _get_objects_from_data(folder: Path, factory: Callable[[Path], Any]) -> List[Any]:
        """
        Loads all of the objects defined in yaml files in ./data/{{folder_name}}
        """
        return [factory(f) for f in folder.iterdir()]

    @staticmethod
    def get_movies(folder: Path) -> Sequence[Movie]:
        """
        Gets all Movie objects defined in the yaml files in ./data/movies
        """
        return YamlCalendar._get_objects_from_data(folder, Movie.from_yaml)

    @staticmethod
    def get_shows(folder: Path) -> Sequence[Show]:
        """
        Gets all Show objects defined in the yaml files in ./data/shows
        """
        return YamlCalendar._get_objects_from_data(folder, Show.from_yaml)

    def _get_google_events(self) -> List[Dict]:
        """
        Gets all of the events currently on the calendar from get_cal_id()
        """
        events_result = self.google_service.list(calendarId=self.cal_id).execute()
        return events_result.get("items", [])

    def _create_google_event(
        self,
        progress_title: str,
        items: Sequence[GoogleMediaEvent],
        existing_events: List[Dict],
        force: bool,
    ) -> None:
        """
        Creates or Updates events if needed on the calendar based on the items objects
        """
        items = sorted(items, key=lambda i: i.sort_val())
        with create_progress() as progress:
            for item in progress.track(items, description=progress_title):
                event = next(
                    (e for e in existing_events if "summary" in e and e["summary"] == item.title),
                    None,
                )
                if event is not None:
                    existing_events.remove(event)
                if event is None:
                    progress.print(f"[reset]{item}", "[red](Adding)")
                    self.google_service.insert(calendarId=self.cal_id, body=item.to_google_event()).execute()
                elif item != event or force:
                    progress.print(f"[reset]{item}", "[yellow](Updating)")
                    self.google_service.update(
                        calendarId=self.cal_id,
                        eventId=event["id"],
                        body=item.to_google_event(),
                    ).execute()
                else:
                    progress.print(f"[reset]{item}", "[cyan](Skipping)")

    def create_google_events(self, force: bool = False) -> None:
        """
        Creates or Updates events all events if needed on the calendar
        """
        print("    UPDATING", self.name)
        cur_events = self._get_google_events()
        movies = [m for mdir in self.movie_dirs for m in YamlCalendar.get_movies(mdir)]
        shows = [s for sdir in self.show_dirs for s in YamlCalendar.get_shows(sdir)]
        self._create_google_event("[bold]Movies..", movies, cur_events, force=force)
        self._create_google_event("[bold]Shows...", shows, cur_events, force=force)

        with create_progress() as progress:
            cur_events.sort(key=lambda i: date.fromisoformat(i["start"]["date"]))
            for old_event in progress.track(cur_events, description="Stale events..."):
                item_time = date.fromisoformat(old_event["start"]["date"])
                item_str = f"{truncate(old_event['summary'], 26)} {item_time.strftime('%b %d, %Y')}"
                progress.print(f"[reset]{item_str}", "[red](Deleting)")
                self.google_service.delete(calendarId=self.cal_id, eventId=old_event["id"]).execute()

        print()
