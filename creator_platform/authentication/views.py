import uuid

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

        raw_key = uuid.uuid4().hex
        APIKey.objects.create(key=raw_key, user=user)

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "api_key": raw_key,
            },
            status=status.HTTP_201_CREATED,
        )
