# API Contract

---

# Endpoint Information

Endpoint Name:

Create Customer

Method:

POST

URL:

/api/v1/customers

Authentication:

Required

Authorization:

Admin

---

# Request Body

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "08123456789"
}
```

---

# Validation Rules

name

Required

Max 255

---

email

Required

Unique

Valid Email

---

phone

Required

Max 20

---

# Success Response

HTTP 201

```json
{
  "success": true,
  "message": "Customer created successfully",
  "data": {
    "id": "uuid"
  }
}
```

---

# Validation Error

HTTP 422

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Email already exists"
    }
  ]
}
```