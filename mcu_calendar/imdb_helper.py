"""
This script provides helper methods for accessing IMDB data about the MCU
"""
from datetime import datetime
# from imdb import IMDb
from .general_helpers import create_progress

# __IMDB__ = IMDb()
#
# def _get_mcu_titles():
#     titles = []
#     done = False
#     page = 0
#     while not done:
#         page += 1
#         cur_titles = __IMDB__.get_keyword('marvel-cinematic-universe', results=100, page=page)
#         titles.extend(cur_titles)
#         done = len(cur_titles) != 100
#     return titles
#
#
# def get_mcu_media():
#     """
#     Gets all of the movies and release dates with the MCU tag from IMDB
#     """
#     titles = _get_mcu_titles()
#     infosets = ['main', 'release dates']
#     with create_progress() as progress:
#         media = []
#         for title in progress.track(titles, description="Querying IMDB"):
#             media.append(__IMDB__.get_movie(title.movieID, info=infosets))
#         media = [m for m in media if 'kind' in m]
#         movies = [m for m in media if m['kind'] == 'movie']
#         tv_shows = [m for m in media if m['kind'] != 'movie']
#
#         for movie in movies:
#             _fix_movie_release_date(movie)
#
#         for tv_show in progress.track(tv_shows, description="Querying Season Info"):
#             __IMDB__.update(tv_show, 'episodes')
#             for _, episodes in tv_show['episodes'].items():
#                 __IMDB__.update(episodes[1], 'release dates')
#                 _fix_movie_release_date(episodes[1])
#
#     return (movies, tv_shows)
#
#
# def _fix_movie_release_date(movie):
#     """
#     Parses out strings in the form of "USA::16 August 2021" into dictionary entries in
#     the form of { "USA": datetime.date(2021, 8, 16) }
#     """
#     if 'release dates' not in movie:
#         return
#
#     dates = {}
#     for release_str in movie['release dates']:
#         vals = release_str.split(':')
#         country_str = vals[0]
#         try:
#             date_str = vals[-1].replace('(internet)', '').strip()
#             date = datetime.strptime(date_str, "%d %B %Y").date()
#         except ValueError:
#             continue
#         dates[country_str] = date
#     movie['release dates'] = dates
import requests

