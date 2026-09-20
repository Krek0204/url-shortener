import pytest

from url_shortener.services.shortener import ShortenerService


@pytest.fixture
def shortener_service() -> ShortenerService:
    return ShortenerService()