# Migration Summary

## Affected Tables
- `customers` (new table)

## New Constraints
- Primary Key: `customers_pkey` on `id`
- Unique: `uq_customers_customer_id_active` on `customer_id` (partial, where `deleted_at IS NULL`)
- Unique: `uq_customers_primary_email_active` on `primary_email` (partial, where `deleted_at IS NULL`)
- Foreign Keys: `created_by`, `updated_by`, `deleted_by` → `users(id)`
- Check: `ck_customers_notes_length` (notes ≤ 2000 chars)
- Check: `ck_customers_customer_type` (valid enum)
- Check: `ck_customers_status` (valid enum)
- Check: `ck_customers_country_length` (country = 2 chars when not null)
- Check: `ck_customers_customer_id_format` (CUST-YYYY-NNNNNN pattern)

## New Indexes
- `idx_customers_full_name_trgm` (GIN, pg_trgm) on `full_name`
- `idx_customers_company_name_trgm` (GIN, pg_trgm) on `company_name`
- `idx_customers_primary_phone_active` (B-Tree) on `primary_phone` WHERE `deleted_at IS NULL`
- `idx_customers_search_composite` (B-Tree) on `status, created_at DESC` WHERE `deleted_at IS NULL`
- `idx_customers_deleted_at` (B-Tree) on `deleted_at`
- `idx_customers_created_by` (B-Tree) on `created_by`
- `idx_customers_updated_by` (B-Tree) on `updated_by`
- `idx_customers_deleted_by` (B-Tree) on `deleted_by`

## Relationships
- `customers.created_by` → `users.id` (NOT NULL)
- `customers.updated_by` → `users.id` (NULLABLE)
- `customers.deleted_by` → `users.id` (NULLABLE)

---

# Up Migration

