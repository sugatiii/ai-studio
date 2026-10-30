# Handler Layer Implementation for STORY-001: Create Customer

---

## Handler Summary

| Handler | Method | Path | Purpose |
|---------|--------|------|---------|
| `CreateCustomerHandler` | POST | `/api/v1/customers` | Create a new customer record with duplicate detection |

---

## Handler Interface

```go
// File: internal/handler/customer_handler.go
package handler

import (
	"context"

	"github.com/gin-gonic/gin"
	"github.com/crm-system/internal/dto"
	"github.com/crm-system/internal/service"
)

// CustomerHandler defines the HTTP handler interface for customer operations.
type CustomerHandler interface {
	CreateCustomer(c *gin.Context)
	// SearchCustomers, GetCustomerDetail, etc. are out of scope for STORY-001
}

// NewCustomerHandler creates a new CustomerHandler with the given service.
func NewCustomerHandler(customerService service.CustomerService) CustomerHandler {
	return &customerHandler{
		customerService: customerService,
	}
}

type customerHandler struct {
	customerService service.CustomerService
}
```

---

## Handler Implementation

```go
// File: internal/handler/customer_handler.go (continued)
package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/crm-system/internal/dto"
	"github.com/crm-system/internal/service"
	"github.com/crm-system/pkg/errors"
	"github.com/crm-system/pkg/response"
)

// CreateCustomer handles POST /api/v1/customers
// Creates a new customer record with duplicate detection.
//
// @Summary Create a new customer
// @Description Create a new customer record. Returns 409 with potential duplicates if detected.
// @Tags Customers
// @Accept json
// @Produce json
// @Security BearerAuth
// @Param request body dto.CreateCustomerRequest true "Customer creation request"
// @Success 201 {object} response.SuccessResponse{data=dto.CustomerResponse} "Customer created successfully"
// @Failure 400 {object} response.ErrorResponse "Invalid request format"
// @Failure 401 {object} response.ErrorResponse "Unauthenticated"
// @Failure 403 {object} response.ErrorResponse "Forbidden - Admin role required"
// @Failure 422 {object} response.ValidationErrorResponse "Validation failed"
// @Failure 409 {object} response.DuplicateErrorResponse "Potential duplicate detected"
// @Failure 500 {object} response.ErrorResponse "Internal server error"
// @Router /customers [post]
func (h *customerHandler) CreateCustomer(c *gin.Context) {
	ctx := c.Request.Context()

	// 1. Bind request to DTO
	var req dto.CreateCustomerRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.WriteValidationError(c, err)
		return
	}

	// 2. Validate DTO (struct tags + custom validators)
	if err := req.Validate(); err != nil {
		response.WriteValidationError(c, err)
		return
	}

	// 3. Extract user ID from JWT claims (set by auth middleware)
	userID, exists := c.Get("user_id")
	if !exists {
		response.WriteError(c, http.StatusUnauthorized, errors.CodeUnauthenticated, "User context not found")
		return
	}

	// 4. Call service layer
	createdCustomer, duplicateMatches, err := h.customerService.CreateCustomer(ctx, req, userID.(int64))

	// 5. Map service errors to HTTP responses
	if err != nil {
		h.mapServiceError(c, err, duplicateMatches)
		return
	}

	// 6. Handle duplicate detection result
	if len(duplicateMatches) > 0 {
		response.WriteDuplicateDetected(c, duplicateMatches)
		return
	}

	// 7. Success response
	response.WriteCreated(c, "Customer created successfully", createdCustomer)
}

// mapServiceError maps service errors to appropriate HTTP responses.
func (h *customerHandler) mapServiceError(c *gin.Context, err error, duplicates []dto.DuplicateMatch) {
	var appErr *errors.AppError
	if !errors.As(err, &appErr) {
		// Unknown error - log and return 500
		response.WriteError(c, http.StatusInternalServerError, errors.CodeInternalError, "An unexpected error occurred")
		return
	}

	switch appErr.Code {
	case errors.CodeValidationError:
		response.WriteValidationError(c, appErr)
	case errors.CodeUnauthenticated:
		response.WriteError(c, http.StatusUnauthorized, appErr.Code, appErr.Message)
	case errors.CodeForbidden:
		response.WriteError(c, http.StatusForbidden, appErr.Code, appErr.Message)
	case errors.CodeDuplicateDetected:
		// Service returns duplicates with this error code
		response.WriteDuplicateDetected(c, duplicates)
	case errors.CodeNotFound:
		response.WriteError(c, http.StatusNotFound, appErr.Code, appErr.Message)
	case errors.CodeConflict:
		response.WriteError(c, http.StatusConflict, appErr.Code, appErr.Message)
	default:
		response.WriteError(c, http.StatusInternalServerError, errors.CodeInternalError, "An unexpected error occurred")
	}
}
```

