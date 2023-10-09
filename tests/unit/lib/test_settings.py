from app.lib import settings


def test_app_slug() -> None:
    """Test app name conversion to slug."""
    settings.APP_NAME = "My Application!"
    assert settings.app_slug == "my-application"
