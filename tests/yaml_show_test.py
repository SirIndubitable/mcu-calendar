"""
Tests for YamlShow
"""
from datetime import date
from os import listdir, path

from mcu_calendar.events import YamlShow
from pytest import mark


@mark.parametrize("show_path", listdir(path.join('data', 'shows')))
def test_shows_yaml(show_path):
    """
    Tests the types of properties from Yaml shows
    """
    show = YamlShow(path.join('data', 'shows', show_path))
    assert type(show.title)       is str
    assert type(show.description) is str
    assert type(show.tmdb_id)     is int
    for season in show.seasons:
        assert type(show.start_date(season)) is date
        assert type(show.weeks(season))      is int
        assert type(show.season_num(season)) is int