```sql
-- Migration: 003_create_customers_table.sql
-- Description: Create customers table with all columns, constraints, indexes, and audit fields
-- Depends on: 001_extensions.sql (pg_trgm), 002_create_users_table.sql (users table)

-- Ensure pg_trgm extension exists for trigram indexes
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create customers table
CREATE TABLE customers (
    -- Primary key (internal surrogate key)
    id BIGSERIAL PRIMARY KEY,

    -- Business key: CUST-YYYY-NNNNNN (unique per active record)
    customer_id VARCHAR(20) NOT NULL,

    -- Required fields (BR-002)
    full_name VARCHAR(200) NOT NULL,
    primary_phone VARCHAR(20) NOT NULL,
    primary_email VARCHAR(254) NOT NULL,

    -- Optional fields
    company_name VARCHAR(200),
    secondary_phone VARCHAR(20),
    secondary_email VARCHAR(254),
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country CHAR(2),

    -- Classification (BR-011, defaults per technical design)
    customer_type VARCHAR(20) NOT NULL DEFAULT 'Individual',
    status VARCHAR(20) NOT NULL DEFAULT 'Active',

    -- Notes (BR-011: max 2000 chars)
    notes TEXT,

    -- Audit fields (BR-015)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by BIGINT,
    deleted_at TIMESTAMPTZ,
    deleted_by BIGINT,

    -- Optimistic locking (ADR-006)
    version BIGINT NOT NULL DEFAULT 1
);

-- Unique constraint on customer_id for active records only (allows reuse after soft delete)
CREATE UNIQUE INDEX uq_customers_customer_id_active
    ON customers (customer_id)
    WHERE deleted_at IS NULL;

-- Unique constraint on primary_email for active records only (BR-004: soft uniqueness)
CREATE UNIQUE INDEX uq_customers_primary_email_active
    ON customers (primary_email)
    WHERE deleted_at IS NULL;

-- Check constraint: notes max 2000 characters (BR-011)
ALTER TABLE customers
    ADD CONSTRAINT ck_customers_notes_length
    CHECK (notes IS NULL OR char_length(notes) <= 2000);

-- Check constraint: customer_type valid enum values
ALTER TABLE customers
    ADD CONSTRAINT ck_customers_customer_type
    CHECK (customer_type IN ('Individual', 'Business', 'Government', 'Other'));

-- Check constraint: status valid enum values
ALTER TABLE customers
    ADD CONSTRAINT ck_customers_status
    CHECK (status IN ('Active', 'Deleted'));

-- Check constraint: country must be 2 characters (ISO 3166-1 alpha-2) when provided
ALTER TABLE customers
    ADD CONSTRAINT ck_customers_country_length
    CHECK (country IS NULL OR char_length(country) = 2);

-- Check constraint: customer_id format CUST-YYYY-NNNNNN (BR-001)
ALTER TABLE customers
    ADD CONSTRAINT ck_customers_customer_id_format
    CHECK (customer_id ~ '^CUST-\d{4}-\d{6}$');

-- Foreign key: created_by → users(id) (NOT NULL, required for audit)
ALTER TABLE customers
    ADD CONSTRAINT fk_customers_created_by
    FOREIGN KEY (created_by) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE;

-- Foreign key: updated_by → users(id) (nullable)
ALTER TABLE customers
    ADD CONSTRAINT fk_customers_updated_by
    FOREIGN KEY (updated_by) REFERENCES users (id)
    ON DELETE SET NULL ON UPDATE CASCADE;

-- Foreign key: deleted_by → users(id) (nullable)
ALTER TABLE customers
    ADD CONSTRAINT fk_customers_deleted_by
    FOREIGN KEY (deleted_by) REFERENCES users (id)
    ON DELETE SET NULL ON UPDATE CASCADE;

-- Index: trigram GIN index on full_name for fuzzy search (ADR-005)
CREATE INDEX idx_customers_full_name_trgm
    ON customers USING GIN (full_name gin_trgm_ops);

-- Index: trigram GIN index on company_name for fuzzy search (ADR-005)
CREATE INDEX idx_customers_company_name_trgm
    ON customers USING GIN (company_name gin_trgm_ops);

-- Index: primary_phone for exact/prefix search on active records
CREATE INDEX idx_customers_primary_phone_active
    ON customers (primary_phone)
    WHERE deleted_at IS NULL;

-- Index: composite for list pagination with status filter (Section 18.3)
CREATE INDEX idx_customers_search_composite
    ON customers (status, created_at DESC)
    WHERE deleted_at IS NULL;

-- Index: deleted_at for soft delete queries and purge jobs
CREATE INDEX idx_customers_deleted_at
    ON customers (deleted_at);

-- Index: created_by for audit queries
CREATE INDEX idx_customers_created_by
    ON customers (created_by);

-- Index: updated_by for audit queries
CREATE INDEX idx_customers_updated_by
    ON customers (updated_by);

-- Index: deleted_by for audit queries
CREATE INDEX idx_customers_deleted_by
    ON customers (deleted_by);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comment on table and columns for documentation
COMMENT ON TABLE customers IS 'Core customer entity with soft delete, audit trail, and optimistic locking';
COMMENT ON COLUMN customers.id IS 'Internal surrogate primary key';
COMMENT ON COLUMN customers.customer_id IS 'Business key: CUST-YYYY-NNNNNN (unique per active record)';
COMMENT ON COLUMN customers.full_name IS 'Customer full name (required, max 200 chars)';
COMMENT ON COLUMN customers.company_name IS 'Company name (optional, max 200 chars)';
COMMENT ON COLUMN customers.primary_phone IS 'Primary phone in E.164 format (required, max 20 chars)';
COMMENT ON COLUMN customers.secondary_phone IS 'Secondary phone in E.164 format (optional, max 20 chars)';
COMMENT ON COLUMN customers.primary_email IS 'Primary email lowercase (required, max 254 chars, unique per active)';
COMMENT ON COLUMN customers.secondary_email IS 'Secondary email lowercase (optional, max 254 chars)';
COMMENT ON COLUMN customers.address_line1 IS 'Address line 1 (optional, max 200 chars)';
COMMENT ON COLUMN customers.address_line2 IS 'Address line 2 (optional, max 200 chars)';
COMMENT ON COLUMN customers.city IS 'City (optional, max 100 chars)';
COMMENT ON COLUMN customers.state_province IS 'State/Province (optional, max 100 chars)';
COMMENT ON COLUMN customers.postal_code IS 'Postal code (optional, max 20 chars)';
COMMENT ON COLUMN customers.country IS 'ISO 3166-1 alpha-2 country code (optional, 2 chars)';
COMMENT ON COLUMN customers.customer_type IS 'Customer type: Individual, Business, Government, Other';
COMMENT ON COLUMN customers.status IS 'Record status: Active, Deleted (soft delete)';
COMMENT ON COLUMN customers.notes IS 'Admin notes (optional, max 2000 chars)';
COMMENT ON COLUMN customers.created_at IS 'Record creation timestamp (UTC)';
COMMENT ON COLUMN customers.created_by IS 'User ID who created this record (FK to users.id)';
COMMENT ON COLUMN customers.updated_at IS 'Last update timestamp (UTC, auto-updated by trigger)';
COMMENT ON COLUMN customers.updated_by IS 'User ID who last updated this record (FK to users.id)';
COMMENT ON COLUMN customers.deleted_at IS 'Soft delete timestamp (NULL = active)';
COMMENT ON COLUMN customers.deleted_by IS 'User ID who deleted this record (FK to users.id)';
COMMENT ON COLUMN customers.version IS 'Optimistic lock version (incremented on each update)';
```

---

# Down Migration