what_if = {
    "imDbId": "tt10168312",
    "title": "What If...?",
    "fullTitle": "What If...? (2021– )",
    "type": "TVSeries",
    "year": "2021",
    "episodes": [
        {
            "id": "tt10670784",
            "seasonNumber": "1",
            "episodeNumber": "1",
            "title": "What If... Captain Carter Were the First Avenger?",
            "image": "https://imdb-api.com/images/original/MV5BMGU2ZjY0MWYtZTc0NS00ZGE4LWIzOWMtMGM4MDhjZjUwYzNlXkEyXkFqcGdeQXVyMTEzMTI1Mjk3._V1_Ratio1.8571_AL_.jpg",
            "year": "2021",
            "released": "11 Aug. 2021",
            "plot": "When Steve Rogers is seriously injured, Peggy Carter becomes the world's first super soldier.",
            "imDbRating": "7.2",
            "imDbRatingCount": "9564"
        },
        {
            "id": "tt13106186",
            "seasonNumber": "1",
            "episodeNumber": "2",
            "title": "What If... T'Challa Became a Star-Lord?",
            "image": "https://imdb-api.com/images/original/MV5BNTBlZjc4NTQtMDFkNy00MDI4LWI3MzAtYzNhZGIzMmUwYzBkXkEyXkFqcGdeQXVyMTEzMTI1Mjk3._V1_Ratio2.2222_AL_.jpg",
            "year": "2021",
            "released": "18 Aug. 2021",
            "plot": "The rough-and-tumble space pirates known as the Ravagers abduct T'Challa instead of Peter Quill.",
            "imDbRating": "8.3",
            "imDbRatingCount": "7697"
        },
        {
            "id": "tt13106188",
            "seasonNumber": "1",
            "episodeNumber": "3",
            "title": "What If... the World Lost Its Mightiest Heroes?",
            "image": "https://imdb-api.com/images/original/MV5BYTVmZGYwMzMtZGZhNC00NjU5LWFhYTYtZGEyMjQwNzZiYzQwXkEyXkFqcGdeQXVyMjExNTA5MTI@._V1_Ratio2.1905_AL_.jpg",
            "year": "2021",
            "released": "25 Aug. 2021",
            "plot": "Nick Fury struggles to launch The Avengers when candidates are targeted by a serial killer.",
            "imDbRating": "8.3",
            "imDbRatingCount": "4551"
        },
        {
            "id": "tt13106190",
            "seasonNumber": "1",
            "episodeNumber": "4",
            "title": "Episode #1.4",
            "image": "https://imdb-api.com/images/original/MV5BMjc5ZjE2YzAtZDFlMi00YTI1LTgyODgtMzhkMjFhMGIwYmMzXkEyXkFqcGdeQXVyNzEzNjU1NDg@._V1_Ratio1.7778_AL_.jpg",
            "year": "2021",
            "released": "1 Sep. 2021",
            "plot": "Know what this is about? Be the first one to add a plot.",
            "imDbRating": "",
            "imDbRatingCount": ""
        },
        {
            "id": "tt13106194",
            "seasonNumber": "1",
            "episodeNumber": "5",
            "title": "Episode #1.5",
            "image": "https://imdb-api.com/images/original/MV5BN2Q0Yzg4NjMtNTAxYS00MGI1LWIyMzMtMmU1ZWM2YmEyZDFjXkEyXkFqcGdeQXVyMTAxNDE3MTE5._V1_Ratio2.1905_AL_.jpg",
            "year": "2021",
            "released": "8 Sep. 2021",
            "plot": "What if Thor was banished to Earth but was still worthy of his mantle?",
            "imDbRating": "",
            "imDbRatingCount": ""
        },
        {
            "id": "tt13106196",
            "seasonNumber": "1",
            "episodeNumber": "6",
            "title": "Episode #1.6",
            "image": "https://imdb-api.com/images/original/MV5BZDAyZmE5MGEtNjQ1Mi00OWJiLThhNjItM2Y0NzcwNDMyYTUzXkEyXkFqcGdeQXVyMTAxNDE3MTE5._V1_Ratio2.1746_AL_.jpg",
            "year": "2021",
            "released": "15 Sep. 2021",
            "plot": "Know what this is about? Be the first one to add a plot.",
            "imDbRating": "",
            "imDbRatingCount": ""
        },
        {
            "id": "tt13106200",
            "seasonNumber": "1",
            "episodeNumber": "7",
            "title": "Episode #1.7",
            "image": "https://imdb-api.com/images/original/MV5BODRmNjA5N2ItODI4YS00NjYyLTg5ZTYtOGU0NmFhNzYwYzg3XkEyXkFqcGdeQXVyMTAxNDE3MTE5._V1_Ratio2.1905_AL_.jpg",
            "year": "2021",
            "released": "22 Sep. 2021",
            "plot": "Know what this is about? Be the first one to add a plot.",
            "imDbRating": "",
            "imDbRatingCount": ""
        },
        {
            "id": "tt13106206",
            "seasonNumber": "1",
            "episodeNumber": "8",
            "title": "Episode #1.8",
            "image": "",
            "year": "2021",
            "released": "29 Sep. 2021",
            "plot": "The infamous Marvel Zombies comic comes to life in this episode.",
            "imDbRating": "",
            "imDbRatingCount": ""
        },
        {
            "id": "tt13106212",
            "seasonNumber": "1",
            "episodeNumber": "9",
            "title": "Episode #1.9",
            "image": "https://imdb-api.com/images/original/MV5BODA3ZGJjYjItNjgxOC00NTI2LWE4YWEtMDBiZDE4MzlhMzJmXkEyXkFqcGdeQXVyMjExNTA5MTI@._V1_Ratio2.0476_AL_.jpg",
            "year": "2021",
            "released": "6 Oct. 2021",
            "plot": "In an alternate timeline, Vision becomes an all-powerful android known as \"Infinite Ultron\" when merged with rival android Ultron. Now, it's up to the newly-formed \"Guardians of the Multiverse\" to put an end to his reign before it's too late.",
            "imDbRating": "",
            "imDbRatingCount": ""
        }
    ],
    "errorMessage": ""
}

