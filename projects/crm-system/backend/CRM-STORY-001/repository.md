# Repository Generation Output

## Repository Summary

Generated repositories for **STORY-001 (Create Customer)**:

| Repository | Interface | Implementation | Purpose |
|------------|-----------|----------------|---------|
| `CustomerRepository` | `internal/module/customer/domain/repository.go` | `internal/module/customer/repository/gorm_repo.go` | Customer persistence, search, duplicate detection queries |

---

## Repository Interface

**File:** `internal/module/customer/domain/repository.go`

```go
package domain

import (
	"context"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// CustomerRepository defines the persistence contract for Customer entity.
// Implementations handle database access only — no business logic.
type CustomerRepository interface {
	// Create inserts a new customer record within the provided transaction.
	// Returns the created entity with all generated fields populated.
	Create(ctx context.Context, tx *gorm.DB, customer *Customer) error

	// FindByID retrieves a customer by internal surrogate key (id).
	// Excludes soft-deleted records (deleted_at IS NULL).
	FindByID(ctx context.Context, id int64) (*Customer, error)

	// FindByCustomerID retrieves a customer by business key (customer_id).
	// Excludes soft-deleted records.
	FindByCustomerID(ctx context.Context, customerID string) (*Customer, error)

	// FindByPrimaryEmail retrieves a customer by exact primary_email match (case-insensitive).
	// Excludes soft-deleted records. Used for duplicate detection.
	FindByPrimaryEmail(ctx context.Context, email string) (*Customer, error)

	// FindByPrimaryPhone retrieves customers by exact primary_phone match (E.164).
	// Excludes soft-deleted records. Used for duplicate detection.
	FindByPrimaryPhone(ctx context.Context, phone string) ([]*Customer, error)

	// FindPotentialDuplicates searches for potential duplicate customers based on
	// the provided criteria. Returns all matching candidates with similarity scores.
	// Excludes soft-deleted records.
	// Criteria (per BR-005):
	//   - Email exact match
	//   - Phone exact match + name similarity > 85%
	//   - Company exact match + phone exact match
	FindPotentialDuplicates(ctx context.Context, criteria DuplicateCriteria) ([]*DuplicateMatch, error)

	// Search retrieves a paginated list of customers matching the search parameters.
	// Excludes soft-deleted records. Supports fuzzy search via pg_trgm on name/company/email/phone.
	Search(ctx context.Context, params SearchParams) ([]*Customer, int64, error)

	// ExistsByPrimaryEmail checks if an active customer exists with the given email.
	// Used as a fast-path duplicate check before full duplicate detection.
	ExistsByPrimaryEmail(ctx context.Context, email string) (bool, error)

	// ExistsByCustomerID checks if a customer exists with the given business key.
	ExistsByCustomerID(ctx context.Context, customerID string) (bool, error)
}

// DuplicateCriteria holds the input fields for duplicate detection.
type DuplicateCriteria struct {
	FullName      string
	PrimaryPhone  string
	PrimaryEmail  string
	CompanyName   string
}

// DuplicateMatch represents a potential duplicate customer with match metadata.
type DuplicateMatch struct {
	Customer     *Customer
	MatchType    string // "EMAIL_EXACT", "NAME_PHONE", "COMPANY_PHONE"
	Similarity   float64 // 0.0 to 1.0 (for name similarity)
	MatchedField string // field that triggered the match
}

// SearchParams holds pagination, filtering, and sorting parameters for customer search.
type SearchParams struct {
	Query      string // Free-text search across name, company, email, phone, customer_id, city
	Page       int    // 1-based page number (default: 1)
	Size       int    // Page size (default: 20, max: 100)
	SortBy     string // Sort field: created_at, full_name, company_name, customer_id (default: created_at)
	SortOrder  string // asc or desc (default: desc)
	CustomerType string // Optional filter by customer_type
	Status     string // Optional filter by status (default: Active)
}
```

---

## Repository Implementation

**File:** `internal/module/customer/repository/gorm_repo.go`

