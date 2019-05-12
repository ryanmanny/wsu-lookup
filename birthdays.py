from collections import namedtuple
import calendar


class Birthday(namedtuple('Birthday', 'month day')):
    def __str__(self):
        return f"Birthday <Month: {self.month}, Day: {self.day}>"


BIRTHDAYS = [  # All possible birthdays
    Birthday(
        str(month).zfill(2),  # Servers reject "1" for "01", frightening
        str(day).zfill(2),
    )
    for month in range(1, 13)  # January to December
    for day in calendar.Calendar(0).itermonthdays(2000, month) if day != 0
]
