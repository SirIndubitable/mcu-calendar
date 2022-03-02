"""
Pytests for yamlcalendar.py
"""
import os
from pathlib import Path

from mcu_calendar.yamlcalendar import YamlCalendar


def test_get_movies():
    movies = YamlCalendar._get_movies(Path("data") / "movies")
    assert len(movies) == len(os.listdir(os.path.join("data", "movies")))


def test_get_shows():
    shows = YamlCalendar._get_shows(Path("data") / "shows")
    assert len(shows) == len(os.listdir(os.path.join("data", "shows")))