```go
package repository

import (
	"context"
	"strings"

	"github.com/google/uuid"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"

	"crm-system/internal/module/customer/domain"
	"crm-system/internal/platform/database"
)

// gormCustomerRepository implements domain.CustomerRepository using GORM.
type gormCustomerRepository struct {
	db *gorm.DB
}

// NewCustomerRepository creates a new GORM-based customer repository.
func NewCustomerRepository(db *gorm.DB) domain.CustomerRepository {
	return &gormCustomerRepository{db: db}
}

// Create inserts a new customer record.
// The transaction is managed by the caller (service layer).
func (r *gormCustomerRepository) Create(ctx context.Context, tx *gorm.DB, customer *domain.Customer) error {
	db := database.GetDB(ctx, tx)
	return db.Create(customer).Error
}

// FindByID retrieves a customer by internal ID, excluding soft-deleted.
func (r *gormCustomerRepository) FindByID(ctx context.Context, id int64) (*domain.Customer, error) {
	var customer domain.Customer
	err := r.db.WithContext(ctx).
		Where("id = ? AND deleted_at IS NULL", id).
		First(&customer).Error
	if err != nil {
		return nil, err
	}
	return &customer, nil
}

// FindByCustomerID retrieves a customer by business key (customer_id), excluding soft-deleted.
func (r *gormCustomerRepository) FindByCustomerID(ctx context.Context, customerID string) (*domain.Customer, error) {
	var customer domain.Customer
	err := r.db.WithContext(ctx).
		Where("customer_id = ? AND deleted_at IS NULL", customerID).
		First(&customer).Error
	if err != nil {
		return nil, err
	}
	return &customer, nil
}

// FindByPrimaryEmail retrieves a customer by exact primary_email match (case-insensitive).
func (r *gormCustomerRepository) FindByPrimaryEmail(ctx context.Context, email string) (*domain.Customer, error) {
	var customer domain.Customer
	normalizedEmail := strings.ToLower(strings.TrimSpace(email))
	err := r.db.WithContext(ctx).
		Where("LOWER(primary_email) = ? AND deleted_at IS NULL", normalizedEmail).
		First(&customer).Error
	if err != nil {
		return nil, err
	}
	return &customer, nil
}

// FindByPrimaryPhone retrieves customers by exact primary_phone match (E.164).
func (r *gormCustomerRepository) FindByPrimaryPhone(ctx context.Context, phone string) ([]*domain.Customer, error) {
	var customers []*domain.Customer
	err := r.db.WithContext(ctx).
		Where("primary_phone = ? AND deleted_at IS NULL", phone).
		Find(&customers).Error
	if err != nil {
		return nil, err
	}
	return customers, nil
}

// FindPotentialDuplicates searches for potential duplicates per BR-005 criteria.
// Returns all matches with match type and similarity scores.
func (r *gormCustomerRepository) FindPotentialDuplicates(ctx context.Context, criteria domain.DuplicateCriteria) ([]*domain.DuplicateMatch, error) {
	var matches []*domain.DuplicateMatch

	// 1. Exact email match (highest priority)
	if criteria.PrimaryEmail != "" {
		emailMatches, err := r.findByEmailExact(ctx, criteria.PrimaryEmail)
		if err != nil {
			return nil, err
		}
		for _, c := range emailMatches {
			matches = append(matches, &domain.DuplicateMatch{
				Customer:     c,
				MatchType:    "EMAIL_EXACT",
				Similarity:   1.0,
				MatchedField: "primary_email",
			})
		}
	}

	// 2. Phone exact match + name similarity > 85%
	if criteria.PrimaryPhone != "" && criteria.FullName != "" {
		phoneNameMatches, err := r.findByPhoneAndNameSimilarity(ctx, criteria.PrimaryPhone, criteria.FullName, 0.85)
		if err != nil {
			return nil, err
		}
		for _, m := range phoneNameMatches {
			matches = append(matches, m)
		}
	}

	// 3. Company exact match + phone exact match
	if criteria.CompanyName != "" && criteria.PrimaryPhone != "" {
		companyPhoneMatches, err := r.findByCompanyAndPhoneExact(ctx, criteria.CompanyName, criteria.PrimaryPhone)
		if err != nil {
			return nil, err
		}
		for _, c := range companyPhoneMatches {
			matches = append(matches, &domain.DuplicateMatch{
				Customer:     c,
				MatchType:    "COMPANY_PHONE",
				Similarity:   1.0,
				MatchedField: "company_name+primary_phone",
			})
		}
	}

	// Deduplicate by customer ID (same customer might match multiple criteria)
	seen := make(map[int64]bool)
	uniqueMatches := make([]*domain.DuplicateMatch, 0, len(matches))
	for _, m := range matches {
		if !seen[m.Customer.ID] {
			seen[m.Customer.ID] = true
			uniqueMatches = append(uniqueMatches, m)
		}
	}

	return uniqueMatches, nil
}

// findByEmailExact finds customers by exact email match (case-insensitive).
func (r *gormCustomerRepository) findByEmailExact(ctx context.Context, email string) ([]*domain.Customer, error) {
	var customers []*domain.Customer
	normalizedEmail := strings.ToLower(strings.TrimSpace(email))
	err := r.db.WithContext(ctx).
		Where("LOWER(primary_email) = ? AND deleted_at IS NULL", normalizedEmail).
		Find(&customers).Error
	return customers, err
}

// findByPhoneAndNameSimilarity finds customers with exact phone match and name similarity > threshold.
// Uses PostgreSQL pg_trgm similarity function.
func (r *gormCustomerRepository) findByPhoneAndNameSimilarity(ctx context.Context, phone, name string, threshold float64) ([]*domain.DuplicateMatch, error) {
	var results []struct {
		Customer domain.Customer
		Sim      float64
	}

	// Use pg_trgm similarity for name comparison
	// similarity(full_name, ?) > threshold AND primary_phone = ?
	query := r.db.WithContext(ctx).
		Table("customers").
		Select("customers.*, similarity(full_name, ?) as sim", name).
		Where("primary_phone = ? AND deleted_at IS NULL AND similarity(full_name, ?) > ?", phone, name, threshold).
		Order("sim DESC")

	err := query.Scan(&results).Error
	if err != nil {
		return nil, err
	}

	matches := make([]*domain.DuplicateMatch, 0, len(results))
	for _, r := range results {
		customer := r.Customer // copy
		matches = append(matches, &domain.DuplicateMatch{
			Customer:     &customer,
			MatchType:    "NAME_PHONE",
			Similarity:   r.Sim,
			MatchedField: "full_name+primary_phone",
		})
	}
	return matches, nil
}

// findByCompanyAndPhoneExact finds customers with exact company_name and primary_phone match.
func (r *gormCustomerRepository) findByCompanyAndPhoneExact(ctx context.Context, companyName, phone string) ([]*domain.Customer, error) {
	var customers []*domain.Customer
	err := r.db.WithContext(ctx).
		Where("company_name = ? AND primary_phone = ? AND deleted_at IS NULL", companyName, phone).
		Find(&customers).Error
	return customers, err
}

// Search retrieves paginated customers matching the search parameters.
// Uses pg_trgm for fuzzy search on text fields, exact match on phone/email/id.
func (r *gormCustomerRepository) Search(ctx context.Context, params domain.SearchParams) ([]*domain.Customer, int64, error) {
	var customers []*domain.Customer
	var total int64

	// Build base query with soft-delete filter
	baseQuery := r.db.WithContext(ctx).Model(&domain.Customer{}).Where("deleted_at IS NULL")

	// Apply free-text search if query provided
	if params.Query != "" {
		searchTerm := params.Query
		// Use pg_trgm for fuzzy search on name, company, email
		// Exact/prefix match on phone, customer_id
		baseQuery = baseQuery.Where(`
			(full_name % ?) OR 
			(company_name % ?) OR 
			(LOWER(primary_email) LIKE ?) OR 
			(LOWER(secondary_email) LIKE ?) OR 
			(primary_phone LIKE ?) OR 
			(secondary_phone LIKE ?) OR 
			(customer_id LIKE ?) OR 
			(city % ?)
		`, searchTerm, searchTerm, "%"+strings.ToLower(searchTerm)+"%", "%"+strings.ToLower(searchTerm)+"%", searchTerm+"%", searchTerm+"%", searchTerm+"%", searchTerm)
	}

	// Apply customer_type filter
	if params.CustomerType != "" {
		baseQuery = baseQuery.Where("customer_type = ?", params.CustomerType)
	}

	// Apply status filter (default: Active)
	status := params.Status
	if status == "" {
		status = "Active"
	}
	baseQuery = baseQuery.Where("status = ?", status)

	// Count total matches (for pagination meta)
	if err := baseQuery.Count(&total).Error; err != nil {
		return nil, 0, err
	}

	// Apply sorting
	sortBy := params.SortBy
	if sortBy == "" {
		sortBy = "created_at"
	}
	// Validate sortBy to prevent SQL injection
	allowedSortFields := map[string]bool{
		"created_at": true, "full_name": true, "company_name": true, "customer_id": true,
	}
	if !allowedSortFields[sortBy] {
		sortBy = "created_at"
	}

	sortOrder := strings.ToUpper(params.SortOrder)
	if sortOrder != "ASC" && sortOrder != "DESC" {
		sortOrder = "DESC"
	}
	baseQuery = baseQuery.Order(clause.OrderByColumn{Column: clause.Column{Name: sortBy}, Desc: sortOrder == "DESC"})

	// Apply pagination
	page := params.Page
	if page < 1 {
		page = 1
	}
	size := params.Size
	if size < 1 {
		size = 20
	}
	if size > 100 {
		size = 100
	}
	offset := (page - 1) * size

	baseQuery = baseQuery.Limit(size).Offset(offset)

	// Execute query
	if err := baseQuery.Find(&customers).Error; err != nil {
		return nil, 0, err
	}

	return customers, total, nil
}

// ExistsByPrimaryEmail checks if an active customer exists with the given email.
func (r *gormCustomerRepository) ExistsByPrimaryEmail(ctx context.Context, email string) (bool, error) {
	var count int64
	normalizedEmail := strings.ToLower(strings.TrimSpace(email))
	err := r.db.WithContext(ctx).
		Model(&domain.Customer{}).
		Where("LOWER(primary_email) = ? AND deleted_at IS NULL", normalizedEmail).
		Count(&count).Error
	return count > 0, err
}

// ExistsByCustomerID checks if a customer exists with the given business key.
func (r *gormCustomerRepository) ExistsByCustomerID(ctx context.Context, customerID string) (bool, error) {
	var count int64
	err := r.db.WithContext(ctx).
		Model(&domain.Customer{}).
		Where("customer_id = ? AND deleted_at IS NULL", customerID).
		Count(&count).Error
	return count > 0, err
}
```

