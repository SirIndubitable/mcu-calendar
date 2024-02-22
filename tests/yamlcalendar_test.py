"""
Pytests for yamlcalendar.py
"""

# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=protected-access

from pathlib import Path
from typing import Any, Dict, List

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