spider_man = {
    "id": "tt10872600",
    "title": "Spider-Man: No Way Home",
    "originalTitle": "",
    "fullTitle": "Spider-Man: No Way Home (2021)",
    "type": "Movie",
    "year": "2021",
    "image": "https://imdb-api.com/images/original/MV5BNTMxOGI4OGMtMTgwMy00NmFjLWIyOTUtYjQ0OGQ4Mjk0YjNjXkEyXkFqcGdeQXVyMDM2NDM2MQ@@._V1_Ratio0.6791_AL_.jpg",
    "releaseDate": "2021-12-16",
    "runtimeMins": "",
    "runtimeStr": "",
    "plot": "A continuation of Spider-Man: Far From Home.",
    "plotLocal": "",
    "plotLocalIsRtl": False,
    "awards": "",
    "directors": "Jon Watts",
    "directorList": [
        {
            "id": "nm1218281",
            "name": "Jon Watts"
        }
    ],
    "writers": "Steve Ditko, Stan Lee, Chris McKenna, Erik Sommers",
    "writerList": [
        {
            "id": "nm0228492",
            "name": "Steve Ditko"
        },
        {
            "id": "nm0498278",
            "name": "Stan Lee"
        },
        {
            "id": "nm0571344",
            "name": "Chris McKenna"
        },
        {
            "id": "nm1273099",
            "name": "Erik Sommers"
        }
    ],
    "stars": "Angourie Rice, Zendaya, Tom Holland, Marisa Tomei",
    "starList": [
        {
            "id": "nm3886028",
            "name": "Angourie Rice"
        },
        {
            "id": "nm3918035",
            "name": "Zendaya"
        },
        {
            "id": "nm4043618",
            "name": "Tom Holland"
        },
        {
            "id": "nm0000673",
            "name": "Marisa Tomei"
        }
    ],
    "actorList": [
        {
            "id": "nm3886028",
            "image": "https://imdb-api.com/images/original/MV5BMzhkMTczYWEtOThmYS00MDEyLTgzZjAtODE5YTUwMmJiMjAzXkEyXkFqcGdeQXVyOTE0NjgwMjY@._V1_Ratio0.8182_AL_.jpg",
            "name": "Angourie Rice",
            "asCharacter": "Betty Brant"
        },
        {
            "id": "nm3918035",
            "image": "https://imdb-api.com/images/original/MV5BMjAxZTk4NDAtYjI3Mi00OTk3LTg0NDEtNWFlNzE5NDM5MWM1XkEyXkFqcGdeQXVyOTI3MjYwOQ@@._V1_Ratio0.7273_AL_.jpg",
            "name": "Zendaya",
            "asCharacter": "MJ"
        },
        {
            "id": "nm4043618",
            "image": "https://imdb-api.com/images/original/MV5BNzZiNTEyNTItYjNhMS00YjI2LWIwMWQtZmYwYTRlNjMyZTJjXkEyXkFqcGdeQXVyMTExNzQzMDE0._V1_Ratio0.7273_AL_.jpg",
            "name": "Tom Holland",
            "asCharacter": "Peter Parker / Spider-Man"
        },
        {
            "id": "nm0000673",
            "image": "https://imdb-api.com/images/original/MV5BMTUwMjA3OTc3N15BMl5BanBnXkFtZTcwNTA1MzY1Mw@@._V1_Ratio0.7273_AL_.jpg",
            "name": "Marisa Tomei",
            "asCharacter": "May Parker"
        },
        {
            "id": "nm1212722",
            "image": "https://imdb-api.com/images/original/MV5BMjE0MDkzMDQwOF5BMl5BanBnXkFtZTgwOTE1Mjg1MzE@._V1_Ratio0.7273_AL_.jpg",
            "name": "Benedict Cumberbatch",
            "asCharacter": "Doctor Strange"
        },
        {
            "id": "nm0799777",
            "image": "https://imdb-api.com/images/original/MV5BMzg2NTI5NzQ1MV5BMl5BanBnXkFtZTgwNjI1NDEwMDI@._V1_Ratio0.8182_AL_.jpg",
            "name": "J.K. Simmons",
            "asCharacter": "J. Jonah Jameson"
        },
        {
            "id": "nm0004937",
            "image": "https://imdb-api.com/images/original/MV5BMTkyNjY1NDg3NF5BMl5BanBnXkFtZTgwNjA2MTg0MzE@._V1_Ratio0.7273_AL_.jpg",
            "name": "Jamie Foxx",
            "asCharacter": "Max Dillon / Electro"
        },
        {
            "id": "nm0771414",
            "image": "https://imdb-api.com/images/original/MV5BYmQ3NDdjNzMtZWIyMC00OWRhLTgzNDYtZDlkMmE4YWY5YTEyXkEyXkFqcGdeQXVyNjc5Mjg0NjU@._V1_Ratio1.5000_AL_.jpg",
            "name": "Martin Starr",
            "asCharacter": "Mr. Harrington"
        },
        {
            "id": "nm0000547",
            "image": "https://imdb-api.com/images/original/MV5BMTEwNTgzNzgxNzNeQTJeQWpwZ15BbWU3MDQ5NzU1NjM@._V1_Ratio0.7727_AL_.jpg",
            "name": "Alfred Molina",
            "asCharacter": "Otto Octavius / Doctor Octopus"
        },
        {
            "id": "nm8188622",
            "image": "https://imdb-api.com/images/original/MV5BMTJmMDA1ODUtYWI0NS00MjA4LWFiZjgtOTk1OGQ3MDQ4Mjg4XkEyXkFqcGdeQXVyMTA1MTQ2ODk1._V1_Ratio1.4545_AL_.jpg",
            "name": "Jacob Batalon",
            "asCharacter": "Ned Leeds"
        },
        {
            "id": "nm1727825",
            "image": "https://imdb-api.com/images/original/MV5BMjgyNGIyZmMtMTFlYy00OWE5LWE2Y2QtYjhhOGU0NzM4YzliXkEyXkFqcGdeQXVyMzk0NzA4MDc@._V1_Ratio0.7273_AL_.jpg",
            "name": "Tony Revolori",
            "asCharacter": "Flash Thompson"
        },
        {
            "id": "nm1356578",
            "image": "https://imdb-api.com/images/original/MV5BNjI1NjI3NDQzOF5BMl5BanBnXkFtZTcwMzYzMDQ1NA@@._V1_Ratio0.7273_AL_.jpg",
            "name": "J.B. Smoove",
            "asCharacter": "Mr. Dell"
        },
        {
            "id": "nm5220941",
            "image": "https://imdb-api.com/images/original/MV5BODY3OGIxOTAtMGMwOS00YzliLTllMTUtZWFlZTNjOWVlYmExXkEyXkFqcGdeQXVyNjUzNjMzMjA@._V1_Ratio0.9091_AL_.jpg",
            "name": "Harry Holland",
            "asCharacter": "Drug Dealer"
        },
        {
            "id": "nm2868110",
            "image": "https://imdb-api.com/images/original/MV5BMjI2NzIwNTQ1N15BMl5BanBnXkFtZTgwMTQzNTc4NDE@._V1_Ratio0.7273_AL_.jpg",
            "name": "Hannibal Buress",
            "asCharacter": "Coach Wilson"
        },
        {
            "id": "nm11184557",
            "image": "https://imdb-api.com/images/original/MV5BZTJlNTM4OGYtYjU5MC00ODRjLTlmN2ItNmI5ODY2YzdmNTBmXkEyXkFqcGdeQXVyMTEwODMyODM1._V1_Ratio0.7727_AL_.jpg",
            "name": "Christopher Cocke",
            "asCharacter": "Security Guard"
        }
    ],
    "fullCast": None,
    "genres": "Action, Adventure, Sci-Fi",
    "genreList": [
        {
            "key": "Action",
            "value": "Action"
        },
        {
            "key": "Adventure",
            "value": "Adventure"
        },
        {
            "key": "Sci-Fi",
            "value": "Sci-Fi"
        }
    ],
    "companies": "Pascal Pictures, Marvel Studios, Columbia Pictures",
    "companyList": [
        {
            "id": "co0532247",
            "name": "Pascal Pictures"
        },
        {
            "id": "co0051941",
            "name": "Marvel Studios"
        },
        {
            "id": "co0050868",
            "name": "Columbia Pictures"
        }
    ],
    "countries": "USA",
    "countryList": [
        {
            "key": "USA",
            "value": "USA"
        }
    ],
    "languages": "English",
    "languageList": [
        {
            "key": "English",
            "value": "English"
        }
    ],
    "contentRating": "",
    "imDbRating": "",
    "imDbRatingVotes": "",
    "metacriticRating": "",
    "ratings": None,
    "wikipedia": None,
    "posters": None,
    "images": None,
    "trailer": None,
    "boxOffice": {
        "budget": "",
        "openingWeekendUSA": "",
        "grossUSA": "",
        "cumulativeWorldwideGross": ""
    },
    "tagline": "",
    "keywords": "superhero,based on comic,marvel comics,marvel cinematic universe,sequel",
    "keywordList": [
        "superhero",
        "based on comic",
        "marvel comics",
        "marvel cinematic universe",
        "sequel"
    ],
    "similars": [
        {
            "id": "tt9419884",
            "title": "Doctor Strange in the Multiverse of Madness",
            "fullTitle": "Doctor Strange in the Multiverse of Madness (2022)",
            "year": "2022",
            "image": "https://imdb-api.com/images/original/MV5BYzljNzE0ZDktNWFkOS00ZjE3LWJjNzEtZTE0NmVhNzBmYzE5XkEyXkFqcGdeQXVyNjg3MDMxNzU@._V1_Ratio0.6737_AL_.jpg",
            "plot": "Plot unknown. Sequel to the 2016 Marvel film 'Doctor Strange'.",
            "directors": "Sam Raimi",
            "stars": "Elizabeth Olsen, Rachel McAdams, Benedict Wong",
            "genres": "Action, Adventure, Fantasy",
            "imDbRating": ""
        },
        {
            "id": "tt6320628",
            "title": "Spider-Man: Far from Home",
            "fullTitle": "Spider-Man: Far from Home (2019)",
            "year": "2019",
            "image": "https://imdb-api.com/images/original/MV5BMGZlNTY1ZWUtYTMzNC00ZjUyLWE0MjQtMTMxN2E3ODYxMWVmXkEyXkFqcGdeQXVyMDM2NDM2MQ@@._V1_Ratio0.6737_AL_.jpg",
            "plot": "Following the events of Avengers: Endgame (2019), Spider-Man must step up to take on new threats in a world that has changed forever.",
            "directors": "Jon Watts",
            "stars": "Tom Holland, Samuel L. Jackson, Jake Gyllenhaal",
            "genres": "Action, Adventure, Sci-Fi",
            "imDbRating": "7.5"
        },
        {
            "id": "tt9765564",
            "title": "Spider-Man 4: Fan Film",
            "fullTitle": "Spider-Man 4: Fan Film (2021)",
            "year": "2021",
            "image": "https://imdb-api.com/images/original/MV5BNTVhMWExZTEtNDgxYi00YmFhLTgwN2UtYjJiODM0YmMyYmU3XkEyXkFqcGdeQXVyODYyNTgyNjc@._V1_Ratio0.6737_AL_.jpg",
            "plot": "Spider-Man returns to face his greatest challenge yet as he faces off against The Vulture.",
            "directors": "Erik Franklin",
            "stars": "Leona Britt, Bryn Clayton Jones, Tommy Lee Driver",
            "genres": "Action, Adventure, Drama",
            "imDbRating": ""
        },
        {
            "id": "tt2250912",
            "title": "Spider-Man: Homecoming",
            "fullTitle": "Spider-Man: Homecoming (2017)",
            "year": "2017",
            "image": "https://imdb-api.com/images/original/MV5BNTk4ODQ1MzgzNl5BMl5BanBnXkFtZTgwMTMyMzM4MTI@._V1_Ratio0.6737_AL_.jpg",
            "plot": "Peter Parker balances his life as an ordinary high school student in Queens with his superhero alter-ego Spider-Man, and finds himself on the trail of a new menace prowling the skies of New York City.",
            "directors": "Jon Watts",
            "stars": "Tom Holland, Michael Keaton, Robert Downey Jr.",
            "genres": "Action, Adventure, Sci-Fi",
            "imDbRating": "7.4"
        },
        {
            "id": "tt10648342",
            "title": "Thor: Love and Thunder",
            "fullTitle": "Thor: Love and Thunder (2022)",
            "year": "2022",
            "image": "https://imdb-api.com/images/original/MV5BMzZjMTIwNjYtYTg0ZS00ZDFjLTk3MDctMTY3ZTgwMjQ4MmFiXkEyXkFqcGdeQXVyNjg2NjQwMDQ@._V1_Ratio0.7053_AL_.jpg",
            "plot": "The sequel to Thor: Ragnarok and the fourth movie in the Thor saga.",
            "directors": "Taika Waititi",
            "stars": "Natalie Portman, Karen Gillan, Chris Hemsworth",
            "genres": "Action, Adventure, Fantasy",
            "imDbRating": ""
        },
        {
            "id": "tt10676052",
            "title": "Fantastic Four",
            "fullTitle": "",
            "year": "",
            "image": "https://imdb-api.com/images/original/MV5BZjZiNmYwYWItNzg4ZC00ZGI5LTlmMjAtMzUyMjlkYzk2NmJkXkEyXkFqcGdeQXVyNTE1NjY5Mg@@._V1_Ratio0.6737_AL_.jpg",
            "plot": "One of Marvel's most iconic families makes it to the big screen: the Fantastic Four.",
            "directors": "Jon Watts",
            "stars": "",
            "genres": "Action, Adventure, Comedy",
            "imDbRating": ""
        },
        {
            "id": "tt5108870",
            "title": "Morbius",
            "fullTitle": "Morbius (2022)",
            "year": "2022",
            "image": "https://imdb-api.com/images/original/MV5BNjIxMDcxMGQtNTViOC00MWM0LWFjYjItNDNmNzRkZThlMmZjXkEyXkFqcGdeQXVyMDA4NzMyOA@@._V1_Ratio0.6737_AL_.jpg",
            "plot": "Biochemist Michael Morbius tries to cure himself of a rare blood disease, but he inadvertently infects himself with a form of vampirism instead.",
            "directors": "Daniel Espinosa",
            "stars": "Jared Leto, Michael Keaton, Adria Arjona",
            "genres": "Action, Adventure, Drama",
            "imDbRating": ""
        },
        {
            "id": "tt10676048",
            "title": "The Marvels",
            "fullTitle": "The Marvels (2022)",
            "year": "2022",
            "image": "https://imdb-api.com/images/original/MV5BNjQ4NzQ2MmUtMTUwYi00ZTVhLWI5Y2MtYWM3ZmM5MTc1OGEyXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1_Ratio0.6737_AL_.jpg",
            "plot": "Sequel of the 2019 title 'Captain Marvel'.",
            "directors": "Nia DaCosta",
            "stars": "Brie Larson, Zawe Ashton, Teyonah Parris",
            "genres": "Action, Adventure, Fantasy",
            "imDbRating": ""
        },
        {
            "id": "tt1464335",
            "title": "Uncharted",
            "fullTitle": "Uncharted (2022)",
            "year": "2022",
            "image": "https://imdb-api.com/images/original/MV5BOTZjZWZhMTAtYTAxZS00ZDMwLWE0YzEtMzFkNzdhZjc5OGQ0XkEyXkFqcGdeQXVyNjI5MDc2MjU@._V1_Ratio0.7053_AL_.jpg",
            "plot": "The story is a prequel to the games, starring Holland as a younger Drake, showing us details of how he came to meet and befriend Sully.",
            "directors": "Ruben Fleischer",
            "stars": "Mark Wahlberg, Tom Holland, Antonio Banderas",
            "genres": "Action, Adventure",
            "imDbRating": ""
        },
        {
            "id": "tt9114286",
            "title": "Black Panther: Wakanda Forever",
            "fullTitle": "Black Panther: Wakanda Forever (2022)",
            "year": "2022",
            "image": "https://imdb-api.com/images/original/MV5BYjJlMjBmYzUtY2E3MC00OWI1LWE1YmUtOTdmM2IyMTQyZDBjXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1_Ratio0.6737_AL_.jpg",
            "plot": "A sequel that will continue to explore the incomparable world of Wakanda and all the rich and varied characters introduced in the 2018 film.",
            "directors": "Ryan Coogler",
            "stars": "Martin Freeman, Tenoch Huerta, Angela Bassett",
            "genres": "Action, Adventure, Drama",
            "imDbRating": ""
        },
        {
            "id": "tt10838180",
            "title": "The Matrix 4",
            "fullTitle": "The Matrix 4 (2021)",
            "year": "2021",
            "image": "https://imdb-api.com/images/original/MV5BNTg3OTQ5OWItMDUwNi00NjhlLTliZTgtZGY1MDc5MjYxZDQ0XkEyXkFqcGdeQXVyMzA2ODQ2OTU@._V1_Ratio2.4421_AL_.jpg",
            "plot": "The plot is currently unknown.",
            "directors": "Lana Wachowski",
            "stars": "Keanu Reeves, Christina Ricci, Jessica Henwick",
            "genres": "Action, Sci-Fi",
            "imDbRating": ""
        },
        {
            "id": "tt7097896",
            "title": "Venom: Let There Be Carnage",
            "fullTitle": "Venom: Let There Be Carnage (2021)",
            "year": "2021",
            "image": "https://imdb-api.com/images/original/MV5BYzljNzQ1MzMtODI5NS00MDRlLTgzYmQtNjE1NDk4MTIxODI0XkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_Ratio0.6737_AL_.jpg",
            "plot": "Plot unknown. Sequel to the 2018 film 'Venom'.",
            "directors": "Andy Serkis",
            "stars": "Stephen Graham, Tom Hardy, Michelle Williams",
            "genres": "Action, Sci-Fi, Thriller",
            "imDbRating": ""
        }
    ],
    "tvSeriesInfo": None,
    "tvEpisodeInfo": None,
    "errorMessage": ""
}


