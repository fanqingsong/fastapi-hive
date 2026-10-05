

import secrets
from typing import Optional

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from example.cornerstone import config
from example.cornerstone.messages import AUTH_REQ, NO_API_KEY

api_key = APIKeyHeader(name="token", auto_error=False)


def validate_header(header: Optional[str]) -> bool:
    if header is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=NO_API_KEY, headers={}
        )
    if not secrets.compare_digest(header, str(config.API_KEY)):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=AUTH_REQ, headers={}
        )
    return True


def validate_request(header: Optional[str] = Security(api_key)) -> bool:
    return validate_header(header)


def validate_http_request(request: Request) -> bool:
    return validate_header(request.headers.get("token"))