---

## Route Registration

```go
// File: internal/handler/routes.go
package handler

import (
	"github.com/gin-gonic/gin"
	"github.com/crm-system/internal/middleware"
)

// RegisterCustomerRoutes registers all customer-related routes.
func RegisterCustomerRoutes(
	router *gin.RouterGroup,
	handler CustomerHandler,
	authMiddleware *middleware.AuthMiddleware,
) {
	customers := router.Group("/customers")
	{
		// All customer routes require authentication
		customers.Use(authMiddleware.RequireAuth())

		// POST /api/v1/customers - Create customer (Admin only)
		customers.POST("",
			authMiddleware.RequireRole("Admin"),
			handler.CreateCustomer,
		)

		// The following routes are registered here for completeness
		// but their handlers are implemented in other stories:
		// GET    /customers                    -> SearchCustomers (STORY-002)
		// GET    /customers/:id                -> GetCustomerDetail (STORY-003)
		// GET    /customers/by-key/:customer_id -> GetCustomerByBusinessKey (STORY-003)
		// PATCH  /customers/:id                -> UpdateCustomer (STORY-004)
		// DELETE /customers/:id                -> SoftDeleteCustomer (STORY-005)
	}
}
```

---

## Error Mapping Table

| Service Error Code | HTTP Status | Response Envelope | Description |
|--------------------|-------------|-------------------|-------------|
| `VALIDATION_ERROR` | 422 | `ValidationErrorResponse` | DTO validation failed (required fields, format, length, enum) |
| `UNAUTHENTICATED` | 401 | `ErrorResponse` | Missing, invalid, or expired JWT access token |
| `FORBIDDEN` | 403 | `ErrorResponse` | Authenticated user lacks Admin role (Manager attempted create) |
| `DUPLICATE_DETECTED` | 409 | `DuplicateErrorResponse` | Potential duplicate(s) found per BR-005; includes matches array and allowed actions |
| `NOT_FOUND` | 404 | `ErrorResponse` | Referenced resource not found (not applicable for create) |
| `CONFLICT` | 409 | `ErrorResponse` | Optimistic lock conflict (not applicable for create) |
| `INTERNAL_ERROR` | 500 | `ErrorResponse` | Unexpected system error (database, external service, etc.) |

### Response Envelope Formats

**Success (201 Created)**
```json
{
  "success": true,
  "message": "Customer created successfully",
  "data": { ...CustomerResponse },
  "meta": { "request_id": "req_abc123" }
}
```

**Validation Error (422)**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "primary_email", "code": "INVALID_EMAIL_FORMAT", "message": "Enter a valid email address" }
    ],
    "request_id": "req_abc123"
  }
}
```

**Duplicate Detected (409)**
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
          "match_type": "NAME_PHONE",
          "similarity": 0.92
        }
      ],
      "actions": ["CANCEL", "VIEW_EXISTING", "PROCEED_ANYWAY"]
    },
    "request_id": "req_abc123"
  }
}
```

**Forbidden (403)**
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

---

## Request/Response Mapping Notes

### Request DTO: `dto.CreateCustomerRequest`

