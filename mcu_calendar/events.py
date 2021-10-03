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
        if 'id' in self.data:
            return f"https://www.imdb.com/title/{self.data['id']}"
        if 'imDbId' in self.data:
            return f"https://www.imdb.com/title/{self.data['imDbId']}"
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
        return True
        # if isinstance(other, GoogleMediaEvent):
        #     return self.description == other.description
        # return self.description == (other["description"] if "description" in other else "")

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
        if 'releaseDate' in self.data:
            return datetime.date.fromisoformat(self.data['releaseDate']) + datetime.timedelta(days=1)
        return None

    def to_yaml(self, yaml_path):
        """
        Serializes a Movie event into a yaml file
        """
        with open(yaml_path, 'w') as yaml_file:
            data = {
                'title':  self.title,
                "release_date": self.release_date,
                "description": self.description
            }
            yaml.dump(data, yaml_file)

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
            print("base not equal")
            return False
        if isinstance(other, Movie):
            return self.title        == other.title       \
               and self.release_date == other.release_date
        event = self.to_google_event()
        if event["summary"] != other["summary"]:
            print(f"{event['summary']} != {other['summary']}")
            return False
        if event["start"]["date"] != other["start"]["date"] \
        or event["end"]["date"]   != other["end"]["date"]:
            print(f"{event['start']['date']} != {other['start']['date']}")
            return False
        return True

    def __str__(self):
        return f"{truncate(self.title, 36)} {self.release_date.strftime('%b %d, %Y')}"


class Show(GoogleMediaEvent):
    """
    The event that describes a show start date and how many weeks it runs for
    """
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
        try:
            return Show._episode_release(self.data['episodes'][0])
        except TypeError:
            return None
        except ValueError:
            return None

    @staticmethod
    def _episode_release(episode):
        return datetime.datetime.strptime(episode['released'], "%d %b. %Y").date()

    @property
    def weeks(self):
        """
        The property for number of weeks
        """
        try:
            dates = [Show._episode_release(episode) for episode in self.data['episodes']]
            time_delta = max(dates) - min(dates)
            return (time_delta.days / 7) + 1
        except TypeError:
            return 0
        except ValueError:
            return 0

    def to_yaml(self, yaml_path):
        """
        Serializes a Show event into a yaml file
        """
        with open(yaml_path, 'w') as yaml_file:
            data = {
                'title':  self.title,
                "release_date": self.release_date,
                "description": self.description
            }
            yaml.dump(data, yaml_file)

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
        return Show(imdb_data)

    def _rfc5545_weekday(self):
        _recurrence_weekday = [ "MO", "TU", "WE", "TH", "FR", "SA", "SU" ]
        return _recurrence_weekday[self.start_date.weekday()]

    def _to_google_event_core(self):
        return {
            "summary": self.title,
            "start": { "date": self.start_date.isoformat() },
            "end": { "date": (self.start_date + datetime.timedelta(days=1)).isoformat() },
            "recurrence": [
                f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT={self.weeks:.0f};BYDAY={self._rfc5545_weekday()}"
            ],
        }

    def sort_val(self):
        return self.start_date

    def __eq__(self, other):
        if not super().__eq__(other):
            print("base not equal")
            return False
        if isinstance(other, Show):
            return self.title      == other.title      \
               and self.start_date == other.start_date \
               and self.weeks      == other.weeks
        event = self.to_google_event()
        if event["summary"] != other["summary"]:
            print(f"{event['summary']} != {other['summary']}")
            return False
        if event["start"]["date"] != other["start"]["date"] \
        or event["end"]["date"]   != other["end"]["date"]:
            print(f"{event['start']['date']} != {other['start']['date']}")
            return False
        if event["recurrence"] != other["recurrence"]:
            print(f"{event['recurrence']} != {other['recurrence']}")
            return False
        return True

    def __str__(self):
        return f"{truncate(self.title, 36)} {self.start_date.strftime('%b %d, %Y')}"
