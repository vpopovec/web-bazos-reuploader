import json
import aiohttp
import asyncio
from helpers import *

ADS_DIR = 'inzeraty'


def download_ad(session, url):
    create_directory(ADS_DIR)

    authority = re.findall(r"https://([^/]*)/", url)[0]

    ad_id = get_id_from_link(url)
    txt = session.get(f"https://{authority}/inzerat/{ad_id}/.php", headers=get_headers(authority)).text

    location_raw = txt.split('Lokalita:<')[-1].split('<tr>')[0]

    img_previews = re.findall(r'src="https://www.bazos.sk/img/([^"]*)"', txt.split('<div class="podobne">')[0])
    img_previews = [f"https://www.bazos.sk/img/{i}" for i in img_previews if re.match(r"\dt/\d+/\d+\.[a-z]*", i)]

    if not img_previews:  # One picture ad with no previews
        img_previews = re.findall(r'src="https://www.bazos.sk/img/([^"]*)"', txt.split('<div class="podobne">')[0])
        img_previews = [f"https://www.bazos.sk/img/{i}" for i in img_previews if re.match(r"\d/\d+/\d+\.[a-z]*", i)]
    img_previews = [f"{route.split('?')[0]}" for route in img_previews]

    info = {'ad_header': txt.split('class=nadpisdetail>')[1].split('</')[0],
            'ad_description': txt.split('class=popisdetail>')[1].split('</')[0],
            'advertiser': txt.split('Meno:')[1].split('</a>')[0].split('>')[-1],
            'authority': authority,
            'category': txt.split('Hlavná stránka')[1].split('</a>')[2].split('>')[-1],
            'zip_code': re.findall(r">(\d{3}.?\d{2})<", location_raw)[0],
            'city': location_raw.split('</a>')[-2].split('>')[-1],
            'price': txt.split('Cena:')[-1].split('</b>')[0].split('<b>')[-1].strip().replace(' ', ''),
            'img_links': [i.replace('t/', '/') for i in img_previews]}

    ad_path = f"{ADS_DIR}{os.path.sep}{ad_id}"
    create_directory(ad_path)

    with open(f'{ad_path}{os.path.sep}info.json', 'w', encoding='utf8') as wf:
        json.dump(info, wf)

    images = asyncio.run(download_images(info['img_links']))
    images = [i for i in images if i]
    if not images:
        return

    for url, img_content in images:
        file_name = url.split('img/')[1].split('/')[0] + ".jpg"
        with open(f"{ad_path}{os.path.sep}{file_name}", mode='wb') as wf:
            wf.write(img_content)
    return True


def delete_ad(session, url, flask_session):
    authority = re.findall(r"https://([^/]*)/", url)[0]
    ad_id = get_id_from_link(url)

    session.get(f'https://{authority}/zmazat/{ad_id}.php', headers=get_headers(authority))

    data = {
        # 'heslobazar': flask_session["ad_psw"],
        'heslobazar': "123456",
        'idad': ad_id,
        'administrace': 'Zmazať',
    }

    resp = session.post(f'https://{authority}/deletei2.php', headers=get_headers(authority, url), data=data).text

    if 'Inzerát bol vymazaný z nášho bazáru.' in resp:
        return True
    elif '<form name="formh" id="formh" method="post" action="https://www.bazos.sk/heslo.php">' in resp:
        raise ValueError(f"Wrong password {ad_id}")
    

async def download_images(urls):
    for i in range(5):
        try:
            async with aiohttp.ClientSession() as session:
                coros = (fetch_image(session, url) for url in urls)
                res = await asyncio.gather(*coros)
        except:
            if i == 4:
                print("Couldn't download images")

    if not all(res):
        print(f"Not all images could be downloaded, check your internet connection and try again")
        return []
    return res


async def fetch_image(session, url):
    async with session.get(url, timeout=10) as response:
        if response.status == 200:
            img_content = await response.content.read()
            return [url, img_content]


def get_my_ads(session):
    txt = session.get('https://www.bazos.sk/moje-inzeraty.php', headers=get_headers()).text
    return txt


def send_authentication(session, flask_session):
    data = {
        'mail': flask_session['email'],
        'telefon': flask_session['tel_num'],
        'Submit': 'Overiť',
    }

    response = session.post('https://www.bazos.sk/moje-inzeraty.php', headers=get_headers(), data=data)
    txt = response.text
    if is_error(txt):
        raise TimeoutError(get_error_msg(txt))


def send_sms_code(session, key, tel_num):
    data = {
        'klic': key,
        'klictelefon': get_international_number(tel_num),
        'Submit': 'Odoslať',
    }

    response = session.post('https://www.bazos.sk/moje-inzeraty.php', headers=get_headers(), data=data)

    txt = response.text
    if is_error(txt):
        raise TimeoutError(get_error_msg(txt))

    save_session(session, tel_num)
    return txt
