"""
Employee Management System - Flask REST API & Web Application
Author: College Mini-Project
Description: A complete, beginner-friendly Flask application demonstrating
             CRUD operations, REST API design, and SQLite persistent storage.
"""

import os
import re
import sqlite3
from flask import Flask, jsonify, render_template, request

# Initialize Flask application
app = Flask(__name__)

# Base directory for reliable file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "employee.db")

# Configure database path (can be overridden during testing)
app.config["DATABASE"] = os.environ.get("EMPLOYEE_DB_PATH", DEFAULT_DB_PATH)


def get_db_connection():
    """
    Establish and return a connection to the SQLite database.
    Configures sqlite3.Row as the row factory so query results
    can be accessed both by index and column name.
    """
    db_path = app.config.get("DATABASE", DEFAULT_DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys and foreign key constraints enforcement
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Initialize the database table if it does not already exist.
    This guarantees persistence: existing data is never wiped or overwritten.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                designation TEXT NOT NULL,
                salary REAL NOT NULL CHECK(salary >= 0),
                contact TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def validate_employee_data(data):
    """
    Validate and clean incoming employee payload.
    Returns:
        tuple: (is_valid: bool, error_message: str | None, cleaned_data: dict | None)
    """
    if not isinstance(data, dict):
        return False, "Request body must be a valid JSON object.", None

    # Required fields
    required_fields = ["employee_id", "name", "department", "designation", "salary", "contact"]
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Missing required field: '{field}'.", None

    # Extract and clean string fields
    emp_id = str(data.get("employee_id", "")).strip()
    name = str(data.get("name", "")).strip()
    department = str(data.get("department", "")).strip()
    designation = str(data.get("designation", "")).strip()
    contact = str(data.get("contact", "")).strip()
    raw_salary = data.get("salary")

    # Check non-empty strings (cannot contain only whitespace)
    if not emp_id:
        return False, "Employee ID cannot be empty or contain only whitespace.", None
    if not name:
        return False, "Employee Name cannot be empty or contain only whitespace.", None
    if not department:
        return False, "Department cannot be empty or contain only whitespace.", None
    if not designation:
        return False, "Designation cannot be empty or contain only whitespace.", None

    # Validate salary (must be numeric, non-negative)
    try:
        salary = float(raw_salary)
        if salary < 0:
            return False, "Salary must be a non-negative number.", None
    except (ValueError, TypeError):
        return False, "Salary must be a valid numeric value.", None

    # Validate contact number (college project rule: exactly 10 digits)
    if not re.fullmatch(r"^\d{10}$", contact):
        return False, "Contact Number must contain exactly 10 digits (0-9).", None

    cleaned_data = {
        "employee_id": emp_id,
        "name": name,
        "department": department,
        "designation": designation,
        "salary": round(salary, 2),
        "contact": contact,
    }
    return True, None, cleaned_data


# -------------------------------------------------------------------------
# Web Page Route
# -------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the main single-page application interface."""
    return render_template("index.html")


# -------------------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------------------
@app.route("/api/employees", methods=["GET"])
def get_employees():
    """
    GET /api/employees
    Retrieve all employees or search dynamically.
    Optional query parameter: ?search=keyword
    Searches by employee_id, name, or department case-insensitively.
    """
    search_query = request.args.get("search", "").strip()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if search_query:
            # SQLite LIKE operator is case-insensitive for ASCII text
            wildcard = f"%{search_query}%"
            cursor.execute(
                """
                SELECT id, employee_id, name, department, designation, salary, contact
                FROM employees
                WHERE employee_id LIKE ? OR name LIKE ? OR department LIKE ?
                ORDER BY id DESC
                """,
                (wildcard, wildcard, wildcard),
            )
        else:
            cursor.execute(
                """
                SELECT id, employee_id, name, department, designation, salary, contact
                FROM employees
                ORDER BY id DESC
                """
            )
        rows = cursor.fetchall()
        employees = [dict(row) for row in rows]
        return jsonify({
            "success": True,
            "count": len(employees),
            "data": employees
        }), 200
    except sqlite3.Error as e:
        return jsonify({
            "success": False,
            "error": "A database error occurred while fetching employees."
        }), 500
    finally:
        conn.close()


@app.route("/api/employees/<int:id>", methods=["GET"])
def get_employee(id):
    """
    GET /api/employees/<int:id>
    Retrieve a single employee by their database primary key.
    Returns 404 if not found.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, employee_id, name, department, designation, salary, contact
            FROM employees
            WHERE id = ?
            """,
            (id,),
        )
        row = cursor.fetchone()
        if row is None:
            return jsonify({
                "success": False,
                "error": f"Employee with database ID {id} was not found."
            }), 404
        return jsonify({
            "success": True,
            "data": dict(row)
        }), 200
    except sqlite3.Error:
        return jsonify({
            "success": False,
            "error": "A database error occurred while retrieving the employee."
        }), 500
    finally:
        conn.close()


