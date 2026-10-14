# Employee Management System

> **College Mini-Project | Full-Stack Web Development & REST API Demonstration**  
> *Built with HTML5, CSS3, Vanilla JavaScript, Python Flask, and SQLite3.*

---

## 1. Project Title
**Employee Management System (EMS)**

---

## 2. Project Aim
To design, develop, and deploy an intuitive, responsive, and robust **Employee Management System** that enables human resource administrators to add, view, search, update, and delete employee records through a clean web interface powered by a lightweight Python Flask REST API and an SQLite persistent database.

---

## 3. Objectives
- **Full-Stack Integration:** Connect a modern, responsive frontend (HTML5/CSS3/Vanilla JS) with a backend RESTful service (Python Flask).
- **CRUD Operations:** Implement complete Create, Read, Update, and Delete operations with persistent storage.
- **Dynamic Search:** Implement fast, client-side debounced search with case-insensitive server-side parameterized querying.
- **Real-Time Analytics:** Dynamically aggregate summary metrics (total employees, unique departments, total payroll, distinct designations) without full-page reloads.
- **Robust Validation:** Enforce strict field-level validation both on the client side (instant UI feedback) and server side (security & data integrity).
- **Security & Integrity:** Use parameterized SQL queries (`?` placeholders) throughout to eliminate SQL injection vulnerabilities.
- **College Practical / Viva Readiness:** Maintain clean, self-documenting code with comprehensive automated tests and zero complex third-party dependencies (no Node.js, React, or heavyweight ORMs).

---

## 4. Project Overview
The **Employee Management System** is a single-page style web application designed specifically as a college mini-project. The frontend communicates asynchronously with the Flask backend using the browser's native `Fetch API` and JSON payloads. All data is persisted in a local SQLite file (`employee.db`), guaranteeing that records remain intact across server restarts without requiring any standalone database servers such as MySQL or PostgreSQL.

---

## 5. Features
- 📊 **Real-Time Overview Dashboard:**
  - Total registered employees count.
  - Number of distinct active departments.
  - Total monthly/annual payroll sum displayed in Indian Rupees (**₹**).
  - Count of unique job designations.
  - Automatically updates immediately after any Add, Update, or Delete operation.
- ➕ **Add Employee Record:**
  - Form validation with clear inline error indicators.
  - Validation rules: Employee ID uniqueness check, whitespace rejection, positive salary constraint, and strictly 10-digit contact numbers.
- 📋 **View Records Directory:**
  - Clean, responsive HTML data table with status badges and formatted currency values.
  - Loading spinner indicator during network requests.
  - Informative empty-state displays when no records exist or search finds zero matches.
- 🔍 **Live Dynamic Search:**
  - Case-insensitive search filtering across Employee ID, Full Name, and Department.
  - Search runs dynamically as the user types with 300ms debouncing.
  - One-click clear search button (`×`) to restore the full directory.
- ✏️ **Update Employee:**
  - Smoothly loads employee data into the form for editing.
  - Form controls dynamically switch to "Edit Mode" with a "Cancel Edit" button.
  - Server prevents accidental ID collisions with other employees.
- 🗑️ **Delete Record with Confirmation Modal:**
  - Accessible modal dialog prevents accidental deletions.
  - Immediate removal from database with instant dashboard reconciliation.
- 🔔 **Interactive Toast Notifications:**
  - Floating status banners with clear color cues (Green for success, Red for errors, Blue for info).
- 🛡️ **XSS-Safe DOM Manipulation:**
  - Table records are rendered safely using DOM creation APIs (`document.createElement`, `textContent`) without unsafe `innerHTML` injection of untrusted user data.

---

## 6. Technologies Used

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend UI** | HTML5 & CSS3 | Semantic markup, responsive Flexbox/Grid layout, custom icons |
| **Client Scripting** | Vanilla JavaScript (ES6+) | Native `Fetch API`, DOM manipulation, event listeners |
| **Backend Framework**| Python 3 (Flask) | Lightweight WSGI web framework & RESTful routing |
| **Database Engine** | SQLite3 | Embedded SQL engine using Python's built-in `sqlite3` module |
| **Data Format** | JSON | Standard exchange format for API communication |
| **Testing** | Python `unittest` | Built-in test runner with isolated temporary test databases |
| **Version Control** | Git & GitHub | Distributed version control & source code hosting |

*Note: No Node.js, npm, React, Angular, Vue, MongoDB, or SQLAlchemy dependencies are used, keeping the project lightweight and beginner-friendly.*

---

