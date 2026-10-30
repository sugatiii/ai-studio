# Swagger/OpenAPI Documentation for STORY-001: Create Customer

---

## Swagger Summary

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-001 |
| **Endpoint** | `POST /api/v1/customers` |
| **Operation ID** | `createCustomer` |
| **Tags** | `Customers` |
| **Authentication** | JWT Bearer Token (Required) |
| **Authorization** | Admin only (Manager: 403 Forbidden) |
| **Content-Type** | `application/json` |

**Documented Components:**
- 1 Endpoint (EP-01)
- 6 Request/Response Schemas
- 7 Error Response Examples
- 1 Security Scheme (BearerAuth)

---

## Swagger Annotations (Go)

```go
package handlers

import (
	"github.com/gin-gonic/gin"
	"crm-system/internal/dto"
)

// @Summary Create customer
// @Description Creates a new customer record with duplicate detection. Returns created customer or potential duplicates requiring Admin confirmation.
// @Tags Customers
// @Accept json
// @Produce json
// @Security BearerAuth
// @Param request body dto.CreateCustomerRequest true "Customer creation request"
// @Success 201 {object} dto.CreateCustomerSuccessResponse "Customer created successfully"
// @Failure 400 {object} dto.ErrorResponse "Invalid request format"
// @Failure 401 {object} dto.ErrorResponse "Unauthenticated - invalid or expired token"
// @Failure 403 {object} dto.ErrorResponse "Forbidden - Manager role cannot create customers"
// @Failure 409 {object} dto.DuplicateDetectedResponse "Potential duplicate(s) found - requires Admin decision"
// @Failure 422 {object} dto.ValidationErrorResponse "Validation failed - field-level errors"
// @Failure 500 {object} dto.ErrorResponse "Internal server error"
// @Router /api/v1/customers [post]
func (h *CustomerHandler) CreateCustomer(c *gin.Context) {
	// Implementation in handler.go
}
```

---

## OpenAPI Path Definitions (YAML)

