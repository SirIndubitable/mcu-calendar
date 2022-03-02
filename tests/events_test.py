"""
Pytests for events.py
"""
import datetime
from pathlib import Path

import pytest

from mcu_calendar.events import Movie, Show


# ======================================
# Tests for events.Movie
# ======================================
@pytest.mark.parametrize("movie_path", (Path("data") / "mcu-movies").iterdir())
def test_movies_yaml(movie_path: Path):
    movie = Movie.from_yaml(movie_path)
    assert isinstance(movie.title, str)
    assert isinstance(movie.release_date, datetime.date)
    assert isinstance(movie.description, str)


def test_movies_equals():
    movie1 = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
    )
    movie2 = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
    )
    assert movie1 == movie1  # pylint: disable=comparison-with-itself
    assert movie1 == movie2
    assert not movie1 != movie1  # pylint: disable=comparison-with-itself
    assert not movie1 != movie2


@pytest.mark.parametrize(
    "movie_dict",
    [
        {
            "title": "MY TITLE 2",
            "release_date": datetime.date(2019, 4, 20),
            "description": "stuff happens",
        },
        {
            "title": "MY TITLE",
            "release_date": datetime.date(2019, 12, 25),
            "description": "stuff happens",
        },
        {
            "title": "MY TITLE",
            "release_date": datetime.date(2019, 4, 20),
            "description": "nothing happens",
        },
    ],
)
def test_movies_not_equals(movie_dict):
    movie1 = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
    )
    movie2 = Movie(**movie_dict)
    assert movie1 != movie2
    assert not movie1 == movie2


def test_movie_event_equals():
    movie = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
    )
    event = {
        "start": {"date": "2019-04-20"},
        "end": {"date": "2019-04-21"},
        "summary": "MY TITLE",
        "description": "stuff happens",
    }
    assert movie == event
    assert event == movie
    assert not movie != event
    assert not event != movie


@pytest.mark.parametrize(
    "event_dict",
    [
        {
            "start": {"date": "2019-10-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "description": "stuff happens",
        },
        {
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-03-14"},
            "summary": "MY TITLE",
            "description": "stuff happens",
        },
        {
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "YOUR TITLE",
            "description": "stuff happens",
        },
        {
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "description": "Something happens",
        },
    ],
)
def test_movie_event_not_equals(event_dict):
    movie = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
    )
    assert movie != event_dict
    assert not movie == event_dict


# ======================================
# Tests for events.Show
# ======================================
@pytest.mark.parametrize("show_path", (Path("data") / "mcu-shows").iterdir())
def test_shows_yaml(show_path: Path):
    show = Show.from_yaml(show_path)
    assert isinstance(show.title, str)
    assert isinstance(show.start_date, datetime.date)
    assert isinstance(show.weeks, int)
    assert isinstance(show.description, str)


def test_shows_equals():
    show1 = Show(
        title="MY TITLE",
        start_date=datetime.date(2019, 4, 20),
        weeks=7,
        description="Lots of stuff",
    )
    show2 = Show(
        title="MY TITLE",
        start_date=datetime.date(2019, 4, 20),
        weeks=7,
        description="Lots of stuff",
    )
    assert show1 == show1  # pylint: disable=comparison-with-itself
    assert show1 == show2
    assert not show1 != show1  # pylint: disable=comparison-with-itself
    assert not show1 != show2


@pytest.mark.parametrize(
    "show_dict",
    [
        {
            "title": "MY TITLE 2",
            "start_date": datetime.date(2019, 4, 20),
            "weeks": 3,
            "description": "Sometimes things happen",
        },
        {
            "title": "MY TITLE",
            "start_date": datetime.date(2019, 12, 25),
            "weeks": 3,
            "description": "Sometimes things happen",
        },
        {
            "title": "MY TITLE",
            "start_date": datetime.date(2019, 4, 20),
            "weeks": 9,
            "description": "Sometimes things happen",
        },
        {
            "title": "MY TITLE",
            "start_date": datetime.date(2019, 4, 20),
            "weeks": 9,
            "description": "Nothing ever happens",
        },
    ],
)
def test_shows_not_equals(show_dict):
    show1 = Show(
        title="MY TITLE",
        start_date=datetime.date(2019, 4, 20),
        weeks=3,
        description="Sometimes things happen",
    )
    show2 = Show(**show_dict)
    assert not show1 == show2
    assert show1 != show2


def test_show_event_equals():
    show = Show(
        title="MY TITLE",
        start_date=datetime.date(2019, 4, 20),
        weeks=20,
        description="Sometimes things happen",
    )
    event = {
        "start": {"date": "2019-04-20"},
        "end": {"date": "2019-04-21"},
        "summary": "MY TITLE",
        "recurrence": ["RRULE:FREQ=WEEKLY;WKST=SU;COUNT=20;BYDAY=SA"],
        "description": "Sometimes things happen",
    }
    assert show == event
    assert event == show
    assert not show != event
    assert not event != show


@pytest.mark.parametrize(
    "event_dict",
    [
        {
            "start": {"date": "2019-10-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-03-14"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "YOUR TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=10;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Nothing ever happens",
        },
    ],
)
def test_show_event_not_equals(event_dict):
    show = Show(
        title="MY TITLE",
        start_date=datetime.date(2019, 4, 20),
        weeks=6,
        description="Sometimes things happen",
    )
    assert not show == event_dict
    assert show != event_dict
