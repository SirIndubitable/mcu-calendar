import pytest
import datetime
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../mcu_calendar"))
import imdb_helper


def test_IMDB():
    assert imdb_helper.__IMDB__ is not None


def test_fix_movie_release_date():
    data = {
        'release dates': [
            "USA::16 August 2021",
            "USA::19 September 3000     (Super Remastered)",
            "France::20 August 2022"
        ]
    }
    imdb_helper._fix_movie_release_date(data)
    assert len(data['release dates']) is 2
    assert data['release dates']['USA'] == datetime.date(2021, 8, 16)
    assert data['release dates']['France'] == datetime.date(2022, 8, 20)