"""
This script provides helper methods for accessing themoviedb.org data about the MCU
"""
import os
from enum import Enum
from functools import wraps
from urllib.parse import quote_plus as url_encode

import requests
from tmdbv3api import TV, Discover, Movie, Season


class Companies(Enum):
    """
    The Movie DB Company ID's
    """

    DC_FILM = 128064

    MARVEL_STUDIOS = 420
    MARVEL_ENTERTAINMENT = 7505
    MARVEL_ANIMATION = 13252

    LUCAS_FILM = 1


class Network(Enum):
    """
    The Movie DB network ID's
    """

    HULU = 453
    NETFLIX = 213
    DISNEYPLUS = 2739
    YOUTUBE = 247
    ABC = 2
    ABC_COM = 3322


class Keyword(Enum):
    """
    The Movie DB keyword ID's
    """

    MCU = "180547"
    SHORT_FILM = "263548"
    STAR_WARS = "297811"


class MovieGenre(Enum):
    """
    The Movie DB Movie genre ID's
    """

    ADVENTURE = 12
    ANIMATION = 16
    COMEDY = 35
    CRIME = 80
    DACTION = 28
    DOCUMENTARY = 99
    DRAMA = 18
    FAMILY = 10751
    FANTASY = 14
    HISTORY = 36
    HORROR = 27
    MUSIC = 10402
    MYSTERY = 9648
    ROMANCE = 10749
    SCIENCE_FICTION = 878
    THRILLER = 53
    TV_MOVIE = 10770
    WAR = 10752
    WESTERN = 37


class TvGenre(Enum):
    """
    The Movie DB TV genre ID's
    """

    ACTIONADVENTURE = 10759
    ANIMATION = 16
    COMEDY = 35
    CRIME = 80
    DOCUMENTARY = 99
    DRAMA = 18
    FAMILY = 10751
    KIDS = 10762
    MYSTERY = 9648
    NEWS = 10763
    REALITY = 10764
    SCIFI_FANTASY = 10765
    SOAP = 10766
    TALK = 10767
    WAR_POLITICS = 10768
    WESTERN = 37


def query_all_pages(func):
    """
    Function decorator that agregates the results of func over multiple pages
    """

    @wraps(func)
    def wrapper(payload: dict = {}):
        discoverer = Discover()
        page = 0
        data = []
        while True:
            page += 1
            data += func(discoverer, page, payload)
            if discoverer.total_pages is None:
                break
            if page >= int(discoverer.total_pages):
                break
        return data

    return wrapper


@query_all_pages
def _discover_movies(discoverer, page, payload: dict):
    """
    Discovers movies from TMDB on all pages
    """
    base_payload = {
        "region": "US",
        "sort_by": "release_date.asc",
        "page": page,
    }
    return discoverer.discover_movies({**base_payload, **payload})


@query_all_pages
def _discover_shows(discoverer, page, payload: dict):
    """
    Discovers shows from TMDB on all pages
    """
    base_payload = {
        "region": "US",
        "language": "en-US",
        "include_null_first_air_dates": False,
        "sort_by": "first_air_date.asc",
        "page": page,
    }
    return discoverer.discover_tv_shows({**base_payload, **payload})


def get_movies(payload={}):
    """
    Gets movies from themoviedb.org with the given keyword
    """
    movies = _discover_movies(payload)
    movies = [m for m in movies if "release_date" in m and m.release_date != ""]
    movie_api = Movie()
    movie_details = []
    for movie in movies:
        movie_details.append(movie_api.details(movie["id"], append_to_response="release_dates"))

    return movie_details


def should_skip(season, payload):
    """
    Checks if the given season should be skipped based on the payload filter criteria
    """
    if "air_date.gte" in payload:
        return season.air_date < payload["air_date.gte"]
    if "air_date.lte" in payload:
        return season.air_date > payload["air_date.gte"]
    return False


def get_shows(payload={}):
    """
    Gets tv shwos from themoviedb.org with the given keyword
    """
    shows = _discover_shows(payload)
    shows = [s for s in shows if "first_air_date" in s and s.first_air_date != ""]
    # The discover api doesn't return season information, so we
    # still need to get the details
    tv_api = TV()
    season_api = Season()
    show_details = []
    for show in shows:
        show_detail = tv_api.details(show["id"], append_to_response="external_ids")
        season_details = []
        for season in show_detail.seasons:
            if should_skip(season, payload):
                continue
            season_details.append(season_api.details(show.id, season.season_number))
        show_detail.seasons = season_details
        show_details.append(show_detail)

    return show_details


MARVEL_SHOWS_CX = "61d919ee1f574fc77"
MARVEL_MOVIES_CX = "0ea857e1a2f692afa"
GOOGLE_SEARCH_FOMRAT = "https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query}"


def get_mcu_movie_link(movie):
    """
    Searches google to try to find the official webpage for the given mcu movie
    """
    result = requests.get(
        GOOGLE_SEARCH_FOMRAT.format(
            api_key=os.environ["GOOGLE_SEARCH_API_KEY"],
            cx=MARVEL_MOVIES_CX,
            query=url_encode(movie.title),
        )
    )
    for item in result.json()["items"]:
        if movie.title.lower() in item["title"].lower():
            return item["link"]
    return None


def get_mcu_show_link(show, season):
    """
    Searches google to try to find the official webpage for the given mcu show/season
    """
    result = requests.get(
        GOOGLE_SEARCH_FOMRAT.format(
            api_key=os.environ["GOOGLE_SEARCH_API_KEY"],
            cx=MARVEL_SHOWS_CX,
            query=url_encode(f"{show.name} {season.name}"),
        )
    )
    for item in result.json()["items"]:
        if show.name.lower() in item["title"].lower():
            return item["link"]
    return None
