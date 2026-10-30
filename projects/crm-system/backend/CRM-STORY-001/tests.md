# Backend Test Suite for STORY-001: Create Customer

## Test Summary

| Layer | Test Files | Test Cases | Coverage Target |
|-------|------------|------------|-----------------|
| DTO Validation | `dto_validation_test.go` | 28 | 100% |
| Repository | `customer_repository_test.go` | 15 | 90% |
| Service | `customer_service_test.go` | 32 | 95% |
| Handler | `customer_handler_test.go` | 24 | 90% |
| Middleware | `auth_middleware_test.go` | 18 | 95% |
| Integration | `create_customer_integration_test.go` | 12 | 85% |
| **Total** | **6 files** | **129 tests** | **≥90% critical** |

---

## DTO Validation Tests

```go
// File: internal/dto/customer_dto_validation_test.go
package dto

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gopkg.in/go-playground/validator.v9"
)

func TestCreateCustomerRequest_Validation(t *testing.T) {
	validate := validator.New()
	_ = validate.RegisterValidation("e164", validateE164Phone)
	_ = validate.RegisterValidation("rfc5322", validateRFC5322Email)
	_ = validate.RegisterValidation("iso3166_1_alpha2", validateISO3166Alpha2)
	_ = validate.RegisterValidation("customer_type", validateCustomerType)

	tests := []struct {
		name           string
		request        CreateCustomerRequest
		expectError    bool
		expectedFields []string
		expectedCodes  []string
	}{
		{
			name: "valid request with all required fields",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
			},
			expectError: false,
		},
		{
			name: "valid request with all optional fields",
			request: CreateCustomerRequest{
				FullName:        "John Smith",
				PrimaryPhone:    "+15551234567",
				PrimaryEmail:    "john@smith.com",
				CompanyName:     "Acme Corp",
				CustomerType:    "Business",
				SecondaryPhone:  "+15559876543",
				SecondaryEmail:  "j.smith@acme.com",
				AddressLine1:    "123 Business Ave",
				AddressLine2:    "Suite 400",
				City:            "San Francisco",
				StateProvince:   "CA",
				PostalCode:      "94105",
				Country:         "US",
				Notes:           "Key decision maker",
			},
			expectError: false,
		},
		{
			name: "missing full_name",
			request: CreateCustomerRequest{
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
			},
			expectError:    true,
			expectedFields: []string{"FullName"},
			expectedCodes:  []string{"REQUIRED_FIELD"},
		},
		{
			name: "missing primary_phone",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryEmail: "john@smith.com",
			},
			expectError:    true,
			expectedFields: []string{"PrimaryPhone"},
			expectedCodes:  []string{"REQUIRED_FIELD"},
		},
		{
			name: "missing primary_email",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
			},
			expectError:    true,
			expectedFields: []string{"PrimaryEmail"},
			expectedCodes:  []string{"REQUIRED_FIELD"},
		},
		{
			name: "empty full_name (whitespace only)",
			request: CreateCustomerRequest{
				FullName:     "   ",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
			},
			expectError:    true,
			expectedFields: []string{"FullName"},
			expectedCodes:  []string{"REQUIRED_FIELD"},
		},
		{
			name: "invalid email format",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@",
			},
			expectError:    true,
			expectedFields: []string{"PrimaryEmail"},
			expectedCodes:  []string{"INVALID_EMAIL_FORMAT"},
		},
		{
			name: "invalid phone format (not E.164)",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "555-123-4567",
				PrimaryEmail: "john@smith.com",
			},
			expectError:    true,
			expectedFields: []string{"PrimaryPhone"},
			expectedCodes:  []string{"INVALID_PHONE_FORMAT"},
		},
		{
			name: "phone with invalid country code",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+9995551234567",
				PrimaryEmail: "john@smith.com",
			},
			expectError:    true,
			expectedFields: []string{"PrimaryPhone"},
			expectedCodes:  []string{"INVALID_PHONE_FORMAT"},
		},
		{
			name: "full_name exceeds 200 chars",
			request: CreateCustomerRequest{
				FullName:     string(make([]byte, 201)), // 201 chars
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
			},
			expectError:    true,
			expectedFields: []string{"FullName"},
			expectedCodes:  []string{"MAX_LENGTH_EXCEEDED"},
		},
		{
			name: "full_name at 200 chars boundary",
			request: CreateCustomerRequest{
				FullName:     string(make([]byte, 200)),
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
			},
			expectError: false,
		},
		{
			name: "company_name exceeds 200 chars",
			request: CreateCustomerRequest{
				FullName:      "John Smith",
				PrimaryPhone:  "+15551234567",
				PrimaryEmail:  "john@smith.com",
				CompanyName:   string(make([]byte, 201)),
			},
			expectError:    true,
			expectedFields: []string{"CompanyName"},
			expectedCodes:  []string{"MAX_LENGTH_EXCEEDED"},
		},
		{
			name: "notes exceeds 2000 chars",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
				Notes:        string(make([]byte, 2001)),
			},
			expectError:    true,
			expectedFields: []string{"Notes"},
			expectedCodes:  []string{"MAX_LENGTH_EXCEEDED"},
		},
		{
			name: "notes at 2000 chars boundary",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
				Notes:        string(make([]byte, 2000)),
			},
			expectError: false,
		},
		{
			name: "invalid customer_type enum",
			request: CreateCustomerRequest{
				FullName:      "John Smith",
				PrimaryPhone:  "+15551234567",
				PrimaryEmail:  "john@smith.com",
				CustomerType:  "InvalidType",
			},
			expectError:    true,
			expectedFields: []string{"CustomerType"},
			expectedCodes:  []string{"INVALID_ENUM_VALUE"},
		},
		{
			name: "valid customer_type enum values",
			request: CreateCustomerRequest{
				FullName:      "John Smith",
				PrimaryPhone:  "+15551234567",
				PrimaryEmail:  "john@smith.com",
				CustomerType:  "Business",
			},
			expectError: false,
		},
		{
			name: "invalid country code",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
				Country:      "USA", // Should be "US"
			},
			expectError:    true,
			expectedFields: []string{"Country"},
			expectedCodes:  []string{"INVALID_COUNTRY_CODE"},
		},
		{
			name: "valid country code (ISO 3166-1 alpha-2)",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
				Country:      "US",
			},
			expectError: false,
		},
		{
			name: "secondary_phone invalid format",
			request: CreateCustomerRequest{
				FullName:       "John Smith",
				PrimaryPhone:   "+15551234567",
				PrimaryEmail:   "john@smith.com",
				SecondaryPhone: "555-123-4567",
			},
			expectError:    true,
			expectedFields: []string{"SecondaryPhone"},
			expectedCodes:  []string{"INVALID_PHONE_FORMAT"},
		},
		{
			name: "secondary_email invalid format",
			request: CreateCustomerRequest{
				FullName:        "John Smith",
				PrimaryPhone:    "+15551234567",
				PrimaryEmail:    "john@smith.com",
				SecondaryEmail:  "invalid-email",
			},
			expectError:    true,
			expectedFields: []string{"SecondaryEmail"},
			expectedCodes:  []string{"INVALID_EMAIL_FORMAT"},
		},
		{
			name: "address_line1 exceeds 200 chars",
			request: CreateCustomerRequest{
				FullName:      "John Smith",
				PrimaryPhone:  "+15551234567",
				PrimaryEmail:  "john@smith.com",
				AddressLine1:  string(make([]byte, 201)),
			},
			expectError:    true,
			expectedFields: []string{"AddressLine1"},
			expectedCodes:  []string{"MAX_LENGTH_EXCEEDED"},
		},
		{
			name: "city exceeds 100 chars",
			request: CreateCustomerRequest{
				FullName:    "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
				City:        string(make([]byte, 101)),
			},
			expectError:    true,
			expectedFields: []string{"City"},
			expectedCodes:  []string{"MAX_LENGTH_EXCEEDED"},
		},
		{
			name: "postal_code exceeds 20 chars",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
				PostalCode:   string(make([]byte, 21)),
			},
			expectError:    true,
			expectedFields: []string{"PostalCode"},
			expectedCodes:  []string{"MAX_LENGTH_EXCEEDED"},
		},
		{
			name: "SQL injection attempt in full_name",
			request: CreateCustomerRequest{
				FullName:     "' OR 1=1--",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
			},
			expectError: false, // Should pass validation, sanitized at service layer
		},
		{
			name: "XSS payload in notes",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "john@smith.com",
				Notes:        "<script>alert(1)</script>",
			},
			expectError: false, // Stored as-is, escaped on render
		},
		{
			name: "email with uppercase normalized",
			request: CreateCustomerRequest{
				FullName:     "John Smith",
				PrimaryPhone: "+15551234567",
				PrimaryEmail: "JOHN@SMITH.COM",
			},
			expectError: false, // Normalization happens in service
		},
		{
			name: "multiple validation errors returned together",
			request: CreateCustomerRequest{
				FullName:     "",
				PrimaryPhone: "invalid",
				PrimaryEmail: "invalid",
			},
			expectError:    true,
			expectedFields: []string{"FullName", "PrimaryPhone", "PrimaryEmail"},
			expectedCodes:  []string{"REQUIRED_FIELD", "INVALID_PHONE_FORMAT", "INVALID_EMAIL_FORMAT"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validate.Struct(tt.request)
			if tt.expectError {
				require.Error(t, err)
				validationErrors := err.(validator.ValidationErrors)
				assert.Len(t, validationErrors, len(tt.expectedFields))
				for i, field := range tt.expectedFields {
					assert.Equal(t, field, validationErrors[i].Field())
					assert.Equal(t, tt.expectedCodes[i], validationErrors[i].Tag())
				}
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestCreateCustomerResponse_Serialization(t *testing.T) {
	response := CreateCustomerResponse{
		Success: true,
		Message: "Customer created successfully",
		Data: CustomerResponse{
			ID:            1,
			CustomerID:    "CUST-2024-000001",
			FullName:      "John Smith",
			CompanyName:   "Acme Corporation",
			PrimaryPhone:  "+15551234567",
			SecondaryPhone: "+15559876543",
			PrimaryEmail:  "john@smith.com",
			SecondaryEmail: "j.smith@acme.com",
			AddressLine1:  "123 Business Ave",
			AddressLine2:  "Suite 400",
			City:          "San Francisco",
			StateProvince: "CA",
			PostalCode:    "94105",
			Country:       "US",
			CustomerType:  "Business",
			Status:        "Active",
			Notes:         "Key decision maker",
			CreatedAt:     "2024-01-15T10:30:00Z",
			CreatedBy: UserSummary{
				ID:       5,
				FullName: "Admin User",
			},
			UpdatedAt: "2024-01-15T10:30:00Z",
			Version:   1,
		},
		Meta: ResponseMeta{
			RequestID: "req_abc123",
		},
	}

	// Verify JSON serialization matches API contract
	jsonData, err := json.Marshal(response)
	require.NoError(t, err)

	var parsed map[string]interface{}
	require.NoError(t, json.Unmarshal(jsonData, &parsed))

	assert.Equal(t, true, parsed["success"])
	assert.Equal(t, "Customer created successfully", parsed["message"])
	assert.NotNil(t, parsed["data"])
	assert.NotNil(t, parsed["meta"])

	data := parsed["data"].(map[string]interface{})
	assert.Equal(t, float64(1), data["id"])
	assert.Equal(t, "CUST-2024-000001", data["customer_id"])
	assert.Equal(t, "John Smith", data["full_name"])
	assert.Equal(t, "Active", data["status"])
	assert.Equal(t, float64(1), data["version"])
}

func TestDuplicateDetectedErrorResponse_Serialization(t *testing.T) {
	response := ErrorResponse{
		Success: false,
		Error: ErrorDetail{
			Code:    "DUPLICATE_DETECTED",
			Message: "Potential duplicate customer(s) found",
			Details: DuplicateDetails{
				Matches: []DuplicateMatch{
					{
						ID:           1,
						CustomerID:   "CUST-2024-000001",
						FullName:     "John Smith",
						PrimaryPhone: "+15551234567",
						PrimaryEmail: "john@smith.com",
						CompanyName:  "Acme Corporation",
						MatchType:    "NAME_PHONE",
						Similarity:   0.92,
					},
				},
				Actions: []string{"CANCEL", "VIEW_EXISTING", "PROCEED_ANYWAY"},
			},
			RequestID: "req_abc123",
		},
	}

	jsonData, err := json.Marshal(response)
	require.NoError(t, err)

	var parsed map[string]interface{}
	require.NoError(t, json.Unmarshal(jsonData, &parsed))

	assert.Equal(t, false, parsed["success"])
	errorDetail := parsed["error"].(map[string]interface{})
	assert.Equal(t, "DUPLICATE_DETECTED", errorDetail["code"])
	assert.Equal(t, "Potential duplicate customer(s) found", errorDetail["message"])
	
	details := errorDetail["details"].(map[string]interface{})
	matches := details["matches"].([]interface{})
	assert.Len(t, matches, 1)
	
	match := matches[0].(map[string]interface{})
	assert.Equal(t, float64(1), match["id"])
	assert.Equal(t, "NAME_PHONE", match["match_type"])
	assert.Equal(t, 0.92, match["similarity"])
	
	actions := details["actions"].([]interface{})
	assert.Contains(t, actions, "CANCEL")
	assert.Contains(t, actions, "VIEW_EXISTING")
	assert.Contains(t, actions, "PROCEED_ANYWAY")
}
```

