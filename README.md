# Fenmo Expense Tracker

A minimal, production-like full-stack expense tracking application built for reliability and correct data handling.

## 🚀 Tech Stack
* **Backend:** FastAPI (Python)
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Database:** SQLite (via SQLAlchemy)

## 🛠️ How to Run Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python -m uvicorn app:app --reload`
3. Open `http://127.0.0.1:8000` in your browser.

## 🧠 Key Design Decisions
1. **Money Handling:** Used Python's `decimal.Decimal` and SQLAlchemy's `Numeric(10, 2)` instead of floats to guarantee precision and avoid binary rounding errors typical in financial data.
2. **Idempotency & Network Resilience:** Implemented an `Idempotency-Key` header sent from the client. If a user has a spotty network and clicks submit multiple times, the backend checks the SQLite database for the unique key and safely returns the existing record rather than creating duplicate charges.
3. **Choice of Persistence (SQLite):** For a time-boxed assessment, SQLite was chosen because it requires no external setup or Docker containers to run locally, while still utilizing a robust ORM (SQLAlchemy) that allows for an easy migration to PostgreSQL in a true production environment.

## ⚖️ Trade-offs Made Due to Timebox
* **Styling vs. Correctness:** Kept the UI styling minimal (Vanilla CSS) to heavily prioritize API resilience, data validation, and idempotency logic.
* **Server-Side Pagination:** The `GET /expenses` endpoint currently returns all records. In a scaled environment, I would implement cursor-based pagination.
* **Python 3.14 Compatibility:** Resolved a bleeding-edge compatibility issue between SQLAlchemy 2.0.29 and Python 3.14's new internal attributes by patching dependencies during deployment.

## 🛑 What was Intentionally Left Out
* **Authentication/Authorization:** Left out to focus purely on the core expense logic.
* **Automated Test Suite:** Prioritized manual edge-case handling (negative amounts, network retries) over building a PyTest suite to ensure a fully functional end-to-end product within the time limit.
