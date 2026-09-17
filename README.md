# 💊 PharmaStock

PharmaStock is a web-based pharmacy inventory management system designed to manage medicines, batches, expiry dates, sellable stock, and medicine dispensing using the **First-Expiry-First-Out (FEFO)** approach.

The system helps pharmacies ensure that medicines are dispensed from the earliest valid expiry batch first while preventing expired batches from being dispensed.

---

## 🚀 Key Features

- User Registration & Login
- Medicine Management
- Batch Management
- Batch Expiry Tracking
- First-Expiry-First-Out (FEFO) Dispensing
- Expired Batch Protection
- Sellable Stock Calculation
- Medicine Search
- Sorting
- Pagination
- Expiry Alerts
- REST API Integration
- Web-based Dashboard
- Persistent SQLite Database

---

## 🎯 Problem Solved

A pharmacy may have the same medicine stored in multiple batches with different expiry dates.

PharmaStock ensures that:

1. Medicines are stored and managed batch-wise.
2. The batch with the earliest valid expiry date is dispensed first.
3. Expired batches are never selected for dispensing.
4. Sellable stock only includes non-expired inventory.
5. Pharmacists can search for medicines quickly.
6. Batches approaching expiry can be identified through expiry alerts.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend Programming |
| Flask | Web Framework and REST APIs |
| SQLite | Persistent Database |
| HTML | Frontend Structure |
| CSS | UI Styling |
| JavaScript | Frontend Logic and API Integration |
| GitHub Codespaces | Development Environment |

---

