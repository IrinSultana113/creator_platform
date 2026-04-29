import csv
import io

from django.conf import settings
from django.http import HttpResponse
from elasticsearch_dsl import Search
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EnrichmentExport


def _get_es_connection():
    from elasticsearch import Elasticsearch

    return Elasticsearch(settings.ELASTICSEARCH_URL)


class DiscoveryView(APIView):
    """Search creators in Elasticsearch with filters."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q", "")
        platform = request.query_params.get("platform", "")
        niche = request.query_params.get("niche", "")
        min_followers = request.query_params.get("min_followers")
        max_followers = request.query_params.get("max_followers")
        location = request.query_params.get("location", "")

        es = _get_es_connection()
        search = Search(using=es, index="creators")

        if q:
            search = search.query(
                "multi_match",
                query=q,
                fields=["name", "bio", "niche", "location"],
            )

        if platform:
            search = search.filter("term", platform=platform)

        if niche:
            search = search.filter("term", niche=niche)

        if location:
            search = search.query("match", location=location)

        followers_filter = {}
        if min_followers:
            followers_filter["gte"] = int(min_followers)
        if max_followers:
            followers_filter["lte"] = int(max_followers)

        if followers_filter:
            search = search.filter("range", followers_count=followers_filter)

        response = search.execute()

        results = []
        for hit in response:
            results.append(
                {
                    "username": hit.username,
                    "name": hit.name,
                    "platform": hit.platform,
                    "followers_count": hit.followers_count,
                    "engagement_rate": hit.engagement_rate,
                    "niche": hit.niche,
                    "location": hit.location,
                    "bio": hit.bio,
                    "profile_url": hit.profile_url,
                    "score": hit.meta.score,
                }
            )

        return Response(
            {
                "count": response.hits.total.value,
                "results": results,
            }
        )


class EnrichCreatorView(APIView):
    """Enrich a single creator by username lookup in Elasticsearch."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.query_params.get("username", "").strip()
        if not username:
            return Response(
                {"error": "username query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        es = _get_es_connection()
        search = Search(using=es, index="creators")
        search = search.query("term", username=username)
        response = search.execute()

        if not response.hits:
            return Response(
                {"error": f"Creator with username '{username}' not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        hit = response.hits[0]
        return Response(
            {
                "username": hit.username,
                "name": hit.name,
                "platform": hit.platform,
                "followers_count": hit.followers_count,
                "engagement_rate": hit.engagement_rate,
                "niche": hit.niche,
                "location": hit.location,
                "bio": hit.bio,
                "profile_url": hit.profile_url,
            }
        )


class BulkEnrichView(APIView):
    """Upload a CSV with a username column, enrich each creator from ES."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response(
                {"error": "A CSV file is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        decoded = csv_file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))
        usernames = [row["username"].strip() for row in reader]

        es = _get_es_connection()

        enriched_rows = []
        not_found = []

        for username in usernames:
            search = Search(using=es, index="creators")
            search = search.query("term", username=username)
            response = search.execute()

            if response.hits:
                hit = response.hits[0]
                enriched_rows.append(
                    {
                        "username": hit.username,
                        "name": hit.name,
                        "platform": hit.platform,
                        "followers_count": hit.followers_count,
                        "engagement_rate": hit.engagement_rate,
                        "niche": hit.niche,
                        "location": hit.location,
                        "bio": hit.bio,
                        "profile_url": hit.profile_url,
                    }
                )
            else:
                not_found.append(username)

        # Build CSV content
        output = io.StringIO()
        fieldnames = [
            "username",
            "name",
            "platform",
            "followers_count",
            "engagement_rate",
            "niche",
            "location",
            "bio",
            "profile_url",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in enriched_rows:
            writer.writerow(row)

        csv_content = output.getvalue()

        export = EnrichmentExport.objects.create(
            name=f"bulk_enrich_{len(enriched_rows)}_creators",
            csv_content=csv_content,
            owner=request.user,
        )

        return Response(
            {
                "id": export.id,
                "name": export.name,
                "download_url": f"/api/exports/{export.id}/download/",
                "enriched_count": len(enriched_rows),
                "not_found_count": len(not_found),
                "created_at": export.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class ExportDownloadView(APIView):
    """Download an enrichment export as a CSV file."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            export = EnrichmentExport.objects.get(pk=pk, owner=request.user)
        except EnrichmentExport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        response = HttpResponse(export.csv_content, content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{export.name}.csv"'
        )
        return response
