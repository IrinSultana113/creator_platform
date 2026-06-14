import hashlib
from django.conf import settings
from django.db import models


class APIKey(models.Model):
    prefix = models.CharField(max_length = 12, db_index = True)
    hashed_key = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"APIKey for {self.user.username}"