## 7. System Requirements
- **Operating System:** Windows 10 / 11, macOS, or Linux.
- **Python Version:** Python 3.8 or higher (Python 3.10+ recommended).
- **Web Browser:** Any modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, Brave, Safari).
- **Terminal:** Windows PowerShell, Command Prompt, or Bash.
- **Disk Space:** Less than 50 MB.

---

## 8. Folder Structure

```text
employee-management-system/
│
├── app.py                  # Main Flask application, routes, and REST API endpoints
├── test_app.py             # Automated unit tests using unittest and Flask test client
├── requirements.txt        # Python dependency manifest (Flask)
├── README.md               # Complete project documentation and viva guide
├── .gitignore              # Files and directories excluded from Git version control
├── employee.db             # SQLite database file (created automatically on first run)
│
├── templates/
│   └── index.html          # Frontend single-page HTML template
│
└── static/
    ├── style.css           # Custom responsive CSS styles (Blue & Slate theme)
    └── script.js           # Vanilla JavaScript for API interaction and DOM updates
```

---

## 9. Database Schema
The database file `employee.db` is initialized automatically when the application starts if it does not already exist.

### Table: `employees`
```sql
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    designation TEXT NOT NULL,
    salary REAL NOT NULL CHECK(salary >= 0),
    contact TEXT NOT NULL
);
```

### Schema Explanations:
- `id`: Auto-incrementing integer representing the internal primary key.
- `employee_id`: Unique business identifier for the employee (e.g. `EMP101`). Enforced unique via `UNIQUE NOT NULL`.
- `name`: Full name of the employee.
- `department`: Department name (e.g., Engineering, Sales, HR).
- `designation`: Job title/role (e.g., Software Engineer, Manager).
- `salary`: Floating-point numeric salary. Constrained to non-negative values using `CHECK(salary >= 0)`.
- `contact`: Stored as `TEXT` to preserve potential leading zeros and accommodate 10-digit telephone strings safely.

---

## 10. API Endpoints and HTTP Methods

| HTTP Method | Endpoint | Description | Request Body | Success Status | Error Statuses |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves the main HTML dashboard | None | `200 OK` | `500` |
| `GET` | `/api/dashboard` | Aggregated dashboard metrics | None | `200 OK` | `500` |
| `GET` | `/api/employees` | List all employees (or filter by `?search=`) | None | `200 OK` | `500` |
| `GET` | `/api/employees/<id>` | Fetch single employee by primary key | None | `200 OK` | `404`, `500` |
| `POST` | `/api/employees` | Register a new employee | JSON Object | `201 Created` | `400`, `409`, `500` |
| `PUT` | `/api/employees/<id>` | Update an existing employee record | JSON Object | `200 OK` | `400`, `404`, `409`, `500` |
| `DELETE`| `/api/employees/<id>` | Delete an employee record | None | `200 OK` | `404`, `500` |

### Sample JSON Request Body (POST / PUT):
```json
{
  "employee_id": "EMP101",
  "name": "Aarav Sharma",
  "department": "Engineering",
  "designation": "Software Engineer",
  "salary": 65000.00,
  "contact": "9876543210"
}
```

### Sample JSON Success Response (201 Created):
```json
{
  "success": true,
  "message": "Employee added successfully.",
  "data": {
    "id": 1,
    "employee_id": "EMP101",
    "name": "Aarav Sharma",
    "department": "Engineering",
    "designation": "Software Engineer",
    "salary": 65000.0,
    "contact": "9876543210"
  }
}
```

---

## 11. Explanation of CRUD Operations

1. **Create (C):**
   - User submits the employee form.
   - Frontend runs `validateForm()`. If valid, it sends a `POST` request to `/api/employees` with JSON payload.
   - Server validates field completeness, checks for duplicate `employee_id`, executes `INSERT INTO employees ... VALUES (?, ...)` using parameterized queries, and responds with `201 Created`.
2. **Read (R):**
   - When the page loads or after CRUD operations, `fetchEmployees()` issues a `GET` request to `/api/employees`.
   - When user searches, `GET /api/employees?search=<term>` executes a SQL `LIKE ?` query.
   - Result rows are received as JSON and safely converted into table DOM elements.
3. **Update (U):**
   - Clicking **Edit** on any row triggers `editEmployee(id)`.
   - Data is fetched via `GET /api/employees/<id>` and filled into form inputs.
   - When the form is submitted, a `PUT` request is dispatched to `/api/employees/<id>`.
   - Server verifies the employee exists, checks if the updated `employee_id` conflicts with another employee, executes `UPDATE employees SET ... WHERE id = ?`, and returns `200 OK`.
