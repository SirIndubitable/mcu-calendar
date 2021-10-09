"""
Tests for all events
"""
from datetime import date, datetime, timedelta

from mcu_calendar.events import TmdbMovie


class MockTmdbData:
    """
    Mock data representing Tmdb reponse object
    """
    def __init__(self, description='desc', title='title', release_date=date(2019, 4, 20), tmdb_id='id'):
        self.__setattr__('overview', description)
        self.__setattr__('title', title)
        self.__setattr__('release_date', release_date.isoformat())
        self.__setattr__('id', tmdb_id)


def test_tmdbmovie_constructor():
    """
    Tests the constructor of yaml movies, and also validates the yaml files
    """
    movie = TmdbMovie(MockTmdbData())
    assert type(movie.title)        is str
    assert type(movie.release_date) is date
    assert type(movie.description)  is str
    assert type(movie.tmdb_id)      is str


def test_tmdbmovie_description_not_released():
    release = datetime.now().date() + timedelta(days=1)
    movie = TmdbMovie(MockTmdbData(release_date=release))
    assert movie.description == "https://www.themoviedb.org/tv/id"


def test_tmdbmovie_description_just_released():
    release = datetime.now().date() - timedelta(days=6)
    movie = TmdbMovie(MockTmdbData(release_date=release))
    assert movie.description == "https://www.themoviedb.org/tv/id"


def test_tmdbmovie_description_released_week_ago():
    release = datetime.now().date() - timedelta(days=7)
    movie = TmdbMovie(MockTmdbData(release_date=release))
    assert movie.description == "desc\n\nhttps://www.themoviedb.org/tv/id"
