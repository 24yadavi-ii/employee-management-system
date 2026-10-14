/**
 * Employee Management System - Vanilla JavaScript Client
 * Handles full CRUD operations, live dashboard updates, dynamic search,
 * validation, and safe DOM manipulation.
 */

// Application State
let currentEditId = null;        // Database ID when in edit mode, or null when in add mode
let searchDebounceTimer = null;  // Timer handle for dynamic search debouncing
let pendingDeleteId = null;      // Database ID of employee pending deletion confirmation

// DOM Element References
const form = document.getElementById("employee-form");
const formHeading = document.getElementById("form-heading");
const formSubheading = document.getElementById("form-subheading");
const employeeDbIdInput = document.getElementById("employee-db-id");
const empIdInput = document.getElementById("emp-id");
const empNameInput = document.getElementById("emp-name");
const empDeptInput = document.getElementById("emp-dept");
const empDesignationInput = document.getElementById("emp-designation");
const empSalaryInput = document.getElementById("emp-salary");
const empContactInput = document.getElementById("emp-contact");
const btnSubmit = document.getElementById("btn-submit");
const btnSubmitText = document.getElementById("btn-submit-text");
const btnReset = document.getElementById("btn-reset");
const btnResetText = document.getElementById("btn-reset-text");

// Error message spans
const errorEmpId = document.getElementById("error-emp-id");
const errorEmpName = document.getElementById("error-emp-name");
const errorEmpDept = document.getElementById("error-emp-dept");
const errorEmpDesignation = document.getElementById("error-emp-designation");
const errorEmpSalary = document.getElementById("error-emp-salary");
const errorEmpContact = document.getElementById("error-emp-contact");

// Dashboard & Table elements
const statTotalEmployees = document.getElementById("stat-total-employees");
const statTotalDepartments = document.getElementById("stat-total-departments");
const statTotalPayroll = document.getElementById("stat-total-payroll");
const statTotalDesignations = document.getElementById("stat-total-designations");
const recordsCounterText = document.getElementById("records-counter-text");
const searchInput = document.getElementById("search-input");
const btnClearSearch = document.getElementById("btn-clear-search");
const btnRefresh = document.getElementById("btn-refresh");
const loadingSpinner = document.getElementById("loading-spinner");
const employeesTable = document.getElementById("employees-table");
const employeesTbody = document.getElementById("employees-tbody");
const emptyState = document.getElementById("empty-state");
const emptyStateTitle = document.getElementById("empty-state-title");
const emptyStateDesc = document.getElementById("empty-state-desc");
const toastContainer = document.getElementById("toast-container");

// Delete confirmation modal elements
const deleteModal = document.getElementById("delete-modal");
const modalEmployeeName = document.getElementById("modal-employee-name");
const modalEmployeeId = document.getElementById("modal-employee-id");
const btnCancelDelete = document.getElementById("btn-cancel-delete");
const btnConfirmDelete = document.getElementById("btn-confirm-delete");


/* ==========================================================================
   Helper Functions
   ========================================================================== */

/**
 * Format numeric value into Indian Rupee currency format (₹).
 * @param {number|string} amount
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    const num = Number(amount) || 0;
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(num);
}

/**
 * Display toast notification at top-right corner.
 * @param {string} message
 * @param {"success"|"error"|"info"} type
 */