## 📦 Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Anil8824/Pharmacy_stock.git
cd Pharmacy_stock
```

### 2. Create a Virtual Environment

#### Linux / GitHub Codespaces

Create the virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

#### Windows

Create the virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Start the Flask application:

```bash
python app.py
```

The application will run on:

```text
http://127.0.0.1:5000
```

For GitHub Codespaces, open **port 5000** in the browser.

---

## 🌐 Application Pages

| Route | Description |
|-------|-------------|
| `/` | Landing Page |
| `/register` | User Registration |
| `/login` | User Login |
| `/dashboard` | Pharmacy Dashboard |

---

## 🗄️ Database

The application uses **SQLite** for persistent data storage.

The database is automatically initialized when the application starts.

### Database Tables

| Table | Description |
|-------|-------------|
| `users` | Stores registered user accounts |
| `medicines` | Stores medicine information |
| `batches` | Stores medicine batches, quantities, and expiry dates |
| `dispense_records` | Stores medicine dispensing records |

The local database file is:

```text
pharmacy.db
```

`pharmacy.db` is excluded from Git using `.gitignore`.

---

## 🔌 REST API Endpoints

### 1. Health Check

**GET**

```text
/api/health
```

Checks whether the backend application is running.

#### Example

```bash
curl http://localhost:5000/api/health
```

#### Response

```json
{
  "status": "healthy"
}
```

---

### 2. User Registration

**POST**

```text
/api/auth/register
```

Creates a new user account.

#### Request Body

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

---

### 3. User Login

**POST**

```text
/api/auth/login
```

Authenticates the user and creates a session.

#### Request Body

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

---

## 💊 Medicine APIs

### 4. Add Medicine

**POST**

```text
/api/medicines
```

Creates a new medicine.

#### Request Body

```json
{
  "name": "Paracetamol",
  "generic_name": "Acetaminophen"
}
```

---

### 5. List / Search Medicines

**GET**

```text
/api/medicines
```

Supports:

- Search
- Pagination
- Sorting

#### Query Parameters

| Parameter | Description |
|-----------|-------------|
| `search` | Search by medicine or generic name |
| `page` | Page number |
| `limit` | Number of results per page |
| `sort_by` | Field used for sorting |
| `sort_order` | Sorting direction |

#### Example

```text
/api/medicines?search=paracetamol&page=1&limit=10&sort_by=name&sort_order=asc
```

#### Supported `sort_by`

```text
name
generic_name
created_at
```

#### Supported `sort_order`

```text
asc
desc
```

---

## 📦 Batch APIs

### 6. Add Medicine Batch

**POST**

```text
/api/medicines/<medicine_id>/batches
```

Adds a new batch for a medicine.

#### Request Body

```json
{
  "batch_number": "PARA-001",
  "quantity": 100,
  "expiry_date": "2027-06-30"
}
```

---

## 🔄 Dispensing API

### 7. Dispense Medicine

**POST**

```text
/api/medicines/<medicine_id>/dispense
```

Dispenses medicine using the **First-Expiry-First-Out (FEFO)** approach.

### System Logic

The system:

1. Finds batches with available stock.
2. Ignores expired batches.
3. Selects the batch with the earliest expiry date.
4. Dispenses from that batch first.
5. Uses the next valid batch if additional quantity is required.
6. Records the dispensing transaction.

#### Request Body

```json
{
  "quantity": 20
}
```

### FEFO Example

Suppose Paracetamol has the following batches:

| Batch | Quantity | Expiry Date |
|-------|----------|-------------|
| PARA-001 | 100 | 2026-09-20 |
| PARA-002 | 150 | 2026-10-15 |
| PARA-003 | 200 | 2027-01-10 |

If 120 units are dispensed:

```text
PARA-001 → 100
PARA-002 → 20
```

The system consumes the earliest valid expiry batch first.

---

## 📊 Stock API

### 8. Get Sellable Stock

**GET**

```text
/api/medicines/<medicine_id>/stock
```

Returns the total **sellable stock** of a medicine.

Expired batches are excluded from the calculation.

#### Example Response

```json
{
  "as_of_date": "2026-09-17",
  "medicine": "Paracetamol",
  "sellable_stock": 330
}
```

> The stock value shown above is sample/test data and may change depending on the current database state.

---

## ⚠️ Expiry Alert API

### 9. Get Expiring Batches

**GET**

```text
/api/alerts/expiring
```

Returns batches that are approaching their expiry date and still have available stock.

#### Query Parameter

```text
days
```

#### Example

```text
/api/alerts/expiring?days=30
```

This returns batches that expire within the next 30 days.

---

## 🧠 Core Business Rules

### FEFO — First-Expiry-First-Out

Medicine is dispensed from the batch with the **earliest valid expiry date first**.

### Expired Batch Protection

Expired batches are never selected for dispensing.

Only batches with a valid expiry date and available quantity are considered for dispensing.

### Sellable Stock

Sellable stock includes only:

- Non-expired batches
- Batches with available quantity

Expired inventory is excluded from the sellable stock calculation.

---

## 🧪 Testing & Validation

The following scenarios were tested during development.

### FEFO Dispensing

A dispensing request was tested across multiple batches with different expiry dates.

The system correctly consumed stock from the earliest-expiring valid batch first.

### Expired Batch Protection

An expired batch was added and a dispensing request was performed.

The system skipped the expired batch and used the next valid batch.

### Sellable Stock

The stock API was tested to verify that expired quantities are excluded from the sellable stock count.

### Expiry Alerts

The expiry alert API was tested with a configurable number of days.

### Search, Sorting & Pagination

Medicine listing was tested with:

- Search
- Ascending sorting
- Descending sorting
- Pagination

---

## 🐛 Debugging

Run the application using:

```bash
python app.py
```

The Flask application runs in debug mode during development.

If the server is already running, stop it using:

```text
Ctrl + C
```

Then start it again:

```bash
python app.py
```

### Check Backend Health

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

### Test Medicine API

```bash
curl "http://localhost:5000/api/medicines?page=1&limit=10&sort_by=name&sort_order=asc"
```

### Test Sellable Stock

```bash
curl http://localhost:5000/api/medicines/1/stock
```

### Test Expiry Alerts

```bash
curl "http://localhost:5000/api/alerts/expiring?days=30"
```

---

## 📁 Project Structure

```text
Pharmacy_stock/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── REASONING.md
├── AI_LOGS.md
├── .gitignore
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
└── templates/
    ├── index.html
    ├── login.html
    ├── register.html
    └── dashboard.html
```

---

## 🔮 Future Enhancements

The following features can be added in future versions:

- Supplier Management
- Sales Reports
- Automated Notifications
- Role-Based Access Control
- Inventory Analytics
- Low Stock Alerts
- Pharmacy Sales Management

---

## 📄 Documentation

| File | Description |
|------|-------------|
| `README.md` | Project setup, usage, API documentation, and project overview |
| `REASONING.md` | Development reasoning, testing, and fixes |
| `AI_LOGS.md` | AI-assisted development conversation log |

---

## 👨‍💻 Development

PharmaStock was developed as a pharmacy inventory management solution focused on:

**FEFO dispensing + expired-stock protection + accurate sellable inventory.**

---

## 📜 License

This project is developed for educational and placement assessment purposes.