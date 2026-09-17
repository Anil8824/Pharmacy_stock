from datetime import date, timedelta

from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, init_db


app = Flask(__name__)
app.config["SECRET_KEY"] = "pharmastock-development-secret-key"

# Make sure the database and tables exist when the application starts.
init_db()


@app.route("/")
def home():
    return render_template("index.html")


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

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

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

    page = max(
        request.args.get("page", 1, type=int),
        1
    )

    limit = min(
        max(request.args.get("limit", 10, type=int), 1),
        50
    )

    sort_by = request.args.get("sort_by", "name").lower()
    sort_order = request.args.get("sort_order", "asc").lower()

    allowed_sort_fields = {
        "name": "name",
        "generic_name": "generic_name",
        "created_at": "created_at"
    }

    sort_field = allowed_sort_fields.get(
        sort_by,
        "name"
    )

    order = "DESC" if sort_order == "desc" else "ASC"

    offset = (page - 1) * limit

    connection = get_db_connection()

    if search:
        search_pattern = f"%{search}%"

        medicines = connection.execute(
            f"""
            SELECT
                id,
                name,
                generic_name,
                created_at
            FROM medicines
            WHERE name LIKE ?
               OR generic_name LIKE ?
            ORDER BY {sort_field} {order}
            LIMIT ? OFFSET ?
            """,
            (
                search_pattern,
                search_pattern,
                limit,
                offset
            )
        ).fetchall()

        total = connection.execute(
            """
            SELECT COUNT(*)
            FROM medicines
            WHERE name LIKE ?
               OR generic_name LIKE ?
            """,
            (
                search_pattern,
                search_pattern
            )
        ).fetchone()[0]

    else:
        medicines = connection.execute(
            f"""
            SELECT
                id,
                name,
                generic_name,
                created_at
            FROM medicines
            ORDER BY {sort_field} {order}
            LIMIT ? OFFSET ?
            """,
            (
                limit,
                offset
            )
        ).fetchall()

        total = connection.execute(
            "SELECT COUNT(*) FROM medicines"
        ).fetchone()[0]

    connection.close()

    return jsonify({
        "medicines": [
            dict(medicine)
            for medicine in medicines
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (
                (total + limit - 1) // limit
            )
        }
    })


@app.route("/api/medicines/<int:medicine_id>/batches", methods=["POST"])
def add_batch(medicine_id):
    data = request.get_json() or {}

    batch_number = data.get("batch_number", "").strip()
    quantity = data.get("quantity")
    expiry_date = data.get("expiry_date", "").strip()

    if not batch_number or quantity is None or not expiry_date:
        return jsonify({"error": "Batch number, quantity and expiry date are required"}), 400

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"error": "Quantity must be a number"}), 400

    if quantity <= 0:
        return jsonify({"error": "Quantity must be greater than 0"}), 400

    connection = get_db_connection()

    medicine = connection.execute(
        "SELECT id FROM medicines WHERE id = ?",
        (medicine_id,)
    ).fetchone()

    if not medicine:
        connection.close()
        return jsonify({"error": "Medicine not found"}), 404

    connection.execute(
        "INSERT INTO batches (medicine_id, batch_number, quantity, expiry_date) VALUES (?, ?, ?, ?)",
        (medicine_id, batch_number, quantity, expiry_date)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Batch added successfully"
    }), 201


@app.route("/api/medicines/<int:medicine_id>/dispense", methods=["POST"])
def dispense_medicine(medicine_id):
    data = request.get_json() or {}
    requested_quantity = data.get("quantity")

    try:
        requested_quantity = int(requested_quantity)
    except (TypeError, ValueError):
        return jsonify({"error": "Quantity must be a number"}), 400

    if requested_quantity <= 0:
        return jsonify({"error": "Quantity must be greater than 0"}), 400

    connection = get_db_connection()

    medicine = connection.execute(
        "SELECT id, name FROM medicines WHERE id = ?",
        (medicine_id,)
    ).fetchone()

    if not medicine:
        connection.close()
        return jsonify({"error": "Medicine not found"}), 404

    today = date.today().isoformat()

    batches = connection.execute(
        "SELECT id, batch_number, quantity, expiry_date FROM batches WHERE medicine_id = ? AND quantity > 0 AND expiry_date >= ? ORDER BY expiry_date ASC, id ASC",
        (medicine_id, today)
    ).fetchall()

    available_quantity = sum(batch["quantity"] for batch in batches)

    if available_quantity < requested_quantity:
        connection.close()
        return jsonify({
            "error": "Insufficient in-date stock",
            "available_quantity": available_quantity
        }), 400

    remaining_quantity = requested_quantity
    dispensed_batches = []

    try:
        for batch in batches:
            if remaining_quantity == 0:
                break

            quantity_from_batch = min(batch["quantity"], remaining_quantity)

            connection.execute(
                "UPDATE batches SET quantity = quantity - ? WHERE id = ?",
                (quantity_from_batch, batch["id"])
            )

            connection.execute(
                "INSERT INTO dispense_records (medicine_id, batch_id, quantity) VALUES (?, ?, ?)",
                (medicine_id, batch["id"], quantity_from_batch)
            )

            dispensed_batches.append({
                "batch_number": batch["batch_number"],
                "quantity": quantity_from_batch,
                "expiry_date": batch["expiry_date"]
            })

            remaining_quantity -= quantity_from_batch

        connection.commit()
    except Exception:
        connection.rollback()
        connection.close()
        return jsonify({"error": "Unable to complete dispensing"}), 500

    connection.close()

    return jsonify({
        "message": "Medicine dispensed successfully",
        "medicine": medicine["name"],
        "requested_quantity": requested_quantity,
        "dispensed_batches": dispensed_batches
    }), 200


@app.route("/api/medicines/<int:medicine_id>/stock", methods=["GET"])
def get_sellable_stock(medicine_id):
    connection = get_db_connection()

    medicine = connection.execute(
        "SELECT id, name FROM medicines WHERE id = ?",
        (medicine_id,)
    ).fetchone()

    if not medicine:
        connection.close()
        return jsonify({"error": "Medicine not found"}), 404

    today = date.today().isoformat()

    stock = connection.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS sellable_stock FROM batches WHERE medicine_id = ? AND quantity > 0 AND expiry_date >= ?",
        (medicine_id, today)
    ).fetchone()["sellable_stock"]

    connection.close()

    return jsonify({
        "medicine": medicine["name"],
        "sellable_stock": stock,
        "as_of_date": today
    })

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))

    return render_template("dashboard.html")


@app.route("/api/alerts/expiring", methods=["GET"])
def get_expiring_batches():
    days = max(request.args.get("days", 30, type=int), 1)

    today = date.today()
    alert_date = today + timedelta(days=days)

    connection = get_db_connection()

    batches = connection.execute(
        """
        SELECT
            batches.id,
            medicines.name AS medicine_name,
            batches.batch_number,
            batches.quantity,
            batches.expiry_date
        FROM batches
        JOIN medicines ON medicines.id = batches.medicine_id
        WHERE batches.quantity > 0
          AND batches.expiry_date >= ?
          AND batches.expiry_date <= ?
        ORDER BY batches.expiry_date ASC
        """,
        (today.isoformat(), alert_date.isoformat())
    ).fetchall()

    connection.close()

    return jsonify({
        "days": days,
        "alerts": [dict(batch) for batch in batches]
    })


@app.route("/api/health")
def health_check():
    return jsonify({
        "status": "healthy"
    })


if __name__ == "__main__":
    app.run(debug=True)