4. **Delete (D):**
   - Clicking **Delete** opens a modal dialog requiring explicit user confirmation.
   - Confirming sends a `DELETE` request to `/api/employees/<id>`.
   - Backend executes `DELETE FROM employees WHERE id = ?` and returns `200 OK`.
   - Frontend removes the row, refreshes the directory, and updates dashboard metrics.

---

## 12. Input Validation and Error Handling

### Client-Side Validation:
- **Empty / Whitespace Check:** Input fields trimmed with `.trim()`. Empty inputs show inline red warnings and red borders.
- **Salary Check:** Must be a valid positive number (`salary >= 0`).
- **Contact Check:** Validated against regular expression `^\d{10}$` to ensure strictly 10 numerical digits.

### Server-Side Validation:
- **Type and Field Existence Check:** Verifies that the payload is valid JSON and contains all 6 required keys.
- **String Sanitization:** Trims strings; rejects values containing only whitespace characters.
- **Numeric Salary Verification:** Rejects non-numeric strings or negative values (`float(val) < 0`).
- **Contact Regex Check:** Enforces 10 digits (`re.fullmatch(r"^\d{10}$", contact)`).
- **Uniqueness Check:** Checks `SELECT id FROM employees WHERE employee_id = ?` before inserting or updating. Returns `409 Conflict` if duplicate.
- **SQL Injection Prevention:** Every query uses parameterized placeholders (`?`). No string concatenation is used in SQL statements.
- **Graceful Error Handling:** SQLite exceptions return sanitized JSON error messages (`500 Internal Server Error`) without exposing raw database tracebacks.

---

## 13. Installation Instructions for Windows

Follow these step-by-step instructions in **Windows PowerShell**:

### Step 1: Open PowerShell
Press `Win + X` and select **Windows PowerShell** or **Terminal**.

### Step 2: Navigate to Project Directory
```powershell
cd C:\Users\lenovo\Desktop\employee-management-system
```

---

## 14. Virtual Environment Setup

Creating an isolated virtual environment ensures packages do not conflict with your global Python installation:

```powershell
# Create virtual environment named 'venv'
python -m venv venv

# Activate virtual environment in PowerShell
.\venv\Scripts\Activate.ps1
```

> **Note on PowerShell Execution Policy:** If you encounter a script execution error (`cannot be loaded because running scripts is disabled on this system`), run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\venv\Scripts\Activate.ps1
> ```

---

## 15. Dependency Installation

With your virtual environment activated (you will see `(venv)` in your terminal prompt):

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 16. Application Execution

Start the Flask development server:

```powershell
python app.py
```

You will see output similar to:
```text
==================================================
 Employee Management System - Local Flask Server
 Access URL: http://127.0.0.1:5000
 Press CTRL+C to stop the server
==================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

