"""
Pytests for events.py
"""

# pylint: disable=missing-function-docstring
# pylint: disable=unnecessary-negation
# pylint: disable=comparison-with-itself

import datetime
from pathlib import Path
from typing import Any, Dict

import pytest

from mcu_calendar.events import Movie, Show

all_movie_paths = [
    *(Path("data") / "mcu-movies").iterdir(),
    *(Path("data") / "mcu-adjacent-movies").iterdir(),
    *(Path("data") / "dceu-movies").iterdir(),
]


# ======================================
# Tests for events.Movie
# ======================================
@pytest.mark.parametrize("movie_path", all_movie_paths)
def test_movies_yaml(movie_path: Path) -> None:
    movie = Movie.from_yaml(movie_path)
    assert isinstance(movie.title, str)
    assert isinstance(movie.release_date, datetime.date)
    assert isinstance(movie.description, str)
    assert isinstance(movie.imdb_id, str)
    assert movie.imdb_id is not None


def test_movies_yaml_unique() -> None:
    all_movies = [Movie.from_yaml(f) for f in all_movie_paths]
    seen = set()
    for movie in all_movies:
        if movie.imdb_id not in seen:
            seen.add(movie.imdb_id)
            continue
        assert False, ", ".join([y.title for y in all_movies if y.imdb_id == movie.imdb_id])


def test_movies_equals() -> None:
    movie1 = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
        file_path=Path("data") / "mcu-movies" / "my-title.yaml",
    )
    movie2 = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
        file_path=Path("data") / "mcu-movies" / "my-title.yaml",
    )
    assert movie1 == movie1
    assert movie1 == movie2
    assert not movie1 != movie1
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
def test_movies_not_equals(movie_dict: Dict[str, Any]) -> None:
    movie1 = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
        file_path=Path("data") / "mcu-movies" / "my-title.yaml",
    )
    movie2 = Movie(**movie_dict, file_path=Path())
    assert movie1 != movie2
    assert not movie1 == movie2


def test_movie_event_equals() -> None:
    movie = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
        file_path=Path("data") / "mcu-movies" / "my-title.yaml",
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
            # Wrong Start Date
            "start": {"date": "2019-10-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "description": "stuff happens",
        },
        {
            # Wrong End Date
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-03-14"},
            "summary": "MY TITLE",
            "description": "stuff happens",
        },
        {
            # Wrong Summary
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "YOUR TITLE",
            "description": "stuff happens",
        },
        {
            # Wrong Description
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "description": "Something happens",
        },
        {
            # Missing Start
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "description": "stuff happens",
        },
        {
            # Missing End
            "start": {"date": "2019-04-20"},
            "summary": "MY TITLE",
            "description": "stuff happens",
        },
        {
            # Missing Start Date
            "start": {},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "description": "stuff happens",
        },
        {
            # Missing End Date
            "start": {"date": "2019-04-20"},
            "end": {},
            "summary": "MY TITLE",
            "description": "stuff happens",
        },
        {
            # Missing Summary
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "description": "stuff happens",
        },
        {
            # Missing Description
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
        },
    ],
)
def test_movie_event_not_equals(event_dict: Dict[str, Any]) -> None:
    movie = Movie(
        title="MY TITLE",
        release_date=datetime.date(2019, 4, 20),
        description="stuff happens",
        file_path=Path("data") / "mcu-movies" / "my-title.yaml",
    )
    assert movie != event_dict
    assert not movie == event_dict


# ======================================
# Tests for events.Show
# ======================================
@pytest.mark.parametrize(
    "show_path",
    [
        *(Path("data") / "mcu-shows").iterdir(),
        *(Path("data") / "starwars-shows").iterdir(),
    ],
)
def test_shows_yaml(show_path: Path) -> None:
    show = Show.from_yaml(show_path)
    assert isinstance(show.title, str)
    assert isinstance(show.release_dates, list)
    for date in show.release_dates:
        assert isinstance(date, datetime.date)
    assert isinstance(show.description, str)


def test_shows_equals() -> None:
    show1 = Show(
        title="MY TITLE",
        release_dates=[
            datetime.date(2019, 4, 20),
            datetime.date(2019, 4, 27),
            datetime.date(2019, 5, 4),
        ],
        description="Lots of stuff",
        file_path=Path("data") / "mcu-shows" / "my-title.yaml",
    )
    show2 = Show(
        title="MY TITLE",
        release_dates=[
            datetime.date(2019, 4, 20),
            datetime.date(2019, 4, 27),
            datetime.date(2019, 5, 4),
        ],
        description="Lots of stuff",
        file_path=Path("data") / "mcu-shows" / "my-title.yaml",
    )
    assert show1 == show1
    assert show1 == show2
    assert not show1 != show1
    assert not show1 != show2