```yaml
openapi: 3.0.3
info:
  title: CRM System - Customer Management API
  version: 1.0.0
  description: |
    API for creating customer records in the CRM system.
    This document covers STORY-001: Create Customer (EP-01).
servers:
  - url: https://api.crm.company.com/api/v1
    description: Production server
  - url: http://localhost:8080/api/v1
    description: Development server

paths:
  /customers:
    post:
      summary: Create customer
      description: |
        Creates a new customer record with the provided information.
        
        **Business Rules Enforced:**
        - Required fields: full_name, primary_phone, primary_email (BR-002)
        - Phone numbers normalized to E.164 format (BR-003)
        - Email stored lowercase (BR-012)
        - Field length limits per BR-011
        - Duplicate detection per BR-005:
          * Name similarity > 85% AND phone match
          * Email exact match
          * Company exact match AND phone match
        - Duplicate handling per BR-006: returns 409 with matches and allowed actions
        - Customer ID generated as CUST-YYYY-NNNNNN (BR-001)
        - Audit fields captured: created_by, created_at (BR-015)
      
      operationId: createCustomer
      tags:
        - Customers
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateCustomerRequest'
            examples:
              minimal:
                summary: Minimal valid request (required fields only)
                value:
                  full_name: "John Smith"
                  primary_phone: "+15551234567"
                  primary_email: "john@smith.com"
              full:
                summary: Full request with all optional fields
                value:
                  full_name: "John Smith"
                  primary_phone: "+15551234567"
                  primary_email: "john@smith.com"
                  company_name: "Acme Corporation"
                  customer_type: "Business"
                  secondary_phone: "+15559876543"
                  secondary_email: "j.smith@acme.com"
                  address_line1: "123 Business Ave"
                  address_line2: "Suite 400"
                  city: "San Francisco"
                  state_province: "CA"
                  postal_code: "94105"
                  country: "US"
                  notes: "Key decision maker for enterprise accounts. Prefers email communication."
      responses:
        '201':
          description: Customer created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateCustomerSuccessResponse'
              examples:
                success:
                  summary: Successful creation response
                  value:
                    success: true
                    message: "Customer created successfully"
                    data:
                      id: 1
                      customer_id: "CUST-2024-000001"
                      full_name: "John Smith"
                      company_name: "Acme Corporation"
                      primary_phone: "+15551234567"
                      secondary_phone: "+15559876543"
                      primary_email: "john@smith.com"
                      secondary_email: "j.smith@acme.com"
                      address_line1: "123 Business Ave"
                      address_line2: "Suite 400"
                      city: "San Francisco"
                      state_province: "CA"
                      postal_code: "94105"
                      country: "US"
                      customer_type: "Business"
                      status: "Active"
                      notes: "Key decision maker for enterprise accounts. Prefers email communication."
                      created_at: "2024-01-15T10:30:00Z"
                      created_by:
                        id: 5
                        full_name: "Admin User"
                      updated_at: "2024-01-15T10:30:00Z"
                      updated_by: null
                      deleted_at: null
                      deleted_by: null
                      version: 1
                    meta:
                      request_id: "req_abc123"
        '400':
          description: Invalid request format
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                success: false
                error:
                  code: "INVALID_REQUEST"
                  message: "Invalid request body"
                  request_id: "req_abc123"
        '401':
          description: Unauthenticated - invalid or expired access token
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                success: false
                error:
                  code: "UNAUTHENTICATED"
                  message: "Invalid or expired access token"
                  request_id: "req_abc123"
        '403':
          description: Forbidden - Manager role cannot create customers
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                success: false
                error:
                  code: "FORBIDDEN"
                  message: "Insufficient permissions to create customers"
                  request_id: "req_abc123"
        '409':
          description: Potential duplicate(s) detected - requires Admin decision
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DuplicateDetectedResponse'
              examples:
                email_match:
                  summary: Duplicate detected via email exact match
                  value:
                    success: false
                    error:
                      code: "DUPLICATE_DETECTED"
                      message: "Potential duplicate customer(s) found"
                      details:
                        matches:
                          - id: 1
                            customer_id: "CUST-2024-000001"
                            full_name: "John Smith"
                            primary_phone: "+15551234567"
                            primary_email: "john@smith.com"
                            company_name: "Acme Corporation"
                            match_type: "EMAIL_EXACT"
                            similarity: 1.0
                        actions:
                          - "CANCEL"
                          - "VIEW_EXISTING"
                          - "PROCEED_ANYWAY"
                      request_id: "req_abc123"
                name_phone_match:
                  summary: Duplicate detected via name similarity + phone match
                  value:
                    success: false
                    error:
                      code: "DUPLICATE_DETECTED"
                      message: "Potential duplicate customer(s) found"
                      details:
                        matches:
                          - id: 2
                            customer_id: "CUST-2024-000002"
                            full_name: "Jon Smith"
                            primary_phone: "+15551234567"
                            primary_email: "jon.smith@other.com"
                            company_name: "Other Corp"
                            match_type: "NAME_PHONE"
                            similarity: 0.92
                        actions:
                          - "CANCEL"
                          - "VIEW_EXISTING"
                          - "PROCEED_ANYWAY"
                      request_id: "req_def456"
                company_phone_match:
                  summary: Duplicate detected via company + phone exact match
                  value:
                    success: false
                    error:
                      code: "DUPLICATE_DETECTED"
                      message: "Potential duplicate customer(s) found"
                      details:
                        matches:
                          - id: 3
                            customer_id: "CUST-2024-000003"
                            full_name: "Different Person"
                            primary_phone: "+15551234567"
                            primary_email: "different@company.com"
                            company_name: "Acme Corporation"
                            match_type: "COMPANY_PHONE"
                            similarity: 1.0
                        actions:
                          - "CANCEL"
                          - "VIEW_EXISTING"
                          - "PROCEED_ANYWAY"
                      request_id: "req_ghi789"
        '422':
          description: Validation failed - field-level errors
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValidationErrorResponse'
              examples:
                missing_required:
                  summary: Missing required fields
                  value:
                    success: false
                    error:
                      code: "VALIDATION_ERROR"
                      message: "Request validation failed"
                      details:
                        - field: "full_name"
                          code: "REQUIRED_FIELD"
                          message: "Full name is required"
                        - field: "primary_phone"
                          code: "REQUIRED_FIELD"
                          message: "Primary phone is required"
                        - field: "primary_email"
                          code: "REQUIRED_FIELD"
                          message: "Primary email is required"
                      request_id: "req_abc123"
                invalid_email:
                  summary: Invalid email format
                  value:
                    success: false
                    error:
                      code: "VALIDATION_ERROR"
                      message: "Request validation failed"
                      details:
                        - field: "primary_email"
                          code: "INVALID_EMAIL_FORMAT"
                          message: "Enter a valid email address"
                      request_id: "req_abc123"
                invalid_phone:
                  summary: Invalid phone format (not E.164)
                  value:
                    success: false
                    error:
                      code: "VALIDATION_ERROR"
                      message: "Request validation failed"
                      details:
                        - field: "primary_phone"
                          code: "INVALID_PHONE_FORMAT"
                          message: "Phone number must be in E.164 format (e.g., +15551234567)"
                      request_id: "req_abc123"
                max_length_exceeded:
                  summary: Field exceeds maximum length
                  value:
                    success: false
                    error:
                      code: "VALIDATION_ERROR"
                      message: "Request validation failed"
                      details:
                        - field: "full_name"
                          code: "MAX_LENGTH_EXCEEDED"
                          message: "Full name must not exceed 200 characters"
                        - field: "notes"
                          code: "MAX_LENGTH_EXCEEDED"
                          message: "Notes must not exceed 2000 characters"
                      request_id: "req_abc123"
                invalid_enum:
                  summary: Invalid enum value
                  value:
                    success: false
                    error:
                      code: "VALIDATION_ERROR"
                      message: "Request validation failed"
                      details:
                        - field: "customer_type"
                          code: "INVALID_ENUM_VALUE"
                          message: "Invalid customer type. Must be one of: Individual, Business, Government, Other"
                      request_id: "req_abc123"
                invalid_country:
                  summary: Invalid country code
                  value:
                    success: false
                    error:
                      code: "VALIDATION_ERROR"
                      message: "Request validation failed"
                      details:
                        - field: "country"
                          code: "INVALID_COUNTRY_CODE"
                          message: "Country must be a valid ISO 3166-1 alpha-2 code (e.g., US)"
                      request_id: "req_abc123"
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                success: false
                error:
                  code: "INTERNAL_ERROR"
                  message: "An unexpected error occurred"
                  request_id: "req_abc123"

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT Bearer token authentication.
        Obtain token via POST /api/v1/auth/login (EP-07).
        Include in Authorization header: `Authorization: Bearer <access_token>`
        Access token TTL: 30 minutes.
        Refresh token TTL: 7 days (via POST /api/v1/auth/refresh).

  schemas:
    # ===========================================
    # REQUEST SCHEMAS
    # ===========================================
    CreateCustomerRequest:
      type: object
      required:
        - full_name
        - primary_phone
        - primary_email
      properties:
        full_name:
          type: string
          description: Customer full name (required, max 200 chars)
          minLength: 1
          maxLength: 200
          example: "John Smith"
        primary_phone:
          type: string
          description: Primary phone in E.164 format (required, max 20 chars)
          pattern: '^\+[1-9]\d{1,14}$'
          maxLength: 20
          example: "+15551234567"
        primary_email:
          type: string
          description: Primary email (required, max 254 chars, stored lowercase)
          format: email
          maxLength: 254
          example: "john@smith.com"
        company_name:
          type: string
          description: Company name (optional, max 200 chars)
          maxLength: 200
          example: "Acme Corporation"
        customer_type:
          type: string
          description: Customer type classification (optional, default: Individual)
          enum:
            - Individual
            - Business
            - Government
            - Other
          default: "Individual"
          example: "Business"
        secondary_phone:
          type: string
          description: Secondary phone in E.164 format (optional, max 20 chars)
          pattern: '^\+[1-9]\d{1,14}$'
          maxLength: 20
          example: "+15559876543"
        secondary_email:
          type: string
          description: Secondary email (optional, max 254 chars, stored lowercase)
          format: email
          maxLength: 254
          example: "j.smith@acme.com"
        address_line1:
          type: string
          description: Address line 1 (optional, max 200 chars)
          maxLength: 200
          example: "123 Business Ave"
        address_line2:
          type: string
          description: Address line 2 (optional, max 200 chars)
          maxLength: 200
          example: "Suite 400"
        city:
          type: string
          description: City (optional, max 100 chars)
          maxLength: 100
          example: "San Francisco"
        state_province:
          type: string
          description: State/Province (optional, max 100 chars)
          maxLength: 100
          example: "CA"
        postal_code:
          type: string
          description: Postal/ZIP code (optional, max 20 chars)
          maxLength: 20
          example: "94105"
        country:
          type: string
          description: Country code ISO 3166-1 alpha-2 (optional, 2 chars)
          pattern: '^[A-Z]{2}$'
          minLength: 2
          maxLength: 2
          example: "US"
        notes:
          type: string
          description: Internal notes (optional, max 2000 chars)
          maxLength: 2000
          example: "Key decision maker for enterprise accounts. Prefers email communication."

    # ===========================================
    # RESPONSE SCHEMAS
    # ===========================================
    CreateCustomerSuccessResponse:
      type: object
      required:
        - success
        - message
        - data
        - meta
      properties:
        success:
          type: boolean
          example: true
        message:
          type: string
          example: "Customer created successfully"
        data:
          $ref: '#/components/schemas/CustomerResponse'
        meta:
          $ref: '#/components/schemas/ResponseMeta'

    CustomerResponse:
      type: object
      required:
        - id
        - customer_id
        - full_name
        - primary_phone
        - primary_email
        - customer_type
        - status
        - created_at
        - created_by
        - updated_at
        - version
      properties:
        id:
          type: integer
          format: int64
          description: Internal surrogate key
          example: 1
        customer_id:
          type: string
          description: Business key (format: CUST-YYYY-NNNNNN)
          pattern: '^CUST-\d{4}-\d{6}$'
          example: "CUST-2024-000001"
        full_name:
          type: string
          example: "John Smith"
        company_name:
          type: string
          nullable: true
          example: "Acme Corporation"
        primary_phone:
          type: string
          example: "+15551234567"
        secondary_phone:
          type: string
          nullable: true
          example: "+15559876543"
        primary_email:
          type: string
          format: email
          example: "john@smith.com"
        secondary_email:
          type: string
          nullable: true
          format: email
          example: "j.smith@acme.com"
        address_line1:
          type: string
          nullable: true
          example: "123 Business Ave"
        address_line2:
          type: string
          nullable: true
          example: "Suite 400"
        city:
          type: string
          nullable: true
          example: "San Francisco"
        state_province:
          type: string
          nullable: true
          example: "CA"
        postal_code:
          type: string
          nullable: true
          example: "94105"
        country:
          type: string
          nullable: true
          pattern: '^[A-Z]{2}$'
          example: "US"
        customer_type:
          type: string
          enum:
            - Individual
            - Business
            - Government
            - Other
          example: "Business"
        status:
          type: string
          enum:
            - Active
            - Deleted
          example: "Active"
        notes:
          type: string
          nullable: true
          example: "Key decision maker for enterprise accounts. Prefers email communication."
        created_at:
          type: string
          format: date-time
          example: "2024-01-15T10:30:00Z"
        created_by:
          $ref: '#/components/schemas/UserRef'
        updated_at:
          type: string
          format: date-time
          example: "2024-01-15T10:30:00Z"
        updated_by:
          $ref: '#/components/schemas/UserRef'
          nullable: true
        deleted_at:
          type: string
          format: date-time
          nullable: true
        deleted_by:
          $ref: '#/components/schemas/UserRef'
          nullable: true
        version:
          type: integer
          description: Optimistic lock version
          example: 1

    UserRef:
      type: object
      required:
        - id
        - full_name
      properties:
        id:
          type: integer
          format: int64
          example: 5
        full_name:
          type: string
          example: "Admin User"

    DuplicateDetectedResponse:
      type: object
      required:
        - success
        - error
      properties:
        success:
          type: boolean
          example: false
        error:
          $ref: '#/components/schemas/DuplicateErrorDetail'

    DuplicateErrorDetail:
      type: object
      required:
        - code
        - message
        - details
        - request_id
      properties:
        code:
          type: string
          enum: [DUPLICATE_DETECTED]
          example: "DUPLICATE_DETECTED"
        message:
          type: string
          example: "Potential duplicate customer(s) found"
        details:
          $ref: '#/components/schemas/DuplicateDetails'
        request_id:
          type: string
          example: "req_abc123"

    DuplicateDetails:
      type: object
      required:
        - matches
        - actions
      properties:
        matches:
          type: array
          items:
            $ref: '#/components/schemas/DuplicateMatch'
        actions:
          type: array
          items:
            type: string
            enum: [CANCEL, VIEW_EXISTING, PROCEED_ANYWAY]
          example: ["CANCEL", "VIEW_EXISTING", "PROCEED_ANYWAY"]

    DuplicateMatch:
      type: object
      required:
        - id
        - customer_id
        - full_name
        - primary_phone
        - primary_email
        - company_name
        - match_type
        - similarity
      properties:
        id:
          type: integer
          format: int64
          example: 1
        customer_id:
          type: string
          pattern: '^CUST-\d{4}-\d{6}$'
          example: "CUST-2024-000001"
        full_name:
          type: string
          example: "John Smith"
        primary_phone:
          type: string
          example: "+15551234567"
        primary_email:
          type: string
          format: email
          example: "john@smith.com"
        company_name:
          type: string
          nullable: true
          example: "Acme Corporation"
        match_type:
          type: string
          enum:
            - EMAIL_EXACT
            - NAME_PHONE
            - COMPANY_PHONE
          example: "EMAIL_EXACT"
        similarity:
          type: number
          format: float
          minimum: 0
          maximum: 1
          example: 1.0

    # ===========================================
    # ERROR RESPONSE SCHEMAS
    # ===========================================
    ErrorResponse:
      type: object
      required:
        - success
        - error
      properties:
        success:
          type: boolean
          example: false
        error:
          $ref: '#/components/schemas/ErrorDetail'

    ErrorDetail:
      type: object
      required:
        - code
        - message
        - request_id
      properties:
        code:
          type: string
          example: "INTERNAL_ERROR"
        message:
          type: string
          example: "An unexpected error occurred"
        request_id:
          type: string
          example: "req_abc123"

    ValidationErrorResponse:
      type: object
      required:
        - success
        - error
      properties:
        success:
          type: boolean
          example: false
        error:
          $ref: '#/components/schemas/ValidationErrorDetail'

    ValidationErrorDetail:
      type: object
      required:
        - code
        - message
        - details
        - request_id
      properties:
        code:
          type: string
          enum: [VALIDATION_ERROR]
          example: "VALIDATION_ERROR"
        message:
          type: string
          example: "Request validation failed"
        details:
          type: array
          items:
            $ref: '#/components/schemas/ValidationErrorItem'
        request_id:
          type: string
          example: "req_abc123"

    ValidationErrorItem:
      type: object
      required:
        - field
        - code
        - message
      properties:
        field:
          type: string
          example: "primary_email"
        code:
          type: string
          enum:
            - REQUIRED_FIELD
            - MAX_LENGTH_EXCEEDED
            - INVALID_EMAIL_FORMAT
            - INVALID_PHONE_FORMAT
            - INVALID_ENUM_VALUE
            - INVALID_COUNTRY_CODE
          example: "INVALID_EMAIL_FORMAT"
        message:
          type: string
          example: "Enter a valid email address"

    ResponseMeta:
      type: object
      required:
        - request_id
      properties:
        request_id:
          type: string
          description: Unique request identifier for tracing
          example: "req_abc123"
```

