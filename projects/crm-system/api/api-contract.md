# API Contract Document

## Customer Management Feature — CRM System

---

## Document Information

| Attribute | Value |
|-----------|-------|
| **Project Name** | CRM System |
| **Feature Name** | Customer Management |
| **Version** | 1.0 |
| **Author** | API Contract Agent |
| **Date** | Current |
| **Status** | Draft for Review |
| **Based On** | Business Analysis v1.0, PRD v1.0, UI/UX Design v1.0, Technical Design v1.0 |

---

## API Overview

This API contract defines the RESTful interface for the Customer Management feature of the CRM System. The API enables centralized customer data management, replacing distributed Excel workflows with a single authoritative application. The contract covers five core CRUD operations (Create, Read, Update, Soft Delete, Search) plus authentication endpoints, serving two user roles: **Admin** (full CRUD) and **Manager** (read/search only).

**Base URL**: `https://api.crm.company.com/api/v1`  
**Protocol**: HTTPS only  
**Content Type**: `application/json`  
**Authentication**: JWT Bearer Token (HS256)  
**Rate Limiting**: 100 requests/minute/IP (general), 10 requests/minute/IP (auth endpoints)

---

## Resource List

| Resource | Description | Business Entity |
|----------|-------------|-----------------|
| **Customer** | Core business entity representing a customer record with contact, company, address, and classification details | Customer |
| **Auth** | Authentication and session management for Admin and Manager users | User |

---

## Endpoint List

| ID | Name | Method | URL | Purpose | Authentication | Authorization |
|----|------|--------|-----|---------|----------------|---------------|
| EP-01 | Create Customer | POST | `/customers` | Create a new customer record | Required | Admin |
| EP-02 | Search Customers | GET | `/customers` | Search and list customers with pagination | Required | Admin, Manager |
| EP-03 | Get Customer Detail | GET | `/customers/{id}` | Retrieve full customer details by internal ID | Required | Admin, Manager |
| EP-04 | Get Customer by Business Key | GET | `/customers/by-key/{customer_id}` | Retrieve customer by CUST-ID (shareable link) | Required | Admin, Manager |
| EP-05 | Update Customer | PATCH | `/customers/{id}` | Update an existing customer record | Required | Admin |
| EP-06 | Soft Delete Customer | DELETE | `/customers/{id}` | Mark customer as deleted (soft delete) | Required | Admin |
| EP-07 | Login | POST | `/auth/login` | Authenticate user and issue tokens | Public | — |
| EP-08 | Refresh Token | POST | `/auth/refresh` | Obtain new access token using refresh token | Required (Refresh) | Admin, Manager |
| EP-09 | Get Current User | GET | `/auth/me` | Retrieve authenticated user profile | Required | Admin, Manager |

---

## Endpoint Detail

### EP-01: Create Customer

#### Endpoint ID
`EP-01`

#### Name
Create Customer

#### Method
`POST`

#### URL
`/api/v1/customers`

#### Authentication
**Required** — Valid JWT Access Token in `Authorization: Bearer <token>` header

#### Authorization
**Allowed Roles**: `Admin`  
**Forbidden**: `Manager` (returns 403)

#### Headers
| Header | Required | Value |
|--------|----------|-------|
| `Authorization` | Yes | `Bearer <access_token>` |
| `Content-Type` | Yes | `application/json` |
| `Idempotency-Key` | No | Client-generated UUID (future: deduplication) |
| `X-Request-ID` | Auto | Injected by Nginx (correlation) |

#### Path Parameters
None

#### Query Parameters
None

#### Request Body
```json
{
  "full_name": "John Smith",
  "primary_phone": "+15551234567",
  "primary_email": "john@smith.com",
  "company_name": "Acme Corporation",
  "customer_type": "Business",
  "secondary_phone": "+15559876543",
  "secondary_email": "j.smith@acme.com",
  "address_line1": "123 Business Ave",
  "address_line2": "Suite 400",
  "city": "San Francisco",
  "state_province": "CA",
  "postal_code": "94105",
  "country": "US",
  "notes": "Key decision maker for enterprise accounts. Prefers email communication."
}
```

#### Request Body Field Definitions
| Field | Type | Required | Validation Rules | Classification |
|-------|------|----------|------------------|----------------|
| `full_name` | string | Yes | Min 1, Max 200 chars, trim whitespace | Public |
| `primary_phone` | string | Yes | Valid E.164 format (e.g., +15551234567), max 20 chars | Sensitive |
| `primary_email` | string | Yes | Valid RFC 5322, max 254 chars, stored lowercase | Sensitive |
| `company_name` | string | No | Max 200 chars, trim whitespace | Public |
| `customer_type` | string | No | Enum: `Individual`, `Business`, `Government`, `Other` (default: `Individual`) | Public |
| `secondary_phone` | string | No | Valid E.164 if provided, max 20 chars | Sensitive |
| `secondary_email` | string | No | Valid RFC 5322 if provided, max 254 chars, stored lowercase | Sensitive |
| `address_line1` | string | No | Max 200 chars | Public |
| `address_line2` | string | No | Max 200 chars | Public |
| `city` | string | No | Max 100 chars | Public |
| `state_province` | string | No | Max 100 chars | Public |
| `postal_code` | string | No | Max 20 chars | Public |
| `country` | string | No | ISO 3166-1 alpha-2 (2 chars), e.g., `US` | Public |
| `notes` | string | No | Max 2000 chars | Internal |

#### Validation Rules
| Rule ID | Field(s) | Rule | Error Code | HTTP Status |
|---------|----------|------|------------|-------------|
| VR-01 | `full_name` | Required, non-empty after trim | `REQUIRED_FIELD` | 422 |
| VR-02 | `full_name` | Max 200 characters | `MAX_LENGTH_EXCEEDED` | 422 |
| VR-03 | `primary_phone` | Required, valid E.164 format | `INVALID_PHONE_FORMAT` | 422 |
| VR-04 | `primary_email` | Required, valid RFC 5322 format | `INVALID_EMAIL_FORMAT` | 422 |
| VR-05 | `primary_email` | Max 254 characters | `MAX_LENGTH_EXCEEDED` | 422 |
| VR-06 | `company_name` | Max 200 characters if provided | `MAX_LENGTH_EXCEEDED` | 422 |
| VR-07 | `customer_type` | Must be valid enum value | `INVALID_ENUM_VALUE` | 422 |
| VR-08 | `secondary_phone` | Valid E.164 if provided | `INVALID_PHONE_FORMAT` | 422 |
| VR-09 | `secondary_email` | Valid RFC 5322 if provided | `INVALID_EMAIL_FORMAT` | 422 |
| VR-10 | Address fields | Respective max lengths per BR-011 | `MAX_LENGTH_EXCEEDED` | 422 |
| VR-11 | `notes` | Max 2000 characters | `MAX_LENGTH_EXCEEDED` | 422 |
| VR-12 | `country` | Valid ISO 3166-1 alpha-2 if provided | `INVALID_COUNTRY_CODE` | 422 |
| VR-13 | Duplicate Check | Business rule BR-005: (Name similarity >85% AND Phone match) OR (Email exact match) OR (Company exact match AND Phone match) | `DUPLICATE_DETECTED` | 409 |

