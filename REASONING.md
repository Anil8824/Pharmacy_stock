# Reasoning

## 1. Problem Understanding

The assigned problem was to build a pharmacy inventory system that manages medicines stored in multiple batches.

Each batch has:

- Batch number
- Quantity
- Expiry date

The main business requirement is that medicines should always be dispensed using the **First-Expiry-First-Out (FEFO)** approach.

The system must also ensure that:

- Expired batches are never dispensed.
- Only in-date stock is counted as sellable stock.
- Pharmacists can search medicines.
- Pharmacists can see batches that are approaching expiry.
- The application provides a usable interface over REST APIs.
- Users can register and log in.

---

## 2. Solution Approach

A small full-stack web application was selected because the problem requires both backend business logic and a usable frontend.

The application was implemented using:

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

Flask was selected for the backend because it provides a lightweight way to implement REST APIs and server-rendered pages.

SQLite was selected as the database because the application is small and requires real persistent storage without requiring a separate database server.

---

## 3. Database Design

The database contains four main tables.

### Users

Stores registered pharmacy users.

Important fields:

- id
- name
- email
- password_hash
- created_at

Passwords are stored as hashes instead of plain text.

### Medicines

Stores medicine information.

Important fields:

- id
- name
- generic_name
- created_at

### Batches

Stores individual medicine batches.

Important fields:

- id
- medicine_id
- batch_number
- quantity
- expiry_date
- created_at

Each batch is linked to a medicine using a foreign key.

### Dispense Records

Stores medicine dispensing history.

Important fields:

- id
- medicine_id
- batch_id
- quantity
- dispensed_at

---

## 4. FEFO Logic

The core business logic uses First-Expiry-First-Out.

When a pharmacist requests a quantity of medicine:

1. The system checks batches belonging to the requested medicine.
2. Batches with zero quantity are ignored.
3. Batches whose expiry date is before the current date are ignored.
4. Remaining valid batches are sorted by expiry date in ascending order.
5. The earliest-expiring valid batch is selected first.
6. If that batch does not contain enough stock, the next valid batch is selected.
7. Quantities are deducted from the selected batches.
8. A dispense record is created for every batch used.

This ensures that the batch closest to expiry is used first while preventing expired stock from being dispensed.

---

## 5. Sellable Stock Logic

Sellable stock is calculated using only batches that:

- Have available quantity.
- Have an expiry date greater than or equal to the current date.

Expired batches are therefore excluded from the sellable stock count.

---

## 6. Expiry Alerts

The application provides an expiry alert API.

The API accepts a number of days and returns batches that:

- Still have available stock.
- Have not expired.
- Will expire within the selected number of days.

The dashboard uses this API to display upcoming expiry alerts.

---

## 7. Authentication

User registration and login were implemented.

During registration:

1. User details are validated.
2. Email addresses are normalized to lowercase.
3. Duplicate emails are rejected.
4. Passwords are hashed using Werkzeug.
5. The user is stored in the database.

During login:

1. The email is searched in the database.
2. The password hash is verified.
3. A Flask session is created after successful authentication.
4. The dashboard checks the session before allowing access.

Unauthenticated users are redirected to the login page.

---

## 8. Search, Sorting and Pagination

The medicine API supports searching by:

- Medicine name
- Generic name

Pagination was added to prevent returning an unnecessarily large number of records.

The API supports sorting by:

- name
- generic_name
- created_at

Both ascending and descending sorting are supported.

---

# 9. Testing

The application was tested incrementally while implementing each feature.

## Authentication Testing

Tested:

- User registration
- Duplicate user registration
- Successful login
- Invalid login
- Dashboard access after login

The login flow was also tested through the browser.

---

## Medicine Testing

Tested:

- Adding a medicine
- Loading medicines on the dashboard
- Searching medicines
- Sorting medicines
- Pagination API support

Test medicines were created during development to verify the functionality.

---

## Batch Testing

Tested:

- Adding medicine batches
- Storing batch quantities
- Storing expiry dates
- Handling multiple batches for the same medicine

---

## FEFO Testing

Multiple Paracetamol batches were created with different expiry dates.

The system was tested by dispensing a quantity larger than the available quantity in the earliest-expiring batch.

The system correctly consumed the earliest valid batch first and then moved to the next valid batch when required.

Example:

```text
PARA-001 → 100 units
PARA-002 → 150 units
PARA-003 → 200 units

When 120 units were dispensed:

PARA-001 → 100
PARA-002 → 20

This verified the FEFO behavior.

Expired Batch Testing

An expired test batch was intentionally added:

Batch: EXPIRED-001
Quantity: 50
Expiry Date: 2026-09-10

A dispensing request was then made.

The system did not select the expired batch.

Instead, it selected the earliest valid non-expired batch.

The expired test batch was removed after testing.

Sellable Stock Testing

The stock API was tested after dispensing operations.

The API correctly returned only stock from non-expired batches.

Example response:

{
  "as_of_date": "2026-09-17",
  "medicine": "Paracetamol",
  "sellable_stock": 330
}
Expiry Alert Testing

The expiry alert API was tested using:

/api/alerts/expiring?days=30

The system correctly returned batches approaching expiry while excluding batches outside the selected expiry window.

10. Issues Found and Fixes
Issue 1 — Dashboard Route

Initially, the dashboard page was not available.

A /dashboard route was added to render the dashboard page.

Issue 2 — Login Protection

Initially, the dashboard could be opened without authentication.

Flask sessions were added.

The dashboard now checks whether a user session exists and redirects unauthenticated users to the login page.

Issue 3 — Stock Display

The stock API returned the medicine name as a string.

The frontend initially expected the medicine value to be an object containing a name property.

This caused the medicine name to appear as undefined.

The frontend was corrected to use the medicine string returned by the API.

Issue 4 — Sorting

Initially, the frontend sent:

sort_by
sort_order

but the backend only handled the sort field and always used ascending order.

The API was updated to support both sort_by and sort_order.

The sorting functionality was then tested with both ascending and descending order.

11. Final Validation

The following functionality was successfully tested:

User registration
User login
Session-based dashboard access
Medicine creation
Medicine search
Medicine sorting
Pagination support
Batch creation
FEFO dispensing
Expired batch protection
Sellable stock calculation
Expiry alerts
Dashboard integration
REST API communication