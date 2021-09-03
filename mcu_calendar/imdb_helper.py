"""
This script provides helper methods for accessing IMDB data about the MCU
"""
from datetime import datetime
from imdb import IMDb
from general_helpers import create_progress

__IMDB__ = IMDb()

def _get_mcu_titles():
    titles = []
    done = False
    page = 0
    while not done:
        page += 1
        cur_titles = __IMDB__.get_keyword('marvel-cinematic-universe', results=100, page=page)
        titles.extend(cur_titles)
        done = len(cur_titles) != 100
    return titles


def get_mcu_media():
    """
    Gets all of the movies and release dates with the MCU tag from IMDB
    """
    titles = _get_mcu_titles()
    with create_progress() as progress:
        media = []
        for title in progress.track(titles, description="Querying IMDB"):
            media.append(__IMDB__.get_movie(title.movieID, info=['main', 'release dates']))
    movies = [m for m in media if m['kind'] == 'movie']
    tv_shows = [m for m in media if m['kind'] != 'movie']
    for movie in movies:
        _fix_movie_release_date(movie)
    for tv_show in tv_shows:
        __IMDB__.update(tv_show, 'episodes')

    return (movies, tv_shows)


def _fix_movie_release_date(movie):
    """
    Parses out strings in the form of "USA::16 August 2021" into dictionary entries in
    the form of { "USA": datetime.date(2021, 8, 16) }
    """
    dates = {}
    for release_str in movie['release dates']:
        vals = release_str.split(':')
        country_str = vals[0]
        try:
            date = datetime.strptime(vals[-1], "%d %B %Y").date()
        except ValueError:
            continue
        dates[country_str] = date
    movie['release dates'] = dates
