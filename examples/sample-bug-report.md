# Bug Report

---

Bug ID:

BUG-001

---

Title

Create Customer returns 500 error

---

Severity

High

---

Priority

P1

---

Environment

Staging

---

Steps To Reproduce

1. Login Admin
2. Open Create Customer
3. Submit form

---

Expected Result

Customer created successfully

---

Actual Result

Internal Server Error

---

Endpoint

POST /api/v1/customers

---

Evidence

Response

```json
{
  "success": false,
  "message": "Internal Server Error"
}
```

---

Impact

Customer cannot be created.

---

Recommendation

Check duplicate email validation logic.