function showNotification(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    // SVG icon based on type
    const iconSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    iconSvg.setAttribute("class", "toast-icon");
    iconSvg.setAttribute("viewBox", "0 0 24 24");
    iconSvg.setAttribute("fill", "none");
    iconSvg.setAttribute("stroke", "currentColor");
    iconSvg.setAttribute("stroke-width", "2");

    if (type === "success") {
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", "M20 6L9 17l-5-5");
        iconSvg.appendChild(path);
    } else if (type === "error") {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", "12");
        circle.setAttribute("cy", "12");
        circle.setAttribute("r", "10");
        const line1 = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line1.setAttribute("x1", "15");
        line1.setAttribute("y1", "9");
        line1.setAttribute("x2", "9");
        line1.setAttribute("y2", "15");
        const line2 = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line2.setAttribute("x1", "9");
        line2.setAttribute("y1", "9");
        line2.setAttribute("x2", "15");
        line2.setAttribute("y2", "15");
        iconSvg.append(circle, line1, line2);
    } else {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", "12");
        circle.setAttribute("cy", "12");
        circle.setAttribute("r", "10");
        const line1 = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line1.setAttribute("x1", "12");
        line1.setAttribute("y1", "16");
        line1.setAttribute("x2", "12");
        line1.setAttribute("y2", "12");
        const line2 = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line2.setAttribute("x1", "12");
        line2.setAttribute("y1", "8");
        line2.setAttribute("x2", "12.01");
        line2.setAttribute("y2", "8");
        iconSvg.append(circle, line1, line2);
    }

    const msgSpan = document.createElement("span");
    msgSpan.className = "toast-msg";
    msgSpan.textContent = message;

    toast.appendChild(iconSvg);
    toast.appendChild(msgSpan);
    toastContainer.appendChild(toast);

    // Auto dismiss after 4 seconds
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(20px)";
        setTimeout(() => toast.remove(), 250);
    }, 4000);
}

/**
 * Toggle table loading spinner.
 * @param {boolean} isLoading
 */
function setLoading(isLoading) {
    if (isLoading) {
        loadingSpinner.classList.remove("hidden");
        employeesTable.classList.add("hidden");
        emptyState.classList.add("hidden");
    } else {
        loadingSpinner.classList.add("hidden");
        employeesTable.classList.remove("hidden");
    }
}

/**
 * Clear all form inline validation errors.
 */
function clearValidationErrors() {
    errorEmpId.textContent = "";
    errorEmpName.textContent = "";
    errorEmpDept.textContent = "";
    errorEmpDesignation.textContent = "";
    errorEmpSalary.textContent = "";
    errorEmpContact.textContent = "";

    empIdInput.classList.remove("input-error");
    empNameInput.classList.remove("input-error");
    empDeptInput.classList.remove("input-error");
    empDesignationInput.classList.remove("input-error");
    empSalaryInput.classList.remove("input-error");
    empContactInput.classList.remove("input-error");
}


/* ==========================================================================
   Core Feature Functions
   ========================================================================== */

/**
 * 1. Load real-time dashboard statistics from Flask API.
 */
async function loadDashboardStats() {
    try {
        const response = await fetch("/api/dashboard");
        if (!response.ok) {
            throw new Error(`Failed to load dashboard: HTTP ${response.status}`);
        }
        const result = await response.json();
        if (result.success && result.data) {
            statTotalEmployees.textContent = result.data.total_employees;
            statTotalDepartments.textContent = result.data.total_departments;
            statTotalPayroll.textContent = formatCurrency(result.data.total_payroll);
            statTotalDesignations.textContent = result.data.total_designations;
        }
    } catch (error) {
        console.error("Dashboard metrics error:", error);
    }
}

/**
 * 2. Fetch employee records with optional dynamic search query.
 * @param {string} [query=""]
 */
async function fetchEmployees(query = "") {
    setLoading(true);
    try {
        let endpoint = "/api/employees";
        if (query && query.trim() !== "") {
            endpoint += `?search=${encodeURIComponent(query.trim())}`;
        }

        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }
        const result = await response.json();
        renderEmployeeTable(result.data || [], Boolean(query && query.trim() !== ""));
    } catch (error) {
        console.error("Fetch employees error:", error);
        showNotification("Failed to connect to the server. Please check if Flask is running.", "error");
        setLoading(false);
    }
}

/**
 * Render employee records into the HTML table using safe DOM methods.
 * Avoids innerHTML injection to protect against XSS.
 * @param {Array} employees
 * @param {boolean} isSearchResult
 */
