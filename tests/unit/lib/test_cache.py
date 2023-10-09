from typing import TYPE_CHECKING

from litestar.config.response_cache import default_cache_key_builder
from litestar.testing import RequestFactory

from app.config import cache_key_builder
from app.lib.settings import Settings

if TYPE_CHECKING:
    import pytest


def test_cache_key_builder(monkeypatch: "pytest.MonkeyPatch") -> None:
    monkeypatch.setattr(Settings, "app_slug", "the-slug")
    request = RequestFactory().get("/test")
    default_cache_key = default_cache_key_builder(request)
    assert cache_key_builder(request) == f"the-slug:{default_cache_key}"
