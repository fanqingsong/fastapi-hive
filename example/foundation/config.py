

from pathlib import Path

from starlette.config import Config
from starlette.datastructures import Secret

APP_VERSION = "0.0.1"
APP_NAME = "House Price Prediction Example"
API_PREFIX = "/api"

EXAMPLE_DIR = Path(__file__).resolve().parents[1]
config = Config(str(EXAMPLE_DIR / ".env"))

API_KEY: Secret = config("API_KEY", cast=Secret)
IS_DEBUG: bool = config("IS_DEBUG", cast=bool, default=False)


def _database_url() -> str:
    url = config("DATABASE_URL", cast=str)
    prefix = "sqlite:///"
    if not url.startswith(prefix) or url.startswith("sqlite:////"):
        return url
    location = url[len(prefix):]
    if location == ":memory:" or Path(location).is_absolute():
        return url
    return prefix + str(EXAMPLE_DIR / location)


DATABASE_URL: str = _database_url()
