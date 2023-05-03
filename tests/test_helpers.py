import pytest

from reuploader.helpers import *


@pytest.fixture
def url():
    return 'https://auto.bazos.sk/inzerat/150676850/.php'


@pytest.fixture()
def phone():
    return '0940123123'


def test_id_from_link(url):
    assert get_id_from_link(url) == '150676850'


def test_international_number(phone):
    assert get_international_number(phone) == '+421940123123'


def test_get_fn_from_tel(phone):
    assert get_fn_from_tel(phone) == '940123123'


def test_input_validation(phone):
    assert validate_user_input('test@gmail.com', phone) is None
    assert validate_user_input('abc@.com', phone) == 'Invalid email address format'
    assert validate_user_input('test@gmail.com', '094012312') == 'Invalid phone number format, use 09XX XXX XXX'


def test_phone_key_validation():
    assert phone_key_correct('1234567')
    assert not phone_key_correct('123')


# test_is_error  # I don't remember how to trigger the error anymore :/
# test_error_msg_extraction
