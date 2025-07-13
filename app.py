from flask import Flask, jsonify, request
import os
import sqlite3

app = Flask(__name__)
DATABASE = 'users.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
        conn.commit()

def to_dict(row):
    return {"id": row[0], "name": row[1]}

@app.route('/')
def home():
    return "Flask app deployed on Render!"

@app.route("/users", methods=["GET"])
def get_users():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT * FROM users")
        users = [to_dict(row) for row in cursor.fetchall()]
    return jsonify(users)

@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("INSERT INTO users (id, name) VALUES (?, ?)", (data["id"], data["name"]))
        conn.commit()
    return jsonify({"message": "User added"}), 201

@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"message": f"User {id} deleted"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT
    app.run(host='0.0.0.0', port=port)
    init_db()
    app.run(debug=True)
