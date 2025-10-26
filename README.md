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
- One customer can have max 5 accounts
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

### **POST /api/v1/accounts**

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
  "currency": "INR",
  "branch_code": "BR001",
  "nominee_name": "John Doe",
  "nominee_relation": "Father"
}
```

**Field Validations:**

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `account_type` | string | ✅ Yes | Enum: `SAVINGS`, `CURRENT`, `FIXED_DEPOSIT` |
| `initial_deposit` | float | ✅ Yes | Min: ₹500 (Savings), ₹1000 (Current), ₹5000 (FD) |
| `currency` | string | ✅ Yes | Default: `INR` |
| `branch_code` | string | ✅ Yes | Format: `BR` + 3 digits |
| `nominee_name` | string | ❌ No | Max 100 chars |
| `nominee_relation` | string | ❌ No | Max 50 chars |

---

## 📤 Output

### ✅ Success Response (201 Created)

```json
{
  "success": true,
  "data": {
    "account_id": 12345,
    "account_number": "ACC1729936201",
    "account_type": "SAVINGS",
    "status": "ACTIVE",
    "balance": 5000.00,
    "currency": "INR",
    "branch_code": "BR001",
    "customer_id": 67890,
    "customer_name": "Rajesh Kumar",
    "nominee": {
      "name": "John Doe",
      "relation": "Father"
    },
    "created_at": "2025-10-26T10:30:01.234Z",
    "daily_limit": 100000.00
  },
  "message": "Account created successfully"
}
```

---

### ❌ Error Responses

**1. KYC Not Completed (403 Forbidden)**
```json
{
  "success": false,
  "error": {
    "code": "KYC_INCOMPLETE",
    "message": "Complete KYC verification before creating account",
    "details": {
      "kyc_status": "PENDING",
      "required_documents": ["Aadhaar", "PAN Card"]
    }
  }
}
```

**2. Insufficient Initial Deposit (400 Bad Request)**
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_INITIAL_DEPOSIT",
    "message": "Minimum deposit requirement not met",
    "details": {
      "account_type": "SAVINGS",
      "minimum_required": 500.00,
      "provided": 200.00,
      "currency": "INR"
    }
  }
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

## ⚠️ Edge Cases Handled

### 1. **Duplicate Account Creation Request**
- **Issue:** User clicks "Create Account" multiple times rapidly
- **Solution:** Implement idempotency using `request_id` in headers
- **Response:** Return existing account if created within last 5 minutes

### 2. **Concurrent Account Creation**
- **Issue:** Same customer tries creating multiple accounts simultaneously
- **Solution:** Database-level unique constraint + row-level locking
- **Response:** Second request fails with `ACCOUNT_CREATION_IN_PROGRESS`

### 3. **Account Number Collision**
- **Issue:** Generated account number already exists (rare)
- **Solution:** Retry generation with exponential backoff (max 3 attempts)
- **Response:** 500 Internal Server Error if all retries fail

### 4. **Initial Deposit Payment Failure**
- **Issue:** Payment gateway fails after account creation
- **Solution:** Two-phase commit pattern
  1. Create account with status `PENDING_DEPOSIT`
  2. After successful payment, update to `ACTIVE`
- **Response:** Account created but marked pending

### 5. **Expired JWT During Request**
- **Issue:** Token expires mid-request
- **Solution:** Token expiry check at middleware level
- **Response:** 401 Unauthorized with refresh token hint

### 6. **Invalid Account Type Enum**
- **Issue:** Client sends `account_type: "LOAN"`
- **Solution:** Pydantic validation rejects at request parsing
- **Response:** 422 Unprocessable Entity with validation error

### 7. **Negative Initial Deposit**
- **Issue:** `initial_deposit: -1000`
- **Solution:** Pydantic constraint `gt=0` (greater than 0)
- **Response:** 422 Validation Error

### 8. **Database Connection Lost**
- **Issue:** PostgreSQL connection drops during transaction
- **Solution:** SQLAlchemy connection pooling + retry logic
- **Response:** 503 Service Unavailable

### 9. **Customer Not Found in JWT**
- **Issue:** JWT contains `customer_id` that doesn't exist in DB
- **Solution:** Validate customer existence before processing
- **Response:** 404 Customer Not Found

### 10. **Special Characters in Nominee Name**
- **Issue:** `nominee_name: "John<script>alert(1)</script>"`
- **Solution:** Input sanitization + Pydantic string validators
- **Response:** 422 Validation Error (invalid characters)

---

## 🧪 Testing with Postman/Swagger

**Swagger UI URL:** `http://localhost:8000/docs`

**Test Sequence:**
1. **Login:** POST `/api/v1/auth/login` → Get JWT token
2. **Create Account:** POST `/api/v1/accounts` with JWT
3. **Verify:** GET `/api/v1/accounts/{account_number}`

**Postman Collection Variables:**
```json
{
  "base_url": "http://localhost:8000",
  "jwt_token": "{{token}}",
  "customer_id": "67890"
}
```

---

## 📊 Database Schema

```sql
CREATE TABLE accounts (
    account_id BIGSERIAL PRIMARY KEY,
    account_number VARCHAR(13) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('SAVINGS', 'CURRENT', 'FIXED_DEPOSIT')),
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    daily_limit DECIMAL(15,2) NOT NULL DEFAULT 100000.00,
    nominee_name VARCHAR(100),
    nominee_relation VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_balance_positive CHECK (balance >= 0),
    INDEX idx_customer (customer_id),
    INDEX idx_account_number (account_number),
    INDEX idx_status (status)
);
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- pip/poetry

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

# Setup database
createdb smartbanking
psql smartbanking < schema.sql