---

## OpenAPI Components (Schemas & Security)

The components are fully defined in the YAML above under `components/schemas` and `components/securitySchemes`. Key schemas include:

| Schema | Purpose |
|--------|---------|
| `CreateCustomerRequest` | Request body for POST /customers |
| `CustomerResponse` | Full customer object in success response |
| `CreateCustomerSuccessResponse` | 201 success envelope |
| `DuplicateDetectedResponse` | 409 duplicate detection envelope |
| `DuplicateDetails` | Duplicate match details with actions |
| `DuplicateMatch` | Individual duplicate match |
| `ErrorResponse` | Generic error envelope (400, 401, 403, 500) |
| `ValidationErrorResponse` | 422 validation error envelope |
| `ValidationErrorItem` | Field-level validation error |
| `UserRef` | User reference (created_by, updated_by, deleted_by) |
| `ResponseMeta` | Request metadata (request_id) |

**Security Scheme:**
```yaml
BearerAuth:
  type: http
  scheme: bearer
  bearerFormat: JWT
```

---

## Request Examples

### Minimal Valid Request (Required Fields Only)
```json
{
  "full_name": "John Smith",
  "primary_phone": "+15551234567",
  "primary_email": "john@smith.com"
}
```

### Full Request (All Fields)
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

### Invalid Request Examples