## 17. Browser URL
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```
or
```text
http://localhost:5000
```

To stop the server at any time, press `Ctrl + C` in the terminal.

---

## 18. Manual Testing Instructions

Perform these manual checks to test every feature during your demonstration or exam:

1. **Verify Empty State & Dashboard:**
   - Launch app on a fresh database.
   - Verify summary cards show `0` employees, `0` departments, `₹0.00` payroll, `0` designations.
   - Verify table shows the "No Employees Registered" empty-state graphic.
2. **Add a Valid Employee:**
   - ID: `EMP101`, Name: `Aarav Sharma`, Dept: `Engineering`, Designation: `Software Engineer`, Salary: `65000`, Contact: `9876543210`.
   - Click **Add Employee**.
   - Check that a green toast notification appears, the record appears in the table, and dashboard cards update to 1 employee, 1 department, ₹65,000 payroll.
3. **Test Duplicate Employee ID:**
   - Attempt to add another record with ID `EMP101`.
   - Verify an error toast appears: `"Employee ID 'EMP101' already exists"`, and the ID field highlights in red.
4. **Test Validation Boundaries:**
   - Try submitting with an empty name or spaces only `   ` $\rightarrow$ Blocked with inline error.
   - Try negative salary `-1000` $\rightarrow$ Blocked with inline error.
   - Try non-numeric salary `abc` $\rightarrow$ Blocked with inline error.
   - Try 9-digit contact `987654321` $\rightarrow$ Blocked with inline error.
5. **Test Dynamic Search:**
   - Add a second employee (e.g., ID: `EMP102`, Name: `Priya Verma`, Dept: `Human Resources`).
   - In the search bar, type `priya` $\rightarrow$ Only Priya's row displays.
   - Type `Eng` $\rightarrow$ Only Aarav's Engineering row displays.
   - Click `×` or clear the search $\rightarrow$ Both employees display.
6. **Test Edit / Update:**
   - Click **Edit** on `EMP101`. Notice form heading changes to "Edit Employee Details", inputs populate, and submit button reads "Update Employee".
   - Modify salary to `75000` and click **Update Employee**.
   - Verify row updates and total payroll reflects the new salary.
   - Click **Edit** and test "Cancel Edit" button $\rightarrow$ Form resets to Add mode.
7. **Test Deletion Confirmation:**
   - Click **Delete** on an employee row.
   - Confirm modal dialog displays asking for confirmation.
   - Click "Yes, Delete Record" $\rightarrow$ Record is removed, dashboard aggregates decrement.
8. **Test Persistence:**
   - Stop Flask server (`Ctrl + C`) and start it again (`python app.py`).
   - Refresh browser $\rightarrow$ All previously saved records remain intact.

---

## 19. Automated Testing Instructions

The project includes an automated test suite written using Python's built-in `unittest` framework and Flask's test client. The tests execute on an isolated, temporary SQLite database and do **not** alter your live application database (`employee.db`).

### Running the Test Suite:
Run the following command from the project root:

```powershell
python test_app.py -v
```

---

## 20. Expected Test Results

When you run `python test_app.py -v`, all 15 tests will execute and pass:

```text
test_add_employee_duplicate_id (__main__.EmployeeManagementSystemTestCase.test_add_employee_duplicate_id)
Ensure duplicate employee_id returns 409 Conflict. ... ok
test_add_employee_invalid_contact_digits (__main__.EmployeeManagementSystemTestCase.test_add_employee_invalid_contact_digits)
Ensure contact number with fewer or more than 10 digits returns 400. ... ok
test_add_employee_missing_fields (__main__.EmployeeManagementSystemTestCase.test_add_employee_missing_fields)
Ensure missing mandatory fields return 400 Bad Request. ... ok
test_add_employee_negative_salary (__main__.EmployeeManagementSystemTestCase.test_add_employee_negative_salary)
Ensure negative salary is rejected with 400 Bad Request. ... ok
test_add_employee_non_numeric_salary (__main__.EmployeeManagementSystemTestCase.test_add_employee_non_numeric_salary)
Ensure non-numeric salary string is rejected with 400 Bad Request. ... ok
test_add_employee_success (__main__.EmployeeManagementSystemTestCase.test_add_employee_success)
Ensure adding an employee with valid data returns 201. ... ok
test_add_employee_whitespace_only (__main__.EmployeeManagementSystemTestCase.test_add_employee_whitespace_only)
Ensure whitespace-only fields are rejected with 400 Bad Request. ... ok
test_dashboard_aggregations_full_cycle (__main__.EmployeeManagementSystemTestCase.test_dashboard_aggregations_full_cycle)
Verify dashboard statistics accurately calculate metrics through add, update, and delete. ... ok
test_database_persistence_across_connections (__main__.EmployeeManagementSystemTestCase.test_database_persistence_across_connections)
Ensure records persist across separate database connection sessions. ... ok
test_delete_employee (__main__.EmployeeManagementSystemTestCase.test_delete_employee)
Ensure DELETE /api/employees/<id> deletes existing and returns 404 for missing. ... ok
test_get_and_search_employees (__main__.EmployeeManagementSystemTestCase.test_get_and_search_employees)
Ensure dynamic search matches employee_id, name, and department case-insensitively. ... ok
test_get_dashboard_empty (__main__.EmployeeManagementSystemTestCase.test_get_dashboard_empty)
Ensure GET /api/dashboard returns zeroes when database is empty. ... ok
test_get_single_employee_by_id (__main__.EmployeeManagementSystemTestCase.test_get_single_employee_by_id)
Ensure GET /api/employees/<id> returns 200 for found and 404 for not found. ... ok
test_index_page_loads (__main__.EmployeeManagementSystemTestCase.test_index_page_loads)
Ensure GET / loads the HTML application successfully. ... ok
test_update_employee (__main__.EmployeeManagementSystemTestCase.test_update_employee)
Ensure PUT /api/employees/<id> updates fields, handles conflicts and 404. ... ok

----------------------------------------------------------------------
Ran 15 tests in 0.234s

