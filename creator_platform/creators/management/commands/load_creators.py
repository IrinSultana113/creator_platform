import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch, helpers


class Command(BaseCommand):
    help = "Load creator data from seed_data/creators.json into Elasticsearch"

    def handle(self, *args, **options):
        seed_file = Path(__file__).resolve().parents[4] / "seed_data" / "creators.json"

        if not seed_file.exists():
            self.stderr.write(self.style.ERROR(f"Seed file not found: {seed_file}"))
            return

        with open(seed_file, "r", encoding="utf-8") as f:
            creators_data = json.load(f)

        es = Elasticsearch(
        settings.ELASTICSEARCH_URL,
        basic_auth=(
            settings.ELASTICSEARCH_USERNAME,
            settings.ELASTICSEARCH_PASSWORD,
        ),
        verify_certs=False,
        )

        index_name = "creators"

        if not es.indices.exists(index=index_name):
            es.indices.create(
                index=index_name,
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                    },
                    "mappings": {
                        "properties": {
                            "username": {"type": "keyword"},
                            "name": {"type": "text"},
                            "platform": {"type": "keyword"},
                            "followers_count": {"type": "integer"},
                            "engagement_rate": {"type": "float"},
                            "niche": {"type": "keyword"},
                            "location": {"type": "text"},
                            "bio": {"type": "text"},
                            "profile_url": {"type": "keyword"},
                        }
                    },
                },
            )
            self.stdout.write(self.style.SUCCESS(f"Created index '{index_name}'"))

        actions = []
        for entry in creators_data:
            actions.append(
                {
                    "_index": index_name,
                    "_id": entry["id"],
                    "_source": {
                        "username": entry["username"],
                        "name": entry["name"],
                        "platform": entry["platform"],
                        "followers_count": entry["followers_count"],
                        "engagement_rate": entry["engagement_rate"],
                        "niche": entry["niche"],
                        "location": entry.get("location", ""),
                        "bio": entry.get("bio", ""),
                        "profile_url": entry["profile_url"],
                    },
                }
            )

        success, failed = helpers.bulk(es, actions, raise_on_error=False)

        self.stdout.write(
            self.style.SUCCESS(f"Indexed {success} creators into Elasticsearch")
        )

        if failed:
            self.stderr.write(self.style.ERROR(f"Some errors occurred: {failed}"))