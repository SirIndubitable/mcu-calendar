import os
import sys
from pathlib import Path

mcu_path = Path(__file__).parent.parent / "mcu_calendar"
sys.path.append(str(mcu_path))

from yamlcalendar import YamlCalendar, find  # noqa: E402


def test_get_movies():
    movies = YamlCalendar._get_movies(Path("data") / "movies")
    assert len(movies) == len(os.listdir(os.path.join("data", "movies")))


def test_get_shows():
    shows = YamlCalendar._get_shows(Path("data") / "shows")
    assert len(shows) == len(os.listdir(os.path.join("data", "shows")))


def test_find():
    fruits = ["apples", "oranges", "bananas", "mangoes", "grapes", "strawberry"]
    assert "bananas" == find(fruits, lambda e: e.count("n") > 1)
    assert "oranges" == find(fruits, lambda e: "r" in e)
