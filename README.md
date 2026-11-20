# Flask API Demo

A clean, production-oriented Flask REST API example.

## Features

- Health check endpoint (`/health`) suitable for Kubernetes/load balancer probes
- Full CRUD for items (`/api/v1/items`)
- Input validation
- CORS enabled
- Gunicorn production server
- Non-root Docker image
- Proper error handling

## Quick Start (Local)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export FLASK_DEBUG=true
python app.py
```

API will be available at `http://localhost:5000`

## Endpoints

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| GET    | `/health`               | Health check             |
| GET    | `/api/v1/items`         | List all items           |
| GET    | `/api/v1/items/<id>`    | Get single item          |
| POST   | `/api/v1/items`         | Create item              |
| PUT    | `/api/v1/items/<id>`    | Update item              |
| DELETE | `/api/v1/items/<id>`    | Delete item              |

### Example Requests

```bash
# Health
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

## Production Notes

- Replace the in-memory store with a real database (PostgreSQL, DynamoDB, etc.)
- Add authentication (JWT, API keys, or OIDC)
- Add structured logging and metrics
- Use environment variables for configuration
- Consider adding rate limiting and request validation libraries (e.g. pydantic + flask-pydantic)

## License

MIT
