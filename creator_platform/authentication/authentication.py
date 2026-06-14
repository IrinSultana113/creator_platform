import hashlib

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    keyword = "Api-Key"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None

        raw_key = auth_header[len(self.keyword) + 1 :]

        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()

        try:
            api_key = APIKey.objects.select_related("user").get(
                hashed_key = hashed_key, is_active=True,
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive API key.")

        return (api_key.user, api_key)