#### Success Response
**HTTP Status**: `201 Created`

```json
{
  "success": true,
  "message": "Customer created successfully",
  "data": {
    "id": 1,
    "customer_id": "CUST-2024-000001",
    "full_name": "John Smith",
    "company_name": "Acme Corporation",
    "primary_phone": "+15551234567",
    "secondary_phone": "+15559876543",
    "primary_email": "john@smith.com",
    "secondary_email": "j.smith@acme.com",
    "address_line1": "123 Business Ave",
    "address_line2": "Suite 400",
    "city": "San Francisco",
    "state_province": "CA",
    "postal_code": "94105",
    "country": "US",
    "customer_type": "Business",
    "status": "Active",
    "notes": "Key decision maker for enterprise accounts. Prefers email communication.",
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": {
      "id": 5,
      "full_name": "Admin User"
    },
    "updated_at": "2024-01-15T10:30:00Z",
    "updated_by": null,
    "deleted_at": null,
    "deleted_by": null,
    "version": 1
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

#### Error Responses

| Scenario | HTTP Status | Error Code | Response Body |
|----------|-------------|------------|---------------|
| Validation failed | 422 | `VALIDATION_ERROR` | `{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "Request validation failed", "details": [{ "field": "primary_email", "code": "INVALID_EMAIL_FORMAT", "message": "Enter a valid email address" }], "request_id": "req_abc123" } }` |
| Unauthenticated | 401 | `UNAUTHENTICATED` | `{ "success": false, "error": { "code": "UNAUTHENTICATED", "message": "Invalid or expired access token", "request_id": "req_abc123" } }` |
| Forbidden (Manager) | 403 | `FORBIDDEN` | `{ "success": false, "error": { "code": "FORBIDDEN", "message": "Insufficient permissions to create customers", "request_id": "req_abc123" } }` |
| Duplicate detected | 409 | `DUPLICATE_DETECTED` | `{ "success": false, "error": { "code": "DUPLICATE_DETECTED", "message": "Potential duplicate customer(s) found", "details": { "matches": [{ "id": 1, "customer_id": "CUST-2024-000001", "full_name": "John Smith", "primary_phone": "+15551234567", "primary_email": "john@smith.com", "company_name": "Acme Corporation", "match_type": "NAME_PHONE", "similarity": 0.92 }], "actions": ["CANCEL", "VIEW_EXISTING", "PROCEED_ANYWAY"] }, "request_id": "req_abc123" } }` |
| Internal server error | 500 | `INTERNAL_ERROR` | `{ "success": false, "error": { "code": "INTERNAL_ERROR", "message": "An unexpected error occurred", "request_id": "req_abc123" } }` |

#### Field Classification
| Field | Classification | Notes |
|-------|----------------|-------|
| `id` | Internal | Surrogate key, not exposed to business users |
| `customer_id` | Public | Business key (CUST-YYYY-NNNNNN) |
| `full_name` | Public | Primary display field |
| `company_name` | Public | |
| `primary_phone` | Sensitive | PII — masked in logs |
| `secondary_phone` | Sensitive | PII — masked in logs |
| `primary_email` | Sensitive | PII — masked in logs |
| `secondary_email` | Sensitive | PII — masked in logs |
| Address fields | Public | |
| `customer_type` | Public | |
| `status` | Public | |
| `notes` | Internal | Free-form admin notes |
| `created_at`, `created_by` | Internal | Audit fields |
| `updated_at`, `updated_by` | Internal | Audit fields |
| `deleted_at`, `deleted_by` | Internal | Audit fields (null if active) |
| `version` | Internal | Optimistic locking |

#### Audit Requirement
**Audit Required: Yes**  
**Event**: `CUSTOMER_CREATED`  
**Captured**: Actor (user_id, role), Timestamp, All field values, Request ID  
**Storage**: Customer entity (`created_by`, `created_at`) + AuditEvent table (Phase 2)

#### Idempotency
**Non-Idempotent** — Each POST creates a new record. Future: `Idempotency-Key` header for deduplication.

#### Performance Expectation
- **Target**: < 1 minute end-to-end (form load → submit → confirmation)
- **Database**: Single INSERT + index updates (~50ms)
- **Network**: < 500ms total API latency (p95)

#### Test Scenarios

| Scenario Type | Test Case | Expected Result |
|---------------|-----------|-----------------|
| **Positive** | Valid request with all required fields | 201 Created, customer returned, immediately searchable |
| **Positive** | Valid request with optional fields only | 201 Created, optional fields populated |
| **Negative** | Missing `full_name` | 422 Validation Error, `REQUIRED_FIELD` on `full_name` |
| **Negative** | Invalid `primary_email` format | 422 Validation Error, `INVALID_EMAIL_FORMAT` |
| **Negative** | Invalid `primary_phone` format | 422 Validation Error, `INVALID_PHONE_FORMAT` |
| **Negative** | Manager role attempts create | 403 Forbidden |
| **Negative** | Expired/missing JWT | 401 Unauthenticated |
| **Boundary** | `full_name` = 200 chars | 201 Created |
| **Boundary** | `full_name` = 201 chars | 422 Validation Error |
| **Boundary** | `notes` = 2000 chars | 201 Created |
| **Boundary** | `notes` = 2001 chars | 422 Validation Error |
| **Security** | SQL injection in `full_name` | 422 or sanitized, no execution |
| **Security** | XSS payload in `notes` | Stored as-is, escaped on render |
| **Business** | Duplicate detected (email match) | 409 with match details, actions provided |
| **Business** | Duplicate detected, proceed anyway | 201 Created (new record) |
| **Business** | Duplicate detected, view existing | 409, frontend navigates to existing detail |

---

### EP-02: Search Customers

#### Endpoint ID
`EP-02`

#### Name
Search Customers

#### Method
`GET`

#### URL
`/api/v1/customers`

#### Authentication
**Required** — Valid JWT Access Token

#### Authorization
**Allowed Roles**: `Admin`, `Manager`

#### Headers
| Header | Required | Value |
|--------|----------|-------|
| `Authorization` | Yes | `Bearer <access_token>` |
| `Accept` | Yes | `application/json` |

#### Path Parameters
None

#### Query Parameters
| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `q` | string | No | — | Max 200 chars | Search query across name, company, phone, email, ID, city |
| `page` | integer | No | 1 | Min 1 | Page number (1-based) |
| `size` | integer | No | 20 | Min 1, Max 100 | Results per page |
| `sort` | string | No | `created_at` | Enum: `created_at`, `full_name`, `company_name`, `customer_id` | Sort field |
| `order` | string | No | `desc` | Enum: `asc`, `desc` | Sort order |
| `customer_type` | string | No | — | Enum filter | Filter by customer type |
| `status` | string | No | `Active` | Enum: `Active`, `Deleted` (Admin only) | Filter by status |

#### Request Body
None

#### Validation Rules
| Rule ID | Parameter | Rule | Error Code | HTTP Status |
|---------|-----------|------|------------|-------------|
| VR-20 | `page` | Integer ≥ 1 | `INVALID_PAGE` | 400 |
| VR-21 | `size` | Integer 1–100 | `INVALID_PAGE_SIZE` | 400 |
| VR-22 | `sort` | Valid enum value | `INVALID_SORT_FIELD` | 400 |
| VR-23 | `order` | `asc` or `desc` | `INVALID_SORT_ORDER` | 400 |
| VR-24 | `customer_type` | Valid enum if provided | `INVALID_ENUM_VALUE` | 400 |
| VR-25 | `status` | Valid enum; `Deleted` only for Admin | `FORBIDDEN` | 403 |
| VR-26 | `q` | Max 200 chars | `QUERY_TOO_LONG` | 400 |

#### Success Response
**HTTP Status**: `200 OK`

```json
{
  "success": true,
  "message": "Customers retrieved successfully",
  "data": [
    {
      "id": 1,
      "customer_id": "CUST-2024-000001",
      "full_name": "John Smith",
      "company_name": "Acme Corporation",
      "primary_phone": "+15551234567",
      "primary_email": "john@smith.com",
      "customer_type": "Business",
      "status": "Active",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "customer_id": "CUST-2024-000002",
      "full_name": "Jane Doe",
      "company_name": null,
      "primary_phone": "+15559876543",
      "primary_email": "jane@doe.com",
      "customer_type": "Individual",
      "status": "Active",
      "created_at": "2024-01-16T14:22:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "size": 20,
    "total": 1234,
    "total_pages": 62,
    "request_id": "req_abc123"
  }
}
```

#### Error Responses
| Scenario | HTTP Status | Error Code |
|----------|-------------|------------|
| Validation failed | 400 | `VALIDATION_ERROR` |
| Unauthenticated | 401 | `UNAUTHENTICATED` |
| Forbidden (Manager accessing Deleted) | 403 | `FORBIDDEN` |
| Internal server error | 500 | `INTERNAL_ERROR` |

#### Field Classification (Response Items)
| Field | Classification |
|-------|----------------|
| `id` | Internal |
| `customer_id` | Public |
| `full_name` | Public |
| `company_name` | Public |
| `primary_phone` | Sensitive |
| `primary_email` | Sensitive |
| `customer_type` | Public |
| `status` | Public |
| `created_at` | Internal |

#### Audit Requirement
**Audit Required: No** — Read-only operation

#### Idempotency
**Idempotent** — Safe to retry

#### Performance Expectation
- **Target**: p95 < 5 seconds end-to-end (including network)
- **Database**: p95 < 500ms (trigram index scan, LIMIT 20)
- **Default Page Size**: 20
- **Maximum Page Size**: 100

#### Test Scenarios

| Scenario Type | Test Case | Expected Result |
|---------------|-----------|-----------------|
| **Positive** | No query params (default page/size) | 200 OK, first 20 active customers |
| **Positive** | `q=john` returns matches | 200 OK, fuzzy matches on name/phone/email |
| **Positive** | `q=CUST-2024-000001` exact ID match | 200 OK, single result |
| **Positive** | `page=2&size=10` | 200 OK, records 11-20 |
| **Positive** | `sort=full_name&order=asc` | 200 OK, alphabetical results |
| **Positive** | `customer_type=Business` filter | 200 OK, only Business type |
| **Negative** | `page=0` | 400 Validation Error |
| **Negative** | `size=101` | 400 Validation Error |
| **Negative** | `sort=invalid_field` | 400 Validation Error |
| **Negative** | Manager with `status=Deleted` | 403 Forbidden |
| **Boundary** | `q` = 200 chars | 200 OK |
| **Boundary** | `q` = 201 chars | 400 Validation Error |
| **Boundary** | `page=999999` (beyond total) | 200 OK, empty data array, correct meta |
| **Security** | Search with special chars (`'";--`) | 200 OK, treated as literal search |
| **Performance** | 10K records, `q=smith` | p95 < 5s |

---

### EP-03: Get Customer Detail

#### Endpoint ID
`EP-03`

#### Name
Get Customer Detail

#### Method
`GET`

#### URL
`/api/v1/customers/{id}`

#### Authentication
**Required** — Valid JWT Access Token

#### Authorization
**Allowed Roles**: `Admin`, `Manager`

#### Headers
| Header | Required | Value |
|--------|----------|-------|
| `Authorization` | Yes | `Bearer <access_token>` |
| `Accept` | Yes | `application/json` |

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Internal surrogate key (BIGINT), not `customer_id` |

#### Query Parameters
None

#### Request Body
None

#### Validation Rules
| Rule ID | Parameter | Rule | Error Code | HTTP Status |
|---------|-----------|------|------------|-------------|
| VR-30 | `id` | Valid positive integer | `INVALID_ID_FORMAT` | 400 |
| VR-31 | `id` | Customer exists and not soft-deleted (or requester is Admin with explicit include) | `NOT_FOUND` | 404 |

#### Success Response
**HTTP Status**: `200 OK`

```json
{
  "success": true,
  "message": "Customer retrieved successfully",
  "data": {
    "id": 1,
    "customer_id": "CUST-2024-000001",
    "full_name": "John Smith",
    "company_name": "Acme Corporation",
    "primary_phone": "+15551234567",
    "secondary_phone": "+15559876543",
    "primary_email": "john@smith.com",
    "secondary_email": "j.smith@acme.com",
    "address_line1": "123 Business Ave",
    "address_line2": "Suite 400",
    "city": "San Francisco",
    "state_province": "CA",
    "postal_code": "94105",
    "country": "US",
    "customer_type": "Business",
    "status": "Active",
    "notes": "Key decision maker for enterprise accounts. Prefers email communication.",
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": {
      "id": 5,
      "full_name": "Admin User"
    },
    "updated_at": "2024-01-20T14:15:00Z",
    "updated_by": {
      "id": 5,
      "full_name": "Admin User"
    },
    "deleted_at": null,
    "deleted_by": null,
    "version": 2
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

#### Error Responses
| Scenario | HTTP Status | Error Code |
|----------|-------------|------------|
| Invalid ID format | 400 | `VALIDATION_ERROR` |
| Customer not found (or soft-deleted for Manager) | 404 | `NOT_FOUND` |
| Unauthenticated | 401 | `UNAUTHENTICATED` |
| Internal server error | 500 | `INTERNAL_ERROR` |

#### Field Classification
| Field | Classification |
|-------|----------------|
| All fields | Same as EP-01 response |

#### Audit Requirement
**Audit Required: No** — Read-only operation

#### Idempotency
**Idempotent** — Safe to retry

#### Performance Expectation
- **Target**: < 2 seconds end-to-end
- **Database**: Single PK lookup (~10ms)

#### Test Scenarios

| Scenario Type | Test Case | Expected Result |
|---------------|-----------|-----------------|
| **Positive** | Valid ID, active customer | 200 OK, full customer data |
| **Positive** | Admin accessing soft-deleted customer | 200 OK, status=Deleted, deleted_at populated |
| **Negative** | Non-existent ID | 404 Not Found |
| **Negative** | Manager accessing soft-deleted customer | 404 Not Found |
| **Negative** | Invalid ID format (string) | 400 Validation Error |
| **Security** | ID enumeration attempt | 404 (no info leak) |

---

### EP-04: Get Customer by Business Key

#### Endpoint ID
`EP-04`

#### Name
Get Customer by Business Key

#### Method
`GET`

#### URL
`/api/v1/customers/by-key/{customer_id}`

#### Authentication
**Required** — Valid JWT Access Token

#### Authorization
**Allowed Roles**: `Admin`, `Manager`

#### Headers
| Header | Required | Value |
|--------|----------|-------|
| `Authorization` | Yes | `Bearer <access_token>` |
| `Accept` | Yes | `application/json` |

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | string | Yes | Business key format: `CUST-YYYY-NNNNNN` |

#### Query Parameters
None

#### Request Body
None

#### Validation Rules
| Rule ID | Parameter | Rule | Error Code | HTTP Status |
|---------|-----------|------|------------|-------------|
| VR-40 | `customer_id` | Matches pattern `^CUST-\d{4}-\d{6}$` | `INVALID_CUSTOMER_ID_FORMAT` | 400 |
| VR-41 | `customer_id` | Customer exists and not soft-deleted (or Admin) | `NOT_FOUND` | 404 |

#### Success Response
**HTTP Status**: `200 OK` — Same response body as EP-03

#### Error Responses
| Scenario | HTTP Status | Error Code |
|----------|-------------|------------|
| Invalid format | 400 | `VALIDATION_ERROR` |
| Not found | 404 | `NOT_FOUND` |
| Unauthenticated | 401 | `UNAUTHENTICATED` |
| Internal server error | 500 | `INTERNAL_ERROR` |

#### Field Classification
Same as EP-03

#### Audit Requirement
**Audit Required: No** — Read-only operation

#### Idempotency
**Idempotent** — Safe to retry

#### Performance Expectation
- **Target**: < 2 seconds end-to-end
- **Database**: Unique index lookup on `customer_id` (~5ms)

#### Test Scenarios

| Scenario Type | Test Case | Expected Result |
|---------------|-----------|-----------------|
| **Positive** | Valid CUST-ID, active customer | 200 OK, full customer data |
| **Positive** | Admin accessing soft-deleted by CUST-ID | 200 OK |
| **Negative** | Invalid format (e.g., `CUST-123`) | 400 Validation Error |
| **Negative** | Non-existent CUST-ID | 404 Not Found |
| **Negative** | Manager accessing soft-deleted | 404 Not Found |

---

### EP-05: Update Customer

#### Endpoint ID
`EP-05`

#### Name
Update Customer

#### Method
`PATCH`

#### URL
`/api/v1/customers/{id}`

#### Authentication
**Required** — Valid JWT Access Token

#### Authorization
**Allowed Roles**: `Admin`  
**Forbidden**: `Manager` (403)

#### Headers
| Header | Required | Value |
|--------|----------|-------|
| `Authorization` | Yes | `Bearer <access_token>` |
| `Content-Type` | Yes | `application/json` |
| `If-Match` | Yes | Current `version` value (optimistic locking) |

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Internal surrogate key |

#### Query Parameters
None

#### Request Body
```json
{
  "full_name": "John Smith Jr.",
  "primary_phone": "+15551234567",
  "primary_email": "john@smith.com",
  "company_name": "Acme Corporation",
  "customer_type": "Business",
  "secondary_phone": "+15559876543",
  "secondary_email": "j.smith@acme.com",
  "address_line1": "123 Business Ave",
  "address_line2": "Suite 400",
  "city": "San Francisco",
  "state_province": "CA",
  "postal_code": "94105",
  "country": "US",
  "notes": "Updated: Now VP of Procurement. Prefers email."
}
```

#### Request Body Field Definitions
| Field | Type | Required | Validation Rules | Notes |
|-------|------|----------|------------------|-------|
| All fields | Same as EP-01 | No (all optional) | Same as EP-01 | Partial update supported; only provided fields updated |
| `version` | integer | No (in header) | Must match current version | Optimistic lock via `If-Match` header |

#### Validation Rules
| Rule ID | Field(s) | Rule | Error Code | HTTP Status |
|---------|----------|------|------------|-------------|
| VR-50 | `id` (path) | Valid positive integer | `INVALID_ID_FORMAT` | 400 |
| VR-51 | `If-Match` header | Required, valid integer | `MISSING_VERSION_HEADER` | 400 |
| VR-52 | `If-Match` value | Matches current `version` in DB | `VERSION_MISMATCH` | 409 |
| VR-53 | Provided fields | Same validation as EP-01 (VR-01 to VR-12) | Various | 422 |
| VR-54 | Duplicate Check | Business rule BR-005 on changed fields only | `DUPLICATE_DETECTED` | 409 |
| VR-55 | Customer exists | Not soft-deleted | `NOT_FOUND` | 404 |

#### Success Response
**HTTP Status**: `200 OK`

```json
{
  "success": true,
  "message": "Customer updated successfully",
  "data": {
    "id": 1,
    "customer_id": "CUST-2024-000001",
    "full_name": "John Smith Jr.",
    "company_name": "Acme Corporation",
    "primary_phone": "+15551234567",
    "secondary_phone": "+15559876543",
    "primary_email": "john@smith.com",
    "secondary_email": "j.smith@acme.com",
    "address_line1": "123 Business Ave",
    "address_line2": "Suite 400",
    "city": "San Francisco",
    "state_province": "CA",
    "postal_code": "94105",
    "country": "US",
    "customer_type": "Business",
    "status": "Active",
    "notes": "Updated: Now VP of Procurement. Prefers email.",
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": {
      "id": 5,
      "full_name": "Admin User"
    },
    "updated_at": "2024-01-20T14:15:00Z",
    "updated_by": {
      "id": 5,
      "full_name": "Admin User"
    },
    "deleted_at": null,
    "deleted_by": null,
    "version": 3
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

#### Error Responses
| Scenario | HTTP Status | Error Code | Notes |
|----------|-------------|------------|-------|
| Validation failed | 422 | `VALIDATION_ERROR` | Field-level details |
| Unauthenticated | 401 | `UNAUTHENTICATED` | |
| Forbidden (Manager) | 403 | `FORBIDDEN` | |
| Not found / soft-deleted | 404 | `NOT_FOUND` | |
| Version mismatch (concurrent edit) | 409 | `CONFLICT` | `{ "error": { "code": "CONFLICT", "message": "Record was modified by another user", "details": { "current_version": 3, "provided_version": 2 }, "request_id": "req_abc123" } }` |
| Duplicate detected | 409 | `DUPLICATE_DETECTED` | Same structure as EP-01 |
| Internal server error | 500 | `INTERNAL_ERROR` | |

#### Field Classification
Same as EP-01

#### Audit Requirement
**Audit Required: Yes**  
**Event**: `CUSTOMER_UPDATED`  
**Captured**: Actor, Timestamp, Changed fields (old/new values), Request ID  
**Storage**: Customer entity (`updated_by`, `updated_at`, `version`) + AuditEvent (Phase 2)

#### Idempotency
**Non-Idempotent** — PATCH with version check; retry with same version fails after first success.

#### Performance Expectation
- **Target**: < 1 minute end-to-end
- **Database**: Single UPDATE with version check (~30ms)

#### Test Scenarios

| Scenario Type | Test Case | Expected Result |
|---------------|-----------|-----------------|
| **Positive** | Update single field (name) | 200 OK, version incremented |
| **Positive** | Update multiple fields | 200 OK, all changes reflected |
| **Positive** | Update with no changes (same values) | 200 OK, version incremented |
| **Negative** | Missing `If-Match` header | 400 Validation Error |
| **Negative** | Stale `If-Match` value | 409 Conflict, current version in response |
| **Negative** | Manager attempts update | 403 Forbidden |
| **Negative** | Update soft-deleted customer | 404 Not Found |
| **Boundary** | Update `notes` to 2000 chars | 200 OK |
| **Boundary** | Update `notes` to 2001 chars | 422 Validation Error |
| **Business** | Update email to existing customer's email | 409 Duplicate Detected |
| **Business** | Duplicate detected, proceed anyway | 200 OK, version incremented |
| **Security** | XSS in `notes` | Stored, escaped on render |

---

### EP-06: Soft Delete Customer

#### Endpoint ID
`EP-06`

#### Name
Soft Delete Customer

#### Method
`DELETE`

#### URL
`/api/v1/customers/{id}`

#### Authentication
**Required** — Valid JWT Access Token

#### Authorization
**Allowed Roles**: `Admin`  
**Forbidden**: `Manager` (403)

#### Headers
| Header | Required | Value |
|--------|----------|-------|
| `Authorization` | Yes | `Bearer <access_token>` |
| `If-Match` | Yes | Current `version` value |

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Internal surrogate key |

#### Query Parameters
None

#### Request Body
None

#### Validation Rules
| Rule ID | Parameter | Rule | Error Code | HTTP Status |
|---------|-----------|------|------------|-------------|
| VR-60 | `id` (path) | Valid positive integer | `INVALID_ID_FORMAT` | 400 |
| VR-61 | `If-Match` header | Required, valid integer | `MISSING_VERSION_HEADER` | 400 |
| VR-62 | `If-Match` value | Matches current `version` | `VERSION_MISMATCH` | 409 |
| VR-63 | Customer exists | Not already soft-deleted | `NOT_FOUND` | 404 |

#### Success Response
**HTTP Status**: `200 OK`

```json
{
  "success": true,
  "message": "Customer archived successfully",
  "data": {
    "id": 1,
    "customer_id": "CUST-2024-000001",
    "full_name": "John Smith Jr.",
    "status": "Deleted",
    "deleted_at": "2024-01-25T09:00:00Z",
    "deleted_by": {
      "id": 5,
      "full_name": "Admin User"
    },
    "version": 4
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

#### Error Responses
| Scenario | HTTP Status | Error Code |
|----------|-------------|------------|
| Validation failed | 400 | `VALIDATION_ERROR` |
| Unauthenticated | 401 | `UNAUTHENTICATED` |
| Forbidden (Manager) | 403 | `FORBIDDEN` |
| Not found / already deleted | 404 | `NOT_FOUND` |
| Version mismatch | 409 | `CONFLICT` |
| Internal server error | 500 | `INTERNAL_ERROR` |

#### Field Classification
| Field | Classification |
|-------|----------------|
| `id`, `customer_id`, `full_name` | Public |
| `status`, `deleted_at`, `deleted_by`, `version` | Internal |

#### Audit Requirement
**Audit Required: Yes**  
**Event**: `CUSTOMER_DELETED` (soft)  
**Captured**: Actor, Timestamp, Customer ID, Request ID  
**Storage**: Customer entity (`deleted_by`, `deleted_at`, `status`, `version`) + AuditEvent (Phase 2)

#### Idempotency
**Idempotent** — Deleting already-deleted returns 404; safe to retry with same version.

#### Performance Expectation
- **Target**: < 500ms end-to-end
- **Database**: Single UPDATE (~20ms)

#### Test Scenarios

| Scenario Type | Test Case | Expected Result |
|---------------|-----------|-----------------|
| **Positive** | Valid ID, active customer | 200 OK, status=Deleted, deleted_at set |
| **Negative** | Missing `If-Match` | 400 Validation Error |
| **Negative** | Stale version | 409 Conflict |
| **Negative** | Manager attempts delete | 403 Forbidden |
| **Negative** | Already soft-deleted | 404 Not Found |
| **Negative** | Non-existent ID | 404 Not Found |
| **Business** | Soft-deleted excluded from standard search | Verified via EP-02 |
| **Business** | Admin can restore (future EP) | Future: POST /customers/{id}/restore |

---

### EP-07: Login

#### Endpoint ID
`EP-07`

#### Name
Login

#### Method
`POST`

#### URL
`/api/v1/auth/login`

#### Authentication
**Public** — No authentication required

#### Authorization
N/A

#### Headers
| Header | Required | Value |
|--------|----------|-------|
| `Content-Type` | Yes | `application/json` |
| `X-Request-ID` | Auto | Injected by Nginx |

#### Path Parameters
None

#### Query Parameters
None

#### Request Body
```json
{
  "username": "admin_user",
  "password": "securePassword123!"
}
```

#### Request Body Field Definitions
| Field | Type | Required | Validation Rules | Classification |
|-------|------|----------|------------------|----------------|
| `username` | string | Yes | Min 1, Max 50 chars | Public (credential) |
| `password` | string | Yes | Min 12 chars, 1 upper, 1 lower, 1 digit, 1 special | Sensitive (never logged) |

#### Validation Rules
| Rule ID | Field | Rule | Error Code | HTTP Status |
|---------|-------|------|------------|-------------|
| VR-70 | `username` | Required | `REQUIRED_FIELD` | 422 |
| VR-71 | `password` | Required | `REQUIRED_FIELD` | 422 |
| VR-72 | Credentials | Valid username/password combination | `INVALID_CREDENTIALS` | 401 |
| VR-73 | Account | User exists and `is_active = true` | `ACCOUNT_DISABLED` | 403 |
| VR-74 | Rate Limit | Max 5 attempts/min/IP | `RATE_LIMIT_EXCEEDED` | 429 |
| VR-75 | Account Lockout | Max 10 failures → 15 min lockout | `ACCOUNT_LOCKED` | 403 |

#### Success Response
**HTTP Status**: `200 OK`

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
    "token_type": "Bearer",
    "expires_in": 1800,
    "user": {
      "id": 5,
      "username": "admin_user",
      "full_name": "Admin User",
      "email": "admin@company.com",
      "role": "Admin"
    }
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

#### Error Responses
| Scenario | HTTP Status | Error Code |
|----------|-------------|------------|
| Validation failed | 422 | `VALIDATION_ERROR` |
| Invalid credentials | 401 | `INVALID_CREDENTIALS` |
| Account disabled | 403 | `ACCOUNT_DISABLED` |
| Account locked | 403 | `ACCOUNT_LOCKED` |
| Rate limited | 429 | `RATE_LIMIT_EXCEEDED` |
| Internal server error | 500 | `INTERNAL_ERROR` |

#### Field Classification
| Field | Classification |
|-------|----------------|
| `access_token` | Sensitive (never log) |
| `refresh_token` | Sensitive (never log) |
| `user.id`, `user.username`, `user.full_name`, `user.email`, `user.role` | Public |

#### Audit Requirement
**Audit Required: Yes**  
**Event**: `USER_LOGIN_SUCCESS` / `USER_LOGIN_FAILURE`  
**Captured**: Actor (username), IP, User-Agent, Success/Failure, Timestamp  
**Storage**: Auth audit log (Phase 2)

#### Idempotency
**Non-Idempotent** — Each login issues new token pair

#### Performance Expectation
- **Target**: < 1 second
- **bcrypt**: Cost 12 (~200ms)

#### Test Scenarios

| Scenario Type | Test Case | Expected Result |
|---------------|-----------|-----------------|
| **Positive** | Valid credentials, active Admin | 200 OK, tokens + user profile |
| **Positive** | Valid credentials, active Manager | 200 OK, tokens + user profile |
| **Negative** | Wrong password | 401 Invalid Credentials |
| **Negative** | Non-existent username | 401 Invalid Credentials (same message) |
| **Negative** | Disabled account | 403 Account Disabled |
| **Negative** | Locked account (10 failures) | 403 Account Locked |
| **Negative** | Rate limit exceeded (6th attempt/min) | 429 Rate Limited |
| **Security** | Password in logs | Never logged (masked) |
| **Security** | Brute force protection | Lockout after 10 failures |

---

### EP-08: Refresh Token

#### Endpoint ID
`EP-08`

#### Name
Refresh Token

#### Method
`POST`

#### URL
`/api/v1/auth/refresh`

#### Authentication
**Required (Refresh Token)** — Valid Refresh Token in body

#### Authorization
**Allowed Roles**: `Admin`, `Manager` (any valid refresh token)

#### Headers
| Header | Required | Value |
|--------|----------|-------|
| `Content-Type` | Yes | `application/json` |

#### Path Parameters
None

#### Query Parameters
None

#### Request Body
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

#### Request Body Field Definitions
| Field | Type | Required | Validation Rules | Classification |
|-------|------|----------|------------------|----------------|
| `refresh_token` | string | Yes | Valid refresh token (not expired, not revoked) | Sensitive |

#### Validation Rules
| Rule ID | Field | Rule | Error Code | HTTP Status |
|---------|-------|------|------------|-------------|
| VR-80 | `refresh_token` | Required | `REQUIRED_FIELD` | 422 |
| VR-81 | `refresh_token` | Valid format (JWT) | `INVALID_TOKEN_FORMAT` | 401 |
| VR-82 | `refresh_token` | Not expired (7 days) | `TOKEN_EXPIRED` | 401 |
| VR-83 | `refresh_token` | Not revoked (not in blocklist) | `TOKEN_REVOKED` | 401 |
| VR-84 | `refresh_token` | Matches stored hash for user | `INVALID_TOKEN` | 401 |

#### Success Response
**HTTP Status**: `200 OK`

```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "bmV3IHJlZnJlc2ggdG9rZW4gd2l0aCByb3RhdGlvbg...",
    "token_type": "Bearer",
    "expires_in": 1800
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

> **Note**: Refresh token is rotated — new refresh token issued, old one revoked (hash added to blocklist).

#### Error Responses
| Scenario | HTTP Status | Error Code |
|----------|-------------|------------|
| Validation failed | 422 | `VALIDATION_ERROR` |
| Invalid/expired/revoked refresh token | 401 | `UNAUTHENTICATED` (with specific code in details) |
| Internal server error | 500 | `INTERNAL_ERROR` |

#### Field Classification
| Field | Classification |
|-------|----------------|
| `access_token`, `refresh_token` | Sensitive (never log) |

#### Audit Requirement
**Audit Required: Yes**  
**Event**: `TOKEN_REFRESH`  
**Captured**: Actor (user_id), IP, Timestamp, Success/Failure

#### Idempotency
**Non-Idempotent** — Each call rotates refresh token

#### Performance Expectation
- **Target**: < 500ms
- **Database**: Single lookup + hash compare + update (~30ms)

#### Test Scenarios

| Scenario Type | Test Case | Expected Result |
|---------------|-----------|-----------------|
| **Positive** | Valid refresh token | 200 OK, new access + refresh tokens |
| **Negative** | Expired refresh token (>7 days) | 401 Token Expired |
| **Negative** | Revoked refresh token (logout) | 401 Token Revoked |
| **Negative** | Malformed token | 401 Invalid Token Format |
| **Negative** | Reuse old refresh token after rotation | 401 Token Revoked |
| **Security** | Refresh token in logs | Never logged |

---

### EP-09: Get Current User

#### Endpoint ID
`EP-09`

#### Name
Get Current User

#### Method
`GET`

#### URL
`/api/v1/auth/me`

#### Authentication
**Required** — Valid JWT Access Token

#### Authorization
**Allowed Roles**: `Admin`, `Manager`

#### Headers
| Header | Required | Value |
|--------|----------|-------|
| `Authorization` | Yes | `Bearer <access_token>` |
| `Accept` | Yes | `application/json` |

#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

#### Validation Rules
| Rule ID | Rule | Error Code | HTTP Status |
|---------|------|------------|-------------|
| VR-90 | Valid access token | `UNAUTHENTICATED` | 401 |
| VR-91 | User exists and active | `NOT_FOUND` | 404 |

#### Success Response
**HTTP Status**: `200 OK`

```json
{
  "success": true,
  "message": "User profile retrieved",
  "data": {
    "id": 5,
    "username": "admin_user",
    "full_name": "Admin User",
    "email": "admin@company.com",
    "role": "Admin",
    "last_login_at": "2024-01-25T08:30:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

#### Error Responses
| Scenario | HTTP Status | Error Code |
|----------|-------------|------------|
| Unauthenticated | 401 | `UNAUTHENTICATED` |
| User not found (deleted) | 404 | `NOT_FOUND` |
| Internal server error | 500 | `INTERNAL_ERROR` |

#### Field Classification
| Field | Classification |
|-------|----------------|
| All user fields | Public (within authenticated context) |

#### Audit Requirement
**Audit Required: No** — Read-only self-lookup

#### Idempotency
**Idempotent** — Safe to retry

#### Performance Expectation
- **Target**: < 200ms
- **Database**: Single PK lookup (~5ms)

#### Test Scenarios

| Scenario Type | Test Case | Expected Result |
|---------------|-----------|-----------------|
| **Positive** | Valid token | 200 OK, user profile |
| **Negative** | Expired token | 401 Unauthenticated |
| **Negative** | Invalid token | 401 Unauthenticated |
| **Negative** | Token for deleted user | 404 Not Found |

---

## Related Business Entities

### Customer
**Description**: Core business entity representing a customer organization or individual.

**Attributes** (from PRD Section 10.1):
- `customer_id` (Business Key): `CUST-YYYY-NNNNNN`, unique, immutable
- `full_name`: Required, 200 chars max
- `company_name`: Optional, 200 chars max
- `primary_phone`: Required, E.164 format
- `secondary_phone`: Optional, E.164 format
- `primary_email`: Required, RFC 5322, lowercase
- `secondary_email`: Optional, RFC 5322, lowercase
- Address fields: Optional, per BR-011 limits
- `customer_type`: Enum [Individual, Business, Government, Other], default Individual
- `status`: Enum [Active, Deleted], default Active
- `notes`: Optional, 2000 chars max
- Audit fields: `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by`
- `version`: Optimistic lock counter

**Searchable Fields** (MVP):
- `full_name` (fuzzy/partial via pg_trgm)
- `company_name` (fuzzy/partial via pg_trgm)
- `primary_phone` (exact/prefix)
- `secondary_phone` (exact/prefix)
- `primary_email` (exact/prefix)
- `secondary_email` (exact/prefix)
- `customer_id` (exact)
- `city` (exact)
- `customer_type` (exact filter)

### User
**Description**: System user with authentication and authorization context.

**Attributes** (from Technical Design Section 6.1.2):
- `id`: BIGSERIAL PK
- `username`: Unique, 50 chars max
- `password_hash`: bcrypt cost 12
- `full_name`: 200 chars max
- `email`: Unique, 254 chars max
- `role`: Enum [Admin, Manager]
- `is_active`: Boolean
- `last_login_at`: Timestamp
- `created_at`, `updated_at`: Timestamps

---

## Security Requirements

### Authentication
| Requirement | Implementation |
|-------------|----------------|
| **Mechanism** | JWT Bearer Token (HS256) |
| **Access Token TTL** | 30 minutes |
| **Refresh Token TTL** | 7 days (rotating, hashed in DB) |
| **Token Refresh** | Silent at 25 min; intercept 401 → refresh → retry |
| **Logout** | Client clears tokens; server adds refresh token JTI to blocklist |
| **Algorithm** | HS256 with 32+ byte secret from `JWT_SECRET` env |
| **Claims** | `sub` (user_id), `role`, `exp`, `iat`, `jti` |

### Authorization
| Role | Customers | Auth |
|------|-----------|------|
| **Admin** | Create, Read, Update, Delete, Search | Self (login, refresh, me) |
| **Manager** | Read, Search | Self (login, refresh, me) |

**Enforcement**: Middleware validates JWT → extracts `role` claim → checks against route permissions.

### Input Validation
| Layer | Responsibility |
|-------|----------------|
| **Frontend (Zod)** | Immediate UX feedback; mirrors backend rules |
| **Backend (DTO + Validator)** | Source of truth; struct tags + custom validators (phone, email, customer_id) |
| **Database** | CHECK constraints, NOT NULL, UNIQUE, FK |
| **Business Rules** | Service layer (duplicate detection, soft-delete filters, optimistic lock) |

### Rate Limiting
| Endpoint Category | Limit | Burst |
|-------------------|-------|-------|
| General API (`/api/v1/*`) | 100 req/min/IP | 20 |
| Auth endpoints (`/auth/login`, `/auth/refresh`) | 10 req/min/IP | 5 |
| Search (`GET /customers`) | Included in general | — |

**Enforcement**: Nginx `limit_req_zone` + application-level middleware for authenticated endpoints.

### Sensitive Data Handling
| Data | At Rest | In Transit | In Logs | In Memory |
|------|---------|------------|---------|-----------|
| Password Hash | bcrypt | Never transmitted | **Never** | Only during verify |
| JWT Secret | Env var | N/A | **Never** | Loaded at startup |
| Refresh Token Hash | bcrypt in DB | HTTPS only | **Never** | Only during rotate |
| Customer PII (phone, email) | Plaintext (PostgreSQL) | TLS 1.2+ | **Masked** (j***@domain.com, +1****4567) | Go structs |
| Database Credentials | Docker secrets | N/A | **Never** | Loaded at startup |

**Log Masking**: Middleware scrubs `Authorization` header, `password`, `refresh_token` fields from request/response logs.

---

## Acceptance Criteria Coverage

| Acceptance Criteria (from PRD Section 7) | Mapped Endpoint(s) |
|------------------------------------------|-------------------|
| **US-CUST-001 AC-001**: Create customer with valid data → redirect to detail | EP-01 |
| **US-CUST-001 AC-002**: Missing required field → validation error | EP-01 (VR-01, VR-03, VR-04) |
| **US-CUST-001 AC-003**: Duplicate detected → show matches, require confirmation | EP-01 (VR-13, 409 response) |
| **US-CUST-001 AC-004**: New customer searchable within 5 sec | EP-01 → EP-02 |
| **US-CUST-001 AC-005**: Creation time < 1 minute | EP-01 (Performance) |
| **US-CUST-002 AC-001**: Search by multiple criteria, p95 < 5 sec | EP-02 |
| **US-CUST-002 AC-002**: Results display Name, Phone, Email, Company, ID | EP-02 (Response data) |
| **US-CUST-002 AC-003**: Click result → Detail view < 2 sec | EP-02 → EP-03 |
| **US-CUST-002 AC-004**: No results → "No customers found" + Create CTA | EP-02 (Empty data array) |
| **US-CUST-002 AC-005**: Recent searches suggested (Admin) | Frontend (localStorage) |
| **US-CUST-003 AC-001**: Detail view shows all fields grouped logically | EP-03, EP-04 |
| **US-CUST-003 AC-002**: Admin Edit button → Edit form pre-populated | EP-03 → EP-05 |
| **US-CUST-003 AC-003**: Admin Delete button → Soft delete flow | EP-03 → EP-06 |
| **US-CUST-003 AC-004**: Manager read-only (no Edit/Delete) | EP-03 (Role-based UI) |
| **US-CUST-003 AC-005**: Direct URL access with auth | EP-03, EP-04 |
| **US-CUST-004 AC-001**: Update saves changes, reflects in detail | EP-05 |
| **US-CUST-004 AC-002**: Update creates duplicate conflict → warning | EP-05 (VR-54) |
| **US-CUST-004 AC-003**: Updated record immediately searchable | EP-05 → EP-02 |
| **US-CUST-004 AC-004**: Cancel edit → no changes persisted | Frontend (no API call) |
| **US-CUST-004 AC-005**: Update time < 1 minute | EP-05 (Performance) |
| **US-CUST-005 AC-001**: Soft delete → removed from search | EP-06 |
| **US-CUST-005 AC-002**: Soft-deleted excluded from standard search | EP-02 (Filter `deleted_at IS NULL`) |
| **US-CUST-005 AC-003**: Deleted customer recoverable (Future) | Future: POST /customers/{id}/restore |
| **US-CUST-005 AC-004**: Confirmation shows name and ID | EP-06 (Response data) |
| **US-CUST-005 AC-005**: Restore → reappears in search | Future |

**Coverage**: All 25 acceptance criteria mapped to at least one endpoint. No orphan endpoints.

---

## Assumptions

| ID | Assumption | Impact if Invalid |
|----|------------|-------------------|
| ASM-01 | JWT secret rotation uses dual-secret strategy (no forced re-login) | Secret rotation breaks active sessions |
| ASM-02 | pg_trgm similarity threshold 0.3 sufficient for fuzzy search | Search relevance poor; threshold tuning needed |
| ASM-03 | 90-day soft delete retention satisfies compliance | Legal requires different retention |
| ASM-04 | Offset pagination performs adequately to 10K records | Deep-page latency > 5s; cursor pagination needed |
| ASM-05 | Single VPS (2 CPU/2GB) handles peak load with Docker limits | Resource exhaustion; vertical scale or read replica needed |
| ASM-06 | No external API consumers (internal SPA only) | CORS, API versioning, rate limits may need adjustment |
| ASM-07 | Manager role never needs write access in MVP | RBAC redesign required |
| ASM-08 | Customer `id` (surrogate) used in URLs, not `customer_id` | URL structure change if business key preferred |
| ASM-09 | Duplicate detection rules (BR-005) finalized before development | Rules change → service logic + API response changes |
| ASM-10 | Concurrent edit conflicts rare (optimistic locking sufficient) | High contention → pessimistic locking or conflict resolution UI |

---

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Current | API Contract Agent | Initial API Contract from approved Technical Design, PRD, UI/UX Design, Business Analysis |

---

## Handoff Package

### Next Agents & Consumable Artifacts

| Agent | Consumes From This Contract | Produces |
|-------|----------------------------|----------|
| **Backend Agent** | All endpoint specs, DTOs, validation rules, error codes, auth/z rules, pagination, search | Go source code, GORM models, handlers, services, migrations, unit/integration tests |
| **Frontend Agent** | All endpoint specs, request/response schemas, error envelopes, field classifications, auth flows | React/TypeScript app, TanStack Query hooks, Zod schemas, components, E2E tests |
| **Mobile Agent** | Auth endpoints, customer CRUD endpoints, error handling, pagination | React Native app (Phase 2) |
| **QA Agent** | All test scenarios, acceptance criteria mapping, performance targets, security requirements | Test plans, Postman collections, k6 load scripts, security test cases |
| **Reviewer Agent** | Complete contract, traceability to PRD/BA, security rules, NFR alignment | Review sign-off, compliance verification |

### Artifacts Produced by This Contract
- ✅ API Contract Document (this document)
- ✅ Validation Rules (per endpoint)
- ✅ Response Standards (envelope format)
- ✅ Security Rules (auth, authz, rate limiting, data handling)
- ✅ Test Scenarios (per endpoint)
- ✅ Acceptance Criteria Mapping (traceability matrix)

---

## Output Validation Checklist

| Checklist Item | Status |
|----------------|--------|
| [x] Every endpoint defined (9 endpoints) | ✅ |
| [x] Authentication defined per endpoint | ✅ |
| [x] Authorization defined per endpoint | ✅ |
| [x] Validation rules defined per field | ✅ |
| [x] Error contracts defined (standardized envelope) | ✅ |
| [x] Audit requirements defined per endpoint | ✅ |
| [x] Sensitive fields classified (Public/Internal/Sensitive) | ✅ |
| [x] Acceptance criteria mapped to endpoints | ✅ |
| [x] Pagination defined (EP-02) | ✅ |
| [x] Search defined (EP-02) | ✅ |
| [x] Security rules defined | ✅ |
| [x] No SQL generated | ✅ |
| [x] No migrations generated | ✅ |
| [x] No repository logic generated | ✅ |
| [x] No service logic generated | ✅ |
| [x] No infrastructure configuration generated | ✅ |
| [x] No source code generated | ✅ |
| [x] No UI design generated | ✅ |
| [x] No database schemas generated (logical only) | ✅ |

---

*End of API Contract Document*  
*Version 1.0 — Ready for Review by Backend, Frontend, QA, and Reviewer Agents*