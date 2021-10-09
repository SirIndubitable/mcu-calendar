"""
Tests for YamlMovie
"""
from datetime import date
from os import listdir, path

from mcu_calendar.events import YamlMovie
from pytest import mark


@mark.parametrize("movie_path", listdir(path.join('data', 'movies')))
def test_yamlmovie_constructor(movie_path):
    """
    Tests the constructor of yaml movies, and also validates the yaml files
    """
    movie = YamlMovie(path.join('data', 'movies', movie_path))
    assert type(movie.title)        is str
    assert type(movie.release_date) is date
    assert type(movie.description)  is str
