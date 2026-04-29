from elasticsearch_dsl import Document, Float, Integer, Keyword, Text


class CreatorDocument(Document):
    username = Keyword()
    name = Text()
    platform = Keyword()
    followers_count = Integer()
    engagement_rate = Float()
    niche = Keyword()
    location = Text()
    bio = Text()
    profile_url = Keyword()

    class Index:
        name = "creators"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}
