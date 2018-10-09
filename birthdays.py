from collections import namedtuple
import calendar

Birthday = namedtuple('Birthday', 'month day')
birthdays = []  # All possible birthdays
for month in range(1, 13):
    for day in calendar.Calendar(0).itermonthdays(2000, month):
        if day != 0:
            birthdays.append(
                Birthday(
                    str(month).zfill(2),  # Servers reject "1" for "01", which is frightening
                    str(day).zfill(2)
                )
            )
