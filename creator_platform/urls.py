"""
URL configuration for creator_platform project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("creator_platform.authentication.urls")),
    path("api/", include("creator_platform.creators.urls")),
]