function renderEmployeeTable(employees, isSearchResult = false) {
    setLoading(false);
    employeesTbody.replaceChildren(); // Safely clear old rows

    recordsCounterText.textContent = `Showing ${employees.length} record${employees.length === 1 ? "" : "s"}`;

    if (employees.length === 0) {
        employeesTable.classList.add("hidden");
        emptyState.classList.remove("hidden");

        if (isSearchResult) {
            emptyStateTitle.textContent = "No Matching Employees Found";
            emptyStateDesc.textContent = "No employee matches your current search criteria. Try a different term or clear the search.";
        } else {
            emptyStateTitle.textContent = "No Employees Registered";
            emptyStateDesc.textContent = "No employee records exist yet. Use the form on the left to add your first employee.";
        }
        return;
    }

    employeesTable.classList.remove("hidden");
    emptyState.classList.add("hidden");

    employees.forEach(emp => {
        const tr = document.createElement("tr");

        // Employee ID badge
        const tdId = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = "emp-id-badge";
        badge.textContent = emp.employee_id;
        tdId.appendChild(badge);

        // Name
        const tdName = document.createElement("td");
        tdName.textContent = emp.name;

        // Department
        const tdDept = document.createElement("td");
        tdDept.textContent = emp.department;

        // Designation
        const tdDesig = document.createElement("td");
        tdDesig.textContent = emp.designation;

        // Salary
        const tdSalary = document.createElement("td");
        tdSalary.className = "salary-cell";
        tdSalary.textContent = formatCurrency(emp.salary);

        // Contact
        const tdContact = document.createElement("td");
        tdContact.textContent = emp.contact;

        // Actions (Edit & Delete buttons)
        const tdActions = document.createElement("td");
        tdActions.className = "text-center";
        const actionsGroup = document.createElement("div");
        actionsGroup.className = "actions-cell";

        const btnEdit = document.createElement("button");
        btnEdit.type = "button";
        btnEdit.className = "btn btn-sm btn-edit";
        btnEdit.textContent = "Edit";
        btnEdit.setAttribute("aria-label", `Edit ${emp.name}`);
        btnEdit.addEventListener("click", () => editEmployee(emp.id));

        const btnDelete = document.createElement("button");
        btnDelete.type = "button";
        btnDelete.className = "btn btn-sm btn-delete";
        btnDelete.textContent = "Delete";
        btnDelete.setAttribute("aria-label", `Delete ${emp.name}`);
        btnDelete.addEventListener("click", () => confirmDelete(emp.id, emp.name, emp.employee_id));

        actionsGroup.appendChild(btnEdit);
        actionsGroup.appendChild(btnDelete);
        tdActions.appendChild(actionsGroup);

        tr.append(tdId, tdName, tdDept, tdDesig, tdSalary, tdContact, tdActions);
        employeesTbody.appendChild(tr);
    });
}

/**
 * 3. Validate form inputs on client side.
 * @param {object} data
 * @returns {boolean}
 */
function validateForm(data) {
    clearValidationErrors();
    let isValid = true;

    // Validate Employee ID
    if (!data.employee_id || data.employee_id.trim() === "") {
        errorEmpId.textContent = "Employee ID is mandatory.";
        empIdInput.classList.add("input-error");
        isValid = false;
    }

    // Validate Full Name
    if (!data.name || data.name.trim() === "") {
        errorEmpName.textContent = "Full Name cannot be empty or only spaces.";
        empNameInput.classList.add("input-error");
        isValid = false;
    }

    // Validate Department
    if (!data.department || data.department.trim() === "") {
        errorEmpDept.textContent = "Department cannot be empty or only spaces.";
        empDeptInput.classList.add("input-error");
        isValid = false;
    }

    // Validate Designation
    if (!data.designation || data.designation.trim() === "") {
        errorEmpDesignation.textContent = "Designation cannot be empty or only spaces.";
        empDesignationInput.classList.add("input-error");
        isValid = false;
    }

    // Validate Salary
    if (data.salary === "" || isNaN(Number(data.salary))) {
        errorEmpSalary.textContent = "Salary must be a valid numeric value.";
        empSalaryInput.classList.add("input-error");
        isValid = false;
    } else if (Number(data.salary) < 0) {
        errorEmpSalary.textContent = "Salary cannot be negative.";
        empSalaryInput.classList.add("input-error");
        isValid = false;
    }

    // Validate Contact Number (strictly 10 digits)
    const contactRegex = /^\d{10}$/;
    if (!data.contact || !contactRegex.test(data.contact.trim())) {
        errorEmpContact.textContent = "Contact Number must contain exactly 10 digits.";
        empContactInput.classList.add("input-error");
        isValid = false;
    }

    return isValid;
}

