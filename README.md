# Smart Banking Application

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?style=flat&logo=python)](https://www.python.org)

## Account Creation API

---

## 📌 Use Case Overview

**Primary Flow:**
1. Customer logs in to the banking application
2. Customer requests to create a new account (Savings/Current/Fixed Deposit)
3. System validates customer eligibility and KYC status
4. System generates unique account number
5. Customer makes initial deposit
6. Account is created and activated

**Business Rules:**
- Customer must have completed KYC verification
- Minimum initial deposit required (₹500 for Savings, ₹1000 for Current, ₹5000 for FD)
- Account number format: ACC + 10 digits (e.g., ACC1234567890)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL 15+ |
| **ORM** | SQLAlchemy 2.0 |
| **Authentication** | JWT (python-jose) |
| **API Testing** | Swagger UI (built-in FastAPI) |
| **Validation** | Pydantic v2 |
| **Password Hashing** | bcrypt / passlib |

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│  (Postman)  │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────┐
│   FastAPI Application       │
│  ┌─────────────────────┐   │
│  │ Auth Middleware     │   │
│  │ (Verify JWT Token)  │   │
│  └──────────┬──────────┘   │
│             ▼               │
│  ┌─────────────────────┐   │
│  │ Account Routes      │   │
│  │ /api/v1/accounts    │   │
│  └──────────┬──────────┘   │
│             ▼               │
│  ┌─────────────────────┐   │
│  │ Business Logic      │   │
│  │ - Validate inputs   │   │
│  │ - Check eligibility │   │
│  │ - Generate acc no   │   │
│  └──────────┬──────────┘   │
│             ▼               │
│  ┌─────────────────────┐   │
│  │ Database Layer      │   │
│  │ (SQLAlchemy ORM)    │   │
│  └──────────┬──────────┘   │
└─────────────┼───────────────┘
              ▼
    ┌──────────────────┐
    │   PostgreSQL     │
    │   - customers    │
    │   - accounts     │
    │   - transactions │
    └──────────────────┘
```

---

## 🚀 API Endpoint

### **POST /api/accounts**

**Tag:** `Accounts`

**Description:** Create a new bank account for an authenticated customer

**Authentication:** Required (JWT Bearer Token)

---

## 📥 Input

**Headers:**
```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
  "account_type": "SAVINGS",
  "initial_deposit": 5000.00,
}
```

**Field Validations:**

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `account_type` | string | ✅ Yes | Enum: `SAVINGS`, `CURRENT`, `FIXED_DEPOSIT` |
| `initial_deposit` | float | ✅ Yes | Min: ₹500 (Savings), ₹1000 (Current), ₹5000 (FD) |


---

## 📤 Output

### ✅ Success Response (201 Created)

```json
{
  "message": "Account created successfully",
  "account_id": 2,
  "account_number": "CUR2025000001",
  "account_type": "CURRENT",
  "balance": "5000.00",
  "created_at": "2025-10-26 10:40:11.316256"
}
```

---

### ❌ Error Responses

**1. KYC Not Completed (403 Forbidden)**
```json
{
  "detail": "KYC not completed"
}
```

**2. Insufficient Initial Deposit (400 Bad Request)**
```json
{
  "detail": "Minimum deposit for CURRENT account is 500"
}
```

**3. Unauthorized (401 Unauthorized)**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired JWT token"
  }
}
```


---


## 📊 Database Schema

```sql
CREATE TABLE customer (
    customer_id bigint NOT NULL DEFAULT nextval('customers_customer_id_seq'::regclass),
    full_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    email character varying(100) COLLATE pg_catalog."default" NOT NULL,
    phone_number character varying(15) COLLATE pg_catalog."default",
    address text COLLATE pg_catalog."default",
    kyc_status character varying(20) COLLATE pg_catalog."default" NOT NULL DEFAULT 'PENDING'::character varying,
    password_hash character varying(128) COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
);

CREATE TABLE customer (
    account_id bigint NOT NULL DEFAULT nextval('accounts_account_id_seq'::regclass),
    account_number character varying(20) COLLATE pg_catalog."default" NOT NULL,
    customer_id bigint NOT NULL,
    account_type character varying(20) COLLATE pg_catalog."default" NOT NULL,
    balance numeric(15,2) NOT NULL DEFAULT 0.00,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP )
```

---

## 🚀 Quick Start


### Live Demo
This application is deployed and running on Render. You can access it here:

**[Smart Banking Application](https://smart-attendance-tracker-2r7y.onrender.com)**

### Deployment
The app is hosted on [Render.com](https://render.com) for reliable and scalable cloud hosting.
### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/smart-banking-application.git
cd smart-banking-application

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

