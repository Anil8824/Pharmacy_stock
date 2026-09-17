# PharmaStock

PharmaStock is a web-based pharmacy inventory management system designed to manage medicines, batches, expiry dates, sellable stock, and medicine dispensing using the First-Expiry-First-Out (FEFO) approach.

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- GitHub Codespaces

---

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Anil8824/Pharmacy_stock.git
cd Pharmacy_stock


2. Create a Virtual Environment
python -m venv venv

Activate the virtual environment.

Linux / GitHub Codespaces
source venv/bin/activate
Windows
venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
Run the Project

Start the Flask application:

python app.py

The application will run on:

http://127.0.0.1:5000

For GitHub Codespaces, open port 5000 in the browser.

Main Pages
/              → Landing Page
/register      → User Registration
/login         → User Login
/dashboard     → Pharmacy Dashboard
Database

The application uses SQLite for persistent data storage.

The database is automatically initialized when the application starts.

Database Tables
users — stores registered users
medicines — stores medicine information
batches — stores medicine batches, quantities and expiry dates
dispense_records — stores medicine dispensing records

The local database file is:

pharmacy.db

pharmacy.db is excluded from Git using .gitignore.

REST API Endpoints
1. Health Check
GET
/api/health

Checks whether the backend application is running.

Example:

curl http://localhost:5000/api/health

Response:

{
  "status": "healthy"
}
2. User Registration
POST
/api/auth/register

Creates a new user account.

Request Body
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
3. User Login
POST
/api/auth/login

Authenticates the user and creates a session.

Request Body
{
  "email": "john@example.com",
  "password": "password123"
}
Medicine APIs
4. Add Medicine
POST
/api/medicines

Creates a new medicine.

Request Body
{
  "name": "Paracetamol",
  "generic_name": "Acetaminophen"
}
5. List / Search Medicines
GET
/api/medicines

Supports:

Search
Pagination
Sorting
Query Parameters
search
page
limit
sort_by
sort_order
Example
/api/medicines?search=paracetamol&page=1&limit=10&sort_by=name&sort_order=asc
Supported sort_by
name
generic_name
created_at
Supported sort_order
asc
desc
Batch APIs
6. Add Medicine Batch
POST
/api/medicines/<medicine_id>/batches

Adds a batch for a medicine.

Request Body
{
  "batch_number": "PARA-001",
  "quantity": 100,
  "expiry_date": "2027-06-30"
}
Dispensing API
7. Dispense Medicine
POST
/api/medicines/<medicine_id>/dispense

Dispenses medicine using the First-Expiry-First-Out (FEFO) approach.

The system:

Finds batches with available stock.
Ignores expired batches.
Selects the batch with the earliest expiry date.
Dispenses from that batch first.
Uses the next valid batch if additional quantity is required.
Request Body
{
  "quantity": 20
}
Stock API
8. Get Sellable Stock
GET
/api/medicines/<medicine_id>/stock

Returns the total sellable stock of a medicine.

Expired batches are excluded from the stock calculation.

Example Response
{
  "as_of_date": "2026-09-17",
  "medicine": "Paracetamol",
  "sellable_stock": 330
}
Expiry Alert API
9. Get Expiring Batches
GET
/api/alerts/expiring

Returns batches that are approaching their expiry date.

Query Parameter
days
Example
/api/alerts/expiring?days=30

This returns batches that expire within the next 30 days and still have available stock.

Debugging

Run the application with:

python app.py

The Flask application runs in debug mode during development.

If the server is already running, stop it using:

Ctrl + C

Then start it again:

python app.py
Check Backend Health
curl http://localhost:5000/api/health

Expected response:

{
  "status": "healthy"
}
Test Medicine API
curl "http://localhost:5000/api/medicines?page=1&limit=10&sort_by=name&sort_order=asc"
Test Sellable Stock
curl http://localhost:5000/api/medicines/1/stock
Test Expiry Alerts
curl "http://localhost:5000/api/alerts/expiring?days=30"
Core Business Rules
FEFO

Medicine is dispensed from the batch with the earliest valid expiry date first.

Expired Batch Protection

Expired batches are never selected for dispensing.

Sellable Stock

Only non-expired batches with available quantity are counted as sellable stock.

Project Structure
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
Future Enhancements
Supplier Management
Sales Reports
Automated Notifications