"""
Google Event objects that represent different media release events
"""
import datetime

import yaml

from .helpers import truncate


class GoogleMediaEvent:
    """
    Base class for a google event that is defined in yaml
    """

    def __init__(self, description):
        self.description = description

    def to_google_event(self):
        """
        Converts this object to a google calendar api event
        https://developers.google.com/calendar/v3/reference/events#resource
        """
        base_event = {
            "description": self.description,
            "source": {
                "title": "MCU Calendar",
                "url": "https://github.com/SirIndubitable/mcu-calendar",
            },
            "transparency": "transparent",  # "transparent" means "Show me as Available "
        }
        return {**base_event, **self._to_google_event_core()}

    @staticmethod
    def load_yaml(yaml_path):
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

    def _to_google_event_core(self):
        """
        The method that subclasses should override for baseclass specific
        google calendar api event data
        """

    def sort_val(self):
        """
        Gets the value that this object should be sorted by
        """

    def __eq__(self, other):
        if isinstance(other, GoogleMediaEvent):
            return self.description == other.description
        return self.description == (other["description"] if "description" in other else "")

    def __ne__(self, other):
        return not self == other


class Movie(GoogleMediaEvent):
    """
    The event that describes a movie release date
    """

    def __init__(self, title, description, release_date):
        super().__init__(description)
        self.title = title
        self.release_date = release_date

    @staticmethod
    def from_yaml(yaml_path):
        """
        Factory method to create a Movie object from yaml
        """
        yaml_data = GoogleMediaEvent.load_yaml(yaml_path)
        return Movie(**yaml_data)

    def _to_google_event_core(self):
        return {
            "start": {"date": self.release_date.isoformat()},
            "end": {"date": (self.release_date + datetime.timedelta(days=1)).isoformat()},
            "summary": self.title,
        }

    def sort_val(self):
        return self.release_date

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        if isinstance(other, Movie):
            return self.title == other.title and self.release_date == other.release_date
        event = self.to_google_event()
        return (
            event["start"]["date"] == other["start"]["date"]
            and event["end"]["date"] == other["end"]["date"]
            and event["summary"] == other["summary"]
        )

    def __str__(self):
        return f"{truncate(self.title, 26)} {self.release_date.strftime('%b %d, %Y')}"


class Show(GoogleMediaEvent):
    """
    The event that describes a show start date and how many weeks it runs for
    """

    def __init__(self, title, release_dates, description):
        super().__init__(description)
        self.title = title
        self.release_dates = release_dates
        self.start_date = release_dates[0]

    @staticmethod
    def from_yaml(yaml_path):
        """
        Factory method to create a Show object from yaml
        """
        yaml_data = GoogleMediaEvent.load_yaml(yaml_path)
        return Show(**yaml_data)

    def _rfc5545_weekday(self):
        _recurrence_weekday = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        return _recurrence_weekday[self.start_date.weekday()]

    def _to_google_event_core(self):
        event_data = {
            "summary": self.title,
            "start": {"date": self.start_date.isoformat()},
            "end": {"date": (self.start_date + datetime.timedelta(days=1)).isoformat()},
        }

        schedule = (j - i for i, j in zip(self.release_dates[:-1], self.release_dates[1:]))
        if len(self.release_dates) == 1:
            event_data["recurrence"] = None
        elif len(schedule) == 1:
            [recurrence] = schedule
            if recurrence == datetime.timedelta(days=7):
                event_data["recurrence"] = [
                    f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT={len(self.release_dates)};BYDAY={self._rfc5545_weekday()}"
                ]
            if recurrence == datetime.timedelta(days=1):
                event_data["recurrence"] = [f"RRULE:FREQ=DAILY;COUNT={len(self.release_dates)}"]
        else:
            event_data["recurrence"] = None

        return event_data

    def sort_val(self):
        return self.start_date

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        if isinstance(other, Show):
            return self.title == other.title and self.release_dates == other.release_dates
        event = self.to_google_event()
        return (
            event["summary"] == other["summary"]
            and event["start"]["date"] == other["start"]["date"]
            and event["end"]["date"] == other["end"]["date"]
            and event["recurrence"] == other["recurrence"]
        )

    def __str__(self):
        return f"{truncate(self.title, 26)} {self.start_date.strftime('%b %d, %Y')}"