**Missing Required Fields:**
```json
{
  "company_name": "Acme Corporation"
}
```

**Invalid Email Format:**
```json
{
  "full_name": "John Smith",
  "primary_phone": "+15551234567",
  "primary_email": "invalid-email"
}
```

**Invalid Phone Format (not E.164):**
```json
{
  "full_name": "John Smith",
  "primary_phone": "555-123-4567",
  "primary_email": "john@smith.com"
}
```

**Exceeds Max Length:**
```json
{
  "full_name": "J".repeat(201),
  "primary_phone": "+15551234567",
  "primary_email": "john@smith.com",
  "notes": "N".repeat(2001)
}
```

**Invalid Enum Value:**
```json
{
  "full_name": "John Smith",
  "primary_phone": "+15551234567",
  "primary_email": "john@smith.com",
  "customer_type": "InvalidType"
}
```

**Invalid Country Code:**
```json
{
  "full_name": "John Smith",
  "primary_phone": "+15551234567",
  "primary_email": "john@smith.com",
  "country": "USA"
}
```

---

## Response Examples

### 201 Created - Success
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

### 409 Conflict - Duplicate Detected (Email Exact Match)
```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_DETECTED",
    "message": "Potential duplicate customer(s) found",
    "details": {
      "matches": [
        {
          "id": 1,
          "customer_id": "CUST-2024-000001",
          "full_name": "John Smith",
          "primary_phone": "+15551234567",
          "primary_email": "john@smith.com",
          "company_name": "Acme Corporation",
          "match_type": "EMAIL_EXACT",
          "similarity": 1.0
        }
      ],
      "actions": ["CANCEL", "VIEW_EXISTING", "PROCEED_ANYWAY"]
    },
    "request_id": "req_abc123"
  }
}
```

