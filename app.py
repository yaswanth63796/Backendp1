from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# Firebase setup
cred = credentials.Certificate("firebaseKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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

    # Check if user already exists
    users_ref = db.collection("users")
    existing_user = users_ref.where("email", "==", email).get()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    # Save into Firestore
    db.collection("users").add({
        "username": username,
        "name": name,
        "email": email,
        "password": password,   # ⚠️ should be hashed in real projects
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
    matching_users = users_ref.where("email", "==", email).where("password", "==", password).get()

    if not matching_users:
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful ✅"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


    
