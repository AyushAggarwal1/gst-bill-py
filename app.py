from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json

# Initialize FastAPI app
app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoiceNo TEXT NOT NULL,
            date TEXT NOT NULL,
            customer TEXT,
            amount REAL
        )
    """)
    conn.commit()
    conn.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Endpoint to save invoice
@app.post("/save-invoice")
async def save_invoice(request: Request):
    try:
        data = await request.json()
        print("Received payload:", data)

        # Validate input
        if not data.get("invoiceNo"):
            return {"message": "Invoice number is missing"}  # Graceful response
        if not data.get("date") or "undefined" in data.get("date"):
            return {"message": "Valid date is required"}

        # Extract optional fields
        customer = data.get("customer", "")
        amount = data.get("amount", 0.0)

        # Save to SQLite database
        conn = sqlite3.connect("invoices.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invoices (invoiceNo, date, customer, amount)
            VALUES (?, ?, ?, ?)
        """, (data["invoiceNo"], data["date"], customer, amount))
        conn.commit()
        conn.close()

        # Success response
        return {"message": "Invoice saved successfully"}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": f"An error occurred: {str(e)}"}  # Ensure JSON is returned
