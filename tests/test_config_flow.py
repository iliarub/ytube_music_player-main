"""Test cookie validation for YouTube Music Player."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from custom_components.ytube_music_player.const import (
    CONF_COOKIE, CONF_PO_TOKEN, CONF_VISITOR_DATA, CONF_NAME,
    ERROR_COOKIE_FORMAT, ERROR_MISSING_PARAM, ERROR_INVALID_COOKIE, ERROR_JSON_SYNTAX, ERROR_FORMAT,
    async_try_login
)

# Sample cookie strings provided by user
COOKIE_STRING_1 = "VISITOR_PRIVACY_METADATA=CgJERRIEEgAgRg%3D%3D; __Secure-ROLLOUT_TOKEN=CLTX3oq-mZOdrAEQs62L--O3kAMYkLyWhKCAkQM%3D; __Secure-1PSIDTS=sidts-CjUBmkD5S3rhzY6Ua_QiQ_fwqzWZE4WWyV1XSN4yqIJP5PQT3rOMYfScBDtv4MZR7cHC0LjjbxAA; __Secure-3PSIDTS=sidts-CjUBmkD5S3rhzY6Ua_QiQ_fwqzWZE4WWyV1XSN4yqIJP5PQT3rOMYfScBDtv4MZR7cHC0LjjbxAA; HSID=AZyhUxT29g6Vyat3U; SSID=AKFreLmIfPBGIlkWq; APISID=fmVcM4I4AceuMUx0/AfeOogzIcvBGRTGp8; SAPISID=lJNkJHb2J9NJQjtr/AWmAjCG8G3AMBxtmC; __Secure-1PAPISID=lJNkJHb2J9NJQjtr/AWmAjCG8G3AMBxtmC; __Secure-3PAPISID=lJNkJHb2J9NJQjtr/AWmAjCG8G3AMBxtmC; SID=g.a0002wjmoNBe6sGqb22Mdp_ZaxpjTthYC1STeD-5Z1ptOH00jXvK0oKA0HRiJ9Y75Y9Gtai3IgACgYKAXYSARMSFQHGX2MiNzIzDMlZ-j1IPwUucr9xtRoVAUF8yKpu2YoC_DrTuigC86bxNg1P0076; __Secure-1PSID=g.a0002wjmoNBe6sGqb22Mdp_ZaxpjTthYC1STeD-5Z1ptOH00jXvKcB2riAUy69y3MuE5RQpzigACgYKAX4SARMSFQHGX2MiToJq2y1_K924UoU9AXjQ7xoVAUF8yKo3Rk2uwfjYD0elUfVQEDY40076; __Secure-3PSID=g.a0002wjmoNBe6sGqb22Mdp_ZaxpjTthYC1STeD-5Z1ptOH00jXvK6J_4nFFHdR7dHmV9rkt12gACgYKAakSARMSFQHGX2Miv837YtXfSTUnbuFeCUJYixoVAUF8yKqe2D5z1E-5iS3LZaZgRgUK0076; LOGIN_INFO=AFmmF2swRQIgRuPI_O1Wjm_g2kv5LTUWHl0_yzzCAqSEB8rQainou1wCIQDq0lwjl4xZsqwC9SeLzPJGcMuIBs473UHK0rqzVdlTyg:QUQ3MjNmeFlxSUhwNVZRM09Qa0l6aVl0YWFfRTdEeXBHNmo3eC1od1pYbFRGVmM2ZUFjbllsd3F0c1FWYS02blpMVnhjaDZqME5zWWNEYkt4YmNQWjh1b2NWdmROdHoxMU9penE4N1p2Wkh1Ri1iUFFwOHozaGt1SzNUTzFUUERUY05jSFVsbGlYS2pOcWtsa1FYM1JIYmRPc1hiS19YREd3; SIDCC=AKEyXzXbSczWY2KNgOE8vrgQeF5zbFq6tVZUU3CV1Cux0Ul9IoVaL02vpPDVHzR5PpgTrCGaLA; __Secure-1PSIDCC=AKEyXzXyyEGyWMSJUAtTlVtHzGLtFAGPliNSk9AnfzqI_XBTBCUVM4DTscUhCEfxG_14NR3SpA; __Secure-3PSIDCC=AKEyXzVkPGG29eubyfCGuur9RCyHpPeajtKqx6haLNnWsFdsYZUxbtM5X2-VRxiIXE9nCBzulA; __Secure-YENID=11.YTE=hgMUtAqeqmcn5oINBEBbOaG9H084lYb4R8A5ZnM5WcNC3WKToXh6NVT_t5rPNvScAsb84atOrPtgawrj8n7QW69fnloWW5udreYV9h4Zlf-ZZifXQJomQlUlHOD1xB8_eC8wXqE07fZ9LWmbrqhKf6nDU0RvReKsysNpXAU8MNmVZB03rYftG2sxyHBWgloPKJYrHPv0xygdHFhUBIidbSkKP0nWT1_1_sdmqHTKZGeOmYOB5jN9FHcDbAKcgeEgIurvjqvEn8aVW67k49bCgUNCcuXgueXrFzdDrDmxtlFt2ZjBaS0OIh_jKW3xJVDfvQuj-bjNIFY48W-oFbUvgg; YSC=VkHQVr2Vibc; __Secure-YEC=CgtlZENNWG52NkNOcyjilPvIBjIKCgJERRIEEgAgRmLgAgrdAjExLllURT1oZ01VdEFxZXFtY241b0lOQkVCYk9hRzlIMDg0bFliNFI4QTVabk01V2NOQzNXS1RvWGg2TlZUX3Q1clBOdlNjQXNiODRhdE9yUHRnYXdyajhuN1FXNjlmbmxvV1c1dWRyZVlWOWg0WmxmLVpaaWZYUUpvbVFsVWxIT0QxeEI4X2VDOHdYcUUwN2ZaOUxXbWJycWhLZjZuRFUwUnZSZUtzeXNOcFhBVThNTm1WWkIwM3JZZnRHMnN4eUhCV2dsb1BLSllySFB2MHh5Z2RIRmhVQklpZGJTa0tQMG5XVDFfMV9zZG1xSFRLWkdlT21ZT0I1ak45RkhjRGJBS2NnZUVnSXVydmpxdkVuOGFWVzY3azQ5YkNnVU5DY3VYZ3VlWHJGemREckRteHRsRnQyWmpCYVMwT0loX2pLVzN4SlZEZnZRdWotYmpOSUZZNDhXLW9GYlV2Z2c%3D"

COOKIE_STRING_2 = "HSID=AoJG9wWSYXA0fUYWv; SSID=AAPJv2FBknu8zTlvJ; APISID=-ZGE7V4kRMABzdLd/AOp0AiNL6imkRq4_i; SAPISID=nG-a3ED9bRGC52-L/AoGvao6lDsSiuUl3k; __Secure-1PAPISID=nG-a3ED9bRGC52-L/AoGvao6lDsSiuUl3k; __Secure-3PAPISID=nG-a3ED9bRGC52-L/AoGvao6lDsSiuUl3k; LOGIN_INFO=AFmmF2swRgIhANpNopKrrFRttHv2XpSeAdYQAsyRTfHbsryqoqefjIGcAiEAu5oyanrw77OIlTbhyzMG1ZSRzhDuNNGYwfzk_PKT5EI:QUQ3MjNmeDBRRnotZkVFZkN4SHRpUGRETzNXY2UwMjVlTHoyWXdydWdwU0dsMTBDQ2M5bGw2VnBPVC1BdWVDanVoQ3pUbW9ZTlJMV2JlazIyR2ozcHd0VENWY3NlZWpiLUtIZ2JoWnpzZV9qV2JUN0dObzZoWjFUTXR4RDBNcUQ5a21XZGFzMi11Mjk3by1mRmlLbG9NSWFfZ3ZBekt3LXFn; PREF=f6=40000000&f7=4150&tz=Asia.Novosibirsk&repeat=NONE; _ga=GA1.1.1056802725.1761130280; _ga_VCGEPY40VB=GS2.1.s1761135695$o2$g0$t1761135695$j60$l0$h0; VISITOR_PRIVACY_METADATA=CgJERRIEEgAgHQ%3D%3D; SID=g.a0002wjmoIIZWJBkrbzEKjqDEFRiWUv1CtJFhDPgdRqNjbqlkhLnrXLIjhcYEB5uZFavnECl1QACgYKAeQSARMSFQHGX2MiZf5cjvjKkX8gc_kuF5fJehoVAUF8yKoZR6Ha2d2qpE9wx2XdhosL0076; __Secure-1PSID=g.a0002wjmoIIZWJBkrbzEKjqDEFRiWUv1CtJFhDPgdRqNjbqlkhLntWKmYglzBEbM63UjCNEHoQACgYKAVsSARMSFQHGX2MiDV0ZUUzkDUWWwfVACzFtmxoVAUF8yKpw1MVM3TJTJmzrX-aVsXx40076; YSC=MKxvSbBEx34; __Secure-3PSID=g.a0002wjmoIIZWJBkrbzEKjqDEFRiWUv1CtJFhDPgdRqNjbqlkhLnwbBhFpoXOCnGEAWVombHFwACgYKAc4SARMSFQHGX2Mi8ChnmbYCiGloAJp0vUE24BoVAUF8yKrVUidmCK6LjrPwmLBnAw-R0076; __Secure-ROLLOUT_TOKEN=CI2qkPa6qNzdChDs19f0ya6KAxiqsL2vhYCRAw%3D%3D; NID=526=c6D6T7md6m9RI42JLyDB2CySlmYWPVndmapY4AxI_MS0-XK425wUccOWHqFUJEwAMQlk_xZl9iUcKRfS80GR6_Tmm_allq9FrDf9aUy4poMGlj-3C-Hs8eyzn5SR-q_q4eAx4VqEXzgifB0_HanJeJuEZNxKHd8vNG1D3FVUPt8acI2HL5sO3pej3rueDT5nQWgm1i0oa3qtyK48DtA-7YVB8L0FSf4CdqMVgKg; __Secure-1PSIDTS=sidts-CjQBwQ9iIwQg0s3GgN9sGcWk6jrWO5IuAN-ivvJj431_NgOoHQ-slWbpP_47QnP0Gi0PE4FrEAA; __Secure-3PSIDTS=sidts-CjQBwQ9iIwQg0s3GgN9sGcWk6jrWO5IuAN-ivvJj431_NgOoHQ-slWbpP_47QnP0Gi0PE4FrEAA; __Secure-YEC=CgtXaXhubE1RNmpmMCjmk_vIBjIKCgJERRIEEgAgHQ%3D%3D; SIDCC=AKEyXzVg0ejA6s-ug2Rwv1aKcsojHgC5pn-pJY-bJHL2sQ3-QqUj6AS9hpE4vOdrxEhSVidUuMbg; __Secure-1PSIDCC=AKEyXzW-ni68QVlfSkO3QVNv1U_Aht_hxmKt5zy-CNCubwTnoGyfWowwlKta5CODzRA3MJxfnAGC; __Secure-3PSIDCC=AKEyXzXhTcjB37khbm8VvGxx2J6U_wjPhK5WMWDJkHSvF4KBGKfPpSu114Npueat3CIIqk4eyPSQ"

VISITOR_DATA = "CgtXaXhubE1RNmpmMCj_jvvIBjIKCgJERRIEEgAgHQ%3D%3D"

@pytest.mark.asyncio
async def test_cookie_validation_success():
    """Test successful cookie validation."""
    mock_hass = MagicMock()
    mock_api = MagicMock()
    mock_api.get_library_songs.return_value = []
    mock_hass.async_add_executor_job = AsyncMock(return_value=mock_api)

    result = await async_try_login(mock_hass, '', cookies=COOKIE_STRING_1, po_token='', visitor_data=VISITOR_DATA)

    assert result[0] == {}  # No errors
    assert result[2] is mock_api  # API object created

    # Check that executor_job was called
    assert mock_hass.async_add_executor_job.call_count >= 1

@pytest.mark.asyncio
async def test_cookie_validation_invalid():
    """Test invalid cookie validation."""
    mock_hass = MagicMock()
    mock_hass.async_add_executor_job = AsyncMock(side_effect=Exception("403 Forbidden"))

    result = await async_try_login(mock_hass, '', cookies="invalid", po_token='', visitor_data='')

    assert "base" in result[0]
    assert result[0]["base"] == ERROR_FORMAT
    assert result[2] is None

@pytest.mark.parametrize("cookie_string", [COOKIE_STRING_1, COOKIE_STRING_2])
@pytest.mark.asyncio
async def test_cookie_string_formats(cookie_string):
    """Test different cookie string formats are accepted."""
    mock_hass = MagicMock()
    mock_hass.async_add_executor_job = AsyncMock()

    # Mock successful API response
    with patch('custom_components.ytube_music_player.const.YTMusic') as mock_ytm:
        mock_api = MagicMock()
        mock_ytm.return_value = mock_api
        mock_api.get_library_songs.return_value = []

        result = await async_try_login(mock_hass, '', cookies=cookie_string, po_token='', visitor_data=VISITOR_DATA)

    assert result[0] == {}  # No errors
    assert result[2] is not None  # API object created