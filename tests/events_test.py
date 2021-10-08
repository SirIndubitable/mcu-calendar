"""
Tests for all events
"""
from datetime import date
import os
import pytest
from mcu_calendar.events import *
from mcu_calendar.events import _rfc5545_weekday

class MockMovie(Movie):
    """
    Test movie event
    """
    def __init__(self, description='desc', title='title', release_date=date(2019, 4, 20), tmdb_id='id'):
        self._description = description
        self._title = title
        self._release_date = release_date
        self._tmdb_id = tmdb_id

    @property
    def description(self):
        return self._description

    @property
    def title(self):
        return self._title

    @property
    def release_date(self):
        return self._release_date

    @property
    def tmdb_id(self):
        return self._tmdb_id

class MockShow(Show):
    """
    Test show event
    """
    def __init__(self, description='desc', title='title', num_seasons=2, tmdb_id='id'):
        self._description = description
        self._title = title
        self._seasons = range(1, num_seasons + 1)
        self._tmdb_id = tmdb_id

    @property
    def description(self):
        return self._description

    @property
    def title(self):
        return self._title

    @property
    def seasons(self):
        return self._seasons

    @property
    def tmdb_id(self):
        return self._tmdb_id

    def season_num(self, season):
        return season

    def start_date(self, season):
        return date(2010 + season, 10, 28)

    def weeks(self, season):
        return 10 + season


def test_movie_to_google_event():
    """
    Tests the google event api object returned from movie classes
    """
    movie = MockMovie()
    expected_event = {
        "description": 'desc',
        "transparency": "transparent", # "transparent" means "Show me as Available"
        "start": { "date": '2019-04-20' },
        "end": { "date": '2019-04-21' },
        "summary": 'title',
        'extendedProperties.shared': {
            'tmdb_id': 'id'
        },
    }
    assert movie.to_google_event() == expected_event


@pytest.mark.parametrize("movie_path", os.listdir(os.path.join('data', 'movies')))
def test_yamlmovie_constructor(movie_path):
    """
    Tests the constructor of yaml movies, and also validates the yaml files
    """
    movie = YamlMovie(os.path.join('data', 'movies', movie_path))
    assert type(movie.title)        is str
    assert type(movie.release_date) is date
    assert type(movie.description)  is str


def test_show_to_google_event():
    """
    Tests the google event api object returned from show classes
    """
    show = MockShow(num_seasons=2)
    event_objects = show.to_google_event()
    event_objects.sort(key=lambda e: e['summary'])
    for i in range(1, 3):
        start_date = date(2010 + i, 10, 28)
        expected_event = {
            "description": 'desc',
            "transparency": "transparent", # "transparent" means "Show me as Available"
            "summary": f"title Season {i}",
            "start": { "date": f"201{i}-10-28" },
            "end": { "date": f"201{i}-10-29" },
            "recurrence": [
                f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT=1{i};BYDAY={_rfc5545_weekday(start_date)}"
            ],
            'extendedProperties': { 'shared': {
                'tmdb_id': 'id'
            }}
        }
        assert event_objects[i-1] == expected_event


@pytest.mark.parametrize("show_path", os.listdir(os.path.join('data', 'shows')))
def test_shows_yaml(show_path):
    """
    Tests the types of properties from Yaml shows
    """
    show = YamlShow(os.path.join('data', 'shows', show_path))
    assert type(show.title)       is str
    assert type(show.description) is str
    assert type(show.tmdb_id)     is int
    for season in show.seasons:
        assert type(show.start_date(season)) is date
        assert type(show.weeks(season))      is int
        assert type(show.season_num(season)) is int


@pytest.mark.parametrize("day, rfc5545", [
    (date(2021, 10, 4), "MO"),
    (date(2021, 10, 5), "TU"),
    (date(2021, 10, 6), "WE"),
    (date(2021, 10, 7), "TH"),
    (date(2021, 10, 8), "FR"),
    (date(2021, 10, 9), "SA"),
    (date(2021, 10, 10), "SU"),
])
def test_rfc5545_weekday(day, rfc5545):
    """
    Tests the helper method to get the rfc5545 weekday string
    """
    return _rfc5545_weekday(day) == rfc5545