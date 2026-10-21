# API Contract

---

# Document Information

Project Name:

```text
```

Feature Name:

```text
```

Version:

```text
v1
```

Author:

```text
```

Date:

```text
YYYY-MM-DD
```

---

# Overview

Deskripsi singkat endpoint dan tujuan bisnis.

---

# Endpoint Information

Endpoint ID:

```text
API-001
```

Module:

```text
User Management
```

Endpoint Name:

```text
Create User
```

Method:

```http
POST
```

URL:

```http
/api/v1/users
```

Authentication:

```text
Required
```

Authorization:

```text
Admin
Manager
```

---

# Business Rules

BR-001

```text
Email harus unik.
```

BR-002

```text
Password minimal 8 karakter.
```

---

# Headers

Required

```http
Authorization: Bearer TOKEN
Content-Type: application/json
Accept: application/json
```

---

# Request Body

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

---

# Validation Rules

| Field | Required | Type | Rules |
|---------|---------|---------|---------|
| name | Yes | String | Max 255 |
| email | Yes | String | Valid Email |
| password | Yes | String | Min 8 |

---

# Success Response

HTTP Status

```http
201 Created
```

Response

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "uuid"
  }
}
```

---

# Error Responses

## Validation Error

```http
422 Unprocessable Entity
```

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": []
}
```

---

## Unauthorized

```http
401 Unauthorized
```

---

## Forbidden

```http
403 Forbidden
```

---

## Conflict

```http
409 Conflict
```

---

# Database Impact

Affected Tables

```text
users
```

Actions

```text
INSERT
```

---

# Audit Requirements

Must Populate

```text
created_at
created_by
updated_at
updated_by
```

---

# Logging Requirements

Log

```text
Request ID
User ID
Error Message
```

Do Not Log

```text
Password
Token
Secret
```

---

# Test Scenarios

Positive

```text
Create User Success
```

Negative

```text
Duplicate Email
Invalid Email
Missing Password
```

Security

```text
Unauthorized Access
Role Validation
```

---

# Acceptance Criteria Mapping

AC-001

```text
Mapped
```

AC-002

```text
Mapped
```

---

# Change History

| Version | Date | Description |
|----------|----------|----------|
| 1.0 | YYYY-MM-DD | Initial |