import csv

from dataclasses import dataclass
from calendar import monthrange


BIRTHDAY_DATA_PATH = 'data/fivethirtyeight-US-births-2000-2014.csv'

@dataclass
class Birthday:
    month: int
    day: int

with open(BIRTHDAY_DATA_PATH, 'r') as f:
    birthdays = list(csv.DictReader(f))
    birthdays.sort(key=lambda row: int(row['births']), reverse=True)
    for birthday in birthdays:
        birthday['day'] = birthday.pop('date_of_month')

EVERY_BIRTHDAY = [
    Birthday(
        # Form rejects "1" for "01", frightening
        str(birthday['month']).zfill(2),
        str(birthday['day']).zfill(2),
    ) for birthday in birthdays
]
