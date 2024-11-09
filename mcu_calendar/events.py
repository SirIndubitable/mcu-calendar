"""
Google Event objects that represent different media release events
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, timedelta
from pathlib import Path
from re import search as re_search
from typing import Any, Dict, List

import yaml

from .helpers import truncate


class GoogleMediaEvent(ABC):
    """
    Base class for a google event that is defined in yaml
    """

    def __init__(self, title: str, description: str, file_path: Path, imdb_id: str | None) -> None:
        self.title = title
        self.description = description
        self.imdb_id = imdb_id
        self.file_path = file_path

        if not self.imdb_id:
            matches = re_search("https://www.imdb.com/title/(.*)", self.description)
            if matches:
                self.imdb_id = matches.group(1)

    def to_google_event(self) -> Dict[str, Any]:
        """
        Converts this object to a google calendar api event
        https://developers.google.com/calendar/v3/reference/events#resource
        """
        base_event = {
            "summary": self.title,
            "description": self.description,
            "source": {
                "title": "MCU Calendar",
                "url": "https://github.com/SirIndubitable/mcu-calendar",
            },
            "transparency": "transparent",  # "transparent" means "Show me as Available "
        }
        return {**base_event, **self._to_google_event_core()}

    @staticmethod
    def load_yaml(yaml_path: Path) -> Dict[str, Any]:
        """
        Factory method to create a Show object from yaml
        """
        with open(yaml_path, "r", encoding="UTF-8") as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
        patch_path = yaml_path.with_suffix(".patch")
        if patch_path.exists():
            with open(patch_path, "r", encoding="UTF-8") as yaml_file:
                yaml_data = yaml_data | yaml.safe_load(yaml_file)
        return yaml_data

    @abstractmethod
    def _to_google_event_core(self) -> Dict[str, Any]:
        """
        The method that subclasses should override for baseclass specific
        google calendar api event data
        """

    @abstractmethod
    def sort_val(self) -> str:
        """
        Gets the value that this object should be sorted by
        """

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GoogleMediaEvent):
            return self.description == other.description
        return self.description == other.get("description", "")

    def __ne__(self, other: Any) -> bool:
        return not self == other


class Movie(GoogleMediaEvent):
    """
    The event that describes a movie release date
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self, title: str, description: str, release_date: date, file_path: Path, imdb_id: str | None = None
    ) -> None:
        super().__init__(title, description, file_path, imdb_id)
        self.release_date = release_date

    @staticmethod
    def from_yaml(yaml_path: Path) -> Movie:
        """
        Factory method to create a Movie object from yaml
        """
        yaml_data = GoogleMediaEvent.load_yaml(yaml_path)
        return Movie(**yaml_data, file_path=yaml_path)

    def _to_google_event_core(self) -> Dict[str, Any]:
        return {
            "start": {"date": self.release_date.isoformat()},
            "end": {"date": (self.release_date + timedelta(days=1)).isoformat()},
        }

    def sort_val(self) -> Any:
        return self.release_date

    def __eq__(self, other: Any) -> bool:
        if not super().__eq__(other):
            return False
        if isinstance(other, Movie):
            return self.title == other.title and self.release_date == other.release_date
        event = self.to_google_event()
        return (
            event.get("summary") == other.get("summary")
            and event.get("start", {}).get("date") == other.get("start", {}).get("date")
            and event.get("end", {}).get("date") == other.get("end", {}).get("date")
        )

    def __str__(self) -> str:
        return f"{truncate(self.title, 26)} {self.release_date.strftime('%b %d, %Y')}"


class Show(GoogleMediaEvent):
    """
    The event that describes a show start date and how many weeks it runs for
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self, title: str, release_dates: List[date], description: str, file_path: Path, imdb_id: str | None = None
    ) -> None:
        super().__init__(title, description, file_path, imdb_id)
        self.release_dates = release_dates
        self.start_date = release_dates[0]

    @staticmethod
    def from_yaml(yaml_path: Path) -> Show:
        """
        Factory method to create a Show object from yaml
        """
        yaml_data = GoogleMediaEvent.load_yaml(yaml_path)
        return Show(**yaml_data, file_path=yaml_path)

    def _rfc5545_weekday(self) -> str:
        _recurrence_weekday = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        return _recurrence_weekday[self.start_date.weekday()]

    def _to_google_event_core(self) -> Dict[str, Any]:
        event_data: Dict[str, Any] = {
            "start": {"date": self.start_date.isoformat()},
            "end": {"date": (self.start_date + timedelta(days=1)).isoformat()},
        }

        schedule = {j - i for i, j in zip(self.release_dates[:-1], self.release_dates[1:])}
        if len(self.release_dates) == 1:
            event_data["recurrence"] = None
        elif len(schedule) == 1:
            [recurrence] = schedule
            if recurrence == timedelta(days=7):
                event_data["recurrence"] = [
                    f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT={len(self.release_dates)};BYDAY={self._rfc5545_weekday()}"
                ]
            elif recurrence == timedelta(days=1):
                event_data["recurrence"] = [f"RRULE:FREQ=DAILY;COUNT={len(self.release_dates)}"]
            else:
                event_data["recurrence"] = None
        else:
            event_data["recurrence"] = None

        return event_data

    def sort_val(self) -> Any:
        return self.start_date

    def __eq__(self, other: Any) -> bool:
        if not super().__eq__(other):
            return False
        if isinstance(other, Show):
            return self.title == other.title and self.release_dates == other.release_dates
        event = self.to_google_event()
        return (
            event.get("summary") == other.get("summary")
            and event.get("start", {}).get("date") == other.get("start", {}).get("date")
            and event.get("end", {}).get("date") == other.get("end", {}).get("date")
            and event.get("recurrence") == other.get("recurrence")
        )

    def __str__(self) -> str:
        return f"{truncate(self.title, 26)} {self.start_date.strftime('%b %d, %Y')}"