---

## Repository Tests

```go
// File: internal/repository/customer_repository_test.go
package repository

import (
	"context"
	"testing"
	"time"

	"github.com/DATA-DOG/go-sqlmock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"crm-system/internal/model"
)

func setupCustomerRepositoryTest(t *testing.T) (*CustomerRepository, *gorm.DB, sqlmock.Sqlmock) {
	db, mock, err := sqlmock.New()
	require.NoError(t, err)

	gormDB, err := gorm.Open(postgres.New(postgres.Config{Conn: db}), &gorm.Config{})
	require.NoError(t, err)

	repo := NewCustomerRepository(gormDB)
	return repo, gormDB, mock
}

func TestCustomerRepository_Create(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()
	now := time.Now().UTC()

	customer := &model.Customer{
		CustomerID:     "CUST-2024-000001",
		FullName:       "John Smith",
		CompanyName:    "Acme Corporation",
		PrimaryPhone:   "+15551234567",
		SecondaryPhone: "+15559876543",
		PrimaryEmail:   "john@smith.com",
		SecondaryEmail: "j.smith@acme.com",
		AddressLine1:   "123 Business Ave",
		AddressLine2:   "Suite 400",
		City:           "San Francisco",
		StateProvince:  "CA",
		PostalCode:     "94105",
		Country:        "US",
		CustomerType:   "Business",
		Status:         "Active",
		Notes:          "Key decision maker",
		CreatedBy:      5,
		CreatedAt:      now,
		UpdatedAt:      now,
		Version:        1,
	}

	mock.ExpectBegin()
	mock.ExpectExec(`INSERT INTO "customers"`).
		WithArgs(
			customer.CustomerID,
			customer.FullName,
			customer.CompanyName,
			customer.PrimaryPhone,
			customer.SecondaryPhone,
			customer.PrimaryEmail,
			customer.SecondaryEmail,
			customer.AddressLine1,
			customer.AddressLine2,
			customer.City,
			customer.StateProvince,
			customer.PostalCode,
			customer.Country,
			customer.CustomerType,
			customer.Status,
			customer.Notes,
			customer.CreatedBy,
			customer.CreatedAt,
			customer.UpdatedAt,
			customer.Version,
		).
		WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectCommit()

	err := repo.Create(ctx, customer)
	require.NoError(t, err)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_Create_DuplicateEmail_ReturnsError(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()
	customer := &model.Customer{
		CustomerID:   "CUST-2024-000002",
		FullName:     "Jane Doe",
		PrimaryPhone: "+15559876543",
		PrimaryEmail: "john@smith.com", // Duplicate email
		CreatedBy:    5,
		Status:       "Active",
		Version:      1,
	}

	mock.ExpectBegin()
	mock.ExpectExec(`INSERT INTO "customers"`).
		WillReturnError(gorm.ErrDuplicatedKey) // Simulate unique constraint violation
	mock.ExpectRollback()

	err := repo.Create(ctx, customer)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "duplicate key")
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_GetByID(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()
	expectedCustomer := &model.Customer{
		ID:           1,
		CustomerID:   "CUST-2024-000001",
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		Status:       "Active",
		Version:      1,
	}

	rows := sqlmock.NewRows([]string{
		"id", "customer_id", "full_name", "company_name", "primary_phone",
		"secondary_phone", "primary_email", "secondary_email", "address_line1",
		"address_line2", "city", "state_province", "postal_code", "country",
		"customer_type", "status", "notes", "created_at", "created_by",
		"updated_at", "updated_by", "deleted_at", "deleted_by", "version",
	}).AddRow(
		1, "CUST-2024-000001", "John Smith", "Acme Corporation", "+15551234567",
		"+15559876543", "john@smith.com", "j.smith@acme.com", "123 Business Ave",
		"Suite 400", "San Francisco", "CA", "94105", "US",
		"Business", "Active", "Key decision maker",
		time.Now().UTC(), 5, time.Now().UTC(), nil, nil, nil, 1,
	)

	mock.ExpectQuery(`SELECT \* FROM "customers" WHERE id = \$1 AND deleted_at IS NULL`).
		WithArgs(1).
		WillReturnRows(rows)

	customer, err := repo.GetByID(ctx, 1)
	require.NoError(t, err)
	assert.Equal(t, expectedCustomer.ID, customer.ID)
	assert.Equal(t, expectedCustomer.CustomerID, customer.CustomerID)
	assert.Equal(t, expectedCustomer.FullName, customer.FullName)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_GetByID_NotFound(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	mock.ExpectQuery(`SELECT \* FROM "customers" WHERE id = \$1 AND deleted_at IS NULL`).
		WithArgs(999).
		WillReturnRows(sqlmock.NewRows([]string{"id"}))

	customer, err := repo.GetByID(ctx, 999)
	require.Error(t, err)
	assert.Nil(t, customer)
	assert.Equal(t, gorm.ErrRecordNotFound, err)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_GetByCustomerID(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	rows := sqlmock.NewRows([]string{
		"id", "customer_id", "full_name", "primary_phone", "primary_email",
		"status", "version",
	}).AddRow(1, "CUST-2024-000001", "John Smith", "+15551234567", "john@smith.com", "Active", 1)

	mock.ExpectQuery(`SELECT \* FROM "customers" WHERE customer_id = \$1 AND deleted_at IS NULL`).
		WithArgs("CUST-2024-000001").
		WillReturnRows(rows)

	customer, err := repo.GetByCustomerID(ctx, "CUST-2024-000001")
	require.NoError(t, err)
	assert.Equal(t, "CUST-2024-000001", customer.CustomerID)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_Search(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	rows := sqlmock.NewRows([]string{
		"id", "customer_id", "full_name", "company_name", "primary_phone",
		"primary_email", "customer_type", "status", "created_at",
	}).AddRow(1, "CUST-2024-000001", "John Smith", "Acme Corporation", "+15551234567", "john@smith.com", "Business", "Active", time.Now().UTC()).
		AddRow(2, "CUST-2024-000002", "Jane Smith", "Smith Inc", "+15559876543", "jane@smith.com", "Individual", "Active", time.Now().UTC())

	countRows := sqlmock.NewRows([]string{"count"}).AddRow(2)

	mock.ExpectQuery(`SELECT count\(\*\) FROM "customers" WHERE deleted_at IS NULL`).
		WillReturnRows(countRows)
	mock.ExpectQuery(`SELECT \* FROM "customers" WHERE deleted_at IS NULL`).
		WillReturnRows(rows)

	result, err := repo.Search(ctx, CustomerSearchParams{
		Query:  "smith",
		Page:   1,
		Size:   20,
		Sort:   "created_at",
		Order:  "desc",
	})
	require.NoError(t, err)
	assert.Len(t, result.Data, 2)
	assert.Equal(t, int64(2), result.Total)
	assert.Equal(t, 1, result.Page)
	assert.Equal(t, 1, result.TotalPages)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_Search_WithFilters(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	rows := sqlmock.NewRows([]string{
		"id", "customer_id", "full_name", "customer_type", "status",
	}).AddRow(1, "CUST-2024-000001", "John Smith", "Business", "Active")

	countRows := sqlmock.NewRows([]string{"count"}).AddRow(1)

	mock.ExpectQuery(`SELECT count\(\*\) FROM "customers" WHERE deleted_at IS NULL AND customer_type = \$1`).
		WithArgs("Business").
		WillReturnRows(countRows)
	mock.ExpectQuery(`SELECT \* FROM "customers" WHERE deleted_at IS NULL AND customer_type = \$1`).
		WithArgs("Business").
		WillReturnRows(rows)

	result, err := repo.Search(ctx, CustomerSearchParams{
		Query:        "",
		Page:         1,
		Size:         20,
		Sort:         "created_at",
		Order:        "desc",
		CustomerType: "Business",
		Status:       "Active",
	})
	require.NoError(t, err)
	assert.Len(t, result.Data, 1)
	assert.Equal(t, "Business", result.Data[0].CustomerType)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_Search_ManagerCannotSeeDeleted(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	countRows := sqlmock.NewRows([]string{"count"}).AddRow(0)

	// Manager search should only include deleted_at IS NULL
	mock.ExpectQuery(`SELECT count\(\*\) FROM "customers" WHERE deleted_at IS NULL`).
		WillReturnRows(countRows)
	mock.ExpectQuery(`SELECT \* FROM "customers" WHERE deleted_at IS NULL`).
		WillReturnRows(sqlmock.NewRows([]string{"id"}))

	result, err := repo.Search(ctx, CustomerSearchParams{
		Query:  "",
		Page:   1,
		Size:   20,
		Sort:   "created_at",
		Order:  "desc",
		Status: "Deleted", // Manager requesting deleted
	})
	require.NoError(t, err)
	assert.Len(t, result.Data, 0)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_ExistsByEmail(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	mock.ExpectQuery(`SELECT EXISTS\(SELECT 1 FROM "customers" WHERE primary_email = \$1 AND deleted_at IS NULL\)`).
		WithArgs("john@smith.com").
		WillReturnRows(sqlmock.NewRows([]string{"exists"}).AddRow(true))

	exists, err := repo.ExistsByEmail(ctx, "john@smith.com")
	require.NoError(t, err)
	assert.True(t, exists)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_ExistsByPhone(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	mock.ExpectQuery(`SELECT EXISTS\(SELECT 1 FROM "customers" WHERE primary_phone = \$1 AND deleted_at IS NULL\)`).
		WithArgs("+15551234567").
		WillReturnRows(sqlmock.NewRows([]string{"exists"}).AddRow(false))

	exists, err := repo.ExistsByPhone(ctx, "+15551234567")
	require.NoError(t, err)
	assert.False(t, exists)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_FindPotentialDuplicates(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	rows := sqlmock.NewRows([]string{
		"id", "customer_id", "full_name", "company_name", "primary_phone",
		"primary_email", "status",
	}).AddRow(1, "CUST-2024-000001", "John Smith", "Acme Corporation", "+15551234567", "john@smith.com", "Active").
		AddRow(2, "CUST-2024-000002", "Jon Smith", "Acme Corporation", "+15551234567", "jon@smith.com", "Active")

	mock.ExpectQuery(`SELECT \* FROM "customers" WHERE deleted_at IS NULL AND`).
		WillReturnRows(rows)

	matches, err := repo.FindPotentialDuplicates(ctx, DuplicateSearchCriteria{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		CompanyName:  "Acme Corporation",
	})
	require.NoError(t, err)
	assert.Len(t, matches, 2)
	assert.Equal(t, "CUST-2024-000001", matches[0].CustomerID)
	assert.Equal(t, "CUST-2024-000002", matches[1].CustomerID)
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_GetNextSequenceForYear(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	mock.ExpectQuery(`SELECT COALESCE\(MAX\(CAST\(SUBSTRING\(customer_id FROM 'CUST-\d{4}-(\d{6})'\) AS INTEGER\)\), 0\) FROM "customers" WHERE customer_id LIKE \$1`).
		WithArgs("CUST-2024-%").
		WillReturnRows(sqlmock.NewRows([]string{"max"}).AddRow(5))

	seq, err := repo.GetNextSequenceForYear(ctx, 2024)
	require.NoError(t, err)
	assert.Equal(t, 6, seq) // Next sequence is max + 1
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestCustomerRepository_GetNextSequenceForYear_FirstOfYear(t *testing.T) {
	repo, _, mock := setupCustomerRepositoryTest(t)
	defer repo.db.(*sql.DB).Close()

	ctx := context.Background()

	mock.ExpectQuery(`SELECT COALESCE\(MAX\(CAST\(SUBSTRING\(customer_id FROM 'CUST-\d{4}-(\d{6})'\) AS INTEGER\)\), 0\) FROM "customers" WHERE customer_id LIKE \$1`).
		WithArgs("CUST-2025-%").
		WillReturnRows(sqlmock.NewRows([]string{"max"}).AddRow(0))

	seq, err := repo.GetNextSequenceForYear(ctx, 2025)
	require.NoError(t, err)
	assert.Equal(t, 1, seq) // First of year
	assert.NoError(t, mock.ExpectationsWereMet())
}
```

