import pytest
import datetime
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/.."))
from mcu_calendar.main import *

def test_google_login():
    creds = get_google_creds()
    assert creds


def test_get_movies():
    movies = get_movies()
    assert len(movies) == len(os.listdir(os.path.join('data', 'movies')))


@pytest.mark.parametrize("movie_path", os.listdir(os.path.join('data', 'movies')))
def test_movies_yaml(movie_path):
    movie = Movie(os.path.join('data', 'movies', movie_path))
    assert type(movie.title)        is str
    assert type(movie.release_date) is datetime.date
    assert type(movie.description)  is str


def test_movies_equals():
    movie1 = Movie({ "title": "MY TITLE", "release_date": datetime.date(2019, 4, 20), "description": "stuff happens"})
    movie2 = Movie({ "title": "MY TITLE", "release_date": datetime.date(2019, 4, 20), "description": "stuff happens"})
    assert movie1 == movie1
    assert movie1 == movie2


@pytest.mark.parametrize("movie_dict", [ 
    { "title": "MY TITLE 2", "release_date": datetime.date(2019, 4, 20), "description": "stuff happens"},
    { "title": "MY TITLE", "release_date": datetime.date(2019, 12, 25), "description": "stuff happens"},
    { "title": "MY TITLE", "release_date": datetime.date(2019, 4, 20), "description": "nothing happens"},
])
def test_movies_not_equals(movie_dict):
    movie1 = Movie({ "title": "MY TITLE", "release_date": datetime.date(2019, 4, 20), "description": "stuff happens"})
    movie2 = Movie(movie_dict)
    assert not movie1 == movie2


def test_movie_event_equals():
    movie = Movie({ "title": "MY TITLE", "release_date": datetime.date(2019, 4, 20), "description": "stuff happens"})
    event = {
        "start": { "date": "2019-04-20" },
        "end": { "date": "2019-04-20" },
        "summary": "MY TITLE",
        "description": "stuff happens",
    }
    assert movie == event
    assert event == movie


@pytest.mark.parametrize("event_dict", [ 
    { "start": { "date": "2019-10-20" }, "end": { "date": "2019-04-20" }, "summary": "MY TITLE", "description": "stuff happens" },
    { "start": { "date": "2019-04-20" }, "end": { "date": "2019-03-14" }, "summary": "MY TITLE", "description": "stuff happens" },
    { "start": { "date": "2019-04-20" }, "end": { "date": "2019-04-20" }, "summary": "YOUR TITLE", "description": "stuff happens" },
    { "start": { "date": "2019-04-20" }, "end": { "date": "2019-04-20" }, "summary": "MY TITLE", "description": "Something happens" },
])
def test_movie_event_not_equals(event_dict):
    movie = Movie({ "title": "MY TITLE", "release_date": datetime.date(2019, 4, 20), "description": "stuff happens"})
    assert not movie == event_dict
