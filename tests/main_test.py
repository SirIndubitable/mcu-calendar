import pytest
import datetime
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../mcu_calendar"))
from main import *


def test_get_movies():
    movies = get_movies()
    assert len(movies) == len(os.listdir(os.path.join('data', 'movies')))


def test_get_shows():
    shows = get_shows()
    assert len(shows) == len(os.listdir(os.path.join('data', 'shows')))
