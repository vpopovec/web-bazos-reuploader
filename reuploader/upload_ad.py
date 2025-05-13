import requests
import os
import json
import re
import urllib3
from reuploader.helpers import get_blob_url, list_blobs_by_prefix, CONTAINER_URL, read_file_bytes_from_azure

"""
    Bazos changes one field and value in insert.php call every few months...
"""

ADS_DIR = 'inzeraty'
from reuploader.helpers import ROOT_DIR
with open(f'{ROOT_DIR}/reuploader/bazos_categories.json', encoding='utf8') as rf:
    CATEGORIES = json.load(rf)


def upload_pic(pic_path, info):
    headers = {
        'authority': info['authority'],
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'origin': f'https://{info["authority"]}',
        'referer': f'https://{info["authority"]}/pridat-inzerat.php',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    file_name = pic_path.split(os.path.sep)[-1]

    fields = {
        "file[0]": (file_name, read_file_bytes_from_azure(get_blob_url(pic_path)), 'image/jpeg'),
    }

    boundary = '----WebKitFormBoundary1GVHUvw40yqeLBTz'
    body, header = urllib3.encode_multipart_formdata(fields, boundary=boundary)
    headers['content-type'] = header

    r = requests.post(f'https://{info["authority"]}/upload.php', data=body, headers=headers)

    ids = r.json()
    return ids[0]


def upload_photos(ad_path, info):
    pic_paths = list_blobs_by_prefix(CONTAINER_URL, ad_path)
    pic_paths = [p for p in pic_paths if re.fullmatch(rf'{ad_path}/\d+\.\w+', p)]
    ids = []
    for pic_p in pic_paths:
        ids.append(upload_pic(pic_p, info))
    return ids


def upload_ad(session, flask_session, ad_path):
    try:
        info = requests.get(get_blob_url(f"{ad_path}/info.json")).json()
    except:
        print(f"Ad {ad_path} not found")
        return

    boundary = '----WebKitFormBoundaryAD87BcSQ0bDtwXmX'
    headers = {
        'authority': info['authority'],
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': f'multipart/form-data; boundary={boundary}',
        'origin': f'https://{info["authority"]}',
        'referer': f'https://{info["authority"]}/pridat-inzerat.php',
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

    try:
        price = re.findall(r'\d+', info["price"])[0]
    except:
        return

    info['zip_code'] = info['zip_code'].replace(' ', '')

    main_cat = info['authority'].split('.')[0]
    sub_cat = info['category']
    if main_cat not in CATEGORIES or sub_cat not in CATEGORIES[main_cat]:
        print(f"CAN'T UPLOAD {main_cat} {sub_cat} MISSING CATEGORY ID")
        return '', info['ad_header']
    category_id = CATEGORIES[main_cat][sub_cat]

    fields = [
        ('category', category_id),  # Convert info['category'] to a number
        ('nadpis', info['ad_header']),
        ('popis', info['ad_description']),
        ('cena', price),
        ('cenavyber', '1'),  # Fixed amount
        ('lokalita', info['zip_code']),
        ('jmeno', info['advertiser']),
        ('telefoni', flask_session["tel_num"]),
        ('maili', flask_session["email"]),
        ('heslobazar', '123456'),
        ('tergdgs', 'gdfgreewr'),
        ('Submit', 'Odoslať')
    ]
    photo_ids = upload_photos(ad_path, info)

    for photo_id in photo_ids[::-1]:
        fields.insert(-6, ('files[]', photo_id))

    data, header = urllib3.encode_multipart_formdata(fields, boundary=boundary)
    headers['content-type'] = header

    response = session.post(f'https://{info["authority"]}/insert.php', headers=headers, data=data)

    return response.text, info['ad_header']
