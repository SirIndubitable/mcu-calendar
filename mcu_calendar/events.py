"""
Google Event objects that represent different media release events
"""
import datetime
import yaml
from .general_helpers import find

def truncate(string, length):
    """
    Truncates a string to a given length with "..." at the end if needed
    """
    return string[:(length-3)].ljust(length, ".")


class GoogleMediaEvent():
    """
    Base class for a google event that is defined in yaml
    """
    def __init__(self, data):
        self.data = data

    # def data_is(self, type_check):
    #     """
    #     checks what the backing datatype of this class is
    #     """
    #     datatype = 'imdb' if 'movieID' in self.data \
    #           else 'yaml'
    #     return datatype == type_check

    @property
    def description(self):
        """
        The description property
        """
        if 'description' in self.data:
            return self.data['description']
        if 'movieID' in self.data:
            return f"https://www.imdb.com/title/tt{self.data.movieID}"
        return None

    def to_google_event(self):
        """
        Converts this object to a google calendar api event
        https://developers.google.com/calendar/v3/reference/events#resource
        """
        base_event = {
            "description": self.description,
            "source": {
                "title": "MCU Calendar",
                "url": "https://github.com/SirIndubitable/mcu-calendar"
            },
            "transparency": "transparent", # "transparent" means "Show me as Available "
        }
        return {**base_event, **self._to_google_event_core()}

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
    @property
    def title(self):
        """
        The title property
        """
        return self.data['title']

    @property
    def release_date(self):
        """
        The original release date property
        """
        if 'release_date' in self.data:
            return self.data['release_date']
        if 'release dates' in self.data and 'USA' in self.data['release dates']:
            return self.data['release dates']['USA']
        return None

    @staticmethod
    def from_yaml(yaml_path):
        """
        Factory method to create a Movie object from yaml
        """
        with open(yaml_path, 'r', encoding='UTF-8') as yaml_file:
            yaml_data = yaml.load(yaml_file, Loader=yaml.Loader)
        return Movie(yaml_data)

    @staticmethod
    def from_imdb(imdb_data):
        """
        Factory method to create a Movie object from IMDB data
        """
        return Movie(imdb_data)

    def _to_google_event_core(self):
        return {
            "start": { "date": self.release_date.isoformat() },
            "end": { "date": (self.release_date + datetime.timedelta(days=1)).isoformat() },
            "summary": self.title,
        }

    def sort_val(self):
        return self.release_date

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        if isinstance(other, Movie):
            return self.title        == other.title       \
               and self.release_date == other.release_date
        event = self.to_google_event()
        return event["start"]["date"] == other["start"]["date"] \
           and event["end"]["date"]   == other["end"]["date"]   \
           and event["summary"]       == other["summary"]

    def __str__(self):
        return f"{truncate(self.title, 36)} {self.release_date.strftime('%b %d, %Y')}"


class Show(GoogleMediaEvent):
    """
    The event that describes a show start date and how many weeks it runs for
    """
    def __init__(self, data, season_num):
        super().__init__(data)
        self.season_num = season_num

    @property
    def title(self):
        """
        The title property
        """
        #return f"{self.data['title']} season {self.season_num}"
        return self.data['title']

    @property
    def start_date(self):
        """
        The season start date property
        """
        if 'start_date' in self.season:
            return self.season['start_date']
        if 'release dates' in self.season[1] and 'USA' in self.season[1]['release dates']:
            return self.season[1]['release dates']['USA']
        return None

    @property
    def weeks(self):
        """
        The property for number of weeks
        """
        if 'weeks' in self.season:
            return self.season['weeks']
        return len(self.season)

    @property
    def season(self):
        """
        The property of the season information
        """
        if 'seasons' in self.data and isinstance(self.data['seasons'], list):
            return find(self.data['seasons'], lambda s: s['num'] == self.season_num)
        if 'episodes' in self.data and isinstance(self.data['episodes'], dict):
            return self.data['episodes'][self.season_num]
        return None

    @staticmethod
    def from_yaml(yaml_path):
        """
        Factory method to create a Show object from yaml
        """
        with open(yaml_path, 'r', encoding='UTF-8') as yaml_file:
            yaml_data = yaml.load(yaml_file, Loader=yaml.Loader)
        return [Show(yaml_data, season['num']) for season in yaml_data['seasons']]

    @staticmethod
    def from_imdb(imdb_data):
        """
        Factory method to create a Show object from IMDB data
        """
        return [Show(imdb_data, season) for season in imdb_data['episodes'].keys()]

    def _rfc5545_weekday(self):
        _recurrence_weekday = [ "MO", "TU", "WE", "TH", "FR", "SA", "SU" ]
        return _recurrence_weekday[self.start_date.weekday()]

    def _to_google_event_core(self):
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
        if not super().__eq__(other):
            return False
        if isinstance(other, Show):
            return self.title      == other.title      \
               and self.start_date == other.start_date \
               and self.weeks      == other.weeks
        event = self.to_google_event()
        return event["summary"]       == other["summary"]       \
           and event["start"]["date"] == other["start"]["date"] \
           and event["end"]["date"]   == other["end"]["date"]   \
           and event["recurrence"]    == other["recurrence"]

    def __str__(self):
        return f"{truncate(self.title, 36)} {self.start_date.strftime('%b %d, %Y')}"