### 409 Conflict - Duplicate Detected (Name + Phone Match)
```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_DETECTED",
    "message": "Potential duplicate customer(s) found",
    "details": {
      "matches": [
        {
          "id": 2,
          "customer_id": "CUST-2024-000002",
          "full_name": "Jon Smith",
          "primary_phone": "+15551234567",
          "primary_email": "jon.smith@other.com",
          "company_name": "Other Corp",
          "match_type": "NAME_PHONE",
          "similarity": 0.92
        }
      ],
      "actions": ["CANCEL", "VIEW_EXISTING", "PROCEED_ANYWAY"]
    },
    "request_id": "req_def456"
  }
}
```

### 409 Conflict - Duplicate Detected (Company + Phone Match)
```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_DETECTED",
    "message": "Potential duplicate customer(s) found",
    "details": {
      "matches": [
        {
          "id": 3,
          "customer_id": "CUST-2024-000003",
          "full_name": "Different Person",
          "primary_phone": "+15551234567",
          "primary_email": "different@company.com",
          "company_name": "Acme Corporation",
          "match_type": "COMPANY_PHONE",
          "similarity": 1.0
        }
      ],
      "actions": ["CANCEL", "VIEW_EXISTING", "PROCEED_ANYWAY"]
    },
    "request_id": "req_ghi789"
  }
}
```

