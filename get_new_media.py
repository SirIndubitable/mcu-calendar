"""
This script adds events to a google users calendar for Movies and TV shows defined in ./data/
"""

import re
from argparse import ArgumentParser
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import yaml

from mcu_calendar.events import GoogleMediaEvent
from mcu_calendar.helpers import create_progress
from mcu_calendar.webscraping import (
    Companies,
    Keyword,
    MovieGenre,
    TmdbObj,
    TvGenre,
    get_mcu_movie_link,
    get_mcu_show_link,
    get_movies,
    get_shows,
)
from mcu_calendar.yamlcalendar import YamlCalendar


def str_presenter(dumper: Union[yaml.Dumper, yaml.representer.SafeRepresenter], data: Any) -> yaml.Node:
    """
    configures yaml for dumping multiline strings
    Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
    """
    if "\n" in data:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_presenter)
yaml.representer.SafeRepresenter.add_representer(str, str_presenter)  # to use with safe_dum


def get_safe_title(title: str) -> str:
    """
    Gets a url-safe title (mostly trying to match the format I already had)
    """
    safe_title = re.sub(r"\s+", "_", title)
    safe_title = safe_title.replace("-", "_")
    safe_title = "".join(c for c in safe_title if c.isalnum() or c == "_")
    safe_title = safe_title.lower()
    return safe_title


def get_release_date(movie: TmdbObj, region: str) -> Optional[date]:
    """
    Gets the release date for the given region if the details exist, otherwise
    returns the default release_date
    """
    for region_releases in movie.release_dates.results:
        if region_releases.iso_3166_1 == region:
            for release_date in region_releases.release_dates:
                # Type 3 is Theatrical release
                if release_date.type == 3:
                    try:
                        return date.fromisoformat(release_date.release_date[:10])
                    except ValueError:
                        pass
    try:
        return date.fromisoformat(movie.release_date)
    except ValueError:
        return None


def handle_stale_yaml(existing: Sequence[GoogleMediaEvent], data: Dict, yaml_path: Path) -> None:
    """
    Removes the yaml file if it is stale
    """
    if any((e.file_path == yaml_path for e in existing)):
        return

    needs_rename = next((e.imdb_id == data["imdb_id"] for e in existing), None)
    if not needs_rename:
        return

    needs_rename["file_path"].rename(yaml_path)


def make_movie_yamls(dir_path: Path, movies: List[TmdbObj]) -> None:
    """
    Makes the movie yamls for each movie from the json data
    """
    existing_movies = YamlCalendar.get_movies(dir_path)

    for movie in movies:
        if movie.imdb_id is None:
            continue
        release_date = get_release_date(movie, "US")
        if release_date is None:
            continue
        yaml_path = dir_path / (get_safe_title(movie.title) + ".yaml")
        movie_data = {
            "title": movie.title,
            "release_date": release_date,
            "imdb_id": movie.imdb_id,
            "description": f"https://www.imdb.com/title/{movie.imdb_id}\n",
        }
        if dir_path.stem == "mcu-movies":
            official_link = get_mcu_movie_link(movie)
            if official_link is not None:
                movie_data["description"] += f"{official_link}\n"

        handle_stale_yaml(existing_movies, movie_data, yaml_path)

        with open(yaml_path, "w", encoding="UTF-8") as yaml_file:
            yaml.safe_dump(movie_data, yaml_file, sort_keys=False)


def get_season_release_dates(season: TmdbObj) -> List[date]:
    """
    Gets the number of distinct weeks in a given season
    """
    air_dates = set()
    for episode in season.episodes:
        air_dates.add(date.fromisoformat(episode.air_date))
    air_dates_list = list(air_dates)
    air_dates_list.sort()
    return air_dates_list


def make_show_yamls(dir_path: Path, shows: List[TmdbObj]) -> None:
    """
    Makes the show yamls for each season from the show json data
    """
    for show in shows:
        # print(movie)
        safe_title = get_safe_title(show.name)
        for season in show.seasons:
            show_data = {
                "title": show.name,
                "release_dates": get_season_release_dates(season),
                "imdb_id": show.external_ids.imdb_id,
                "description": f"https://www.imdb.com/title/{show.external_ids.imdb_id}\n",
            }
            if dir_path.stem == "mcu-shows":
                official_link = get_mcu_show_link(show, season)
                if official_link is not None:
                    show_data["description"] += f"{official_link}\n"

            if season.season_number == 1:
                yaml_path = dir_path / (safe_title + ".yaml")
            else:
                show_data["title"] += f" ({season.name})"
                yaml_path = dir_path / f"{safe_title}_{season.season_number}.yaml"

            with open(yaml_path, "w", encoding="UTF-8") as yaml_file:
                yaml.safe_dump(show_data, yaml_file, sort_keys=False)


def get_new_media(release_date_gte: date) -> None:
    """
    Gets all new media given the query definitions
    """
    movie_queries: Dict[str, Dict[str, Any]] = {
        "mcu-movies": {
            "with_companies": Companies.MARVEL_STUDIOS.value,
            "without_genres": MovieGenre.DOCUMENTARY.value,
            "primary_release_date.gte": release_date_gte.isoformat(),
        },
        "mcu-adjacent-movies": {
            "with_companies": Companies.MARVEL_ENTERTAINMENT.value,
            "without_genres": MovieGenre.DOCUMENTARY.value,
            "primary_release_date.gte": release_date_gte.isoformat(),
        },
        "dceu-movies": {
            "with_companies": Companies.DC_FILM.value,
            "without_genres": MovieGenre.DOCUMENTARY.value,
            "primary_release_date.gte": release_date_gte.isoformat(),
        },
    }

    show_queries: Dict[str, Dict[str, Any]] = {
        "mcu-shows": {
            "with_companies": f"{Companies.MARVEL_STUDIOS.value} | {Companies.MARVEL_STUDIOS_ANIMATION.value}",
            "without_genres": f"{TvGenre.DOCUMENTARY.value}, {TvGenre.KIDS.value}",
            "air_date.gte": release_date_gte.isoformat(),
        },
        "starwars-shows": {
            "with_companies": Companies.LUCAS_FILM.value,
            "with_keywords": Keyword.STAR_WARS_UNIVERSE.value,
            "air_date.gte": release_date_gte.isoformat(),
        },
    }

    data_dir = Path("data")
    with create_progress() as progress:
        task = progress.add_task("Working...", total=len(movie_queries) + len(show_queries))

        for folder, payload in movie_queries.items():
            movies = get_movies(payload)
            print(folder, [s.title for s in movies])
            make_movie_yamls(data_dir / folder, movies)
            progress.update(task, advance=1)

        for folder, payload in show_queries.items():
            shows = get_shows(payload)
            print(folder, [s.name for s in shows])
            make_show_yamls(data_dir / folder, shows)
            progress.update(task, advance=1)


if __name__ == "__main__":
    parser = ArgumentParser(description="Update a google calendarwith MCU Release info")
    parser.add_argument("--release_date", type=date.fromisoformat, default=(date.today() - timedelta(weeks=4)))
    args = parser.parse_args()

    get_new_media(args.release_date)
