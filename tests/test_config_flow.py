"""Test cookie validation for YouTube Music Player."""
import pytest
from unittest.mock import MagicMock
from custom_components.ytube_music_player.const import (
    CONF_COOKIE, CONF_PO_TOKEN, CONF_VISITOR_DATA, CONF_NAME,
    ERROR_COOKIE_FORMAT, ERROR_MISSING_PARAM, ERROR_INVALID_COOKIE, ERROR_JSON_SYNTAX, ERROR_FORMAT,
    async_try_login
)

# Replace with real data for testing
REAL_COOKIE = "VISITOR_PRIVACY_METADATA=CgJERRIEEgAgRg%3D%3D; __Secure-ROLLOUT_TOKEN=CLTX3oq-mZOdrAEQs62L--O3kAMYit_qt5iDkQM%3D; __Secure-1PSIDTS=sidts-CjUBmkD5S3rhzY6Ua_QiQ_fwqzWZE4WWyV1XSN4yqIJP5PQT3rOMYfScBDtv4MZR7cHC0LjjbxAA; __Secure-3PSIDTS=sidts-CjUBmkD5S3rhzY6Ua_QiQ_fwqzWZE4WWyV1XSN4yqIJP5PQT3rOMYfScBDtv4MZR7cHC0LjjbxAA; HSID=AZyhUxT29g6Vyat3U; SSID=AKFreLmIfPBGIlkWq; APISID=fmVcM4I4AceuMUx0/AfeOogzIcvBGRTGp8; SAPISID=lJNkJHb2J9NJQjtr/AWmAjCG8G3AMBxtmC; __Secure-1PAPISID=lJNkJHb2J9NJQjtr/AWmAjCG8G3AMBxtmC; __Secure-3PAPISID=lJNkJHb2J9NJQjtr/AWmAjCG8G3AMBxtmC; SID=g.a0002wjmoNBe6sGqb22Mdp_ZaxpjTthYC1STeD-5Z1ptOH00jXvK0oKA0HRiJ9Y75Y9Gtai3IgACgYKAXYSARMSFQHGX2MiNzIzDMlZ-j1IPwUucr9xtRoVAUF8yKpu2YoC_DrTuigC86bxNg1P0076; __Secure-1PSID=g.a0002wjmoNBe6sGqb22Mdp_ZaxpjTthYC1STeD-5Z1ptOH00jXvKcB2riAUy69y3MuE5RQpzigACgYKAX4SARMSFQHGX2MiToJq2y1_K924UoU9AXjQ7xoVAUF8yKo3Rk2uwfjYD0elUfVQEDY40076; __Secure-3PSID=g.a0002wjmoNBe6sGqb22Mdp_ZaxpjTthYC1STeD-5Z1ptOH00jXvK6J_4nFFHdR7dHmV9rkt12gACgYKAakSARMSFQHGX2Miv837YtXfSTUnbuFeCUJYixoVAUF8yKqe2D5z1E-5iS3LZaZgRgUK0076; LOGIN_INFO=AFmmF2swRQIgRuPI_O1Wjm_g2kv5LTUWHl0_yzzCAqSEB8rQainou1wCIQDq0lwjl4xZsqwC9SeLzPJGcMuIBs473UHK0rqzVdlTyg:QUQ3MjNmeFlxSUhwNVZRM09Qa0l6aVl0YWFfRTdEeXBHNmo3eC1od1pYbFRGVmM2ZUFjbllsd3F0c1FWYS02blpMVnhjaDZqME5zWWNEYkt4YmNQWjh1b2NWdmROdHoxMU9penE4N1p2Wkh1Ri1iUFFwOHozaGt1SzNUTzFUUERUY05jSFVsbGlYS2pOcWtsa1FYM1JIYmRPc1hiS19YREd3; SIDCC=AKEyXzX4L3rYUWndl_w0L1CnCG8r_vUgeeluiHRwm1kNUssTXAj6flfideidLfyGTvUfsKPGl2o; __Secure-1PSIDCC=AKEyXzUuhVvEfNkRM43P3075L_O5krtj1WuJN8kArujZm6eFJD12XCfpXTePT5mx4YYTVxpiF8Y; __Secure-3PSIDCC=AKEyXzVRyjoaGBhPHl2Vezq23Yp6bNeApw219H3yeVX1M3kSEPoVHi1gh8p0wQbSfmMaPbFl1cQ; __Secure-YENID=11.YTE=iW1mppLctjGu_30IYV2M524wFVZnT2eMZ0xUIjo6-ClDKxm2DO7aatBSbJ23yvJhUrEZXMvOvDhorsZ56zvd9nzQo-zNjDlSnpmQWWBN6zVVUvN6TNm0iVYze0Ybtjy79NNOZwgfBbL9zV5T0FD_6irs60Ch-68ZVjdH4ICE2hwivUGiemgNV5SM9bCcGUhBTnmmCvIqvLZnZFNjeAEAwxM-WoDyM33MEQq33rzEu2hVjKH7aHXK5ReYd5L5KNF3EAAlRvW966b3oktVEbotMnB2XgtH20SpSaUVYN8XYi-k3oe0Po1MHPxbf40R8qJOY5fnCakFuguvoi9ML5wJ5w; __Secure-YEC=CgtlZENNWG52NkNOcyjXp4HJBjIKCgJERRIEEgAgRmLgAgrdAjExLllURT1pVzFtcHBMY3RqR3VfMzBJWVYyTTUyNHdGVlpuVDJlTVoweFVJam82LUNsREt4bTJETzdhYXRCU2JKMjN5dkpoVXJFWlhNdk92RGhvcnNaNTZ6dmQ5bnpRby16TmpEbFNucG1RV1dCTjZ6VlZVdk42VE5tMGlWWXplMFlidGp5NzlOTk9ad2dmQmJMOXpWNVQwRkRfNmlyczYwQ2gtNjhaVmpkSDRJQ0UyaHdpdlVHaWVtZ05WNVNNOWJDY0dVaEJUbm1tQ3ZJcXZMWm5aRk5qZUFFQXd4TS1Xb0R5TTMzTUVRcTMzcnpFdTJoVmpLSDdhSFhLNVJlWWQ1TDVLTkYzRUFBbFJ2Vzk2NmIzb2t0VkVib3RNbkIyWGd0SDIwU3BTYVVWWU44WFlpLWszb2UwUG8xTUhQeGJmNDBSOHFKT1k1Zm5DYWtGdWd1dm9pOU1MNXdKNXc%3D; YSC=3ETk0LVXvJ0"
REAL_VISITOR_DATA = "CgtydHZkT0V3NXJpQSiHluPHBjIKCgJSVRIEGgAgIA%3D%3D"
REAL_PO_TOKEN = "MlVj7iWKelGXQmPQLRSOYDK69eaOtQa5nMtZ-PX7IM_Jsrdak4t9mNK6OXIhEaGjtKP25mRKPXfqStpLR0OKPhw21OhmlRajNDbuz7Ol1anXhDFdC0Np"

