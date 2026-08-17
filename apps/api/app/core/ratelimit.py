"""Rate limit login — slowapi (FR-AUTH-08).

Batas dari ``settings.ratelimit_login`` (default "10/15minutes"). Dua kunci
independen: alamat IP dan alamat email dari body.
"""

import json

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)


def login_ip_key(request: Request) -> str:
    return get_remote_address(request)


def login_email_key(request: Request) -> str:
    try:
        body = json.loads(request._body) if request._body else {}
        return str(body.get("email", "")).lower()
    except Exception:
        return ""


def login_rate() -> str:
    return settings.ratelimit_login
