import pickle
import re
import traceback
import requests
import os
import requests
from flask import render_template


def get_headers(authority='www.bazos.sk', ref=''):
    return {
        'authority': authority,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'origin': f'https://{authority}',
        'referer': ref if ref else 'https://www.bazos.sk/moje-inzeraty.php',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }


def create_directory(directory):
    if not os.path.exists(f"{directory}"):
        os.mkdir(f"{directory}")


def get_id_from_link(url):
    return re.findall(r'\d+', url)[0]


def is_error(txt):
    return 1 if '<span class="ztop">' in txt and '<span class="ztop">*<' not in txt else 0


def get_error_msg(txt):
    return txt.split('<span class="ztop">')[1].split('</span>')[0]


def get_international_number(phone_num):
    phone_codes = {"SK": 421}
    country = "SK"
    return f"+{phone_codes[country]}{phone_num[1:]}"


def phone_key_correct(k):
    return 1 if len(k) == 7 and all([i.isdigit() for i in k]) else 0


def validate_user_input(email, phone):
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid email address format"

    if not re.fullmatch(r"\d{10}", phone):
        return "Invalid phone number format, use 09XX XXX XXX"
    

def get_fn_from_tel(tel_num):
    return tel_num.replace(' ', '')[-9:]


def load_session_cookies(session, tel_num):
    try:
        with open(f'sessions/{get_fn_from_tel(tel_num)}.txt', 'rb') as f:
            session.cookies.update(pickle.load(f))
    except FileNotFoundError:
        print("FILE NOT FOUND IN LOAD SESSION")


def save_session(session, tel_num):
    try:
        with open(f'sessions/{get_fn_from_tel(tel_num)}.txt', 'wb') as f:
            pickle.dump(session.cookies, f)
    except FileNotFoundError:
        print("FILE NOT FOUND IN SAVE SESSION")


def already_logged_in(txt):
    if 'Nikto zatiaľ užívateľa nehodnotil.' in txt:
        return 1


def get_ad_links(resp):
    adverts_num = 0
    if 'Všetky inzeráty užívateľa' in resp:
        adverts_num = int(resp.split('Všetky inzeráty užívateľa (')[1].split(')')[0])
    print(f"Number of adverts {adverts_num}")

    ads = re.findall(r"https://[a-z]+.bazos.sk/zmazat/\d+.php", resp)
    ads = list(set(ads))
    return ads


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
