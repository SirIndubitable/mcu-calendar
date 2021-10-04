"""
Google Event objects that represent different media release events
"""
import datetime
import yaml

def _rfc5545_weekday(date):
    _recurrence_weekday = [ "MO", "TU", "WE", "TH", "FR", "SA", "SU" ]
    return _recurrence_weekday[date.weekday()]

class Movie():
    """
    The event that describes a movie release date
    """
    def __init__(self, data):
        self.data = data

    @property
    def description(self):
        """
        The description property
        """
        return self.data['description']

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
        return self.data['release_date']

    @staticmethod
    def from_yaml(yaml_path):
        """
        Factory method to create a Movie object from yaml
        """
        with open(yaml_path, 'r', encoding='UTF-8') as yaml_file:
            yaml_data = yaml.load(yaml_file, Loader=yaml.Loader)
        return Movie(yaml_data)

    def to_google_event(self):
        """
        Converts this object to a google calendar api event
        https://developers.google.com/calendar/v3/reference/events#resource
        """
        return  {
            "description": self.description,
            "transparency": "transparent", # "transparent" means "Show me as Available"
            "start": { "date": self.release_date.isoformat() },
            "end": { "date": (self.release_date + datetime.timedelta(days=1)).isoformat() },
            "summary": self.title,
        }


class Show():
    """
    The event that describes a show start date and how many weeks it runs for
    """
    def __init__(self, data):
        self.data = data

    @property
    def description(self):
        """
        The description property
        """
        return self.data['description']

    @property
    def title(self):
        """
        The title property
        """
        return self.data['title']

    def start_date(self, season):
        """
        The season start date
        """
        return self.data['seasons'][season]['start_date']

    def weeks(self, season):
        """
        The property for number of weeks
        """
        return self.data['seasons'][season]['weeks']

    @staticmethod
    def from_yaml(yaml_path):
        """
        Factory method to create a Show object from yaml
        """
        with open(yaml_path, 'r', encoding='UTF-8') as yaml_file:
            yaml_data = yaml.load(yaml_file, Loader=yaml.Loader)
        return Show(yaml_data)

    def to_yaml(self, yaml_path):
        """
        Factory method to create a Show object from yaml
        """
        with open(yaml_path, 'w') as yaml_file:
            yaml.dump(self.data, yaml_file, Loader=yaml.Dumper)

    def to_google_event(self):
        """
        Converts this object to a google calendar api event
        https://developers.google.com/calendar/v3/reference/events#resource
        """
        events = []
        for season in range(len(self.data['seasons'])):
            start_date = self.start_date(season)
            events.append({
                "description": self.description,
                "transparency": "transparent", # "transparent" means "Show me as Available"
                "summary": f"{self.title} Season {season + 1}",
                "start": { "date": start_date.isoformat() },
                "end": { "date": (start_date + datetime.timedelta(days=1)).isoformat() },
                "recurrence": [
                    f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT={self.weeks(season):.0f};BYDAY={_rfc5545_weekday(start_date)}"
                ],
            })
        return events