---

## Query Methods Summary

| Method | Query Type | Index Used | Purpose |
|--------|------------|------------|---------|
| `Create` | INSERT | PK, Unique indexes | Persist new customer |
| `FindByID` | PK Lookup | `idx_customers_id` (PK) | Detail view redirect |
| `FindByCustomerID` | Unique Lookup | `idx_customers_customer_id` | Business key lookup |
| `FindByPrimaryEmail` | Unique Lookup | `idx_customers_primary_email` | Duplicate detection (email) |
| `FindByPrimaryPhone` | Index Scan | `idx_customers_primary_phone` | Duplicate detection (phone) |
| `FindPotentialDuplicates` | Composite | `idx_customers_primary_email`, `idx_customers_primary_phone`, `idx_customers_full_name_trgm`, `idx_customers_company_name_trgm` | BR-005 duplicate detection |
| `Search` | Full-text + Filter | `idx_customers_full_name_trgm`, `idx_customers_company_name_trgm`, `idx_customers_search_composite` | EP-02 Search customers |
| `ExistsByPrimaryEmail` | Index Count | `idx_customers_primary_email` | Fast duplicate check |
| `ExistsByCustomerID` | Index Count | `idx_customers_customer_id` | Business key uniqueness |

---

## Dependency Notes

### Model Dependencies
The repository implementation depends on the following domain entity (defined in `internal/module/customer/domain/entity.go`):

