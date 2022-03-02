"""
Calendars objects that sync data to a google Calendar
"""
from pathlib import Path
from typing import Any, Callable, Dict, List

from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn

from .events import GoogleMediaEvent, Movie, Show


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
    def _get_objects_from_data(
        folder: Path, factory: Callable[[Path], Any]
    ) -> List[Any]:
        """
        Loads all of the objects defined in yaml files in ./data/{{folder_name}}
        """
        return [factory(f) for f in folder.iterdir()]

    @staticmethod
    def _get_movies(folder: Path) -> List[Movie]:
        """
        Gets all Movie objects defined in the yaml files in ./data/movies
        """
        return YamlCalendar._get_objects_from_data(folder, Movie.from_yaml)

    @staticmethod
    def _get_shows(folder: Path) -> List[Show]:
        """
        Gets all Show objects defined in the yaml files in ./data/shows
        """
        return YamlCalendar._get_objects_from_data(folder, Show.from_yaml)

    def _get_google_events(self) -> List[Dict]:
        """
        Gets all of the events currently on the calender from get_cal_id()
        """
        events_result = self.google_service.list(calendarId=self.cal_id).execute()
        return events_result.get("items", [])

    def _create_google_event(
        self,
        progress_title: str,
        items: List[GoogleMediaEvent],
        existing_events: List[Dict],
        force: bool,
    ):
        """
        Creates or Updates events if needed on the calendar based on the items objects
        """
        progress = Progress(
            TextColumn(progress_title),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
        )
        items.sort(key=lambda i: i.sort_val())
        with progress:
            for item in progress.track(items):
                event = next(
                    (
                        e
                        for e in existing_events
                        if "summary" in e and e["summary"] == item.title
                    ),
                    None,
                )
                if event is None:
                    progress.print(f"[reset]{item}", "[red](Adding)")
                    self.google_service.insert(
                        calendarId=self.cal_id, body=item.to_google_event()
                    ).execute()
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
        movies = [m for mdir in self.movie_dirs for m in YamlCalendar._get_movies(mdir)]
        shows = [s for sdir in self.show_dirs for s in YamlCalendar._get_shows(sdir)]
        self._create_google_event("[bold]Movies..", movies, cur_events, force=force)
        self._create_google_event("[bold]Shows...", shows, cur_events, force=force)
        print()
