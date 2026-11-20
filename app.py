"""
Flask REST API Demo
A clean, production-oriented example suitable for interviews and learning.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timezone
import uuid
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend testing

# Simple in-memory store (replace with a real DB in production)
items = {}


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for load balancers and Kubernetes probes."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "flask-api-demo"
    }), 200


@app.route("/api/v1/items", methods=["GET"])
def list_items():
    """Return all items."""
    return jsonify({
        "count": len(items),
        "items": list(items.values())
    }), 200


@app.route("/api/v1/items/<item_id>", methods=["GET"])
def get_item(item_id):
    """Return a single item by ID."""
    item = items.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/api/v1/items", methods=["POST"])
def create_item():
    """Create a new item."""
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Field 'name' is required and must be a non-empty string"}), 400

    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "name": name.strip(),
        "description": data.get("description", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    items[item_id] = item
    return jsonify(item), 201


@app.route("/api/v1/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    """Update an existing item."""
    if item_id not in items:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True) or {}
    item = items[item_id]

    if "name" in data:
        name = data["name"]
        if not name or not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Field 'name' must be a non-empty string"}), 400
        item["name"] = name.strip()

    if "description" in data:
        item["description"] = data.get("description", "")

    item["updated_at"] = datetime.now(timezone.utc).isoformat()
    return jsonify(item), 200


@app.route("/api/v1/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete an item."""
    if item_id not in items:
        return jsonify({"error": "Item not found"}), 404
    del items[item_id]
    return "", 204


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
