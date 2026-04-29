from django.urls import path

from . import views

urlpatterns = [
    path("discovery/", views.DiscoveryView.as_view(), name="discovery"),
    path("enrich/creator/", views.EnrichCreatorView.as_view(), name="enrich-creator"),
    path("enrich/bulk/", views.BulkEnrichView.as_view(), name="enrich-bulk"),
    path(
        "exports/<int:pk>/download/",
        views.ExportDownloadView.as_view(),
        name="export-download",
    ),
]
