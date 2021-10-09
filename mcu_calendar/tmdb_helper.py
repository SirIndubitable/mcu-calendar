"""
This script provides helper methods for accessing themoviedb.org data about the MCU
"""
from functools import wraps
from tmdbv3api import TV, Discover
from .general_helpers import create_progress

NETWORK_HULU = 453
NETWORK_NETFLIX = 213
NETWORK_DISNEYPLUS = 2739
NETWORK_YOUTUBE = 247
NETWORK_ABC = 2
NETWORK_ABC_COM = 3322

KEYWORD_MCU = "180547"
KEYWORD_SHORT_FILM = "263548"

GENRE_DOCUMENTERY = "99"

def query_all_pages(func):
    """
    Function decorator that agregates the results of func over multiple pages
    """
    @wraps(func)
    def wrapper():
        discoverer = Discover()
        page = 0
        data = []
        while True:
            page += 1
            data += func(discoverer, page)
            if discoverer.total_pages is None:
                break
            if page >= int(discoverer.total_pages):
                break
        return data
    return wrapper


@query_all_pages
def discover_movies(discoverer, page):
    """
    Discovers movies from TMDB on all pages
    """
    return discoverer.discover_movies({
        'region': 'US',
        "with_keywords": KEYWORD_MCU,
        'without_keywords': KEYWORD_SHORT_FILM,
        'without_genres': GENRE_DOCUMENTERY,
        'sort_by': 'release_date.asc',
        "page": page
    })

@query_all_pages
def discover_shows(discoverer, page):
    """
    Discovers shows from TMDB on all pages
    """
    return discoverer.discover_tv_shows({
        'region': 'US',
        'language': 'en-US',
        'include_null_first_air_dates': False,
        'with_keywords': KEYWORD_MCU,
        'with_networks': f"{NETWORK_DISNEYPLUS}",
        'sort_by': 'first_air_date.asc',
        'page': page
    })

def get_mcu_media():
    """
    Gets mcu data from themoviedb.org
    """
    with create_progress() as progress:
        movies = discover_movies()
        movies = [m for m in movies if "release_date" in m and m.release_date != ""]
        shows = discover_shows()
        shows = [s for s in shows if "first_air_date" in s and s.first_air_date != ""]
        # The discover api doesn't return season information, so we
        # still need to get the details
        tv_api = TV()
        show_details = []
        for show in progress.track(shows, description="Getting Show info..."):
            show_details.append(tv_api.details(show['id'], append_to_response="external_ids"))

    return (movies, show_details)
