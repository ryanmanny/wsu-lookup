from collections import defaultdict
import csv
from dataclasses import dataclass


BIRTHDAY_DATA_PATH = 'data/fivethirtyeight-US-births-2000-2014.csv'


@dataclass
class Birthday:
    month: str
    day: str

    def __str__(self):
        return f"{self.month}/{self.day}"


def get_all_birthdays():
    with open(BIRTHDAY_DATA_PATH, 'r') as f:
        births_by_day = defaultdict(lambda: 0)

        for date in csv.DictReader(f):
            birthday_key = (date['month'], date['date_of_month'])
            births_by_day[birthday_key] += int(date['births'])

        ordered_birthdays = [
            birthday for birthday, _ in sorted(
                list(births_by_day.items()),
                key=lambda x: int(x[1]),
                reverse=True,
            )
        ]

    return [
        Birthday(
            # Form rejects "1" for "01", frightening
            str(birthday[0]).zfill(2),
            str(birthday[1]).zfill(2),
        ) for birthday in ordered_birthdays
    ]
