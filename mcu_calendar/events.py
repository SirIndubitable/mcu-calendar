"""
Google Event objects that represent different media release events
"""
from abc import ABC, abstractmethod
from datetime import date, timedelta, datetime
from yaml import load, dump, Loader, Dumper

def _rfc5545_weekday(date_to_convert):
    _recurrence_weekday = [ "MO", "TU", "WE", "TH", "FR", "SA", "SU" ]
    return _recurrence_weekday[date_to_convert.weekday()]

class Movie(ABC):
    """
    The event that describes a movie release date
    """
    @property
    @abstractmethod
    def description(self):
        """
        The description property
        """

    @property
    @abstractmethod
    def title(self):
        """
        The title property
        """

    @property
    @abstractmethod
    def release_date(self):
        """
        The original release date property
        """

    @property
    @abstractmethod
    def tmdb_id(self):
        """
        The id of this movie from themoviedb.org
        """

    def to_google_event(self):
        """
        Converts this object to a google calendar api event
        https://developers.google.com/calendar/v3/reference/events#resource
        """
        return  {
            "description": self.description,
            "transparency": "transparent", # "transparent" means "Show me as Available"
            "start": { "date": self.release_date.isoformat() },
            "end": { "date": (self.release_date + timedelta(days=1)).isoformat() },
            "summary": self.title,
            'extendedProperties': { 'shared': {
                'tmdb_id': str(self.tmdb_id)
            }},
        }


class TmdbMovie(Movie):
    """
    The event that describes a movie release date, backed with the result
    of a TMDB query
    """
    def __init__(self, data):
        self.tmdb = data

    @property
    def description(self):
        if self.release_date <= (datetime.now().date() - timedelta(days=7)):
            descr = self.tmdb.overview
            descr += "\n\n"
        else:
            descr = ""
        descr += f"https://www.themoviedb.org/tv/{self.tmdb.id}"
        return descr

    @property
    def title(self):
        return self.tmdb.title

    @property
    def release_date(self):
        return date.fromisoformat(self.tmdb.release_date)

    @property
    def tmdb_id(self):
        return self.tmdb.id


class YamlMovie(Movie):
    """
    The event that describes a movie release date, backed by the information
    of a yaml file
    """
    def __init__(self, yaml_path):
        with open(yaml_path, 'r', encoding="utf-8") as yaml_file:
            yaml_data = load(yaml_file, Loader=Loader)
        self.data = yaml_data

    @property
    def description(self):
        return self.data['description']

    @property
    def title(self):
        return self.data['title']

    @property
    def release_date(self):
        return self.data['release_date']

    @property
    def tmdb_id(self):
        return self.data['tmdb_id']


class Show(ABC):
    """
    The event that describes a show start date and how many weeks it runs for
    """
    @property
    @abstractmethod
    def description(self):
        """
        The description property
        """

    @property
    @abstractmethod
    def title(self):
        """
        The title property
        """

    @property
    @abstractmethod
    def seasons(self):
        """
        List of season objects
        """

    @abstractmethod
    def season_num(self, season):
        """
        Gets the season number of the given season
        """

    @abstractmethod
    def start_date(self, season):
        """
        Gets the start date of the given season
        """

    @abstractmethod
    def weeks(self, season):
        """
        Gets the number of weeks of the given season
        """

    @property
    @abstractmethod
    def tmdb_id(self):
        """
        The id of this show from themoviedb.org
        """

    def to_google_event(self):
        """
        Converts this object to a google calendar api event
        https://developers.google.com/calendar/v3/reference/events#resource
        """
        events = []
        for season in self.seasons:
            start_date = self.start_date(season)
            season_num = self.season_num(season)
            weekday = _rfc5545_weekday(start_date)
            events.append({
                "description": self.description,
                "transparency": "transparent", # "transparent" means "Show me as Available"
                "summary": f"{self.title} Season {season_num}",
                "start": { "date": start_date.isoformat() },
                "end": { "date": (start_date + timedelta(days=1)).isoformat() },
                "recurrence": [
                    f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT={self.weeks(season):.0f};BYDAY={weekday}"
                ],
                'extendedProperties': { 'shared': {
                    'tmdb_id': str(self.tmdb_id),
                    'season_number': str(season_num),
                }},
            })
        return events

class TmdbShow(Show):
    """
    The event that describes a tv show with any number of seasons, backed with the result
    of a TMDB query
    """
    def __init__(self, data):
        self.tmdb = data

    @property
    def description(self):
        descr = self.tmdb.overview
        descr += "\n\nhttps://www.themoviedb.org/tv/{self.tmdb.id}"
        if self.tmdb.external_ids.imdb_id:
            descr += f"\nhttps://www.imdb.com/title/{self.tmdb.external_ids.imdb_id}"
        return descr

    @property
    def title(self):
        return self.tmdb.name

    @property
    def seasons(self):
        return self.tmdb.seasons

    @property
    def tmdb_id(self):
        return self.tmdb.id

    def season_num(self, season):
        return season.season_number

    def start_date(self, season):
        return date.fromisoformat(season.air_date)

    def weeks(self, season):
        return season.episode_count


class YamlShow(Show):
    """
    The event that describes a tv show with any number of seasons, backed by the information
    of a yaml file
    """
    def __init__(self, yaml_path):
        with open(yaml_path, 'r', encoding="utf-8") as yaml_file:
            yaml_data = load(yaml_file, Loader=Loader)
        self.data = yaml_data

    @property
    def description(self):
        return self.data['description']

    @property
    def title(self):
        return self.data['title']

    @property
    def seasons(self):
        return self.data['seasons']

    @property
    def tmdb_id(self):
        return self.data['tmdb_id']

    def season_num(self, season):
        return season['num']

    def start_date(self, season):
        return season['start_date']
        # if isinstance(date, datetime.date):
        #     return date
        # return datetime.date.fromisoformat(date)

    def weeks(self, season):
        return season['weeks']

    def to_yaml(self, yaml_path):
        """
        Dumps this Show object into a yaml file
        """
        with open(yaml_path, 'w', encoding="utf-8") as yaml_file:
            dump(self.data, yaml_file, Loader=Dumper)
