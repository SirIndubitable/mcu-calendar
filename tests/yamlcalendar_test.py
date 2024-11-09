"""
Pytests for yamlcalendar.py
"""

# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=protected-access

import re
from pathlib import Path
from typing import Any, Dict, List

import yaml

from mcu_calendar.events import GoogleMediaEvent
from mcu_calendar.yamlcalendar import YamlCalendar


class MockExecutor:  # pylint: disable=too-few-public-methods
    def execute(self, *_: Any, **__: Any) -> None:
        pass


class MockService:
    def __init__(self) -> None:
        self.insert_kwargs: List[Dict] = []
        self.update_kwargs: List[Dict] = []

    def insert(self, **kwargs: Any) -> MockExecutor:
        self.insert_kwargs.append(kwargs)
        return MockExecutor()

    def update(self, **kwargs: Any) -> MockExecutor:
        self.update_kwargs.append(kwargs)
        return MockExecutor()


class MockEvent(GoogleMediaEvent):
    def _to_google_event_core(self) -> Dict[str, Any]:
        return {}

    def sort_val(self) -> str:
        return self.title


def test_get_movies() -> None:
    path = Path("data") / "mcu-movies"
    movies = YamlCalendar._get_movies(path)
    assert len(movies) == len(list(path.iterdir()))


def test_get_shows() -> None:
    path = Path("data") / "mcu-shows"
    shows = YamlCalendar._get_shows(path)
    assert len(shows) == len(list(path.iterdir()))


def test_create_google_event_add() -> None:
    service = MockService()
    cal = YamlCalendar("Test", "uuid", [], [], service)
    cal._create_google_event(
        progress_title="Test...",
        items=[MockEvent("Test Movie", "Movie Description")],
        existing_events=[],
        force=False,
    )
    assert len(service.insert_kwargs) == 1
    assert len(service.update_kwargs) == 0
    assert service.insert_kwargs[0]["body"]["summary"] == "Test Movie"
    assert service.insert_kwargs[0]["body"]["description"] == "Movie Description"


def test_create_google_event_update() -> None:
    service = MockService()
    cal = YamlCalendar("Test", "uuid", [], [], service)
    cal._create_google_event(
        progress_title="Test...",
        items=[MockEvent("Test Movie", "Movie Description")],
        existing_events=[{"summary": "Test Movie", "description": "Bad Description", "id": ""}],
        force=False,
    )
    assert len(service.insert_kwargs) == 0
    assert len(service.update_kwargs) == 1
    assert service.update_kwargs[0]["body"]["summary"] == "Test Movie"
    assert service.update_kwargs[0]["body"]["description"] == "Movie Description"


def test_create_google_event_skip() -> None:
    service = MockService()
    cal = YamlCalendar("Test", "uuid", [], [], service)
    cal._create_google_event(
        progress_title="Test...",
        items=[MockEvent("Test Movie", "Movie Description")],
        existing_events=[{"summary": "Test Movie", "description": "Movie Description", "id": ""}],
        force=False,
    )
    assert len(service.insert_kwargs) == 0
    assert len(service.update_kwargs) == 0


def test_create_google_event_skip_force() -> None:
    service = MockService()
    cal = YamlCalendar("Test", "uuid", [], [], service)
    cal._create_google_event(
        progress_title="Test...",
        items=[MockEvent("Test Movie", "Movie Description")],
        existing_events=[{"summary": "Test Movie", "description": "Movie Description", "id": ""}],
        force=True,
    )
    assert len(service.insert_kwargs) == 0
    assert len(service.update_kwargs) == 1
    assert service.update_kwargs[0]["body"]["summary"] == "Test Movie"
    assert service.update_kwargs[0]["body"]["description"] == "Movie Description"


def test_no_duplicate_ids() -> None:
    all_yaml = []
    for folder in Path("data").iterdir():
        if not folder.is_dir():
            continue

        if not str(folder).endswith("movies"):
            continue

        for file in folder.iterdir():
            if file.suffix != ".yaml":
                continue

            with open(file, "r", encoding="UTF-8") as yaml_file:
                data = yaml.safe_load(yaml_file)
                if "imdb_id" not in data:
                    matches = re.search("https://www.imdb.com/title/(.*)", data["description"])
                    if matches:
                        data["imdb_id"] = matches.group(1)
                all_yaml.append(data)

    seen = set()
    for data in all_yaml:
        if data["imdb_id"] not in seen:
            seen.add(data["imdb_id"])
            continue

        assert False, ", ".join([y["title"] for y in all_yaml if y["imdb_id"] == data["imdb_id"]])
