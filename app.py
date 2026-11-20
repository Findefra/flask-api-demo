"""
Flask REST API Demo with SQLAlchemy database integration.
Uses SQLite by default. Set DATABASE_URL to switch to PostgreSQL or other DBs.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import inspect
import os
import uuid

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
# Default: SQLite file in the project directory (good for local / demos)
# Production example: postgresql+psycopg2://user:pass@host:5432/dbname
database_url = os.environ.get("DATABASE_URL", "sqlite:///items.db")

# Handle Heroku-style postgres:// URLs
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,  # useful for cloud databases
}

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Create tables on startup (simple approach; use Flask-Migrate / Alembic for production)
with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for load balancers and Kubernetes probes."""
    db_status = "unknown"
    try:
        # Lightweight check that the database is reachable
        inspect(db.engine).get_table_names()
        db_status = "connected"
    except Exception:
        db_status = "unavailable"

    status_code = 200 if db_status == "connected" else 503
    return jsonify({
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "flask-api-demo",
    }), status_code


@app.route("/api/v1/items", methods=["GET"])
def list_items():
    """Return all items."""
    items = Item.query.order_by(Item.created_at.desc()).all()
    return jsonify({
        "count": len(items),
        "items": [item.to_dict() for item in items],
    }), 200


@app.route("/api/v1/items/<item_id>", methods=["GET"])
def get_item(item_id):
    """Return a single item by ID."""
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item.to_dict()), 200


@app.route("/api/v1/items", methods=["POST"])
def create_item():
    """Create a new item."""
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Field 'name' is required and must be a non-empty string"}), 400

    item = Item(
        name=name.strip(),
        description=data.get("description", "") or "",
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route("/api/v1/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    """Update an existing item."""
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = data["name"]
        if not name or not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Field 'name' must be a non-empty string"}), 400
        item.name = name.strip()

    if "description" in data:
        item.description = data.get("description", "") or ""

    db.session.commit()
    return jsonify(item.to_dict()), 200


@app.route("/api/v1/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete an item."""
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return "", 204


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