@pytest.mark.parametrize(
    "show_dict",
    [
        {
            "title": "MY TITLE 2",
            "release_dates": [
                datetime.date(2019, 4, 20),
                datetime.date(2019, 4, 27),
                datetime.date(2019, 5, 4),
            ],
            "description": "Sometimes things happen",
        },
        {
            "title": "MY TITLE",
            "release_dates": [
                datetime.date(2019, 12, 25),
                datetime.date(2020, 1, 1),
                datetime.date(2020, 1, 8),
            ],
            "description": "Sometimes things happen",
        },
        {
            "title": "MY TITLE",
            "release_dates": [
                datetime.date(2019, 4, 20),
                datetime.date(2019, 4, 27),
                datetime.date(2019, 5, 4),
                datetime.date(2019, 5, 11),
                datetime.date(2019, 5, 18),
            ],
            "description": "Sometimes things happen",
        },
        {
            "title": "MY TITLE",
            "release_dates": [
                datetime.date(2019, 4, 20),
                datetime.date(2019, 4, 27),
                datetime.date(2019, 5, 4),
            ],
            "description": "Nothing ever happens",
        },
    ],
)
def test_shows_not_equals(show_dict: Dict[str, Any]) -> None:
    show1 = Show(
        title="MY TITLE",
        release_dates=[
            datetime.date(2019, 4, 20),
            datetime.date(2019, 4, 27),
            datetime.date(2019, 5, 4),
        ],
        description="Sometimes things happen",
        file_path=Path("data") / "mcu-shows" / "my-title.yaml",
    )
    show2 = Show(**show_dict, file_path=Path())
    assert not show1 == show2
    assert show1 != show2


def test_show_event_equals() -> None:
    show = Show(
        title="MY TITLE",
        release_dates=[
            datetime.date(2019, 4, 20),
            datetime.date(2019, 4, 27),
            datetime.date(2019, 5, 4),
            datetime.date(2019, 5, 11),
            datetime.date(2019, 5, 18),
        ],
        description="Sometimes things happen",
        file_path=Path("data") / "mcu-shows" / "my-title.yaml",
    )
    event = {
        "start": {"date": "2019-04-20"},
        "end": {"date": "2019-04-21"},
        "summary": "MY TITLE",
        "recurrence": ["RRULE:FREQ=WEEKLY;WKST=SU;COUNT=5;BYDAY=SA"],
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
            # Wrong Start Date
            "start": {"date": "2019-10-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            # Wrong End Date
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-03-14"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            # Wrong Summary
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "YOUR TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            # Wrong Recurrence
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=10;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            # Wrong Description
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Nothing ever happens",
        },
        {
            # Missing Start
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            # Missing End
            "start": {"date": "2019-04-20"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            # Missing Start Date
            "start": {},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            # Missing End Date
            "start": {"date": "2019-04-20"},
            "end": {},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            # Missing Summary
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
            "description": "Sometimes things happen",
        },
        {
            # Missing Recurrence
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "description": "Sometimes things happen",
        },
        {
            # Missing Description
            "start": {"date": "2019-04-20"},
            "end": {"date": "2019-04-21"},
            "summary": "MY TITLE",
            "recurrence": "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=6;BYDAY=SA",
        },
    ],
)
def test_show_event_not_equals(event_dict: Dict[str, Any]) -> None:
    show = Show(
        title="MY TITLE",
        release_dates=[
            datetime.date(2019, 4, 20),
            datetime.date(2019, 4, 27),
            datetime.date(2019, 5, 4),
            datetime.date(2019, 5, 11),
            datetime.date(2019, 5, 18),
            datetime.date(2019, 5, 25),
        ],
        description="Sometimes things happen",
        file_path=Path("data") / "mcu-shows" / "my-title.yaml",
    )
    assert not show == event_dict
    assert show != event_dict


@pytest.mark.parametrize(
    ("event", "recurrence"),
    [
        (
            {
                "title": "TITLE",
                "release_dates": [
                    datetime.date(2019, 4, 20),
                    datetime.date(2019, 4, 27),
                    datetime.date(2019, 5, 4),
                ],
                "description": "Sometimes things happen",
            },
            "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=3;BYDAY=SA",
        ),
        (
            {
                "title": "TITLE",
                "release_dates": [
                    datetime.date(2019, 4, 20),
                    datetime.date(2019, 4, 21),
                    datetime.date(2019, 4, 22),
                ],
                "description": "Sometimes things happen",
            },
            "RRULE:FREQ=DAILY;COUNT=3",
        ),
        (
            {
                "title": "TITLE",
                "release_dates": [
                    datetime.date(2019, 4, 20),
                    datetime.date(2019, 4, 21),
                    datetime.date(2019, 4, 27),
                ],
                "description": "Sometimes things happen",
            },
            None,
        ),
        (
            {
                "title": "TITLE 2",
                "release_dates": [
                    datetime.date(2019, 4, 20),
                ],
                "description": "Sometimes things happen",
            },
            None,
        ),
    ],
)
def test_show_recurrence(event: Dict[str, Any], recurrence: str) -> None:
    show = Show(**event, file_path=Path())
    google_event = show.to_google_event()
    if recurrence is None:
        assert google_event["recurrence"] is None
    else:
        assert google_event["recurrence"][0] == recurrence