```go
// Customer entity (per technical-design.md Section 6.1.1)
type Customer struct {
	ID              int64      `gorm:"column:id;primaryKey;autoIncrement"`
	CustomerID      string     `gorm:"column:customer_id;type:varchar(20);uniqueIndex:idx_customers_customer_id,where:deleted_at_is_null;not null"`
	FullName        string     `gorm:"column:full_name;type:varchar(200);not null"`
	CompanyName     *string    `gorm:"column:company_name;type:varchar(200)"`
	PrimaryPhone    string     `gorm:"column:primary_phone;type:varchar(20);not null;index:idx_customers_primary_phone,where:deleted_at_is_null"`
	SecondaryPhone  *string    `gorm:"column:secondary_phone;type:varchar(20)"`
	PrimaryEmail    string     `gorm:"column:primary_email;type:varchar(254);not null;uniqueIndex:idx_customers_primary_email,where:deleted_at_is_null"`
	SecondaryEmail  *string    `gorm:"column:secondary_email;type:varchar(254)"`
	AddressLine1    *string    `gorm:"column:address_line1;type:varchar(200)"`
	AddressLine2    *string    `gorm:"column:address_line2;type:varchar(200)"`
	City            *string    `gorm:"column:city;type:varchar(100)"`
	StateProvince   *string    `gorm:"column:state_province;type:varchar(100)"`
	PostalCode      *string    `gorm:"column:postal_code;type:varchar(20)"`
	Country         *string    `gorm:"column:country;type:char(2)"`
	CustomerType    string     `gorm:"column:customer_type;type:varchar(20);not null;default:'Individual'"`
	Status          string     `gorm:"column:status;type:varchar(20);not null;default:'Active'"`
	Notes           *string    `gorm:"column:notes;type:text"`
	CreatedAt       time.Time  `gorm:"column:created_at;type:timestamptz;not null;default:now()"`
	CreatedBy       int64      `gorm:"column:created_by;type:bigint;not null"`
	UpdatedAt       time.Time  `gorm:"column:updated_at;type:timestamptz;not null;default:now()"`
	UpdatedBy       *int64     `gorm:"column:updated_by;type:bigint"`
	DeletedAt       *time.Time `gorm:"column:deleted_at;type:timestamptz;index:idx_customers_deleted_at"`
	DeletedBy       *int64     `gorm:"column:deleted_by;type:bigint"`
	Version         int64      `gorm:"column:version;type:bigint;not null;default:1"`

	// Relations (populated by service when needed)
	Creator *User `gorm:"foreignKey:CreatedBy;references:ID"`
	Updater *User `gorm:"foreignKey:UpdatedBy;references:ID"`
	Deleter *User `gorm:"foreignKey:DeletedBy;references:ID"`
}

func (Customer) TableName() string { return "customers" }
```