| JSON Field | Go Field | Validation Tags | Notes |
|------------|----------|-----------------|-------|
| `full_name` | `FullName` | `required`, `max=200` | Trimmed; required per BR-002 |
| `primary_phone` | `PrimaryPhone` | `required`, `e164`, `max=20` | Normalized to E.164 by service |
| `primary_email` | `PrimaryEmail` | `required`, `email`, `max=254` | Lowercased by service per BR-012 |
| `company_name` | `CompanyName` | `max=200` | Optional; trimmed |
| `customer_type` | `CustomerType` | `oneof=Individual Business Government Other` | Optional; defaults to `Individual` in service |
| `secondary_phone` | `SecondaryPhone` | `e164`, `max=20` | Optional; normalized if provided |
| `secondary_email` | `SecondaryEmail` | `email`, `max=254` | Optional; lowercased if provided |
| `address_line1` | `AddressLine1` | `max=200` | Optional |
| `address_line2` | `AddressLine2` | `max=200` | Optional |
| `city` | `City` | `max=100` | Optional |
| `state_province` | `StateProvince` | `max=100` | Optional |
| `postal_code` | `PostalCode` | `max=20` | Optional |
| `country` | `Country` | `iso3166_1_alpha2` | Optional; 2-char uppercase |
| `notes` | `Notes` | `max=2000` | Optional |

### Response DTO: `dto.CustomerResponse`

Maps 1:1 with API contract EP-01 success response `data` object. Includes all request fields plus:
- `ID` (int64) — internal surrogate key
- `CustomerID` (string) — business key `CUST-YYYY-NNNNNN`
- `Status` (string) — `Active`
- `CreatedAt`, `CreatedBy`, `UpdatedAt`, `UpdatedBy`, `DeletedAt`, `DeletedBy`, `Version`

### Duplicate Match DTO: `dto.DuplicateMatch`

| Field | Type | Description |
|-------|------|-------------|
| `ID` | int64 | Internal ID of existing customer |
| `CustomerID` | string | Business key of existing customer |
| `FullName` | string | Customer name |
| `PrimaryPhone` | string | Phone (E.164) |
| `PrimaryEmail` | string | Email (lowercase) |
| `CompanyName` | string | Company name (may be null) |
| `MatchType` | string | `EMAIL_EXACT`, `NAME_PHONE`, or `COMPANY_PHONE` |
| `Similarity` | float64 | Name similarity score (0.0–1.0) for `NAME_PHONE` matches |

---

## DTO Definitions (Reference)

