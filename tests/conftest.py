

import pytest
from starlette.config import environ
from starlette.testclient import TestClient

environ["API_KEY"] = "a1279d26-63ac-41f1-8266-4ef3702ad7cb"


from fastapi_modules.main import get_app  # noqa: E402


@pytest.fixture()
def test_client():
    app = get_app()
    with TestClient(app) as test_client:
        yield test_client
