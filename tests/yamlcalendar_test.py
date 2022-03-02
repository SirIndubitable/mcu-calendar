"""
Pytests for yamlcalendar.py
"""
from pathlib import Path

from mcu_calendar.events import GoogleMediaEvent
from mcu_calendar.yamlcalendar import YamlCalendar


class MockExecutor:
    def execute(self, *_, **__):
        pass


class MockService:
    def __init__(self):
        self.insert_kwargs = []
        self.update_kwargs = []

    def insert(self, **kwargs):
        self.insert_kwargs.append(kwargs)
        return MockExecutor()

    def update(self, **kwargs):
        self.update_kwargs.append(kwargs)
        return MockExecutor()


class MockEvent(GoogleMediaEvent):
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description

    def sort_val(self):
        return self.title

    def to_google_event(self):
        return self.title


def test_get_movies():
    path = Path("data") / "mcu-movies"
    movies = YamlCalendar._get_movies(path)
    assert len(movies) == len([p for p in path.iterdir()])


def test_get_shows():
    path = Path("data") / "mcu-shows"
    shows = YamlCalendar._get_shows(path)
    assert len(shows) == len([p for p in path.iterdir()])


def test_create_google_event_add():
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
    assert service.insert_kwargs[0]["body"] == "Test Movie"


def test_create_google_event_update():
    service = MockService()
    cal = YamlCalendar("Test", "uuid", [], [], service)
    cal._create_google_event(
        progress_title="Test...",
        items=[MockEvent("Test Movie", "Movie Description")],
        existing_events=[
            {"summary": "Test Movie", "description": "Bad Description", "id": ""}
        ],
        force=False,
    )
    assert len(service.insert_kwargs) == 0
    assert len(service.update_kwargs) == 1
    assert service.update_kwargs[0]["body"] == "Test Movie"


def test_create_google_event_skip():
    service = MockService()
    cal = YamlCalendar("Test", "uuid", [], [], service)
    cal._create_google_event(
        progress_title="Test...",
        items=[MockEvent("Test Movie", "Movie Description")],
        existing_events=[
            {"summary": "Test Movie", "description": "Movie Description", "id": ""}
        ],
        force=False,
    )
    assert len(service.insert_kwargs) == 0
    assert len(service.update_kwargs) == 0


def test_create_google_event_skip_force():
    service = MockService()
    cal = YamlCalendar("Test", "uuid", [], [], service)
    cal._create_google_event(
        progress_title="Test...",
        items=[MockEvent("Test Movie", "Movie Description")],
        existing_events=[
            {"summary": "Test Movie", "description": "Movie Description", "id": ""}
        ],
        force=True,
    )
    assert len(service.insert_kwargs) == 0
    assert len(service.update_kwargs) == 1
    assert service.update_kwargs[0]["body"] == "Test Movie"