```sql
-- Migration: 003_create_customers_table.sql (ROLLBACK)
-- Description: Drop customers table and all associated objects in reverse order

-- Drop trigger and function
DROP TRIGGER IF EXISTS trigger_customers_updated_at ON customers;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop indexes (order doesn't matter for indexes, but following reverse creation order)
DROP INDEX IF EXISTS idx_customers_deleted_by;
DROP INDEX IF EXISTS idx_customers_updated_by;
DROP INDEX IF EXISTS idx_customers_created_by;
DROP INDEX IF EXISTS idx_customers_deleted_at;
DROP INDEX IF EXISTS idx_customers_search_composite;
DROP INDEX IF EXISTS idx_customers_primary_phone_active;
DROP INDEX IF EXISTS idx_customers_company_name_trgm;
DROP INDEX IF EXISTS idx_customers_full_name_trgm;

-- Drop foreign key constraints
ALTER TABLE customers DROP CONSTRAINT IF EXISTS fk_customers_deleted_by;
ALTER TABLE customers DROP CONSTRAINT IF EXISTS fk_customers_updated_by;
ALTER TABLE customers DROP CONSTRAINT IF EXISTS fk_customers_created_by;

-- Drop check constraints
ALTER TABLE customers DROP CONSTRAINT IF EXISTS ck_customers_customer_id_format;
ALTER TABLE customers DROP CONSTRAINT IF EXISTS ck_customers_country_length;
ALTER TABLE customers DROP CONSTRAINT IF EXISTS ck_customers_status;
ALTER TABLE customers DROP CONSTRAINT IF EXISTS ck_customers_customer_type;
ALTER TABLE customers DROP CONSTRAINT IF EXISTS ck_customers_notes_length;

-- Drop unique indexes (which implement unique constraints)
DROP INDEX IF EXISTS uq_customers_primary_email_active;
DROP INDEX IF EXISTS uq_customers_customer_id_active;

-- Drop primary key and table
DROP TABLE IF EXISTS customers;

-- Note: pg_trgm extension is NOT dropped here as it may be used by other tables
-- It should be dropped in a separate migration if truly no longer needed
```

---

# Migration Validation Notes

## Order Verification
✅ **Extensions First**: `CREATE EXTENSION IF NOT EXISTS pg_trgm` runs before GIN indexes that depend on it  
✅ **Parent Tables First**: Assumes `users` table exists (created in migration 002) before FK constraints reference it  
✅ **Child Tables After**: `customers` created after `users`  
✅ **Foreign Keys After Parents**: FKs added after both tables exist  
✅ **Indexes After Tables**: All indexes created after `customers` table exists  

## Dependencies
- **Migration 001**: `pg_trgm` extension (required for `gin_trgm_ops` indexes)
- **Migration 002**: `users` table (required for FK references on `created_by`, `updated_by`, `deleted_by`)

## Rollback Strategy
- Down migration drops objects in **exact reverse order** of creation
- Trigger/function dropped first (depends on table)
- Indexes dropped before constraints (no dependency)
- Foreign keys dropped before check constraints (no dependency)
- Unique indexes dropped before table
- Table dropped last
- `pg_trgm` extension **preserved** (may be used by other migrations)

## Compile-Safe Verification
- ✅ All SQL uses valid PostgreSQL 16 syntax
- ✅ No references to non-existent tables/columns
- ✅ Constraint names are unique (`uq_`, `ck_`, `fk_` prefixes with table name)
- ✅ Index names are unique (`idx_` prefix with table and column names)
- ✅ Partial indexes use correct `WHERE deleted_at IS NULL` syntax
- ✅ GIN indexes specify `gin_trgm_ops` operator class
- ✅ Check constraints use valid expressions
- ✅ Foreign keys reference existing `users(id)` column
- ✅ `ON DELETE` actions appropriate (RESTRICT for required `created_by`, SET NULL for optional)

## Story Scope Compliance
✅ **Only STORY-001 requirements implemented**:
- Customer table with all fields from technical-design.md Section 6.1.1
- Required fields: `full_name`, `primary_phone`, `primary_email` (BR-002)
- Business key `customer_id` with format constraint (BR-001)
- Email uniqueness on active records only (BR-004)
- Phone E.164 storage (BR-003) - enforced at application layer, DB stores VARCHAR(20)
- Email lowercase storage (BR-012) - enforced at application layer
- Field length limits via VARCHAR/CHECK (BR-011)
- Audit fields: `created_at`, `created_by`, `updated_at`, `updated_by`, `deleted_at`, `deleted_by` (BR-015)
- Soft delete via `deleted_at` (ADR-002)
- Optimistic locking via `version` (ADR-006)
- Search indexes for EP-02 performance (pg_trgm, composite)

❌ **No future features added**:
- No `audit_events` table (Phase 2, ADR-002)
- No `customer_interactions`, `campaigns`, etc. (other domains)
- No restore endpoint support (future EP)
- No partition on `audit_events` (future)

## Output Validation Checklist
- [x] SQL Valid PostgreSQL 16
- [x] Rollback Included (complete down migration)
- [x] Foreign Keys Valid (reference `users.id`)
- [x] Tables Created In Correct Order (after users, after extensions)
- [x] Indexes Created In Correct Order (after table, after extension)
- [x] Audit Columns Included (all 6 fields)
- [x] Story Scope Respected (only Create Customer requirements)
- [x] No Future Features Added
- [x] No Application Code Generated