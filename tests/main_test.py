import pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/.."))
from mcu_calendar.main import *

def test_google_login():
    creds = get_google_creds()
    assert creds


def test_get_movies():
    movies = get_movies()
    assert len(movies) == len(os.listdir('data'))