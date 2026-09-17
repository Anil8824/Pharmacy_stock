from datetime import date, timedelta

from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, init_db


app = Flask(__name__)

# Make sure the database and tables exist when the application starts.
init_db()


@app.route("/")
def home():
    return jsonify({
        "message": "Pharmacy Inventory System is running!",
        "status": "success"
    })


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    connection = get_db_connection()

    existing_user = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if existing_user:
        connection.close()
        return jsonify({"error": "Email already registered"}), 409

    password_hash = generate_password_hash(password)

    connection.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash)
    )

    connection.commit()
    connection.close()

    return jsonify({"message": "Registration successful"}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    connection = get_db_connection()

    user = connection.execute(
        "SELECT id, name, email, password_hash FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    connection.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200


@app.route("/api/medicines", methods=["POST"])
def add_medicine():
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    generic_name = data.get("generic_name", "").strip()

    if not name:
        return jsonify({"error": "Medicine name is required"}), 400

    connection = get_db_connection()

    cursor = connection.execute(
        "INSERT INTO medicines (name, generic_name) VALUES (?, ?)",
        (name, generic_name)
    )

    connection.commit()

    medicine_id = cursor.lastrowid
    connection.close()

    return jsonify({
        "message": "Medicine added successfully",
        "medicine_id": medicine_id
    }), 201


@app.route("/api/medicines", methods=["GET"])
def get_medicines():
    search = request.args.get("search", "").strip()
    page = max(request.args.get("page", 1, type=int), 1)
    limit = min(max(request.args.get("limit", 10, type=int), 1), 50)
    sort = request.args.get("sort", "name").lower()

    allowed_sort_fields = {
        "name": "name",
        "generic_name": "generic_name",
        "created_at": "created_at"
    }

    sort_field = allowed_sort_fields.get(sort, "name")
    offset = (page - 1) * limit

    connection = get_db_connection()

    if search:
        search_pattern = f"%{search}%"

        medicines = connection.execute(
            f"SELECT id, name, generic_name, created_at FROM medicines WHERE name LIKE ? OR generic_name LIKE ? ORDER BY {sort_field} ASC LIMIT ? OFFSET ?",
            (search_pattern, search_pattern, limit, offset)
        ).fetchall()

        total = connection.execute(
            "SELECT COUNT(*) FROM medicines WHERE name LIKE ? OR generic_name LIKE ?",
            (search_pattern, search_pattern)
        ).fetchone()[0]
    else:
        medicines = connection.execute(
            f"SELECT id, name, generic_name, created_at FROM medicines ORDER BY {sort_field} ASC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()

        total = connection.execute(
            "SELECT COUNT(*) FROM medicines"
        ).fetchone()[0]

    connection.close()

    return jsonify({
        "medicines": [dict(medicine) for medicine in medicines],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    })


@app.route("/api/health")
def health_check():
    return jsonify({
        "status": "healthy"
    })


if __name__ == "__main__":
    app.run(debug=True)