/**
 * 4. Add a new employee record via POST /api/employees.
 * @param {object} data
 */
async function addEmployee(data) {
    try {
        const response = await fetch("/api/employees", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.status === 201 && result.success) {
            showNotification(result.message || "Employee registered successfully!", "success");
            resetForm();
            refreshInterface();
        } else if (response.status === 409) {
            errorEmpId.textContent = result.error || "Employee ID already exists.";
            empIdInput.classList.add("input-error");
            showNotification(result.error, "error");
        } else {
            showNotification(result.error || "Failed to add employee.", "error");
        }
    } catch (error) {
        console.error("Add employee error:", error);
        showNotification("Network error while adding employee.", "error");
    }
}

/**
 * 5. Load employee into form for editing.
 * @param {number} id
 */
async function editEmployee(id) {
    try {
        const response = await fetch(`/api/employees/${id}`);
        if (!response.ok) {
            showNotification("Employee not found or already deleted.", "error");
            refreshInterface();
            return;
        }

        const result = await response.json();
        if (result.success && result.data) {
            const emp = result.data;
            currentEditId = emp.id;
            employeeDbIdInput.value = emp.id;
            empIdInput.value = emp.employee_id;
            empNameInput.value = emp.name;
            empDeptInput.value = emp.department;
            empDesignationInput.value = emp.designation;
            empSalaryInput.value = emp.salary;
            empContactInput.value = emp.contact;

            clearValidationErrors();

            // Toggle to Edit mode UI
            formHeading.textContent = "Edit Employee Details";
            formSubheading.textContent = `Modifying record for ${emp.name} (${emp.employee_id})`;
            btnSubmitText.textContent = "Update Employee";
            btnResetText.textContent = "Cancel Edit";

            // Scroll form into view on mobile
            form.scrollIntoView({ behavior: "smooth", block: "start" });
            empNameInput.focus();
        }
    } catch (error) {
        console.error("Edit employee error:", error);
        showNotification("Failed to fetch employee details for editing.", "error");
    }
}

/**
 * 6. Update existing employee via PUT /api/employees/<id>.
 * @param {number} id
 * @param {object} data
 */