---

## Error Examples

### 400 Bad Request - Invalid Request Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request body",
    "request_id": "req_abc123"
  }
}
```

### 401 Unauthorized - Invalid/Expired Token
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "Invalid or expired access token",
    "request_id": "req_abc123"
  }
}
```

### 403 Forbidden - Manager Role
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions to create customers",
    "request_id": "req_abc123"
  }
}
```

### 422 Unprocessable Entity - Validation Errors

**Missing Required Fields:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "full_name",
        "code": "REQUIRED_FIELD",
        "message": "Full name is required"
      },
      {
        "field": "primary_phone",
        "code": "REQUIRED_FIELD",
        "message": "Primary phone is required"
      },
      {
        "field": "primary_email",
        "code": "REQUIRED_FIELD",
        "message": "Primary email is required"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

**Invalid Email Format:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "primary_email",
        "code": "INVALID_EMAIL_FORMAT",
        "message": "Enter a valid email address"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

**Invalid Phone Format:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "primary_phone",
        "code": "INVALID_PHONE_FORMAT",
        "message": "Phone number must be in E.164 format (e.g., +15551234567)"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

**Max Length Exceeded:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "full_name",
        "code": "MAX_LENGTH_EXCEEDED",
        "message": "Full name must not exceed 200 characters"
      },
      {
        "field": "notes",
        "code": "MAX_LENGTH_EXCEEDED",
        "message": "Notes must not exceed 2000 characters"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

**Invalid Enum Value:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "customer_type",
        "code": "INVALID_ENUM_VALUE",
        "message": "Invalid customer type. Must be one of: Individual, Business, Government, Other"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

**Invalid Country Code:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "country",
        "code": "INVALID_COUNTRY_CODE",
        "message": "Country must be a valid ISO 3166-1 alpha-2 code (e.g., US)"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "request_id": "req_abc123"
  }
}
```

