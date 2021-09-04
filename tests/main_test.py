import os
import pytest
from mcu_calendar.main import *

def test_get_movies():
    movies = get_yaml_movies()
    assert len(movies) == len(os.listdir(os.path.join('data', 'movies')))


def test_get_shows():
    shows = get_yaml_shows()
    assert len(shows) == len(os.listdir(os.path.join('data', 'shows')))


def test_find():
    fruits=['apples','oranges','bananas','mangoes','grapes','strawberry']
    assert 'bananas' == find(fruits, lambda e: e.count('n') > 1)
    assert 'oranges' == find(fruits, lambda e: 'r' in e)
