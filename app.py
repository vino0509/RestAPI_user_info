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
    key = request.headers.get("x-api-key")  # standard header
    if key != API_KEY:
        abort(401, description="Unauthorized: Invalid or missing API key")

# Create the database and table if not exists
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
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

# Add new user
@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    if not data or "name" not in data:
        abort(400, description="Bad Request: 'name' is required")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("INSERT INTO users (name) VALUES (?)", (data["name"],))
        conn.commit()
        new_id = cursor.lastrowid
    return jsonify({"message": "User added", "id": new_id}), 201

# Update user
@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.json
    if not data or "name" not in data:
        abort(400, description="Bad Request: 'name' is required")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("UPDATE users SET name = ? WHERE id = ?", (data["name"], id))
        conn.commit()
        if cursor.rowcount == 0:
            abort(404, description=f"User {id} not found")
    return jsonify({"message": f"User {id} updated", "new_name": data["name"]})

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
