import pytest
import requests
import shutil
from reuploader.main import *
from reuploader.upload_ad import upload_ad
from reuploader.helpers import load_session_cookies, already_logged_in, ROOT_DIR
from dotenv import load_dotenv
load_dotenv()
TEST_NUM = os.environ['PHONE_NUM']
TEST_EMAIL = 'tester@gmail.com'


@pytest.fixture
def b_session():
    b_session = requests.Session()
    load_session_cookies(b_session, TEST_NUM)
    return b_session


@pytest.fixture
def flask_session():
    return {
        "tel_num": TEST_NUM,
        "email": TEST_EMAIL
    }


@pytest.fixture
def ad_fpath():
    return os.path.join(ROOT_DIR, 'tests', 'fixtures', 'test_1')


def test_session_working(b_session):
    ads_resp = get_my_ads(b_session)
    assert already_logged_in(ads_resp)


def test_remove_residue_ads(b_session):
    for ad_link in get_ad_links(get_my_ads(b_session)):
        delete_ad(b_session, ad_link)


def test_upload_ad(b_session, flask_session):
    ad_path = os.path.join(ROOT_DIR, 'tests', 'fixtures', 'test_ad')
    resp, ad_title = upload_ad(b_session, flask_session, ad_path)
    success = 1 if 'Inzerát bol vložený' in resp else 0
    assert success


def test_scrape_ads(b_session, ad_fpath):
    ad_links = get_ad_links(get_my_ads(b_session))
    assert len(ad_links) == 1
    assert download_ad(b_session, ad_links[0], ad_fpath)


def test_remove_ad(b_session, ad_fpath):
    ad_link = get_ad_links(get_my_ads(b_session))[0]
    assert delete_ad(b_session, ad_link)
    shutil.rmtree(ad_fpath)
