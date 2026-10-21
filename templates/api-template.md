# API Specification

---

# General Information

Service

```text
```

Feature

```text
```

Version

```text
v1
```

---

# Endpoint

```http
POST /api/v1/resource
```

---

# Authentication

```text
JWT Required
```

---

# Request Headers

```http
Authorization: Bearer TOKEN
Content-Type: application/json
```

---

# Request Body

```json
{
  "name": ""
}
```

---

# Validation Rules

name

```text
Required
Maximum 100 characters
```

---

# Success Response

HTTP

```text
201 Created
```

Body

```json
{
  "success": true,
  "message": "Success",
  "data": {}
}
```

---

# Error Response

HTTP

```text
400 Bad Request
```

```json
{
  "success": false,
  "message": "Validation failed"
}
```

---

# Database Impact

```text
users
customers
orders
```

---

# Security Notes

```text
JWT Validation
RBAC Validation
```

---

# Test Scenarios

```text
Success
Validation Error
Unauthorized
Forbidden
```