async function updateEmployee(id, data) {
    try {
        const response = await fetch(`/api/employees/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (response.status === 200 && result.success) {
            showNotification(result.message || "Employee updated successfully!", "success");
            resetForm();
            refreshInterface();
        } else if (response.status === 409) {
            errorEmpId.textContent = result.error || "Employee ID conflicts with another record.";
            empIdInput.classList.add("input-error");
            showNotification(result.error, "error");
        } else if (response.status === 404) {
            showNotification("Employee does not exist.", "error");
            resetForm();
            refreshInterface();
        } else {
            showNotification(result.error || "Failed to update employee.", "error");
        }
    } catch (error) {
        console.error("Update employee error:", error);
        showNotification("Network error while updating employee.", "error");
    }
}

/**
 * 7. Open confirmation modal for deletion.
 * @param {number} id
 * @param {string} name
 * @param {string} empId
 */
function confirmDelete(id, name, empId) {
    pendingDeleteId = id;
    modalEmployeeName.textContent = name;
    modalEmployeeId.textContent = empId;
    deleteModal.classList.remove("hidden");
}

/**
 * Close confirmation modal.
 */
function closeDeleteModal() {
    pendingDeleteId = null;
    deleteModal.classList.add("hidden");
}

/**
 * 8. Delete employee record via DELETE /api/employees/<id>.
 * @param {number} id
 */
async function deleteEmployee(id) {
    try {
        const response = await fetch(`/api/employees/${id}`, {
            method: "DELETE"
        });

        const result = await response.json();
        if (response.status === 200 && result.success) {
            showNotification(result.message || "Employee record deleted.", "success");
            // If the deleted employee was currently being edited, reset the form
            if (currentEditId === id) {
                resetForm();
            }
            refreshInterface();
        } else if (response.status === 404) {
            showNotification("Employee not found or already deleted.", "error");
            refreshInterface();
        } else {
            showNotification(result.error || "Failed to delete employee.", "error");
        }
    } catch (error) {
        console.error("Delete employee error:", error);
        showNotification("Network error while deleting employee.", "error");
    } finally {
        closeDeleteModal();
    }
}

/**
 * 9. Reset employee form and restore Add mode.
 */
function resetForm() {
    form.reset();
    currentEditId = null;
    employeeDbIdInput.value = "";
    clearValidationErrors();

    formHeading.textContent = "Add New Employee";
    formSubheading.textContent = "Fill in all fields to register an employee record.";
    btnSubmitText.textContent = "Add Employee";
    btnResetText.textContent = "Reset Form";
}

/**
 * 10. Refresh both table records and dashboard totals without page reload.
 */
function refreshInterface() {
    const currentSearch = searchInput.value.trim();
    fetchEmployees(currentSearch);
    loadDashboardStats();
}

/**
 * 11. Dynamic search handler with debouncing (300ms).
 */
function searchEmployees() {
    const query = searchInput.value;
    if (query.trim() !== "") {
        btnClearSearch.style.display = "block";
    } else {
        btnClearSearch.style.display = "none";
    }

    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        fetchEmployees(query);
    }, 300);
}


/* ==========================================================================
   Event Listeners (No inline event handlers in HTML)
   ========================================================================== */

// Form Submission (Add or Update)
form.addEventListener("submit", (e) => {
    e.preventDefault();

    const data = {
        employee_id: empIdInput.value.trim(),
        name: empNameInput.value.trim(),
        department: empDeptInput.value.trim(),
        designation: empDesignationInput.value.trim(),
        salary: empSalaryInput.value.trim(),
        contact: empContactInput.value.trim()
    };

    if (!validateForm(data)) {
        return;
    }

    if (currentEditId !== null) {
        updateEmployee(currentEditId, data);
    } else {
        addEmployee(data);
    }
});

// Reset or Cancel Button
btnReset.addEventListener("click", () => {
    resetForm();
});

// Search input typing
searchInput.addEventListener("input", searchEmployees);

// Clear search button
btnClearSearch.addEventListener("click", () => {
    searchInput.value = "";
    btnClearSearch.style.display = "none";
    fetchEmployees("");
    searchInput.focus();
});

// Refresh button
btnRefresh.addEventListener("click", () => {
    refreshInterface();
    showNotification("Directory refreshed.", "info");
});

// Delete Modal Buttons
btnCancelDelete.addEventListener("click", closeDeleteModal);

btnConfirmDelete.addEventListener("click", () => {
    if (pendingDeleteId !== null) {
        deleteEmployee(pendingDeleteId);
    }
});

// Close modal when clicking on backdrop
deleteModal.addEventListener("click", (e) => {
    if (e.target === deleteModal) {
        closeDeleteModal();
    }
});

// Close modal on Escape key
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !deleteModal.classList.contains("hidden")) {
        closeDeleteModal();
    }
});

// Input real-time field error clearing as user fixes mistakes
[empIdInput, empNameInput, empDeptInput, empDesignationInput, empSalaryInput, empContactInput].forEach(input => {
    input.addEventListener("input", () => {
        if (input.classList.contains("input-error")) {
            input.classList.remove("input-error");
            const errorSpan = document.getElementById(`error-${input.id}`);
            if (errorSpan) errorSpan.textContent = "";
        }
    });
});

// Initial application load on DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
    loadDashboardStats();
    fetchEmployees();
});
