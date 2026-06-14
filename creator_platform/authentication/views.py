import hashlib
import secrets

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import APIKey
from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        raw_key = secrets.token_hex(32)
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
        
        APIKey.objects.create(prefix = raw_key[:12], hashed_key = hashed_key, user=user)

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "api_key": raw_key,
            },
            status=status.HTTP_201_CREATED,
        )