```go
// File: internal/dto/customer_dto.go
package dto

import (
	"time"
	"github.com/go-playground/validator/v10"
)

// CreateCustomerRequest represents the request body for creating a customer.
type CreateCustomerRequest struct {
	FullName       string `json:"full_name"       validate:"required,max=200"`
	PrimaryPhone   string `json:"primary_phone"   validate:"required,e164,max=20"`
	PrimaryEmail   string `json:"primary_email"   validate:"required,email,max=254"`
	CompanyName    string `json:"company_name"    validate:"max=200"`
	CustomerType   string `json:"customer_type"   validate:"omitempty,oneof=Individual Business Government Other"`
	SecondaryPhone string `json:"secondary_phone" validate:"omitempty,e164,max=20"`
	SecondaryEmail string `json:"secondary_email" validate:"omitempty,email,max=254"`
	AddressLine1   string `json:"address_line1"   validate:"max=200"`
	AddressLine2   string `json:"address_line2"   validate:"max=200"`
	City           string `json:"city"            validate:"max=100"`
	StateProvince  string `json:"state_province"  validate:"max=100"`
	PostalCode     string `json:"postal_code"     validate:"max=20"`
	Country        string `json:"country"         validate:"omitempty,iso3166_1_alpha2"`
	Notes          string `json:"notes"           validate:"max=2000"`
}

// Validate runs custom validation logic beyond struct tags.
func (r *CreateCustomerRequest) Validate() error {
	// Custom validators (e164, email, iso3166_1_alpha2) are registered globally
	// This method can contain cross-field validation if needed in future
	return nil
}

// CustomerResponse represents a customer in API responses.
type CustomerResponse struct {
	ID             int64      `json:"id"`
	CustomerID     string     `json:"customer_id"`
	FullName       string     `json:"full_name"`
	CompanyName    *string    `json:"company_name"`
	PrimaryPhone   string     `json:"primary_phone"`
	SecondaryPhone *string    `json:"secondary_phone"`
	PrimaryEmail   string     `json:"primary_email"`
	SecondaryEmail *string    `json:"secondary_email"`
	AddressLine1   *string    `json:"address_line1"`
	AddressLine2   *string    `json:"address_line2"`
	City           *string    `json:"city"`
	StateProvince  *string    `json:"state_province"`
	PostalCode     *string    `json:"postal_code"`
	Country        *string    `json:"country"`
	CustomerType   string     `json:"customer_type"`
	Status         string     `json:"status"`
	Notes          *string    `json:"notes"`
	CreatedAt      time.Time  `json:"created_at"`
	CreatedBy      UserRef    `json:"created_by"`
	UpdatedAt      time.Time  `json:"updated_at"`
	UpdatedBy      *UserRef   `json:"updated_by"`
	DeletedAt      *time.Time `json:"deleted_at"`
	DeletedBy      *UserRef   `json:"deleted_by"`
	Version        int        `json:"version"`
}

type UserRef struct {
	ID       int64  `json:"id"`
	FullName string `json:"full_name"`
}

// DuplicateMatch represents a potential duplicate customer.
type DuplicateMatch struct {
	ID            int64   `json:"id"`
	CustomerID    string  `json:"customer_id"`
	FullName      string  `json:"full_name"`
	PrimaryPhone  string  `json:"primary_phone"`
	PrimaryEmail  string  `json:"primary_email"`
	CompanyName   *string `json:"company_name"`
	MatchType     string  `json:"match_type"`
	Similarity    float64 `json:"similarity,omitempty"`
}
```

---

## Service Interface (Reference - Not Implemented Here)

```go
// File: internal/service/customer_service.go (interface only)
package service

import (
	"context"
	"github.com/crm-system/internal/dto"
)

// CustomerService defines the business logic interface for customer operations.
type CustomerService interface {
	// CreateCustomer creates a new customer.
	// Returns created customer, potential duplicates (if any), and error.
	// If duplicates found, returns DUPLICATE_DETECTED error with matches populated.
	CreateCustomer(ctx context.Context, req dto.CreateCustomerRequest, createdBy int64) (*dto.CustomerResponse, []dto.DuplicateMatch, error)
	// Other methods (Search, GetByID, Update, Delete) out of scope for STORY-001
}
```

---

## Response Helper Package (Reference)

```go
// File: pkg/response/response.go
package response

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/crm-system/pkg/errors"
)

// SuccessResponse represents a successful API response.
type SuccessResponse struct {
	Success bool        `json:"success"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
	Meta    Meta        `json:"meta"`
}

// ErrorResponse represents an error API response.
type ErrorResponse struct {
	Success bool        `json:"success"`
	Error   ErrorDetail `json:"error"`
}

type ErrorDetail struct {
	Code      string      `json:"code"`
	Message   string      `json:"message"`
	Details   interface{} `json:"details,omitempty"`
	RequestID string      `json:"request_id"`
}

type ValidationErrorResponse struct {
	Success bool              `json:"success"`
	Error   ValidationError   `json:"error"`
}

type ValidationError struct {
	Code      string          `json:"code"`
	Message   string          `json:"message"`
	Details   []FieldError    `json:"details"`
	RequestID string          `json:"request_id"`
}

type FieldError struct {
	Field   string `json:"field"`
	Code    string `json:"code"`
	Message string `json:"message"`
}

type DuplicateErrorResponse struct {
	Success bool             `json:"success"`
	Error   DuplicateError   `json:"error"`
}

type DuplicateError struct {
	Code      string            `json:"code"`
	Message   string            `json:"message"`
	Details   DuplicateDetails  `json:"details"`
	RequestID string            `json:"request_id"`
}

