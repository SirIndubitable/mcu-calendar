"""
This script adds events to a google users calendar for Movies and TV shows defined in ./data/
"""
from argparse import ArgumentParser
from pathlib import Path

import yaml

from mcu_calendar.google_service_helper import MockService, create_service
from mcu_calendar.yamlcalendar import YamlCalendar

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def get_cal_ids(dry: bool):
    """
    Gets the ID of the calender that this script should write to.  This ID should
    belong to the user that logged in from get_google_creds()
    This tries to pull from a cal_id.yaml file first, for easy overriding when debuuging
    or running locally
    """
    # Only use test calender information if we're not running a dry run, it's useful to
    # see what would be updated in the real system
    if not dry:
        cal_id_path = Path("cal_id.yaml")
        if cal_id_path.exists():
            with open(cal_id_path, "r", encoding="UTF-8") as reader:
                try:
                    return yaml.safe_load(reader)
                except yaml.YAMLError as exc:
                    print(exc)

    # This would normally be secret, but this project is so people can add this calendar
    # to their calendars, and this information is on the iCal url, so why hide it?
    return {
        "mcu": "unofficial.mcu.calendar@gmail.com",
        "mcu-movies": "6t5rvfalpq6oejmd53jats1ir4@group.calendar.google.com",
        "mcu-shows": "kkgjb6avtmbocime1ecos0d49c@group.calendar.google.com",
        "mcu-adjacent": "a28nf2scue1viptdqoiv33g718@group.calendar.google.com",
        "dceu": "g8i6h4j0978715cl0o6amilsb0@group.calendar.google.com",
        "starwars": "9apr3vur3hcfkafq8s36njhkhs@group.calendar.google.com",
    }


def main(dry: bool, force: bool):
    """
    Main method that updates the users google calendar
    """
    service = create_service(SCOPES)
    if dry:
        service = MockService(service)

    ids = get_cal_ids(dry)
    data = Path("data")
    calendars = [
        YamlCalendar(
            "MCU",
            ids["mcu"],
            [data / "mcu-movies"],
            [data / "mcu-shows"],
            service,
        ),
        YamlCalendar(
            "MCU Movies",
            ids["mcu-movies"],
            [data / "mcu-movies"],
            [],
            service,
        ),
        YamlCalendar(
            "MCU Shows",
            ids["mcu-shows"],
            [],
            [data / "mcu-shows"],
            service,
        ),
        YamlCalendar(
            "MCU Adjacent Movies",
            ids["mcu-adjacent"],
            [data / "mcu-adjacent-movies"],
            [],
            service,
        ),
        YamlCalendar(
            "DCEU",
            ids["dceu"],
            [data / "dceu-movies"],
            [],
            service,
        ),
        YamlCalendar(
            "Starwars",
            ids["starwars"],
            [],
            [data / "starwars-shows"],
            service,
        ),
    ]

    for cal in calendars:
        cal.create_google_events(force)


if __name__ == "__main__":
    parser = ArgumentParser(description="Update a google calendarwith MCU Release info")
    parser.add_argument("--force", action="store_true", help="Force update the existing events")
    parser.add_argument("--dry", action="store_true", help="A dry run where nothing is updated")
    args = parser.parse_args()

    main(args.dry, args.force)
