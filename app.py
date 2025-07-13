from flask import Flask, jsonify, request

app = Flask(__name__)

# Fake DB (will reset on restart)
users = [{"id": 1, "name": "Vinoth"}, {"id": 2, "name": "Sara"}]

@app.route("/")
def welcome():
    return "Welcome"
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    users.append(data)
    return jsonify({"message": "User added", "user": data}), 201

@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    global users
    users = [u for u in users if u["id"] != id]
    return jsonify({"message": f"User {id} deleted"})

if __name__ == "__main__":
    app.run(debug=True)
