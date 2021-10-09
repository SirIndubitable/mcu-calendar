"""
Tests for Movie
"""
from datetime import date

from mcu_calendar.events import Movie


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
        'extendedProperties': { 'shared': {
            'tmdb_id': 'id'
        }},
    }
    assert movie.to_google_event() == expected_event
