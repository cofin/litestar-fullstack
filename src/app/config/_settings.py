from app.lib.settings import BASE_DIR, TEMPLATES_DIR, load_settings

settings = load_settings()

__all__ = ("settings", "BASE_DIR", "TEMPLATES_DIR")
