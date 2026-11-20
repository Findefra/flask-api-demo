# Flask API Demo

A clean, production-oriented Flask REST API with **SQLAlchemy database integration**.

## Features

- SQLAlchemy + Flask-SQLAlchemy
- SQLite by default (zero config for local development)
- Easily switch to PostgreSQL (or any SQLAlchemy-supported DB) via `DATABASE_URL`
- Health check includes database connectivity status
- Full CRUD for items (`/api/v1/items`)
- Input validation
- CORS enabled
- Gunicorn production server
- Non-root Docker image
- Proper error handling + transaction rollback

## Quick Start (Local)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export FLASK_DEBUG=true
python app.py
```

API will be available at `http://localhost:5000`

A SQLite database file (`items.db`) is created automatically on first run.

## Database Configuration

| Environment Variable | Default              | Description                          |
|----------------------|----------------------|--------------------------------------|
| `DATABASE_URL`       | `sqlite:///items.db` | Full SQLAlchemy connection string    |

### Examples

```bash
# SQLite (default)
export DATABASE_URL="sqlite:///items.db"

# PostgreSQL
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/flask_demo"

# Docker + external Postgres
docker run -e DATABASE_URL="postgresql+psycopg2://..." -p 5000:5000 flask-api-demo
```

> Note: Uncomment `psycopg2-binary` in `requirements.txt` when using PostgreSQL.

## Endpoints

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| GET    | `/health`               | Health check + DB status |
| GET    | `/api/v1/items`         | List all items           |
| GET    | `/api/v1/items/<id>`    | Get single item          |
| POST   | `/api/v1/items`         | Create item              |
| PUT    | `/api/v1/items/<id>`    | Update item              |
| DELETE | `/api/v1/items/<id>`    | Delete item              |

### Example Requests

```bash
# Health (now also reports database status)
curl http://localhost:5000/health

# Create item
curl -X POST http://localhost:5000/api/v1/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Sample Item", "description": "My first item"}'

# List items
curl http://localhost:5000/api/v1/items
```

## Docker

```bash
docker build -t flask-api-demo .
docker run -p 5000:5000 flask-api-demo
```

For persistent SQLite data:

```bash
docker run -p 5000:5000 -v $(pwd)/data:/app flask-api-demo
```

## Production Notes

- For schema changes, prefer **Flask-Migrate / Alembic** instead of `db.create_all()`
- Add authentication (JWT, API keys, or OIDC)
- Add structured logging and metrics
- Use connection pooling and proper secrets management
- Consider rate limiting and stronger request validation (e.g. Pydantic)

## License

MIT