OK
```

---

## 21. Common Errors and Troubleshooting

| Issue / Error | Likely Cause | Solution |
| :--- | :--- | :--- |
| `Address already in use` or `Port 5000 is in use` | Another program or previous Flask instance is running on port 5000 | In PowerShell run: `Get-Process python \| Stop-Process -Force` or run Flask on port 5001: edit `app.run(..., port=5001)` |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell execution policy restricted | Run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then activate again |
| `ModuleNotFoundError: No module named 'flask'` | Flask was not installed or virtual environment not activated | Activate virtual environment (`.\venv\Scripts\Activate.ps1`) and run `python -m pip install -r requirements.txt` |
| `sqlite3.OperationalError: database is locked` | Database file opened in another tool with an exclusive write lock | Close external SQLite viewer software (e.g. DB Browser for SQLite) before writing |
| Employee table does not update after form submit | Browser cached old JavaScript | Perform a hard refresh using `Ctrl + F5` or `Ctrl + Shift + R` |

---

## 22. Limitations and Future Enhancements

### Current Limitations:
- Single-user access model without role-based authentication (Admin vs. Employee).
- SQLite is file-based and suited for lightweight applications or college projects; not recommended for high-concurrency enterprise scale.
- Contact numbers are strictly validated to 10 digits suited for Indian mobile formats as per college exam requirements.

### Future Enhancements:
- 🔐 User authentication and session management (JWT or Flask-Login).
- 📄 Export employee directory to CSV and PDF formats.
- 🖼️ Profile picture upload functionality with thumbnail rendering.
- 📈 Advanced analytics charts (departmental salary distribution charts via Chart.js).
- 📑 Server-side pagination for organizations with thousands of records.

---

## 23. Author Details & Academic Information
*(Editable placeholders for your college submission)*

- **Student Name:** [Your Name Here]
- **Roll Number / Hall Ticket:** [Your Roll / Registration Number]
- **Degree & Branch:** B.Tech / B.E. / BCA / MCA / B.Sc in Computer Science & Engineering
- **College / University:** [Your College / Institute Name]
- **Academic Year:** 2026 – 2027
- **Course / Subject:** Full-Stack Web Development / Web Technologies Lab
- **Project Mentor / Guide:** [Guide Professor Name]

---

## 24. GitHub Upload Instructions

Prepare and publish your project to GitHub using standard Git commands.

### Prerequisites:
1. Install Git for Windows if not already installed: [https://git-scm.com/download/win](https://git-scm.com/download/win).
2. Create an empty repository on GitHub named: `employee-management-system`.
   - **Repository description:** `"Employee Management System built with HTML, CSS, JavaScript, Python Flask, and SQLite, featuring employee CRUD operations, search, dashboard statistics, and REST APIs."`
   - Leave "Initialize with README" **unchecked** (we already have a complete README).

### PowerShell Commands to Push:
Run the following commands from your project root folder (`C:\Users\lenovo\Desktop\employee-management-system`):

```powershell
# 1. Initialize local Git repository
git init

# 2. Add all project files (respecting .gitignore)
git add .

# 3. Create your initial commit
git commit -m "Initial commit: Employee Management System"

# 4. Rename default branch to main
git branch -M main

# 5. Connect local repository to your remote GitHub repository
# Replace <YOUR_GITHUB_REPOSITORY_URL> with your actual repository URL
# e.g., https://github.com/your-username/employee-management-system.git
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>

# 6. Push project code to GitHub
git push -u origin main
```

---

## 25. Viva / Practical Exam Questions & Answers (Cheat Sheet)

1. **Q: Why did you choose SQLite over MySQL or PostgreSQL?**  
   *A:* SQLite is a serverless, self-contained, zero-configuration database that stores all data in a single cross-platform file (`employee.db`). It comes built-in with Python's standard library (`import sqlite3`), eliminating extra server setups while providing full ACID transactions and SQL standards.

2. **Q: How does your code prevent SQL Injection attacks?**  
   *A:* By using **parameterized queries** with placeholder question marks (`?`) in every SQL statement (e.g., `cursor.execute("SELECT * FROM employees WHERE id = ?", (id,))`). The database driver treats user input strictly as data, never as executable SQL code.

3. **Q: What is a REST API and which HTTP methods did you implement?**  
   *A:* REST (Representational State Transfer) is an architectural style for web services. We implemented:
   - `GET`: Retrieve employee records or dashboard statistics.
   - `POST`: Create a new employee record.
   - `PUT`: Update an existing employee record.
   - `DELETE`: Remove an employee record.

4. **Q: How does the dashboard update without reloading the page?**  
   *A:* Through asynchronous JavaScript using the modern `Fetch API` (`fetch("/api/dashboard")`). When an operation completes, `refreshInterface()` calls `loadDashboardStats()` and `fetchEmployees()`, updating the DOM dynamically.

5. **Q: How does the application prevent XSS (Cross-Site Scripting)?**  
   *A:* Rather than concatenating strings directly into `innerHTML`, the application uses safe DOM APIs (`document.createElement` and `element.textContent`), ensuring user-supplied strings are treated purely as text and never executed as HTML/script.
