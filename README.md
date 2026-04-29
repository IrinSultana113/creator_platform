# Creator Discovery & Enrichment API

A Django/DRF API for discovering content creators via Elasticsearch and enriching creator profiles (single + bulk CSV).

**Stack:** Python 3.11, Django 5.x, DRF, PostgreSQL 15, Elasticsearch 8.x, Docker

## Getting Started

```bash
docker compose up --build
```

First startup takes 1–2 minutes (waits for services, runs migrations, loads 100 seed creators into Elasticsearch).

API available at **http://localhost:8000**.

## API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | None | Register user, returns API key |

### Discovery & Enrichment
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/discovery/` | API Key | Search creators with filters |
| GET | `/api/enrich/creator/` | API Key | Enrich single creator by `?username=` |
| POST | `/api/enrich/bulk/` | API Key | Upload CSV with `username` column, returns enriched export |
| GET | `/api/exports/<id>/download/` | API Key | Download enriched CSV |

## Quick Test

```bash
# Register (returns an API key)
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123", "password_confirm": "testpass123", "email": "test@example.com"}'

# Search creators (use the api_key from register response)
curl http://localhost:8000/api/discovery/?q=fitness \
  -H "Authorization: Api-Key <your_api_key>"

# Enrich a single creator
curl http://localhost:8000/api/enrich/creator/?username=janesmith \
  -H "Authorization: Api-Key <your_api_key>"

# Bulk enrich (upload CSV with username column)
echo "username
janesmith
marcusjfit
priyalaugh" > /tmp/creators.csv

curl -X POST http://localhost:8000/api/enrich/bulk/ \
  -H "Authorization: Api-Key <your_api_key>" \
  -F "file=@/tmp/creators.csv"

# Download enriched CSV (use the id from bulk response)
curl http://localhost:8000/api/exports/1/download/ \
  -H "Authorization: Api-Key <your_api_key>"
```
