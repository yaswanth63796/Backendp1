from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import bcrypt

app = Flask(__name__)
CORS(app)

# ---------------- Firebase Setup ----------------
firebase_key = os.environ.get("FIREBASE_KEY")
if not firebase_key:
    raise ValueError("FIREBASE_KEY environment variable not set!")

cred_dict = json.loads(firebase_key)  # convert JSON string to dict
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------- Routes ----------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask backend is running 🚀"}), 200

@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    username = data.get("username")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    info = data.get("info")

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    users_ref = db.collection("users")
    existing_user = users_ref.where("email", "==", email).get()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    db.collection("users").add({
        "username": username,
        "name": name,
        "email": email,
        "password": hashed_password.decode("utf-8"),  # store as string
        "info": info
    })

    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    users_ref = db.collection("users")
    matching_users = users_ref.where("email", "==", email).get()

    if not matching_users:
        return jsonify({"error": "Invalid email or password"}), 401

    user_doc = matching_users[0].to_dict()
    stored_hashed_password = user_doc["password"].encode("utf-8")

    if not bcrypt.checkpw(password.encode("utf-8"), stored_hashed_password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful ✅"}), 200

# ---------------- Run App ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)



    