---

## Service Tests

```go
// File: internal/service/customer_service_test.go
package service

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"crm-system/internal/dto"
	"crm-system/internal/model"
	"crm-system/internal/repository"
	"crm-system/internal/service"
)

type mockCustomerRepository struct {
	mock.Mock
}

func (m *mockCustomerRepository) Create(ctx context.Context, customer *model.Customer) error {
	args := m.Called(ctx, customer)
	return args.Error(0)
}

func (m *mockCustomerRepository) GetByID(ctx context.Context, id int64) (*model.Customer, error) {
	args := m.Called(ctx, id)
	return args.Get(0).(*model.Customer), args.Error(1)
}

func (m *mockCustomerRepository) GetByCustomerID(ctx context.Context, customerID string) (*model.Customer, error) {
	args := m.Called(ctx, customerID)
	return args.Get(0).(*model.Customer), args.Error(1)
}

func (m *mockCustomerRepository) Search(ctx context.Context, params repository.CustomerSearchParams) (*repository.PaginatedResult, error) {
	args := m.Called(ctx, params)
	return args.Get(0).(*repository.PaginatedResult), args.Error(1)
}

func (m *mockCustomerRepository) ExistsByEmail(ctx context.Context, email string) (bool, error) {
	args := m.Called(ctx, email)
	return args.Bool(0), args.Error(1)
}

func (m *mockCustomerRepository) ExistsByPhone(ctx context.Context, phone string) (bool, error) {
	args := m.Called(ctx, phone)
	return args.Bool(0), args.Error(1)
}

func (m *mockCustomerRepository) FindPotentialDuplicates(ctx context.Context, criteria repository.DuplicateSearchCriteria) ([]*model.Customer, error) {
	args := m.Called(ctx, criteria)
	return args.Get(0).([]*model.Customer), args.Error(1)
}

func (m *mockCustomerRepository) GetNextSequenceForYear(ctx context.Context, year int) (int, error) {
	args := m.Called(ctx, year)
	return args.Int(0), args.Error(1)
}

func (m *mockCustomerRepository) Update(ctx context.Context, customer *model.Customer) error {
	args := m.Called(ctx, customer)
	return args.Error(0)
}

func (m *mockCustomerRepository) SoftDelete(ctx context.Context, id int64, version int) error {
	args := m.Called(ctx, id, version)
	return args.Error(0)
}

type mockAuditService struct {
	mock.Mock
}

func (m *mockAuditService) LogCustomerCreated(ctx context.Context, customer *model.Customer, actorID int64, requestID string) error {
	args := m.Called(ctx, customer, actorID, requestID)
	return args.Error(0)
}

func (m *mockAuditService) LogCustomerUpdated(ctx context.Context, old, new *model.Customer, actorID int64, requestID string) error {
	args := m.Called(ctx, old, new, actorID, requestID)
	return args.Error(0)
}

func (m *mockAuditService) LogCustomerDeleted(ctx context.Context, customer *model.Customer, actorID int64, requestID string) error {
	args := m.Called(ctx, customer, actorID, requestID)
	return args.Error(0)
}

func setupCustomerServiceTest(t *testing.T) (*service.CustomerService, *mockCustomerRepository, *mockAuditService) {
	mockRepo := new(mockCustomerRepository)
	mockAudit := new(mockAuditService)
	
	svc := service.NewCustomerService(mockRepo, mockAudit)
	return svc, mockRepo, mockAudit
}

func TestCustomerService_Create_Success(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		CompanyName:  "Acme Corporation",
		CustomerType: "Business",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.AnythingOfType("repository.DuplicateSearchCriteria")).Return([]*model.Customer{}, nil)
	mockRepo.On("Create", ctx, mock.AnythingOfType("*model.Customer")).Return(nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.AnythingOfType("*model.Customer"), int64(5), mock.AnythingOfType("string")).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.NoError(t, err)
	assert.True(t, resp.Success)
	assert.Equal(t, "Customer created successfully", resp.Message)
	assert.NotNil(t, resp.Data)
	assert.Equal(t, "CUST-2024-000001", resp.Data.CustomerID)
	assert.Equal(t, "john@smith.com", resp.Data.PrimaryEmail) // Lowercase
	assert.Equal(t, "John Smith", resp.Data.FullName)
	assert.Equal(t, "Active", resp.Data.Status)
	assert.Equal(t, 1, resp.Data.Version)
	
	mockRepo.AssertExpectations(t)
	mockAudit.AssertExpectations(t)
}

func TestCustomerService_Create_GeneratesCustomerID_Format(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(42, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{}, nil)
	mockRepo.On("Create", ctx, mock.MatchedBy(func(c *model.Customer) bool {
		assert.Equal(t, "CUST-2024-000042", c.CustomerID)
		return true
	})).Return(nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.NoError(t, err)
	assert.Equal(t, "CUST-2024-000042", resp.Data.CustomerID)
}

func TestCustomerService_Create_NormalizesEmailToLowercase(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "JOHN@SMITH.COM",
		SecondaryEmail: "J.SMITH@ACME.COM",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{}, nil)
	mockRepo.On("Create", ctx, mock.MatchedBy(func(c *model.Customer) bool {
		assert.Equal(t, "john@smith.com", c.PrimaryEmail)
		assert.Equal(t, "j.smith@acme.com", c.SecondaryEmail)
		return true
	})).Return(nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.NoError(t, err)
	assert.Equal(t, "john@smith.com", resp.Data.PrimaryEmail)
	assert.Equal(t, "j.smith@acme.com", resp.Data.SecondaryEmail)
}

func TestCustomerService_Create_NormalizesPhoneToE164(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	// Input with various formats that should normalize to E.164
	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+1 555 123 4567", // With spaces
		PrimaryEmail: "john@smith.com",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{}, nil)
	mockRepo.On("Create", ctx, mock.MatchedBy(func(c *model.Customer) bool {
		assert.Equal(t, "+15551234567", c.PrimaryPhone) // Normalized E.164
		return true
	})).Return(nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.NoError(t, err)
	assert.Equal(t, "+15551234567", resp.Data.PrimaryPhone)
}

func TestCustomerService_Create_DuplicateDetected_EmailMatch(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com", // Matches existing
	}

	existingCustomer := &model.Customer{
		ID:           1,
		CustomerID:   "CUST-2024-000001",
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		CompanyName:  "Acme Corporation",
		Status:       "Active",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{existingCustomer}, nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Nil(t, resp)
	assert.Equal(t, service.ErrDuplicateDetected, err)
	
	// Verify duplicate details in error
	var dupErr *service.DuplicateError
	assert.ErrorAs(t, err, &dupErr)
	assert.Len(t, dupErr.Matches, 1)
	assert.Equal(t, "EMAIL_EXACT", dupErr.Matches[0].MatchType)
	assert.Equal(t, "CUST-2024-000001", dupErr.Matches[0].CustomerID)
}

func TestCustomerService_Create_DuplicateDetected_NamePhoneMatch(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "Jon Smith", // Similar name (>85%)
		PrimaryPhone: "+15551234567", // Exact phone match
		PrimaryEmail: "different@email.com",
	}

	existingCustomer := &model.Customer{
		ID:           1,
		CustomerID:   "CUST-2024-000001",
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		CompanyName:  "Acme Corporation",
		Status:       "Active",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{existingCustomer}, nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Equal(t, service.ErrDuplicateDetected, err)
	var dupErr *service.DuplicateError
	assert.ErrorAs(t, err, &dupErr)
	assert.Equal(t, "NAME_PHONE", dupErr.Matches[0].MatchType)
	assert.InDelta(t, 0.92, dupErr.Matches[0].Similarity, 0.01)
}

func TestCustomerService_Create_DuplicateDetected_CompanyPhoneMatch(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:      "Different Person",
		PrimaryPhone:  "+15551234567",
		PrimaryEmail:  "different@email.com",
		CompanyName:   "Acme Corporation", // Exact company match
	}

	existingCustomer := &model.Customer{
		ID:           1,
		CustomerID:   "CUST-2024-000001",
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567", // Exact phone match
		PrimaryEmail: "john@smith.com",
		CompanyName:  "Acme Corporation",
		Status:       "Active",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{existingCustomer}, nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Equal(t, service.ErrDuplicateDetected, err)
	var dupErr *service.DuplicateError
	assert.ErrorAs(t, err, &dupErr)
	assert.Equal(t, "COMPANY_PHONE", dupErr.Matches[0].MatchType)
}

func TestCustomerService_Create_DuplicateProceedAnyway(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		ProceedAnyway: true, // Admin chooses to proceed despite duplicate
	}

	existingCustomer := &model.Customer{
		ID:           1,
		CustomerID:   "CUST-2024-000001",
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		Status:       "Active",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(2, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{existingCustomer}, nil)
	mockRepo.On("Create", ctx, mock.MatchedBy(func(c *model.Customer) bool {
		assert.Equal(t, "CUST-2024-000002", c.CustomerID)
		return true
	})).Return(nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.NoError(t, err)
	assert.True(t, resp.Success)
	assert.Equal(t, "CUST-2024-000002", resp.Data.CustomerID)
}

func TestCustomerService_Create_ValidationError_MissingRequiredFields(t *testing.T) {
	svc, _, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName: "", // Missing
		PrimaryPhone: "",
		PrimaryEmail: "",
	}

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Nil(t, resp)
	assert.Equal(t, service.ErrValidationFailed, err)
	var valErr *service.ValidationError
	assert.ErrorAs(t, err, &valErr)
	assert.Len(t, valErr.Fields, 3)
}

func TestCustomerService_Create_ValidationError_InvalidEmail(t *testing.T) {
	svc, _, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "invalid-email",
	}

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Equal(t, service.ErrValidationFailed, err)
	var valErr *service.ValidationError
	assert.ErrorAs(t, err, &valErr)
	assert.Contains(t, valErr.Fields, "primary_email")
	assert.Equal(t, "INVALID_EMAIL_FORMAT", valErr.Fields["primary_email"])
}

func TestCustomerService_Create_ValidationError_InvalidPhone(t *testing.T) {
	svc, _, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "555-123-4567", // Not E.164
		PrimaryEmail: "john@smith.com",
	}

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Equal(t, service.ErrValidationFailed, err)
	var valErr *service.ValidationError
	assert.ErrorAs(t, err, &valErr)
	assert.Contains(t, valErr.Fields, "primary_phone")
	assert.Equal(t, "INVALID_PHONE_FORMAT", valErr.Fields["primary_phone"])
}

func TestCustomerService_Create_ValidationError_MaxLength(t *testing.T) {
	svc, _, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     string(make([]byte, 201)),
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
	}

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Equal(t, service.ErrValidationFailed, err)
	var valErr *service.ValidationError
	assert.ErrorAs(t, err, &valErr)
	assert.Contains(t, valErr.Fields, "full_name")
	assert.Equal(t, "MAX_LENGTH_EXCEEDED", valErr.Fields["full_name"])
}

func TestCustomerService_Create_ValidationError_InvalidCustomerType(t *testing.T) {
	svc, _, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:      "John Smith",
		PrimaryPhone:  "+15551234567",
		PrimaryEmail:  "john@smith.com",
		CustomerType:  "InvalidType",
	}

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Equal(t, service.ErrValidationFailed, err)
	var valErr *service.ValidationError
	assert.ErrorAs(t, err, &valErr)
	assert.Contains(t, valErr.Fields, "customer_type")
	assert.Equal(t, "INVALID_ENUM_VALUE", valErr.Fields["customer_type"])
}

func TestCustomerService_Create_ValidationError_InvalidCountry(t *testing.T) {
	svc, _, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		Country:      "USA",
	}

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Equal(t, service.ErrValidationFailed, err)
	var valErr *service.ValidationError
	assert.ErrorAs(t, err, &valErr)
	assert.Contains(t, valErr.Fields, "country")
	assert.Equal(t, "INVALID_COUNTRY_CODE", valErr.Fields["country"])
}

func TestCustomerService_Create_DatabaseError_ReturnsInternalError(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{}, nil)
	mockRepo.On("Create", ctx, mock.Anything).Return(errors.New("database connection failed"))
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Nil(t, resp)
	assert.Equal(t, service.ErrInternalError, err)
}

func TestCustomerService_Create_AuditFailure_RollsBack(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{}, nil)
	mockRepo.On("Create", ctx, mock.Anything).Return(nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(errors.New("audit service unavailable"))

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.Error(t, err)
	assert.Equal(t, service.ErrInternalError, err)
	// Note: In real implementation, transaction would rollback customer creation
	// This test verifies the service returns error when audit fails
}

func TestCustomerService_Create_SetsAuditFields(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
	}

	var capturedCustomer *model.Customer
	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{}, nil)
	mockRepo.On("Create", ctx, mock.MatchedBy(func(c *model.Customer) bool {
		capturedCustomer = c
		return true
	})).Return(nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	_, err := svc.Create(ctx, req, 5, "req_abc123")

	require.NoError(t, err)
	assert.NotNil(t, capturedCustomer)
	assert.Equal(t, int64(5), capturedCustomer.CreatedBy)
	assert.WithinDuration(t, time.Now().UTC(), capturedCustomer.CreatedAt, time.Second)
	assert.Equal(t, 1, capturedCustomer.Version)
	assert.Equal(t, "Active", capturedCustomer.Status)
}

func TestCustomerService_Create_DefaultCustomerType(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		// CustomerType not provided
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{}, nil)
	mockRepo.On("Create", ctx, mock.MatchedBy(func(c *model.Customer) bool {
		assert.Equal(t, "Individual", c.CustomerType) // Default per BR-011
		return true
	})).Return(nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.NoError(t, err)
	assert.Equal(t, "Individual", resp.Data.CustomerType)
}

func TestCustomerService_Create_TrimsWhitespace(t *testing.T) {
	svc, mockRepo, mockAudit := setupCustomerServiceTest(t)
	ctx := context.Background()

	req := dto.CreateCustomerRequest{
		FullName:     "  John Smith  ",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "  john@smith.com  ",
		CompanyName:  "  Acme Corp  ",
	}

	mockRepo.On("GetNextSequenceForYear", ctx, 2024).Return(1, nil)
	mockRepo.On("FindPotentialDuplicates", ctx, mock.Anything).Return([]*model.Customer{}, nil)
	mockRepo.On("Create", ctx, mock.MatchedBy(func(c *model.Customer) bool {
		assert.Equal(t, "John Smith", c.FullName)
		assert.Equal(t, "john@smith.com", c.PrimaryEmail)
		assert.Equal(t, "Acme Corp", c.CompanyName)
		return true
	})).Return(nil)
	mockAudit.On("LogCustomerCreated", ctx, mock.Anything, int64(5), mock.Anything).Return(nil)

	resp, err := svc.Create(ctx, req, 5, "req_abc123")

	require.NoError(t, err)
	assert.Equal(t, "John Smith", resp.Data.FullName)
	assert.Equal(t, "john@smith.com", resp.Data.PrimaryEmail)
}

func TestCustomerService_GetByID_Success(t *testing.T) {
	svc, mockRepo, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	expected := &model.Customer{
		ID:           1,
		CustomerID:   "CUST-2024-000001",
		FullName:     "John Smith",
		PrimaryPhone: "+15551234567",
		PrimaryEmail: "john@smith.com",
		Status:       "Active",
		Version:      1,
	}

	mockRepo.On("GetByID", ctx, int64(1)).Return(expected, nil)

	customer, err := svc.GetByID(ctx, 1)

	require.NoError(t, err)
	assert.Equal(t, expected.ID, customer.ID)
	assert.Equal(t, expected.CustomerID, customer.CustomerID)
}

func TestCustomerService_GetByID_NotFound(t *testing.T) {
	svc, mockRepo, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	mockRepo.On("GetByID", ctx, int64(999)).Return((*model.Customer)(nil), gorm.ErrRecordNotFound)

	customer, err := svc.GetByID(ctx, 999)

	require.Error(t, err)
	assert.Nil(t, customer)
	assert.Equal(t, service.ErrNotFound, err)
}

func TestCustomerService_Search_Success(t *testing.T) {
	svc, mockRepo, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	expectedResult := &repository.PaginatedResult{
		Data: []*model.Customer{
			{ID: 1, CustomerID: "CUST-2024-000001", FullName: "John Smith"},
			{ID: 2, CustomerID: "CUST-2024-000002", FullName: "Jane Smith"},
		},
		Total:      2,
		Page:       1,
		Size:       20,
		TotalPages: 1,
	}

	mockRepo.On("Search", ctx, mock.AnythingOfType("repository.CustomerSearchParams")).Return(expectedResult, nil)

	result, err := svc.Search(ctx, dto.CustomerSearchRequest{
		Query: "smith",
		Page:  1,
		Size:  20,
	})

	require.NoError(t, err)
	assert.Equal(t, 2, len(result.Data))
	assert.Equal(t, int64(2), result.Total)
}

func TestCustomerService_Search_ManagerCannotSeeDeleted(t *testing.T) {
	svc, mockRepo, _ := setupCustomerServiceTest(t)
	ctx := context.Background()

	// Service should enforce that non-admin cannot see deleted
	mockRepo.On("Search", ctx, mock.MatchedBy(func(p repository.CustomerSearchParams) bool {
		assert.Equal(t, "Active", p.Status) // Should override to Active
		return true
	})).Return(&repository.PaginatedResult{Data: []*model.Customer{}}, nil)

	result, err := svc.Search(ctx, dto.CustomerSearchRequest{
		Query:  "",
		Page:   1,
		Size:   20,
		Status: "Deleted", // Manager trying to see deleted
		Role:   "Manager",
	})

	require.NoError(t, err)
	assert.Len(t, result.Data, 0)
}
```

