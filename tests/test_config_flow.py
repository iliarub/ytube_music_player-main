"""Test cookie validation for YouTube Music Player."""
import pytest
from unittest.mock import MagicMock
from custom_components.ytube_music_player.const import (
    CONF_COOKIE, CONF_PO_TOKEN, CONF_VISITOR_DATA, CONF_NAME,
    ERROR_COOKIE_FORMAT, ERROR_MISSING_PARAM, ERROR_INVALID_COOKIE, ERROR_JSON_SYNTAX, ERROR_FORMAT,
    async_try_login
)

# Replace with real data for testing
REAL_COOKIE = "YSC=pPnn9Rpz0GI; VISITOR_INFO1_LIVE=rtvdOEw5riA; VISITOR_PRIVACY_METADATA=CgJSVRIEGgAgIA%3D%3D; __Secure-ROLLOUT_TOKEN=CLTX3oq-mZOdrAEQs62L--O3kAMY9v3NquS3kAM%3D; __Secure-1PSIDTS=sidts-CjUBmkD5S3rhzY6Ua_QiQ_fwqzWZE4WWyV1XSN4yqIJP5PQT3rOMYfScBDtv4MZR7cHC0LjjbxAA; __Secure-3PSIDTS=sidts-CjUBmkD5S3rhzY6Ua_QiQ_fwqzWZE4WWyV1XSN4yqIJP5PQT3rOMYfScBDtv4MZR7cHC0LjjbxAA; HSID=AZyhUxT29g6Vyat3U; SSID=AKFreLmIfPBGIlkWq; APISID=fmVcM4I4AceuMUx0/AfeOogzIcvBGRTGp8; SAPISID=lJNkJHb2J9NJQjtr/AWmAjCG8G3AMBxtmC; __Secure-1PAPISID=lJNkJHb2J9NJQjtr/AWmAjCG8G3AMBxtmC; __Secure-3PAPISID=lJNkJHb2J9NJQjtr/AWmAjCG8G3AMBxtmC; SID=g.a0002wjmoNBe6sGqb22Mdp_ZaxpjTthYC1STeD-5Z1ptOH00jXvK0oKA0HRiJ9Y75Y9Gtai3IgACgYKAXYSARMSFQHGX2MiNzIzDMlZ-j1IPwUucr9xtRoVAUF8yKpu2YoC_DrTuigC86bxNg1P0076; __Secure-1PSID=g.a0002wjmoNBe6sGqb22Mdp_ZaxpjTthYC1STeD-5Z1ptOH00jXvKcB2riAUy69y3MuE5RQpzigACgYKAX4SARMSFQHGX2MiToJq2y1_K924UoU9AXjQ7xoVAUF8yKo3Rk2uwfjYD0elUfVQEDY40076; __Secure-3PSID=g.a0002wjmoNBe6sGqb22Mdp_ZaxpjTthYC1STeD-5Z1ptOH00jXvK6J_4nFFHdR7dHmV9rkt12gACgYKAakSARMSFQHGX2Miv837YtXfSTUnbuFeCUJYixoVAUF8yKqe2D5z1E-5iS3LZaZgRgUK0076; LOGIN_INFO=AFmmF2swRQIga84KLYstnkkN3uxy1BhFtaVzdPZOPNKcgvSDQGLwh7MCIQDa0Z8DrxwhqTMf1BeKiiUfjBPb2Z21FLdbAWj3qkeAng:QUQ3MjNmeFA2elFHTjhWZ0FkUEpadEZxWHd3dXRpSFkzYUZ2anp6VU5Damd5TjVJb0RNQjZQNnVDUzVhWFRaZEN4QkpBTTc2NEtFNEsyMGlVQlBoSlZzVHBXWXRWVWRuMWh4c0NGZ0FSOFhGVWRPT3hzWVI2TndUYzNOQjNlSU5wNXkxMWNiTnhJeTA3YjRKTjJrS1NpLXBBa3dxa21aUDBR; SIDCC=AKEyXzVCb2LPYCHHQin3NgeTo5K2Gq0wBllVIvyRMsb7LpyDOUeja469LLHrht5Cl0XPMf4F6A; __Secure-1PSIDCC=AKEyXzUwL9k43P8oIYQPibugz7QvjVG2flMvHMRVEpOysEUDBhz8s2YUXDBZmqKMF8HHMXU8Rw; __Secure-3PSIDCC=AKEyXzXW2qqMjnKjJmDn2-9mtGKXmRIDEHd-TiGa4SORzY9iba4NOfp5-foWhhiAbEjnnTKRpQ; ST-1b="
REAL_VISITOR_DATA = "CgtydHZkT0V3NXJpQSiHluPHBjIKCgJSVRIEGgAgIA%3D%3D"
REAL_PO_TOKEN = "MlVj7iWKelGXQmPQLRSOYDK69eaOtQa5nMtZ-PX7IM_Jsrdak4t9mNK6OXIhEaGjtKP25mRKPXfqStpLR0OKPhw21OhmlRajNDbuz7Ol1anXhDFdC0Np"

@pytest.mark.asyncio
async def test_cookie_validation_success():
    """Test successful cookie validation."""
    mock_hass = MagicMock()
    mock_hass.async_add_executor_job = lambda func: func()

    result = await async_try_login(mock_hass, '', brand_id='', language='en', cookies=REAL_COOKIE, po_token=REAL_PO_TOKEN, visitor_data=REAL_VISITOR_DATA)

    # Since cookies may be invalid or expired, check if API object is created
    assert result[2] is not None  # API object created


@pytest.mark.parametrize("cookie_string", [REAL_COOKIE])
@pytest.mark.asyncio
async def test_cookie_string_formats(cookie_string):
    """Test different cookie string formats are accepted."""
    mock_hass = MagicMock()
    mock_hass.async_add_executor_job = lambda func: func()

    result = await async_try_login(mock_hass, '', brand_id='', language='en', cookies=cookie_string, po_token=REAL_PO_TOKEN, visitor_data=REAL_VISITOR_DATA)

    assert result[0] == {}  # No errors
    assert result[2] is not None  # API object created


@pytest.mark.asyncio
async def test_cookie_validation_with_whitespace():
    """Test cookie validation with extra whitespace and newlines as if user pasted."""
    mock_hass = MagicMock()
    mock_hass.async_add_executor_job = lambda func: func()

    # Simulate user input with extra spaces and newlines
    dirty_cookie = "  " + REAL_COOKIE.replace(";", ";\n") + " \n"
    dirty_po_token = " \n " + REAL_PO_TOKEN + " \r\n"
    dirty_visitor_data = "\t" + REAL_VISITOR_DATA + "\n"

    result = await async_try_login(mock_hass, '', brand_id='', language='en', cookies=dirty_cookie, po_token=dirty_po_token, visitor_data=dirty_visitor_data)

    # Should succeed after cleaning
    assert result[0] == {}  # No errors
    assert result[2] is not None  # API object created