### Required Database Indexes (Migration)
The following indexes must exist in the database migration (per technical-design.md Section 18.3):

```sql
-- Unique business key (active only)
CREATE UNIQUE INDEX idx_customers_customer_id ON customers (customer_id) WHERE deleted_at IS NULL;

-- Unique email (active only)
CREATE UNIQUE INDEX idx_customers_primary_email ON customers (primary_email) WHERE deleted_at IS NULL;

-- Phone exact match (active only)
CREATE INDEX idx_customers_primary_phone ON customers (primary_phone) WHERE deleted_at IS NULL;

-- Trigram indexes for fuzzy search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_customers_full_name_trgm ON customers USING GIN (full_name gin_trgm_ops);
CREATE INDEX idx_customers_company_name_trgm ON customers USING GIN (company_name gin_trgm_ops);

-- Composite for list pagination + sort
CREATE INDEX idx_customers_search_composite ON customers (status, created_at DESC) WHERE deleted_at IS NULL;

-- Soft delete queries
CREATE INDEX idx_customers_deleted_at ON customers (deleted_at);
```

### Platform Dependencies
- `internal/platform/database` - Provides `GetDB(ctx, tx *gorm.DB) *gorm.DB` helper for transaction-aware DB access
- `gorm.io/gorm` - ORM
- `github.com/google/uuid` - For potential future use (not used in current queries)

---

## Validation Checklist

| Checklist Item | Status |
|----------------|--------|
| [x] Compile Safe - All types referenced exist in domain/entity.go | ✅ |
| [x] Story Scope Respected - Only Create, Read, Search, Duplicate queries | ✅ |
| [x] No Business Rules Implemented - Repository returns data only | ✅ |
| [x] No Transactions Started - Uses caller-provided `tx *gorm.DB` | ✅ |
| [x] Parameterized Queries Used - All `Where` clauses use `?` placeholders | ✅ |
| [x] Repository Interface Generated | ✅ |
| [x] Repository Implementation Generated | ✅ |
| [x] Search Queries Generated (pg_trgm + exact match) | ✅ |
| [x] Pagination Supported (page, size, sort, offset) | ✅ |
| [x] Soft Delete Supported (deleted_at IS NULL filters) | ✅ |
| [x] No Services Generated | ✅ |
| [x] No Handlers Generated | ✅ |
| [x] No Middleware Generated | ✅ |
| [x] Duplicate Detection Queries (3 criteria per BR-005) | ✅ |
| [x] Transaction-Aware (accepts `tx *gorm.DB`) | ✅ |

---

## Handoff to Backend Service Agent

**Artifacts Produced:**
1. `internal/module/customer/domain/repository.go` - Repository interface
2. `internal/module/customer/repository/gorm_repo.go` - GORM implementation

**Next Agent:** Backend Service Agent  
**Consumes:** Repository interfaces for dependency injection into CustomerService

**Service Layer Responsibilities (NOT in repository):**
- Customer ID generation (CUST-YYYY-NNNNNN)
- Phone normalization (E.164 via libphonenumber-go)
- Email normalization (lowercase)
- Duplicate detection orchestration (calling FindPotentialDuplicates)
- Business rule validation (BR-002, BR-003, BR-011, BR-012)
- Audit field population (created_by, created_at, version=1)
- Transaction management (Begin/Commit/Rollback)
- Error mapping to API error codes (VALIDATION_ERROR, DUPLICATE_DETECTED, etc.)