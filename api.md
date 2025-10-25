# GoalFlow API Documentation

### Overview

This document describes the REST API for the **GoalFlow Backend**, built with Flask and SQLite. It manages user accounts, financial transactions, personal goals, and weekly missions.

---

## Base URL

```
http://127.0.0.1:5000/
```

---

## Accounts Endpoints

### `GET /accounts/`

Returns a list of all user accounts.

**Response Example:**

```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "5551234567",
    "email": "john@example.com",
    "balance": 1500.75
  }
]
```

---

### `GET /accounts/<id>`

Retrieve details for a specific account.

**Response Example:**

```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "balance": 1500.75
}
```

---

### `POST /accounts/`

Create a new account.

**Request Body:**

```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "5559876543",
  "email": "jane@example.com",
  "balance": 0.0
}
```

**Response:** `201 Created`

---

### `PATCH /accounts/<id>`

Update account information (e.g., balance).

**Request Body Example:**

```json
{
  "balance": 2500.0
}
```

**Response:** `200 OK`

---

### `DELETE /accounts/<id>`

Delete an existing account.

**Response:** `200 OK`

---

## Transactions Endpoints

### `GET /transactions/`

Retrieve all transactions.

### `GET /transactions/<id>`

Retrieve a specific transaction.

**Response Example:**

```json
{
  "id": 5,
  "origin_account": 1,
  "destination_account": 2,
  "amount": 200.0,
  "datetime": "2025-10-25 10:00:00"
}
```

---

### `GET /transactions/account/<account_id>`

Get all transactions associated with a specific account.

---

### `POST /transactions/`

Add a new transaction.

**Request Body:**

```json
{
  "origin_account": 1,
  "destination_account": 2,
  "amount": 50.0,
  "business_type": "TRANSFER"
}
```

**Response:** `201 Created`

---

### `PATCH /transactions/<id>`

Update a transaction (e.g., business type).

**Request Body Example:**

```json
{
  "business_type": "PAYMENT"
}
```

---

### `DELETE /transactions/<id>`

Delete a transaction.

**Response:** `200 OK`

---

## Goals Endpoints

### `GET /goals/`

Retrieve all goals.

### `GET /goals/<id>`

Retrieve a specific goal by ID.

**Response Example:**

```json
{
  "GoalId": 1,
  "UserId": 2,
  "GoalName": "Emergency Fund",
  "TargetAmount": 1000,
  "CurrentAmount": 450
}
```

---

### `POST /goals/`

Create a new goal.

**Request Body:**

```json
{
  "UserId": 2,
  "GoalName": "Trip to Japan",
  "Description": "Save for travel",
  "TargetAmount": 5000,
  "Deadline": "2026-01-01"
}
```

**Response:** `201 Created`

---

### `PATCH /goals/<id>`

Update an existing goal (e.g., progress or amount).

**Request Body Example:**

```json
{
  "CurrentAmount": 1200
}
```

---

### `DELETE /goals/<id>`

Delete a goal.

**Response:** `200 OK`

---

## Missions Endpoints

### `GET /missions/`

Retrieve all weekly missions.

### `GET /missions/<id>`

Retrieve a specific mission.

**Response Example:**

```json
{
  "MissionId": 3,
  "UserId": 2,
  "GoalId": 1,
  "Title": "Save 100 this week",
  "TargetAmount": 100,
  "IsCompleted": 0
}
```

---

### `POST /missions/`

Create a new mission.

**Request Body:**

```json
{
  "UserId": 2,
  "GoalId": 1,
  "Title": "Spend less than 200 this week",
  "Description": "Limit unnecessary purchases",
  "Type": "LIMIT_SPENDING",
  "TargetAmount": 200,
  "Deadline": "2025-11-01"
}
```

**Response:** `201 Created`

---

### `PATCH /missions/<id>`

Update mission status or progress.

**Request Body Example:**

```json
{
  "IsCompleted": 1
}
```

**Response:** `200 OK`

---

### `DELETE /missions/<id>`

Delete a mission.

**Response:** `200 OK`

---

## Notes

* All data is stored in **SQLite**.
* Foreign key constraints are enforced.
* Balance updates are triggered by transactions.
* Use PATCH for incremental updates (balance, goal progress, mission completion).

---

### Testing

Use the provided `tests/endpoints.py` script to automatically verify all endpoints.

Run with:

```bash
python tests/endpoints.py
```