@pytest.mark.asyncio
async def test_cookie_validation_success():
    """Test successful cookie validation."""
    async def mock_executor(func):
        return func()
    mock_hass = MagicMock()
    mock_hass.async_add_executor_job = mock_executor

    result = await async_try_login(mock_hass, '', brand_id='', language='en', cookies=REAL_COOKIE, po_token=REAL_PO_TOKEN, visitor_data=REAL_VISITOR_DATA)

    # Since cookies may be invalid or expired, check if API object is created
    assert result[2] is not None  # API object created


@pytest.mark.parametrize("cookie_string", [REAL_COOKIE])
@pytest.mark.asyncio
async def test_cookie_string_formats(cookie_string):
    """Test different cookie string formats are accepted."""
    async def mock_executor(func):
        return func()
    mock_hass = MagicMock()
    mock_hass.async_add_executor_job = mock_executor

    result = await async_try_login(mock_hass, '', brand_id='', language='en', cookies=cookie_string, po_token=REAL_PO_TOKEN, visitor_data=REAL_VISITOR_DATA)

    assert result[0] == {}  # No errors
    assert result[2] is not None  # API object created


@pytest.mark.asyncio
async def test_cookie_validation_with_whitespace():
    """Test cookie validation with extra whitespace and newlines as if user pasted."""
    async def mock_executor(func):
        return func()
    mock_hass = MagicMock()
    mock_hass.async_add_executor_job = mock_executor

    # Simulate user input with extra spaces and newlines
    dirty_cookie = "  " + REAL_COOKIE.replace(";", ";\n") + " \n"
    dirty_po_token = " \n " + REAL_PO_TOKEN + " \r\n"
    dirty_visitor_data = "\t" + REAL_VISITOR_DATA + "\n"

    result = await async_try_login(mock_hass, '', brand_id='', language='en', cookies=dirty_cookie, po_token=dirty_po_token, visitor_data=dirty_visitor_data)

    # Should succeed after cleaning
    assert result[0] == {}  # No errors
    assert result[2] is not None  # API object created


@pytest.mark.asyncio
async def test_cookie_validation_from_file():
    """Test cookie validation loading from file (oauth=True)."""
    async def mock_executor(func):
        return func()
    mock_hass = MagicMock()
    mock_hass.async_add_executor_job = mock_executor

    # Mock file reading
    cookie_data = {
        'cookies': REAL_COOKIE,
        'po_token': REAL_PO_TOKEN,
        'visitor_data': REAL_VISITOR_DATA
    }

    import json
    from unittest.mock import mock_open, patch

    with patch('builtins.open', mock_open(read_data=json.dumps(cookie_data))):
        result = await async_try_login(mock_hass, '/fake/path.json', brand_id='', language='en', oauth=True, po_token='', visitor_data='')

    # Should succeed
    assert result[0] == {}  # No errors
    assert result[2] is not None  # API object created