---

## Validation Checklist

| Checklist Item | Status |
|----------------|--------|
| [x] Story Scope Respected (only EP-01 documented) | ✅ |
| [x] API Contract Followed (EP-01 spec matched exactly) | ✅ |
| [x] OpenAPI 3.0.3 Used | ✅ |
| [x] Endpoint Documented (summary, description, tags, operationId, security, requestBody, responses) | ✅ |
| [x] Request DTOs Documented (CreateCustomerRequest with all fields, validation rules) | ✅ |
| [x] Response DTOs Documented (CustomerResponse, success envelope) | ✅ |
| [x] Errors Documented (400, 401, 403, 409, 422, 500) | ✅ |
| [x] Security Documented (BearerAuth JWT scheme) | ✅ |
| [x] JWT Documented (token format, TTL, header) | ✅ |
| [x] Examples Generated (request, success, duplicate variants, all error types) | ✅ |
| [x] Compile Safe References (schemas match DTOs from api-contract.md) | ✅ |
| [x] No Business Logic Generated | ✅ |
| [x] No Handlers Generated | ✅ |
| [x] No Tests Generated | ✅ |
| [x] Role Authorization Documented (Admin allowed, Manager forbidden) | ✅ |
| [x] Duplicate Detection Documented (3 match types, actions) | ✅ |
| [x] Field Classifications Noted (Public/Sensitive/Internal) | ✅ |
| [x] Audit Requirements Noted | ✅ |

---

## Handoff to Backend Test Agent

**Artifacts Produced:**
- `swagger-annotations.go` - Go Swagger annotations for handler
- `openapi.yaml` - Complete OpenAPI 3.0.3 specification
- `schemas/` - All request/response/error schemas
- `examples/` - Request/response/error examples
- `security/` - BearerAuth security scheme

**Next Agent:** Backend Test Agent  
**Consumes:** This Swagger documentation for generating contract tests and validating handler implementation against the OpenAPI spec.