import json

def _request_imdb(api, query, progress):
    try:
        response = requests.request('GET', f"https://imdb-api.com/en/API/{api}/k_yoi2scp8/{query}")
        return response.json()
    except json.decoder.JSONDecodeError:
        progress.console.print(f"   {response.text}")
        return None

import os;

def get_mcu_media():
    """
    Gets mcu data from imdb-api.com
    """
    if os.path.isfile('./movies.json') and os.path.isfile('./shows.json'):
        with open('./movies.json', 'r', encoding='utf-8') as f:
            movies = json.load(f)
        with open('./shows.json', 'r', encoding='utf-8') as f:
            show_seasons = json.load(f)
    else:
        with create_progress() as progress:
            mcu_item = _request_imdb("Keyword"," marvel-cinematic-universe", progress)['items']
            mcu_item.sort(key=lambda i: i['title'])
            media = [_request_imdb("Title", item['id'], progress) for item in progress.track(mcu_item, description="Getting MCU Titles...")]
            media = [m for m in media if m is not None]
            movies = [m for m in media if m["type"] == "Movie"]
            shows = [m for m in media if m["type"] == "TVSeries"]
            show_seasons = []
            for show in progress.track(shows, description="Getting Show info..."):
                for season in progress.track(show['tvSeriesInfo']['seasons'], description="Getting season info..."):
                    show_seasons.append(_request_imdb("SeasonEpisodes", f"{show['id']}/{season}", progress))
        with open('./movies.json', 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)
        with open('./shows.json', 'w', encoding='utf-8') as f:
            json.dump(show_seasons, f, ensure_ascii=False, indent=4)

    return (movies, show_seasons)
