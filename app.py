import sqlite3
from flask import Flask, jsonify, request, abort
import os

app = Flask(__name__)

API_KEY = "vinothbaburajkumar"
DATABASE = 'users.db'

# Middleware to check API key
@app.before_request
def check_api_key():
    if request.endpoint == 'home':
        return
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        abort(401, description="Unauthorized: Invalid or missing API key")

# Create the database and table if not exists
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)')
        conn.commit()

# Convert DB row to dict
def to_dict(row):
    return {"id": row[0], "name": row[1]}

@app.route('/')
def home():
    return "Flask app deployed with SQLite and API Key!"

# Get all users
@app.route("/users", methods=["GET"])
def get_users():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT * FROM users")
        users = [to_dict(row) for row in cursor.fetchall()]
    return jsonify(users)

# Add new user (only name, id auto-generated)
@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    if not data or "name" not in data:
        abort(400, description="Bad Request: 'name' is required")

    name = data["name"].strip()

    with sqlite3.connect(DATABASE) as conn:
        # Check if name already exists
        cursor = conn.execute("SELECT id FROM users WHERE name = ?", (name,))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"message": "User already exists", "id": existing[0]}), 200

        # Insert new user
        cursor = conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        new_id = cursor.lastrowid

    return jsonify({"message": "User added", "id": new_id, "name": name}), 201

# Update user
@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.json
    if not data or "name" not in data:
        abort(400, description="Bad Request: 'name' is required")

    new_name = data["name"].strip()

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, id))
        conn.commit()
        if cursor.rowcount == 0:
            abort(404, description=f"User {id} not found")

    return jsonify({"message": f"User {id} updated", "new_name": new_name})

# Delete user
@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("DELETE FROM users WHERE id = ?", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            abort(404, description=f"User {id} not found")
    return jsonify({"message": f"User {id} deleted"})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
