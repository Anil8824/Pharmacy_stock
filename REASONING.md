# 🧠 Reasoning

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

- `id`
- `name`
- `email`
- `password_hash`
- `created_at`

Passwords are stored as hashes instead of plain text.

### Medicines

Stores medicine information.

Important fields:

- `id`
- `name`
- `generic_name`
- `created_at`

### Batches

Stores individual medicine batches.

Important fields:

- `id`
- `medicine_id`
- `batch_number`
- `quantity`
- `expiry_date`
- `created_at`

Each batch is linked to a medicine using a foreign key.

### Dispense Records

Stores medicine dispensing history.

Important fields:

- `id`
- `medicine_id`
- `batch_id`
- `quantity`
- `dispensed_at`

---

## 4. FEFO Logic

The core business logic uses **First-Expiry-First-Out (FEFO)**.

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

### Registration

During registration:

1. User details are validated.
2. Email addresses are normalized to lowercase.
3. Duplicate emails are rejected.
4. Passwords are hashed using Werkzeug.
5. The user is stored in the database.

### Login

During login:

1. The email is searched in the database.
2. The password hash is verified.
3. A Flask session is created.
4. The dashboard checks the session before allowing access.
5. Unauthenticated users are redirected to the login page.

---

## 8. Search, Sorting and Pagination

The medicine API supports searching by:

- Medicine name
- Generic name

Pagination was added to prevent returning an unnecessarily large number of records.

The API supports sorting by:

- `name`
- `generic_name`
- `created_at`

Both ascending and descending sorting are supported.

---

# 9. Testing

The application was tested incrementally while implementing each feature.

## 9.1 Authentication Testing

Tested:

- User registration
- Duplicate user registration
- Successful login
- Invalid login
- Dashboard access after login

The login flow was also tested through the browser.

---

## 9.2 Medicine Testing

Tested:

- Adding a medicine
- Loading medicines on the dashboard
- Searching medicines
- Sorting medicines
- Pagination API support

Test medicines were created during development to verify the functionality.

---

## 9.3 Batch Testing

Tested:

- Adding medicine batches
- Storing batch quantities
- Storing expiry dates
- Handling multiple batches for the same medicine

---

## 9.4 FEFO Testing

Multiple Paracetamol batches were created with different expiry dates.

The system was tested by dispensing a quantity larger than the available quantity in the earliest-expiring batch.

The system correctly consumed the earliest valid batch first and then moved to the next valid batch when required.

### Example

```text
PARA-001 → 100 units
PARA-002 → 150 units
PARA-003 → 200 units