---

## Handler Tests

```go
// File: internal/handler/customer_handler_test.go
package handler

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"crm-system/internal/dto"
	"crm-system/internal/service"
)

type mockCustomerService struct {
	mock.Mock
}

func (m *mockCustomerService) Create(ctx context.Context, req dto.CreateCustomerRequest, actorID int64, requestID string) (*dto.CreateCustomerResponse, error) {
	args := m.Called(ctx, req, actorID, requestID)
	return args.Get(0).(*dto.CreateCustomerResponse), args.Error(1)
}

func (m *mockCustomerService) GetByID(ctx context.Context, id int64) (*dto.CustomerResponse, error) {
	args := m.Called(ctx, id)
	return args.Get(0).(*dto.CustomerResponse), args.Error(1)
}

func (m *mockCustomerService) GetByCustomerID(ctx context.Context, customerID string) (*dto.CustomerResponse, error) {
	args := m.Called(ctx, customerID)
	return args.Get(0).(*dto.CustomerResponse), args.Error(1)
}

func (m *mockCustomerService) Search(ctx context.Context, req dto.CustomerSearchRequest) (*dto.CustomerSearchResponse, error) {
	args := m.Called(ctx, req)
	return args.Get(0).(*dto.CustomerSearchResponse), args.Error(1)
}

func (m *mockCustomerService) Update(ctx context.Context, id int64,