"""
Automated Unit and Integration Tests for Employee Management System
Uses Python's built-in unittest framework and Flask test client with an isolated temporary SQLite database.
"""

import os
import tempfile
import unittest
import json
import sqlite3

# Import app, config, and init_db from app.py
from app import app, init_db, get_db_connection


class EmployeeManagementSystemTestCase(unittest.TestCase):
    def setUp(self):
        """Set up an isolated temporary database for each test run."""
        # Create a temporary file to act as the test database
        self.db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        app.config["DATABASE"] = self.temp_db_path
        app.config["TESTING"] = True

        # Initialize schema in temporary database
        init_db()

        # Create Flask test client
        self.client = app.test_client()

    def tearDown(self):
        """Close and remove the temporary database file after each test."""
        os.close(self.db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    # ---------------------------------------------------------------------
    # Test 1: Frontend Route
    # ---------------------------------------------------------------------
    def test_index_page_loads(self):
        """Ensure GET / loads the HTML application successfully."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Employee Management System", response.data)
        self.assertIn(b"Overview Dashboard", response.data)

    # ---------------------------------------------------------------------
    # Test 2: Initial Dashboard
    # ---------------------------------------------------------------------
    def test_get_dashboard_empty(self):
        """Ensure GET /api/dashboard returns zeroes when database is empty."""
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["total_employees"], 0)
        self.assertEqual(data["data"]["total_departments"], 0)
        self.assertEqual(data["data"]["total_payroll"], 0.0)
        self.assertEqual(data["data"]["total_designations"], 0)

    # ---------------------------------------------------------------------
    # Test 3: Add Employee Success
    # ---------------------------------------------------------------------
    def test_add_employee_success(self):
        """Ensure adding an employee with valid data returns 201."""
        payload = {
            "employee_id": "EMP101",
            "name": "Aarav Sharma",
            "department": "Engineering",
            "designation": "Software Engineer",
            "salary": 65000.0,
            "contact": "9876543210"
        }
        response = self.client.post(
            "/api/employees",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["employee_id"], "EMP101")
        self.assertEqual(data["data"]["name"], "Aarav Sharma")
        self.assertEqual(data["data"]["salary"], 65000.0)
        self.assertIn("id", data["data"])

    # ---------------------------------------------------------------------
    # Test 4: Add Duplicate Employee ID
    # ---------------------------------------------------------------------
    def test_add_employee_duplicate_id(self):
        """Ensure duplicate employee_id returns 409 Conflict."""
        payload = {
            "employee_id": "EMP101",
            "name": "Aarav Sharma",
            "department": "Engineering",
            "designation": "Software Engineer",
            "salary": 65000.0,
            "contact": "9876543210"
        }
        # First creation succeeds
        self.client.post("/api/employees", data=json.dumps(payload), content_type="application/json")

        # Second creation with same employee_id
        duplicate_payload = {
            "employee_id": "EMP101",
            "name": "Different Name",
            "department": "Marketing",
            "designation": "Executive",
            "salary": 45000.0,
            "contact": "9123456780"
        }
        response = self.client.post(
            "/api/employees",
            data=json.dumps(duplicate_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertIn("already exists", data["error"])

    # ---------------------------------------------------------------------
    # Test 5: Add Employee Missing Fields
    # ---------------------------------------------------------------------
    def test_add_employee_missing_fields(self):
        """Ensure missing mandatory fields return 400 Bad Request."""
        payload = {
            "employee_id": "EMP102",
            "name": "Rohan Gupta"
            # Missing department, designation, salary, contact
        }
        response = self.client.post(
            "/api/employees",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertIn("Missing required field", data["error"])

    # ---------------------------------------------------------------------
    # Test 6: Add Employee Whitespace Only Fields
    # ---------------------------------------------------------------------
    def test_add_employee_whitespace_only(self):
        """Ensure whitespace-only fields are rejected with 400 Bad Request."""
        payload = {
            "employee_id": "EMP103",
            "name": "   ",
            "department": "Engineering",
            "designation": "Developer",
            "salary": 50000.0,
            "contact": "9876543210"
        }
        response = self.client.post(
            "/api/employees",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertIn("cannot be empty or contain only whitespace", data["error"])

    # ---------------------------------------------------------------------
    # Test 7: Add Employee Negative Salary
    # ---------------------------------------------------------------------
    def test_add_employee_negative_salary(self):
        """Ensure negative salary is rejected with 400 Bad Request."""
        payload = {
            "employee_id": "EMP104",
            "name": "Priya Verma",
            "department": "Finance",
            "designation": "Accountant",
            "salary": -500.0,
            "contact": "9876543210"
        }
        response = self.client.post(
            "/api/employees",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertIn("non-negative", data["error"])

    # ---------------------------------------------------------------------
    # Test 8: Add Employee Non-Numeric Salary
    # ---------------------------------------------------------------------
    def test_add_employee_non_numeric_salary(self):
        """Ensure non-numeric salary string is rejected with 400 Bad Request."""
        payload = {
            "employee_id": "EMP105",
            "name": "Karan Mehra",
            "department": "HR",
            "designation": "HR Executive",
            "salary": "FiftyThousand",
            "contact": "9876543210"
        }
        response = self.client.post(
            "/api/employees",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertIn("numeric value", data["error"])

    # ---------------------------------------------------------------------
    # Test 9: Add Employee Invalid Contact
    # ---------------------------------------------------------------------
    def test_add_employee_invalid_contact_digits(self):
        """Ensure contact number with fewer or more than 10 digits returns 400."""
        # Case A: 9 digits
        payload_short = {
            "employee_id": "EMP106",
            "name": "Anita Rao",
            "department": "Design",
            "designation": "UI Designer",
            "salary": 45000.0,
            "contact": "987654321"  # 9 digits
        }
        res_short = self.client.post("/api/employees", data=json.dumps(payload_short), content_type="application/json")
        self.assertEqual(res_short.status_code, 400)

        # Case B: letters in contact
        payload_alpha = {
            "employee_id": "EMP107",
            "name": "Anita Rao",
            "department": "Design",
            "designation": "UI Designer",
            "salary": 45000.0,
            "contact": "987654321A"
        }
        res_alpha = self.client.post("/api/employees", data=json.dumps(payload_alpha), content_type="application/json")
        self.assertEqual(res_alpha.status_code, 400)

    # ---------------------------------------------------------------------
    # Test 10: Get All Employees & Search
    # ---------------------------------------------------------------------
    def test_get_and_search_employees(self):
        """Ensure dynamic search matches employee_id, name, and department case-insensitively."""
        # Insert test records
        emp1 = {
            "employee_id": "EMP201",
            "name": "Vikram Patel",
            "department": "Engineering",
            "designation": "DevOps Engineer",
            "salary": 70000.0,
            "contact": "9876543210"
        }
        emp2 = {
            "employee_id": "EMP202",
            "name": "Sunita Sen",
            "department": "Marketing",
            "designation": "SEO Specialist",
            "salary": 48000.0,
            "contact": "9123456789"
        }
        self.client.post("/api/employees", data=json.dumps(emp1), content_type="application/json")
        self.client.post("/api/employees", data=json.dumps(emp2), content_type="application/json")

        # 1. Fetch all
        res_all = self.client.get("/api/employees")
        self.assertEqual(res_all.status_code, 200)
        data_all = json.loads(res_all.data)
        self.assertEqual(data_all["count"], 2)

        # 2. Search by department (Engineering)
        res_search_dept = self.client.get("/api/employees?search=engineer")
        self.assertEqual(res_search_dept.status_code, 200)
        data_dept = json.loads(res_search_dept.data)
        self.assertEqual(data_dept["count"], 1)
        self.assertEqual(data_dept["data"][0]["name"], "Vikram Patel")

        # 3. Search case-insensitive name ("sunita")
        res_search_name = self.client.get("/api/employees?search=SUNITA")
        self.assertEqual(res_search_name.status_code, 200)
        data_name = json.loads(res_search_name.data)
        self.assertEqual(data_name["count"], 1)
        self.assertEqual(data_name["data"][0]["employee_id"], "EMP202")

        # 4. Search non-existent
        res_search_none = self.client.get("/api/employees?search=NonExistentTerm")
        self.assertEqual(res_search_none.status_code, 200)
        data_none = json.loads(res_search_none.data)
        self.assertEqual(data_none["count"], 0)

    # ---------------------------------------------------------------------
    # Test 11: Get Single Employee By ID
    # ---------------------------------------------------------------------
    def test_get_single_employee_by_id(self):
        """Ensure GET /api/employees/<id> returns 200 for found and 404 for not found."""
        emp = {
            "employee_id": "EMP301",
            "name": "Neha Joshi",
            "department": "Quality Assurance",
            "designation": "QA Lead",
            "salary": 60000.0,
            "contact": "9887766554"
        }
        create_res = self.client.post("/api/employees", data=json.dumps(emp), content_type="application/json")
        new_id = json.loads(create_res.data)["data"]["id"]

        # Found
        res_found = self.client.get(f"/api/employees/{new_id}")
        self.assertEqual(res_found.status_code, 200)
        data_found = json.loads(res_found.data)
        self.assertEqual(data_found["data"]["name"], "Neha Joshi")

        # Not found
        res_missing = self.client.get("/api/employees/99999")
        self.assertEqual(res_missing.status_code, 404)
        data_missing = json.loads(res_missing.data)
        self.assertFalse(data_missing["success"])

    # ---------------------------------------------------------------------
    # Test 12: Update Employee
    # ---------------------------------------------------------------------
    def test_update_employee(self):
        """Ensure PUT /api/employees/<id> updates fields, handles conflicts and 404."""
        emp1 = {
            "employee_id": "EMP401",
            "name": "Amit Shah",
            "department": "Sales",
            "designation": "Representative",
            "salary": 35000.0,
            "contact": "9000000001"
        }
        emp2 = {
            "employee_id": "EMP402",
            "name": "Deepa Roy",
            "department": "Sales",
            "designation": "Manager",
            "salary": 75000.0,
            "contact": "9000000002"
        }
        r1 = self.client.post("/api/employees", data=json.dumps(emp1), content_type="application/json")
        r2 = self.client.post("/api/employees", data=json.dumps(emp2), content_type="application/json")
        id1 = json.loads(r1.data)["data"]["id"]
        id2 = json.loads(r2.data)["data"]["id"]

        # Successful update
        update_payload = {
            "employee_id": "EMP401",
            "name": "Amit K. Shah",
            "department": "Sales",
            "designation": "Senior Representative",
            "salary": 42000.0,
            "contact": "9000000001"
        }
        res_update = self.client.put(
            f"/api/employees/{id1}",
            data=json.dumps(update_payload),
            content_type="application/json"
        )
        self.assertEqual(res_update.status_code, 200)
        data_update = json.loads(res_update.data)
        self.assertEqual(data_update["data"]["name"], "Amit K. Shah")
        self.assertEqual(data_update["data"]["salary"], 42000.0)

        # Conflict update: try to change id1's employee_id to id2's employee_id ("EMP402")
        conflict_payload = {
            "employee_id": "EMP402",  # Conflicts with emp2
            "name": "Amit K. Shah",
            "department": "Sales",
            "designation": "Senior Representative",
            "salary": 42000.0,
            "contact": "9000000001"
        }
        res_conflict = self.client.put(
            f"/api/employees/{id1}",
            data=json.dumps(conflict_payload),
            content_type="application/json"
        )
        self.assertEqual(res_conflict.status_code, 409)

        # 404 update
        res_404 = self.client.put(
            "/api/employees/88888",
            data=json.dumps(update_payload),
            content_type="application/json"
        )
        self.assertEqual(res_404.status_code, 404)

    # ---------------------------------------------------------------------
    # Test 13: Delete Employee
    # ---------------------------------------------------------------------
    def test_delete_employee(self):
        """Ensure DELETE /api/employees/<id> deletes existing and returns 404 for missing."""
        emp = {
            "employee_id": "EMP501",
            "name": "Rajesh Kumar",
            "department": "Operations",
            "designation": "Supervisor",
            "salary": 38000.0,
            "contact": "9988776655"
        }
        r = self.client.post("/api/employees", data=json.dumps(emp), content_type="application/json")
        new_id = json.loads(r.data)["data"]["id"]

        # Delete existing
        del_res = self.client.delete(f"/api/employees/{new_id}")
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(json.loads(del_res.data)["success"])

        # Verify deletion from DB
        get_res = self.client.get(f"/api/employees/{new_id}")
        self.assertEqual(get_res.status_code, 404)

        # Deleting non-existent returns 404
        del_404 = self.client.delete(f"/api/employees/{new_id}")
        self.assertEqual(del_404.status_code, 404)

    # ---------------------------------------------------------------------
    # Test 14: Dashboard Aggregations After Full CRUD Cycle
    # ---------------------------------------------------------------------
    def test_dashboard_aggregations_full_cycle(self):
        """Verify dashboard statistics accurately calculate metrics through add, update, and delete."""
        # 1. Add Employee 1
        emp1 = {
            "employee_id": "EMP601",
            "name": "Employee One",
            "department": "Engineering",
            "designation": "Developer",
            "salary": 50000.0,
            "contact": "9000000011"
        }
        self.client.post("/api/employees", data=json.dumps(emp1), content_type="application/json")

        # 2. Add Employee 2 (same department, distinct designation)
        emp2 = {
            "employee_id": "EMP602",
            "name": "Employee Two",
            "department": "Engineering",
            "designation": "Architect",
            "salary": 90000.0,
            "contact": "9000000022"
        }
        r2 = self.client.post("/api/employees", data=json.dumps(emp2), content_type="application/json")
        id2 = json.loads(r2.data)["data"]["id"]

        # 3. Add Employee 3 (different department, distinct designation)
        emp3 = {
            "employee_id": "EMP603",
            "name": "Employee Three",
            "department": "Human Resources",
            "designation": "HR Generalist",
            "salary": 40000.0,
            "contact": "9000000033"
        }
        self.client.post("/api/employees", data=json.dumps(emp3), content_type="application/json")

        # Check stats: 3 employees, 2 departments, 180000 payroll, 3 designations
        dash_res = self.client.get("/api/dashboard")
        dash_data = json.loads(dash_res.data)["data"]
        self.assertEqual(dash_data["total_employees"], 3)
        self.assertEqual(dash_data["total_departments"], 2)
        self.assertEqual(dash_data["total_payroll"], 180000.0)
        self.assertEqual(dash_data["total_designations"], 3)

        # 4. Delete Employee 2 (salary 90000)
        self.client.delete(f"/api/employees/{id2}")

        dash_res_after_del = self.client.get("/api/dashboard")
        dash_data_after_del = json.loads(dash_res_after_del.data)["data"]
        self.assertEqual(dash_data_after_del["total_employees"], 2)
        self.assertEqual(dash_data_after_del["total_departments"], 2)
        self.assertEqual(dash_data_after_del["total_payroll"], 90000.0)
        self.assertEqual(dash_data_after_del["total_designations"], 2)

    # ---------------------------------------------------------------------
    # Test 15: Database Persistence
    # ---------------------------------------------------------------------
    def test_database_persistence_across_connections(self):
        """Ensure records persist across separate database connection sessions."""
        emp = {
            "employee_id": "EMP701",
            "name": "Persistent Record",
            "department": "Security",
            "designation": "Analyst",
            "salary": 62000.0,
            "contact": "9112233445"
        }
        self.client.post("/api/employees", data=json.dumps(emp), content_type="application/json")

        # Open a fresh connection directly to the test database file
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id, name, salary FROM employees WHERE employee_id = 'EMP701'")
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "EMP701")
        self.assertEqual(row[1], "Persistent Record")
        self.assertEqual(row[2], 62000.0)


if __name__ == "__main__":
    unittest.main()
