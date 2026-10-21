# API Standards

Version: 1.0

---

# Purpose

Dokumen ini mendefinisikan standar API yang wajib digunakan oleh seluruh AI Agent dan Developer.

Tujuan:

- Konsistensi
- Maintainability
- Scalability
- Security
- Easier Frontend Integration
- Easier Testing

Semua API wajib mengikuti standar ini.

---

# API Architecture

Architecture Style:

```text
REST API
```

Protocol:

```text
HTTPS
```

Format:

```text
JSON
```

Encoding:

```text
UTF-8
```

---

# API Versioning

Semua endpoint wajib menggunakan versioning.

Format:

```text
/api/v1
```

Example:

```http
GET /api/v1/users
```

```http
POST /api/v1/users
```

---

# Endpoint Naming Convention

Gunakan:

```text
kebab-case
plural resource
```

Good:

```http
GET /users

GET /users/{id}

POST /users

PUT /users/{id}

DELETE /users/{id}
```

Bad:

```http
GET /getUsers

POST /createUser

POST /deleteUser
```

---

# REST Standards

Create

```http
POST /users
```

Read All

```http
GET /users
```

Read One

```http
GET /users/{id}
```

Update

```http
PUT /users/{id}
```

Delete

```http
DELETE /users/{id}
```

---

# HTTP Methods

GET

```text
Read Data
```

POST

```text
Create Data
```

PUT

```text
Replace Data
```

PATCH

```text
Partial Update
```

DELETE

```text
Delete Data
```

---

# Request Headers

Standard:

```http
Content-Type: application/json

Accept: application/json
```

Authenticated Request:

```http
Authorization: Bearer <access_token>
```

---

# Success Response

Standard Format

```json
{
  "success": true,
  "message": "Success",
  "data": {}
}
```

---

# Success Response Collection

```json
{
  "success": true,
  "message": "Success",
  "data": []
}
```

---

# Error Response

Standard Format

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": []
}
```

---

# Validation Error Example

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Email is required"
    }
  ]
}
```

---

# Pagination Standard

Query Params

```http
GET /users?page=1&limit=20
```

Response

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_rows": 150,
    "total_pages": 8
  }
}
```

---

# Filter Standard

Example

```http
GET /users?status=active
```

```http
GET /products?category=electronics
```

---

# Search Standard

Example

```http
GET /users?search=ahmad
```

Multiple field search harus dilakukan di backend.

---

# Sorting Standard

Example

```http
GET /users?sort=created_at
```

Descending

```http
GET /users?sort=-created_at
```

---

# Standard Query Parameters

Allowed

```text
page
limit
search
sort
status
```

---

# HTTP Status Codes

Success

```http
200 OK
```

Created

```http
201 Created
```

No Content

```http
204 No Content
```

Bad Request

```http
400 Bad Request
```

Unauthorized

```http
401 Unauthorized
```

Forbidden

```http
403 Forbidden
```

Not Found

```http
404 Not Found
```

Conflict

```http
409 Conflict
```

Validation Error

```http
422 Unprocessable Entity
```

Server Error

```http
500 Internal Server Error
```

---

# Authentication Standard

Method:

```text
JWT
```

Request:

```http
Authorization: Bearer ACCESS_TOKEN
```

---

# Login Response

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 900
  }
}
```

---

# Audit Fields

Every response object should include:

```json
{
  "id": "uuid",
  "created_at": "",
  "updated_at": ""
}
```

where applicable.

---

# Date Format

Standard:

```text
ISO 8601
```

Example:

```text
2026-10-21T12:30:00Z
```

Use:

```text
UTC
```

---

# UUID Standard

Resource ID wajib menggunakan:

```text
UUID
```

Example:

```text
8c6f7038-1a55-4f09-aec3-6b662fa8824f
```

---

# File Upload Standard

Endpoint

```http
POST /files/upload
```

Content Type

```text
multipart/form-data
```

Response

```json
{
  "success": true,
  "data": {
    "file_name": "avatar.jpg",
    "url": "/uploads/avatar.jpg"
  }
}
```

---

# API Documentation

Semua endpoint wajib terdokumentasi.

Tool:

```text
Swagger
OpenAPI
```

Minimal berisi:

- Description
- Request Example
- Response Example
- Error Example
- Authentication Requirement

---

# Logging Standard

Log Request:

```text
Request ID
Endpoint
Response Time
Status Code
```

Do Not Log:

```text
Password
Token
API Key
```

---

# Rate Limiting

Mandatory:

```text
Login
Register
Forgot Password
OTP
```

Example:

```text
5 requests / minute
```

---

# Deprecation Policy

Jika endpoint diganti:

Old

```text
/api/v1/users
```

New

```text
/api/v2/users
```

Old endpoint tetap tersedia selama masa transisi.

---

# API Security Rules

Must:

- Validate Input
- Validate JWT
- Validate Role
- Sanitize Data

Must Not:

- Return Database Error
- Return Stack Trace
- Return Internal Query

---

# Frontend Integration Rules

Frontend hanya boleh berkomunikasi dengan:

```text
Backend API
```

Frontend tidak boleh:

```text
Connect Directly To Database
```

Frontend tidak boleh:

```text
Call OpenRouter Directly
```

Semua request AI harus melalui Backend API.

---

# QA Rules

Semua endpoint wajib memiliki:

```text
Positive Test
Negative Test
Authorization Test
Validation Test
```

---

# AI Agent Rules

Backend Agent wajib:

- Membuat Swagger Documentation
- Mengikuti Response Standard
- Menggunakan UUID
- Menggunakan JWT Authentication

Frontend Agent wajib:

- Mengikuti Response Standard
- Menggunakan Pagination Standard

QA Agent wajib:

- Menguji semua status code
- Menguji semua validation rules

---

# API Review Checklist

Request Validation

```text
[ ] Passed
```

Authentication

```text
[ ] Passed
```

Authorization

```text
[ ] Passed
```

Pagination

```text
[ ] Passed
```

Swagger

```text
[ ] Passed
```

Response Standard

```text
[ ] Passed
```

Error Handling

```text
[ ] Passed
```

Logging

```text
[ ] Passed
```

---

# Golden Rule

Every API must be:

```text
Predictable
Documented
Versioned
Secure
Tested
```

If not:

```text
DO NOT MERGE
```