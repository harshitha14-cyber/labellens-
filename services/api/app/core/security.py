"""Supabase JWT verification.

Accepts either an HS256 shared secret (Supabase local/dev default) or an asymmetric
key set via JWKS (newer Supabase projects). The algorithm is pinned per mode, so a
token cannot choose its own algorithm (blocks alg=none / key-confusion attacks).
"""
from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import Depends, Request
from jwt import PyJWKClient

from app.core.config import Settings, get_settings
from app.core.errors import ApiError


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str | None
    claims: dict[str, Any]


_jwks_clients: dict[str, PyJWKClient] = {}


def verify_token(token: str, settings: Settings) -> dict[str, Any]:
    try:
        if settings.supabase_jwks_url:
            client = _jwks_clients.setdefault(settings.supabase_jwks_url, PyJWKClient(settings.supabase_jwks_url))
            key = client.get_signing_key_from_jwt(token).key
            algs = ["ES256", "RS256"]
        elif settings.supabase_jwt_secret:
            key, algs = settings.supabase_jwt_secret, ["HS256"]
        else:
            raise ApiError(500, "INTERNAL", "Server auth is not configured")
        claims: dict[str, Any] = jwt.decode(
            token, key, algorithms=algs, audience=settings.jwt_audience,
            options={"require": ["exp", "sub"]},
        )
    except ApiError:
        raise
    except jwt.ExpiredSignatureError:
        raise ApiError(401, "UNAUTHENTICATED", "Token expired") from None
    except jwt.PyJWTError:
        raise ApiError(401, "UNAUTHENTICATED", "Invalid token") from None
    if claims.get("role") not in (None, "authenticated"):
        raise ApiError(401, "UNAUTHENTICATED", "Not an authenticated user token")
    return claims


def current_user(request: Request, settings: Settings = Depends(get_settings)) -> AuthUser:
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise ApiError(401, "UNAUTHENTICATED", "Missing bearer token")
    claims = verify_token(token, settings)
    return AuthUser(id=str(claims["sub"]), email=claims.get("email"), claims=claims)
