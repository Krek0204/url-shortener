from url_shortener.services.shortener import ShortenerService


def test_create_code(shortener_service: ShortenerService):
    assert shortener_service.create_code(1) == '1'

    