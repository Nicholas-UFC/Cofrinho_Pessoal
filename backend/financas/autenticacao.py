from typing import Any

from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Lê o token JWT do cookie 'access' — OWASP prática 76."""

    def authenticate(self, request: Request) -> tuple[Any, Any] | None:  # type: ignore[override]
        raw_token = request.COOKIES.get("access")
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
