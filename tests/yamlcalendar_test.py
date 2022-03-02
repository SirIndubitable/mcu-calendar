"""
Pytests for yamlcalendar.py
"""
from pathlib import Path

from mcu_calendar.yamlcalendar import YamlCalendar


def test_get_movies():
    path = Path("data") / "movies"
    movies = YamlCalendar._get_movies(path)
    assert len(movies) == len([p for p in path.iterdir()])


def test_get_shows():
    path = Path("data") / "shows"
    shows = YamlCalendar._get_shows(path)
    assert len(shows) == len([p for p in path.iterdir()])
