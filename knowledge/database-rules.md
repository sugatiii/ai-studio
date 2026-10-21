# Database Rules

Version: 1.0

---

# Purpose

Dokumen ini mendefinisikan standar database yang wajib digunakan oleh seluruh AI Agent dan Developer.

Tujuan:

- Konsistensi
- Data Integrity
- Maintainability
- Scalability
- Performance
- Security

Semua perubahan database wajib mengikuti aturan pada dokumen ini.

---

# Database Standard

Primary Database:

```text
PostgreSQL
```

ORM:

```text
GORM
```

Database Access:

```text
Repository Pattern
```

Migration Tool:

```text
golang-migrate
```

---

# Database Principles

Database harus:

```text
Consistent
Maintainable
Auditable
Optimized
Secure
```

Database bukan tempat business logic.

Business logic harus berada di:

```text
Service Layer
```

---

# Naming Convention

## Table Name

Gunakan:

```text
snake_case
plural
```

Good:

```text
users
roles
permissions
products
orders
order_items
customer_addresses
```

Bad:

```text
User
ProductTable
tbl_user
```

---

## Column Name

Gunakan:

```text
snake_case
```

Good:

```text
first_name
last_name
order_number
created_at
updated_at
```

Bad:

```text
FirstName
LastName
ORDERNUMBER
```

---

## Primary Key

Standar:

```text
id
```

Type:

```text
UUID
```

Contoh:

```sql
id UUID PRIMARY KEY
```

---

# Audit Columns

Semua table wajib memiliki:

```sql
created_at
created_by
updated_at
updated_by
```

Jika mendukung soft delete:

```sql
deleted_at
deleted_by
```

---

# Base Table Example

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,

    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,

    created_at TIMESTAMP NOT NULL,
    created_by UUID,

    updated_at TIMESTAMP NOT NULL,
    updated_by UUID,

    deleted_at TIMESTAMP,
    deleted_by UUID
);
```

---

# Foreign Key Rules

Foreign key wajib digunakan.

Contoh:

```sql
user_id UUID NOT NULL
```

```sql
FOREIGN KEY (user_id)
REFERENCES users(id)
```

---

# Unique Constraint

Gunakan unique constraint untuk data yang harus unik.

Contoh:

```sql
email
username
order_number
invoice_number
```

Example:

```sql
CREATE UNIQUE INDEX idx_users_email
ON users(email);
```

---

# Index Rules

Buat index untuk:

```text
Foreign Key
Search Column
Frequently Filtered Column
Frequently Sorted Column
```

Contoh:

```sql
CREATE INDEX idx_orders_user_id
ON orders(user_id);
```

---

# Composite Index

Digunakan jika query sering menggunakan lebih dari satu kolom.

Contoh:

```sql
CREATE INDEX idx_orders_status_created_at
ON orders(status, created_at);
```

---

# Data Type Standard

## UUID

```sql
UUID
```

---

## Text

Short Text

```sql
VARCHAR(255)
```

Long Text

```sql
TEXT
```

---

## Number

Integer

```sql
INTEGER
```

Large Number

```sql
BIGINT
```

Decimal

```sql
NUMERIC(18,2)
```

---

## Date

```sql
TIMESTAMP
```

Gunakan UTC.

---

## Boolean

```sql
BOOLEAN
```

---

# Soft Delete Standard

Default:

```text
Use Soft Delete
```

Column:

```sql
deleted_at
deleted_by
```

Data tidak langsung dihapus.

---

# Hard Delete Rule

Hard delete hanya diperbolehkan untuk:

```text
Temporary Data
Cache Data
Log Cleanup
```

---

# Migration Rules

Semua perubahan schema wajib menggunakan migration.

Dilarang:

```text
Manual Database Changes
```

Production database tidak boleh diubah langsung.

---

# Migration Naming

Format:

```text
YYYYMMDDHHMMSS_description
```

Contoh:

```text
202610211530_create_users_table
```

---

# Repository Pattern

Database hanya boleh diakses melalui:

```text
Repository Layer
```

Allowed:

```text
Handler
 ↓
Service
 ↓
Repository
 ↓
Database
```

Forbidden:

```text
Handler
 ↓
Database
```

---

# Transaction Rules

Gunakan transaction jika:

```text
Lebih dari satu table
Financial Process
Order Process
Inventory Update
```

Contoh:

```text
Create Order
↓
Create Order Item
↓
Deduct Stock
```

Harus dalam satu transaction.

---

# Query Rules

Allowed:

```go
db.Where("email = ?", email)
```

Forbidden:

```go
fmt.Sprintf(
 "SELECT * FROM users WHERE email='%s'",
 email,
)
```

---

# Pagination Standard

Semua list endpoint wajib menggunakan:

```text
page
limit
sort
search
```

Default:

```text
page=1
limit=20
```

Maximum:

```text
limit=100
```

---

# Lookup Tables

Gunakan lookup table untuk data master.

Contoh:

```text
roles
permissions
statuses
categories
```

Jangan hardcode di source code.

---

# Database Performance

Query harus:

```text
Indexed
Limited
Optimized
```

Tidak boleh:

```sql
SELECT * FROM huge_table
```

tanpa kebutuhan.

---

# N+1 Query Prevention

Backend Agent wajib:

```text
Use Preload
Use Join
Optimize Queries
```

Hindari:

```text
Loop Query Pattern
```

---

# Backup Rules

Frequency:

```text
Daily
```

Retention:

```text
7 Days
```

Backup File:

```text
Compressed
Timestamped
```

Format:

```text
postgres_backup_YYYYMMDD.sql.gz
```

---

# Restore Testing

Minimal:

```text
1x per month
```

Harus dipastikan backup dapat direstore.

---

# Security Rules

Database credential wajib disimpan di:

```text
.env
```

Dilarang:

```text
Hardcoded Credentials
```

---

# Environment Variables

Example:

```env
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
```

---

# Logging Rules

Log:

```text
Query Error
Transaction Error
Migration Error
```

Jangan log:

```text
Passwords
Tokens
Sensitive Data
```

---

# AI Agent Rules

Backend Agent wajib:

- Membuat migration
- Membuat index
- Membuat foreign key
- Membuat repository
- Membuat transaction jika diperlukan
- Menggunakan UUID

Backend Agent dilarang:

- Hard delete tanpa alasan
- Query langsung dari handler
- Hardcode SQL tanpa parameter
- Membuat table tanpa audit column

---

# Database Review Checklist

Table Naming

```text
[ ] Passed
```

Audit Columns

```text
[ ] Passed
```

Index

```text
[ ] Passed
```

Foreign Key

```text
[ ] Passed
```

Migration

```text
[ ] Passed
```

Repository Pattern

```text
[ ] Passed
```

Transaction

```text
[ ] Passed
```

Backup

```text
[ ] Passed
```

---

# Golden Rules

Every database change must be:

```text
Reversible
Auditable
Indexed
Documented
```

If not:

```text
DO NOT MERGE
```