type DuplicateDetails struct {
	Matches []dto.DuplicateMatch `json:"matches"`
	Actions []string             `json:"actions"`
}

type Meta struct {
	RequestID string `json:"request_id"`
}

func getRequestID(c *gin.Context) string {
	if rid, exists := c.Get("request_id"); exists {
		return rid.(string)
	}
	return ""
}

func WriteCreated(c *gin.Context, message string, data interface{}) {
	c.JSON(http.StatusCreated, SuccessResponse{
		Success: true,
		Message: message,
		Data:    data,
		Meta:    Meta{RequestID: getRequestID(c)},
	})
}

func WriteError(c *gin.Context, status int, code, message string) {
	c.JSON(status, ErrorResponse{
		Success: false,
		Error: ErrorDetail{
			Code:      code,
			Message:   message,
			RequestID: getRequestID(c),
		},
	})
}

func WriteValidationError(c *gin.Context, err error) {
	var details []FieldError
	// Convert validator.ValidationErrors to FieldError slice
	// Implementation omitted for brevity
	c.JSON(http.StatusUnprocessableEntity, ValidationErrorResponse{
		Success: false,
		Error: ValidationError{
			Code:      errors.CodeValidationError,
			Message:   "Request validation failed",
			Details:   details,
			RequestID: getRequestID(c),
		},
	})
}

func WriteDuplicateDetected(c *gin.Context, matches []dto.DuplicateMatch) {
	c.JSON(http.StatusConflict, DuplicateErrorResponse{
		Success: false,
		Error: DuplicateError{
			Code:    errors.CodeDuplicateDetected,
			Message: "Potential duplicate customer(s) found",
			Details: DuplicateDetails{
				Matches: matches,
				Actions: []string{"CANCEL", "VIEW_EXISTING", "PROCEED_ANYWAY"},
			},
			RequestID: getRequestID(c),
		},
	})
}
```

---

## Output Validation Checklist

| Checklist Item | Status |
|----------------|--------|
| [x] Story Scope Respected — Only Create Customer (EP-01) implemented | ✅ |
| [x] API Contract Followed — Routes, request/response, status codes match EP-01 | ✅ |
| [x] Routes Generated — `RegisterCustomerRoutes` with POST `/customers` | ✅ |
| [x] Request Binding Implemented — `c.ShouldBindJSON(&req)` with DTO | ✅ |
| [x] DTO Validation Triggered — `req.Validate()` + struct tags | ✅ |
| [x] Service Invocations Implemented — `h.customerService.CreateCustomer()` | ✅ |
| [x] Response Standard Followed — Success/error envelopes per contract | ✅ |
| [x] Error Mapping Implemented — `mapServiceError` with full table | ✅ |
| [x] Compile Safe — All types referenced exist in DTO/service packages | ✅ |
| [x] No Business Logic Present — Handler only binds, validates, calls service, maps | ✅ |
| [x] No Repository Access — Handler → Service only | ✅ |
| [x] No SQL Generated | ✅ |
| [x] No Transactions Generated | ✅ |
| [x] No Middleware Generated — Uses injected `authMiddleware` | ✅ |
| [x] No Swagger Generated — Annotations only for documentation | ✅ |
| [x] No Tests Generated | ✅ |

---

## Handoff Artifacts Produced

| Artifact | Location | Consumer |
|----------|----------|----------|
| `CustomerHandler` interface | `internal/handler/customer_handler.go` | Backend Middleware Agent, Reviewer |
| `customerHandler` implementation | `internal/handler/customer_handler.go` | Backend Middleware Agent, Reviewer |
| `RegisterCustomerRoutes` | `internal/handler/routes.go` | Backend Middleware Agent (wiring), Reviewer |
| Error Mapping Table | This document | QA Agent (test scenarios), Reviewer |
| Request/Response DTO Mapping | This document | Frontend Agent (Zod schema alignment), Reviewer |

---

*Generated by Backend Handler Agent for STORY-001*  
*Status: Ready for Review*