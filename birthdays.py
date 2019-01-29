from collections import namedtuple
import calendar


class Birthday(namedtuple('Birthday', 'month day')):
    pass


def get_birthdays():
    return [
        Birthday(
            str(month).zfill(2),  # Servers reject "1" for "01", frightening
            str(day).zfill(2),
        )
        for month in range(1, 13)  # January to December
        for day in calendar.Calendar(0).itermonthdays(2000, month) if day != 0
    ]  # All possible birthdays


birthdays = get_birthdays()