@app.route("/api/employees", methods=["POST"])
def add_employee():
    """
    POST /api/employees
    Create a new employee record.
    Returns:
        201: Successfully created
        400: Validation error or missing data
        409: Conflict (Duplicate employee_id)
    """
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            "success": False,
            "error": "Invalid or missing JSON payload in request."
        }), 400

    is_valid, error_msg, cleaned = validate_employee_data(payload)
    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Explicit check for unique employee_id before insert
        cursor.execute("SELECT id FROM employees WHERE employee_id = ?", (cleaned["employee_id"],))
        if cursor.fetchone() is not None:
            return jsonify({
                "success": False,
                "error": f"Employee ID '{cleaned['employee_id']}' already exists. Please use a unique ID."
            }), 409

        cursor.execute(
            """
            INSERT INTO employees (employee_id, name, department, designation, salary, contact)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                cleaned["employee_id"],
                cleaned["name"],
                cleaned["department"],
                cleaned["designation"],
                cleaned["salary"],
                cleaned["contact"],
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cleaned["id"] = new_id

        return jsonify({
            "success": True,
            "message": "Employee added successfully.",
            "data": cleaned
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "error": f"Employee ID '{cleaned['employee_id']}' already exists."
        }), 409
    except sqlite3.Error:
        return jsonify({
            "success": False,
            "error": "Failed to add employee due to a database error."
        }), 500
    finally:
        conn.close()


@app.route("/api/employees/<int:id>", methods=["PUT"])
def update_employee(id):
    """
    PUT /api/employees/<int:id>
    Update an existing employee record.
    Returns:
        200: Successfully updated
        400: Validation error or malformed data
        404: Employee not found
        409: Conflict (Employee ID already used by another record)
    """
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            "success": False,
            "error": "Invalid or missing JSON payload in request."
        }), 400

    is_valid, error_msg, cleaned = validate_employee_data(payload)
    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Verify employee exists
        cursor.execute("SELECT id FROM employees WHERE id = ?", (id,))
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Employee with database ID {id} was not found."
            }), 404

        # Check if the employee_id is taken by a DIFFERENT employee
        cursor.execute(
            "SELECT id FROM employees WHERE employee_id = ? AND id != ?",
            (cleaned["employee_id"], id),
        )
        if cursor.fetchone() is not None:
            return jsonify({
                "success": False,
                "error": f"Employee ID '{cleaned['employee_id']}' is already assigned to another employee."
            }), 409

        cursor.execute(
            """
            UPDATE employees
            SET employee_id = ?, name = ?, department = ?, designation = ?, salary = ?, contact = ?
            WHERE id = ?
            """,
            (
                cleaned["employee_id"],
                cleaned["name"],
                cleaned["department"],
                cleaned["designation"],
                cleaned["salary"],
                cleaned["contact"],
                id,
            ),
        )
        conn.commit()
        cleaned["id"] = id

        return jsonify({
            "success": True,
            "message": "Employee updated successfully.",
            "data": cleaned
        }), 200
    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "error": f"Employee ID '{cleaned['employee_id']}' conflicts with another record."
        }), 409
    except sqlite3.Error:
        return jsonify({
            "success": False,
            "error": "Failed to update employee due to a database error."
        }), 500
    finally:
        conn.close()


@app.route("/api/employees/<int:id>", methods=["DELETE"])
def delete_employee(id):
    """
    DELETE /api/employees/<int:id>
    Delete an employee record by database primary key.
    Returns:
        200: Successfully deleted
        404: Employee not found
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, employee_id FROM employees WHERE id = ?", (id,))
        record = cursor.fetchone()
        if record is None:
            return jsonify({
                "success": False,
                "error": f"Employee with database ID {id} was not found."
            }), 404

        cursor.execute("DELETE FROM employees WHERE id = ?", (id,))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Employee '{record['name']}' ({record['employee_id']}) deleted successfully."
        }), 200
    except sqlite3.Error:
        return jsonify({
            "success": False,
            "error": "Failed to delete employee due to a database error."
        }), 500
    finally:
        conn.close()


@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_stats():
    """
    GET /api/dashboard
    Return real-time aggregated metrics:
    - total_employees: Total number of active employees
    - total_departments: Count of unique departments
    - total_payroll: Sum of all employee salaries
    - total_designations: Count of unique designations
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_employees,
                COUNT(DISTINCT department) AS total_departments,
                COALESCE(SUM(salary), 0) AS total_payroll,
                COUNT(DISTINCT designation) AS total_designations
            FROM employees
            """
        )
        stats = cursor.fetchone()
        return jsonify({
            "success": True,
            "data": {
                "total_employees": stats["total_employees"] if stats else 0,
                "total_departments": stats["total_departments"] if stats else 0,
                "total_payroll": round(stats["total_payroll"], 2) if stats else 0.0,
                "total_designations": stats["total_designations"] if stats else 0,
            }
        }), 200
    except sqlite3.Error:
        return jsonify({
            "success": False,
            "error": "Failed to calculate dashboard statistics."
        }), 500
    finally:
        conn.close()


# -------------------------------------------------------------------------
# Custom Error Handlers
# -------------------------------------------------------------------------
@app.errorhandler(404)
def not_found_handler(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Endpoint not found."}), 404
    return "<h1>404 Not Found</h1><p>The requested page does not exist.</p>", 404


@app.errorhandler(405)
def method_not_allowed_handler(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "HTTP Method not allowed on this endpoint."}), 405
    return "<h1>405 Method Not Allowed</h1>", 405


@app.errorhandler(500)
def internal_error_handler(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    return "<h1>500 Internal Server Error</h1>", 500


# Automatically initialize the database on startup
init_db()

if __name__ == "__main__":
    # Run the Flask development server on localhost
    print("==================================================")
    print(" Employee Management System - Local Flask Server")
    print(" Access URL: http://127.0.0.1:5000")
    print(" Press CTRL+C to stop the server")
    print("==================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
