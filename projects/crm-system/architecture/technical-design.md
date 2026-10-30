# Technical Design Document

## Customer Management Feature — CRM System

---

## 1. Executive Summary

### 1.1 Business Objective
Centralize customer data management into a single authoritative web application, replacing distributed Excel files across departments. The solution must eliminate duplicate records (80% reduction target), enable sub-5-second search across 10,000+ records, and support customer creation in under 1 minute — all while operating within a constrained VPS environment (2 CPU / 2 GB RAM).

### 1.2 Technical Direction
A **monolithic backend** (Go/Gin/GORM/PostgreSQL) serving a **React/TypeScript/Tailwind SPA** with **JWT-based authentication**. The architecture prioritizes:
- **Resource efficiency** — Single process, connection pooling, optimized queries
- **Operational simplicity** — Docker Compose deployment, single binary, minimal moving parts
- **Extensibility** — Clean domain boundaries, interface-driven design for future modules
- **Performance-first** — Indexing strategy, pagination, debounced search, soft-delete filtering at query level

### 1.3 Architecture Summary
| Layer | Technology | Deployment |
|-------|------------|------------|
| **Frontend** | React 18, TypeScript, Tailwind CSS, TanStack Query, React Hook Form, Zod | Nginx static serve + reverse proxy |
| **Backend** | Go 1.22, Gin, GORM v2, PostgreSQL 16 | Single Go binary in Docker container |
| **Database** | PostgreSQL 16 (single instance) | Docker container with volume persistence |
| **Auth** | JWT (HS256), 30-min access / 7-day refresh | Stateless, middleware-based |
| **Infrastructure** | Docker Compose, Nginx | Single VPS (2 CPU / 2 GB RAM) |

---

## 2. Architecture Overview

### 2.1 Layer Responsibilities

```text
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                           │
│  React SPA (Admin + Manager interfaces)                         │
│  - State: TanStack Query (server), React Context (auth/UI)      │
│  - Forms: React Hook Form + Zod (client validation mirror)      │
│  - Routing: React Router v6                                     │
└─────────────────────────────────────────────────────────────────┘
                                │ HTTPS / JSON
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER (Gin)                         │
│  - Routing, Middleware (Auth, Logging, Recovery, CORS)          │
│  - Request/Response DTOs, Validation                            │
│  - Error Handling (standardized envelope)                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BUSINESS SERVICES LAYER                    │
│  - Customer Service (CRUD, Search, Duplicate Detection)         │
│  - Auth Service (Login, Refresh, Token Validation)              │
│  - Domain Events (for future audit/integration)                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PERSISTENCE LAYER (GORM)                   │
│  - Repository Interfaces + GORM Implementations                 │
│  - Connection Pool (tuned for 2GB RAM)                          │
│  - Migrations (GORM AutoMigrate + versioned SQL)                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│  - PostgreSQL 16 (primary + WAL)                                │
│  - Nginx (TLS termination, static assets, rate limiting)        │
│  - Docker Compose (orchestration, health checks, restart)       │
│  - Log Aggregation (stdout → Loki/Grafana or file rotation)     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Request Flow (Search Example)
```text
User types in Global Search (Frontend)
        │
        ▼
Debounce 300ms → GET /api/v1/customers?q=john&page=1&size=20
        │
        ▼
Nginx: TLS termination, rate limit (100 req/min/IP), proxy to :8080
        │
        ▼
Gin: JWT validation → Role check (Admin/Manager) → Request DTO binding
        │
        ▼
CustomerService.Search(ctx, params)
        │
        ▼
CustomerRepository.Search(ctx, params) → GORM query with:
        │   - ILIKE on name, company, email, phone (trigram index)
        │   - WHERE deleted_at IS NULL
        │   - ORDER BY created_at DESC
        │   - LIMIT 20 OFFSET 0
        ▼
PostgreSQL: Bitmap index scan → Return 20 rows + total count
        │
        ▼
Service: Map to Response DTOs → Return to Handler
        │
        ▼
Handler: JSON envelope { data: [], meta: { total, page, size } }
        │
        ▼
Frontend: TanStack Query caches → Renders Customer Cards/Table
```

---

## 3. High-Level Architecture

### 3.1 System Context Diagram
```text
┌──────────────┐     HTTPS      ┌──────────────┐
│   Admin      │◄──────────────►│              │
│   Manager    │                │   Nginx      │
│   (Browser)  │                │   (TLS,      │
└──────────────┘                │   Rate Limit,│
                                │   Static)    │
                                └──────┬───────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │  Go/Gin API  │
                                │  (Port 8080) │
                                └──────┬───────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
             ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
             │ PostgreSQL  │   │  File Logs  │   │  (Future)   │
             │  (Port 5432)│   │  (stdout)   │   │  Redis      │
             └─────────────┘   └─────────────┘   │  (Cache)    │
                                                 └─────────────┘
```

### 3.2 Deployment Topology (Single VPS)
```text
VPS (2 CPU / 2 GB RAM)
├── Docker Engine
│   ├── nginx:alpine (128 MB limit)
│   │   ├── Port 80 → 443 redirect
│   │   ├── Port 443 → TLS termination
│   │   ├── /var/www/static → React build
│   │   └── /api/* → proxy_pass http://backend:8080
│   │
│   ├── backend:latest (Go binary, 512 MB limit)
│   │   ├── Port 8080 (internal)
│   │   ├── Env: DB_DSN, JWT_SECRET, LOG_LEVEL
│   │   ├── Health: GET /healthz
│   │   └── Depends on: postgres
│   │
│   └── postgres:16-alpine (1 GB limit)
│       ├── Port 5432 (internal)
│       ├── Volume: pgdata → /var/lib/postgresql/data
│       ├── Config: shared_buffers=256MB, work_mem=4MB, max_connections=100
│       └── Health: pg_isready
│
├── /opt/crm/backups (daily pg_dump cron)
└── /var/log/crm (nginx + app logs with rotation)
```

### 3.3 Resource Allocation Strategy
| Component | CPU Limit | Memory Limit | Rationale |
|-----------|-----------|--------------|-----------|
| **PostgreSQL** | 1.0 CPU | 1024 MB | Primary consumer; shared_buffers=256MB, effective_cache_size=768MB |
| **Backend (Go)** | 0.5 CPU | 512 MB | Gin + GORM lightweight; connection pool = 20 |
| **Nginx** | 0.25 CPU | 128 MB | Static serve + proxy; minimal footprint |
| **System/Buffer** | 0.25 CPU | 384 MB | OS, Docker overhead, log rotation, backup processes |

> **Total**: ~2 CPU / ~2 GB — fits VPS with headroom for backup spikes.

---

## 4. Domain Design

### 4.1 Domain: Customer Management
| Aspect | Definition |
|--------|------------|
| **Domain Name** | Customer Management |
| **Responsibilities** | Customer lifecycle (CRUD), search, duplicate detection, soft delete/restore |
| **Business Boundaries** | Owns Customer entity and all direct attributes. Does NOT own: interactions, campaigns, analytics, loyalty, integrations. |
| **Dependencies** | Auth Domain (for actor context), Audit Domain (future, for change tracking) |
| **Ubiquitous Language** | Customer, Admin, Manager, Soft Delete, Duplicate Match, CUST-ID |

### 4.2 Domain: Authentication & Authorization
| Aspect | Definition |
|--------|------------|
| **Domain Name** | Authentication & Authorization |
| **Responsibilities** | User login, JWT issuance/validation, role enforcement (Admin/Manager), session management |
| **Business Boundaries** | Owns User credentials, roles, tokens. Does NOT own: customer data, business logic. |
| **Dependencies** | None (foundational) |
| **Ubiquitous Language** | Access Token, Refresh Token, Role, Permission, Session |

### 4.3 Domain: Audit (Future-Ready)
| Aspect | Definition |
|--------|------------|
| **Domain Name** | Audit |
| **Responsibilities** | Immutable event log for Create/Update/Delete on Customer (and future entities) |
| **Business Boundaries** | Owns AuditEvent entity. Subscribes to domain events from Customer, Auth domains. |
| **Dependencies** | Customer Domain (events), Auth Domain (actor identity) |
| **Ubiquitous Language** | Audit Event, Actor, Action, Field Changes, Timestamp |

---

## 5. Module Design

### 5.1 Backend Modules (Go Package Structure)
```text
internal/
├── module/
│   ├── customer/                 # Customer Domain
│   │   ├── domain/
│   │   │   ├── entity.go         # Customer struct + methods
│   │   │   ├── repository.go     # Repository interface
│   │   │   ├── service.go        # Service interface
│   │   │   └── events.go         # Domain events (Created, Updated, Deleted)
│   │   ├── repository/
│   │   │   └── gorm_repo.go      # GORM implementation
│   │   ├── service/
│   │   │   └── service.go        # Business logic implementation
│   │   ├── handler/
│   │   │   └── handler.go        # HTTP handlers (Gin)
│   │   ├── dto/
│   │   │   ├── request.go        # Request DTOs + validation tags
│   │   │   └── response.go       # Response DTOs
│   │   └── routes.go             # Route registration
│   │
│   ├── auth/                     # Auth Domain
│   │   ├── domain/
│   │   │   ├── entity.go         # User, Role
│   │   │   ├── repository.go
│   │   │   └── service.go
│   │   ├── repository/
│   │   │   └── gorm_repo.go
│   │   ├── service/
│   │   │   └── service.go        # Login, Refresh, Validate, Hash
│   │   ├── handler/
│   │   │   └── handler.go
│   │   ├── dto/
│   │   └── middleware/
│   │       └── auth.go           # JWT validation, role check
│   │
│   └── audit/                    # Audit Domain (Phase 2 scaffold)
│       ├── domain/
│       ├── repository/
│       └── subscriber.go         # Listens to domain events
│
├── platform/                     # Cross-cutting concerns
│   ├── database/
│   │   ├── postgres.go           # GORM init, connection pool tuning
│   │   └── migrations/           # Versioned SQL migrations
│   ├── logger/
│   │   └── zap.go                # Structured logging (Zap)
│   ├── errors/
│   │   └── app_error.go          # Standardized error types
│   ├── validator/
│   │   └── validator.go          # Custom validators (phone, email, etc.)
│   └── middleware/
│       ├── logging.go            # Request/Response logging
│       ├── recovery.go           # Panic recovery
│       ├── cors.go
│       └── rate_limit.go         # IP-based rate limiting
│
├── config/
│   └── config.go                 # Viper-based config (env + file)
│
└── main.go                       # App bootstrap, DI wiring
```

### 5.2 Frontend Modules (React Feature Structure)
```text
src/
├── features/
│   ├── customers/                # Customer Feature
│   │   ├── api/
│   │   │   ├── customerApi.ts    # TanStack Query hooks + Axios calls
│   │   │   └── types.ts          # TypeScript interfaces (match backend DTOs)
│   │   ├── components/
│   │   │   ├── CustomerTable.tsx     # Desktop list
│   │   │   ├── CustomerCard.tsx      # Tablet/Mobile list
│   │   │   ├── CustomerForm.tsx      # Create/Edit (shared)
│   │   │   ├── CustomerDetail.tsx    # Detail view
│   │   │   ├── DuplicateModal.tsx    # SC-06
│   │   │   ├── DeleteConfirmModal.tsx # SC-05
│   │   │   └── ConcurrentEditModal.tsx # SC-07
│   │   ├── hooks/
│   │   │   ├── useCustomers.ts       # Search, pagination, infinite query
│   │   │   ├── useCustomer.ts        # Single customer (detail)
│   │   │   └── useCustomerMutations.ts # Create, Update, Delete
│   │   ├── pages/
│   │   │   ├── CustomerListPage.tsx  # SC-01
│   │   │   ├── CreateCustomerPage.tsx # SC-02
│   │   │   ├── CustomerDetailPage.tsx # SC-03
│   │   │   └── EditCustomerPage.tsx  # SC-04
│   │   ├── validation/
│   │   │   └── customerSchema.ts     # Zod schemas (mirror backend)
│   │   └── index.ts
│   │
│   └── auth/
│       ├── api/
│       ├── components/
│       ├── hooks/
│       └── context/
│           └── AuthContext.tsx       # JWT storage, refresh, role
│
├── shared/
│   ├── components/           # Design system (Button, Input, Modal, Table, Card, etc.)
│   ├── hooks/                # useDebounce, useLocalStorage, etc.
│   ├── utils/                # formatPhone, formatDate, cn (clsx), etc.
│   ├── constants/            # Roles, CustomerTypes, Statuses
│   └── styles/               # Tailwind config, global CSS
│
├── app/
│   ├── routes.tsx            # React Router config (role-based)
│   ├── layout/
│   │   ├── Header.tsx        # Global search, user menu
│   │   ├── Sidebar.tsx       # Navigation
│   │   └── MainLayout.tsx
│   └── providers/
│       └── QueryProvider.tsx # TanStack Query + Axios interceptors
│
└── main.tsx                  # Entry point
```

### 5.3 Module Relationships & Dependencies
```text
Backend Dependency Graph:
main.go
  ├── config
  ├── platform/database → postgres
  ├── platform/logger
  ├── platform/validator
  ├── module/auth
  │   ├── domain
  │   ├── repository → platform/database
  │   ├── service → domain, repository
  │   ├── handler → service, dto
  │   └── middleware → domain, platform/errors
  ├── module/customer
  │   ├── domain
  │   ├── repository → platform/database
  │   ├── service → domain, repository, auth/domain (actor)
  │   ├── handler → service, dto, platform/errors
  │   └── routes → handler, auth/middleware
  └── module/audit (future)
      └── subscriber → customer/domain/events, auth/domain

Frontend Dependency Graph:
main.tsx
  ├── app/providers/QueryProvider → Axios (baseURL, interceptors)
  ├── app/routes → features/*/pages
  ├── features/auth/context/AuthContext → localStorage, features/auth/api
  ├── features/customers
  │   ├── pages → components, hooks, validation
  │   ├── hooks → api, types
  │   ├── api → shared/utils (format), types
  │   └── components → shared/components, hooks
  └── shared/components → Tailwind, Radix UI primitives (if used)
```

---

## 6. Database Strategy

### 6.1 Core Business Entities

#### 6.1.1 Customer (Primary Entity)
| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | BIGSERIAL | PK, Unique | Internal surrogate key |
| customer_id | VARCHAR(20) | Unique, Not Null | Business key: CUST-YYYY-NNNNNN |
| full_name | VARCHAR(200) | Not Null | Primary display field |
| company_name | VARCHAR(200) | Nullable | |
| primary_phone | VARCHAR(20) | Not Null | E.164 normalized |
| secondary_phone | VARCHAR(20) | Nullable | E.164 normalized |
| primary_email | VARCHAR(254) | Not Null | Lowercase, RFC 5322 |
| secondary_email | VARCHAR(254) | Nullable | Lowercase |
| address_line1 | VARCHAR(200) | Nullable | |
| address_line2 | VARCHAR(200) | Nullable | |
| city | VARCHAR(100) | Nullable | |
| state_province | VARCHAR(100) | Nullable | |
| postal_code | VARCHAR(20) | Nullable | |
| country | CHAR(2) | Nullable | ISO 3166-1 alpha-2 |
| customer_type | VARCHAR(20) | Not Null, Default 'Individual' | Enum: Individual, Business, Government, Other |
| status | VARCHAR(20) | Not Null, Default 'Active' | Enum: Active, Deleted |
| notes | TEXT | Nullable | Max 2000 chars (CHECK constraint) |
| created_at | TIMESTAMPTZ | Not Null, Default now() | |
| created_by | BIGINT | Not Null, FK → users(id) | Admin who created |
| updated_at | TIMESTAMPTZ | Not Null, Default now() | Auto-updated by trigger |
| updated_by | BIGINT | Nullable, FK → users(id) | Admin who last updated |
| deleted_at | TIMESTAMPTZ | Nullable | Soft delete marker |
| deleted_by | BIGINT | Nullable, FK → users(id) | Admin who deleted |
| version | BIGINT | Not Null, Default 1 | Optimistic locking |

#### 6.1.2 User (Auth Entity)
| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | BIGSERIAL | PK | |
| username | VARCHAR(50) | Unique, Not Null | Login identifier |
| password_hash | VARCHAR(255) | Not Null | bcrypt cost 12 |
| full_name | VARCHAR(200) | Not Null | Display name |
| email | VARCHAR(254) | Unique, Not Null | |
| role | VARCHAR(20) | Not Null | Enum: Admin, Manager |
| is_active | BOOLEAN | Not Null, Default true | |
| last_login_at | TIMESTAMPTZ | Nullable | |
| created_at | TIMESTAMPTZ | Not Null, Default now() | |
| updated_at | TIMESTAMPTZ | Not Null, Default now() | |

#### 6.1.3 Audit Event (Future Entity - Scaffolded)
| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | BIGSERIAL | PK | |
| entity_type | VARCHAR(50) | Not Null | e.g., 'Customer' |
| entity_id | BIGINT | Not Null | Customer.id |
| action | VARCHAR(20) | Not Null | CREATE, UPDATE, DELETE, RESTORE |
| actor_id | BIGINT | Not Null, FK → users(id) | |
| actor_role | VARCHAR(20) | Not Null | Snapshot at event time |
| field_changes | JSONB | Nullable | {field: {old, new}} for UPDATE |
| metadata | JSONB | Nullable | IP, User-Agent, Request ID |
| created_at | TIMESTAMPTZ | Not Null, Default now() | Partition by month (future) |

### 6.2 Entity Relationships
```text
User (1) ──────< (N) Customer
  │                    │
  │ created_by         │ created_by
  │ updated_by         │ updated_by
  │ deleted_by         │ deleted_by
  ▼                    ▼
(All FKs nullable except created_by)
```

### 6.3 Data Ownership
| Entity | Owner Domain | Write Access | Read Access |
|--------|--------------|--------------|-------------|
| Customer | Customer Management | Customer Service only | Customer Service, Audit Subscriber |
| User | Authentication | Auth Service only | Auth Service, Customer Service (for FK resolution) |
| Audit Event | Audit | Audit Subscriber only | Audit Service (future), Admin UI (future) |

### 6.4 Transaction Boundaries
| Operation | Transaction Scope | Isolation Level | Notes |
|-----------|-------------------|-----------------|-------|
| Create Customer | Single (Customer insert + Audit event) | READ COMMITTED | Duplicate check outside TX (read-only) |
| Update Customer | Single (Customer update + Audit event) | READ COMMITTED | Optimistic lock via version column |
| Soft Delete Customer | Single (Customer update + Audit event) | READ COMMITTED | |
| Search Customer | Read-only | READ COMMITTED | No transaction needed (SELECT only) |
| Login | Read-only (User lookup) | READ COMMITTED | bcrypt verify outside TX |

### 6.5 Data Retention Strategy
| Data Category | Retention Policy | Disposal Method |
|---------------|------------------|-----------------|
| Active Customers | Indefinite (business asset) | N/A |
| Soft-Deleted Customers | 90 days (configurable) | Background job: hard delete where deleted_at < now() - 90 days |
| Audit Events | 7 years (compliance-ready) | Partition by month; drop partitions > 7 years |
| Application Logs | 30 days (operational) | Log rotation (daily, compress, max 30 files) |
| Database Backups | 30 days (daily), 12 months (monthly) | pg_dump to /opt/crm/backups; S3 sync (future) |

### 6.6 Audit Strategy
- **MVP**: Capture `created_by`, `updated_by`, `deleted_by`, timestamps on Customer entity (already in schema)
- **Phase 2**: Enable `audit_event` table via domain event subscriber
- **Event Payload**: `{ entity_type, entity_id, action, actor_id, actor_role, field_changes?, metadata? }`
- **Delivery**: In-process async (goroutine) for MVP; message queue (Redis Streams) if scale demands

---

## 7. API Strategy

### 7.1 Primary Resources
| Resource | Path | Description |
|----------|------|-------------|
| Customers | `/api/v1/customers` | Collection resource for search, create |
| Customer | `/api/v1/customers/{id}` | Single resource (by internal `id`, not `customer_id`) |
| Customer by Business Key | `/api/v1/customers/by-key/{customer_id}` | Lookup by CUST-ID (for sharing) |
| Auth | `/api/v1/auth` | Login, refresh, me |

### 7.2 Business Operations Mapping
| Business Operation | HTTP Method | Endpoint | Auth Required | Roles Allowed |
|--------------------|-------------|----------|---------------|---------------|
| Create Customer | POST | `/api/v1/customers` | Yes | Admin |
| Search Customers | GET | `/api/v1/customers` | Yes | Admin, Manager |
| Get Customer Detail | GET | `/api/v1/customers/{id}` | Yes | Admin, Manager |
| Get Customer by CUST-ID | GET | `/api/v1/customers/by-key/{customer_id}` | Yes | Admin, Manager |
| Update Customer | PATCH | `/api/v1/customers/{id}` | Yes | Admin |
| Soft Delete Customer | DELETE | `/api/v1/customers/{id}` | Yes | Admin |
| Restore Customer (Future) | POST | `/api/v1/customers/{id}/restore` | Yes | Admin |
| Login | POST | `/api/v1/auth/login` | No | - |
| Refresh Token | POST | `/api/v1/auth/refresh` | Yes (Refresh) | Admin, Manager |
| Get Current User | GET | `/api/v1/auth/me` | Yes | Admin, Manager |

### 7.3 Authentication Requirements
- **Mechanism**: JWT in Authorization header (`Bearer <access_token>`)
- **Access Token**: 30 minutes, HS256, claims: `sub` (user_id), `role`, `exp`, `iat`, `jti`
- **Refresh Token**: 7 days, stored hashed in DB (revocable), rotated on use
- **Token Refresh**: Silent refresh at 25 min (client-side); intercept 401 → refresh → retry
- **Logout**: Client clears tokens; server adds refresh token jti to blocklist (Redis or DB table)

### 7.4 Authorization Requirements
| Role | Customers (CRUD) | Customers (Search/Read) | Auth (Self) | Admin Users (Future) |
|------|------------------|-------------------------|-------------|----------------------|
| **Admin** | ✅ Create, Update, Delete | ✅ | ✅ | ✅ |
| **Manager** | ❌ | ✅ | ✅ | ❌ |

- **Enforcement**: Middleware extracts claims → `role` check per route group
- **Resource-level**: Not required in MVP (no department ownership)

### 7.5 Search Strategy
- **Endpoint**: `GET /api/v1/customers?q={query}&page={n}&size={n}&sort={field}&order={asc|desc}`
- **Query Parameter `q`**: Single string, searched across: `full_name`, `company_name`, `primary_phone`, `secondary_phone`, `primary_email`, `secondary_email`, `customer_id`, `city`
- **Matching**: PostgreSQL `pg_trgm` (trigram) for fuzzy/partial on text fields; exact/prefix on phone/email/id
- **Ranking**: Exact matches first (customer_id, email, phone), then trigram similarity on name/company
- **Performance Target**: p95 < 500ms DB time for 10K records (total < 5s including network)

### 7.6 Pagination Strategy
- **Style**: Offset-based (simple, predictable for UI)
- **Parameters**: `page` (1-based, default 1), `size` (default 20, max 100)
- **Response Meta**: `{ total, page, size, total_pages }`
- **Cursor Alternative**: Deferred to Phase 2 if offset performance degrades > 50K records

### 7.7 Error Response Envelope (Standardized)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "primary_email", "code": "INVALID_FORMAT", "message": "Enter a valid email address" }
    ],
    "request_id": "req_abc123"
  }
}
```
| Error Code | HTTP Status | When |
|------------|-------------|------|
| `VALIDATION_ERROR` | 400 | Request body/query validation failed |
| `UNAUTHENTICATED` | 401 | Missing/invalid/expired access token |
| `FORBIDDEN` | 403 | Role not permitted for action |
| `NOT_FOUND` | 404 | Resource not found (or soft-deleted) |
| `CONFLICT` | 409 | Optimistic lock failure (version mismatch) |
| `DUPLICATE_DETECTED` | 409 | Duplicate warning (non-blocking, includes matches) |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 8. Security Design

### 8.1 Authentication Strategy
| Aspect | Implementation |
|--------|----------------|
| **Credential Storage** | bcrypt (cost 12) for passwords; never logged |
| **Token Format** | JWT (HS256) — symmetric key from env `JWT_SECRET` (32+ bytes) |
| **Access Token TTL** | 30 minutes |
| **Refresh Token TTL** | 7 days; stored as hash in `user.refresh_token_hash`; rotated on use |
| **Token Revocation** | Refresh token blocklist (in-memory map with TTL cleanup; Redis in Phase 2) |
| **Session Management** | Stateless; no server-side session store |
| **Password Policy** | Min 12 chars, 1 upper, 1 lower, 1 digit, 1 special (enforced at registration) |
| **Brute Force Protection** | Rate limit login: 5 attempts/min/IP; account lockout after 10 failures (15 min) |

### 8.2 Authorization Strategy
| Layer | Mechanism |
|-------|-----------|
| **Transport** | TLS 1.2+ (Nginx termination, Let's Encrypt certs) |
| **API Gateway** | Nginx rate limit: 100 req/min/IP (burst 20); 10 req/min for auth endpoints |
| **Application** | JWT middleware validates signature, expiry, `jti` not in blocklist |
| **Route-Level** | Gin route groups with role middleware: `RequireRole("Admin")` |
| **Resource-Level** | Not in MVP (single-tenant, org-wide data) |

### 8.3 Validation Strategy
| Layer | Responsibility |
|-------|----------------|
| **Frontend (Zod)** | Immediate UX feedback; mirrors backend rules; prevents unnecessary requests |
| **Backend (DTO + Validator)** | Source of truth; struct tags + custom validators (phone E.164, email RFC 5322, customer_id format) |
| **Database** | CHECK constraints (notes length, enum values), NOT NULL, UNIQUE, FK |
| **Business Rules** | Service layer (duplicate detection, soft-delete filters, optimistic lock) |

### 8.4 Audit Strategy
| Event | Captured Fields | Storage |
|-------|-----------------|---------|
| **Customer Created** | actor_id, actor_role, customer_id, all field values | Customer entity (created_by, created_at) + AuditEvent (Phase 2) |
| **Customer Updated** | actor_id, actor_role, customer_id, changed fields (old/new) | Customer entity (updated_by, updated_at) + AuditEvent (Phase 2) |
| **Customer Deleted** | actor_id, actor_role, customer_id | Customer entity (deleted_by, deleted_at) + AuditEvent (Phase 2) |
| **Login/Logout** | actor_id, ip, user_agent, success/failure | Auth audit log (separate table, Phase 2) |

### 8.5 Sensitive Data Handling
| Data | At Rest | In Transit | In Logs | In Memory |
|------|---------|------------|---------|-----------|
| **Password Hash** | bcrypt (irreversible) | N/A (never transmitted) | **Never** | Only during verify |
| **JWT Secret** | Env var (file) | N/A | **Never** | Loaded at startup |
| **Refresh Token Hash** | bcrypt in DB | HTTPS only | **Never** | Only during rotate |
| **Customer PII** | Plaintext (PostgreSQL) | TLS 1.2+ | **Masked** (email: j***@domain.com, phone: +1****4567) | Go structs (GC managed) |
| **Database Credentials** | Docker secrets / env file | N/A | **Never** | Loaded at startup |

> **Log Masking**: Middleware scrubs `Authorization` header, `password` fields, `refresh_token` from request/response logs.

---

## 9. Logging Strategy

### 9.1 Log Levels & Sampling
| Level | Usage | Sampling |
|-------|-------|----------|
| **DEBUG** | Detailed flow (SQL params, cache hits) | Disabled in prod (env `LOG_LEVEL=info`) |
| **INFO** | Request/Response (method, path, status, latency, user_id, request_id) | 100% |
| **WARN** | Validation failures, duplicate warnings, rate limit hits, slow queries (>1s) | 100% |
| **ERROR** | Unhandled errors, DB connection failures, panic recovery | 100% + alert |

### 9.2 Structured Log Format (JSON)
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "info",
  "logger": "http",
  "message": "HTTP request completed",
  "request_id": "req_abc123",
  "method": "GET",
  "path": "/api/v1/customers",
  "query": "q=john&page=1&size=20",
  "status": 200,
  "latency_ms": 42,
  "user_id": 5,
  "user_role": "Admin",
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

### 9.3 Log Categories

#### 9.3.1 Application Logs
- **Source**: Backend (Zap logger), Frontend (console → log aggregation)
- **Content**: Request/response, business events (create/update/delete), errors
- **Retention**: 30 days (stdout → Loki or file rotation)
- **Key Fields**: `request_id`, `user_id`, `trace_id` (future distributed tracing)

#### 9.3.2 Audit Logs
- **Source**: Domain event subscriber (Phase 2) or service layer (MVP: Customer entity fields)
- **Content**: Who did what to which customer, when, field changes
- **Retention**: 7 years (regulatory readiness)
- **Storage**: `audit_events` table (partitioned by month)

#### 9.3.3 Security Logs
- **Source**: Auth middleware, rate limiter, login handler
- **Content**: Login success/failure, token refresh, blocked IPs, permission denials, password changes
- **Retention**: 1 year
- **Alerting**: Failed login burst (>10/min), token reuse detection, privilege escalation attempts

#### 9.3.4 Error Logs
- **Source**: Recovery middleware, database errors, external call failures
- **Content**: Stack trace, request context, error code, user impact
- **Retention**: 90 days
- **Alerting**: Error rate > 1% over 5 min; any `INTERNAL_ERROR` on critical paths

### 9.4 Correlation & Traceability
- **Request ID**: Generated at Nginx (`$request_id`) → passed via `X-Request-ID` header → logged by backend
- **Trace ID**: Future (OpenTelemetry); for now, `request_id` suffices for single-service tracing

---

## 10. Integration Strategy

### 10.1 Internal Integrations
| Integration | Pattern | Protocol | Description |
|-------------|---------|----------|-------------|
| **Frontend ↔ Backend** | Request/Response | HTTPS/JSON | SPA calls REST API; TanStack Query manages cache |
| **Backend ↔ Database** | Synchronous | PostgreSQL Wire Protocol | GORM connection pool (20 connections) |
| **Backend ↔ Auth (Self)** | In-process | Function Call | Auth middleware validates JWT; service calls auth repo for user lookup |
| **Domain Events (Future)** | Async (In-process) | Go Channels | Customer service emits events → Audit subscriber consumes |

### 10.2 External Dependencies
| Dependency | Type | Criticality | Fallback |
|------------|------|-------------|----------|
| **PostgreSQL** | Infrastructure | Critical | None (single VPS); backup/restore documented |
| **Nginx** | Infrastructure | Critical | None; static files served directly by Go if needed |
| **Let's Encrypt / Cert Manager** | External Service | High | Manual cert renewal (90-day cycle); calendar reminder |
| **Time (NTP)** | System | High | VPS provider NTP; app uses `time.Now()` |
| **DNS** | External | Medium | `/etc/hosts` override for local dev |

### 10.3 Communication Patterns
| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| **Synchronous Request/Response** | All CRUD, Search, Auth | Gin handlers → Service → Repository → DB |
| **Async Event Emission** | Audit logging, future notifications | Go goroutine + channel (non-blocking); fire-and-forget |
| **Polling (Frontend)** | Not used | TanStack Query refetch on window focus / manual trigger |
| **WebSocket / SSE** | Not in MVP | Deferred to Phase 2 (real-time updates) |

---

## 11. Non-Functional Requirements

### 11.1 Performance
| NFR ID | Requirement | Target | Implementation Approach |
|--------|-------------|--------|-------------------------|
| **NFR-01** | Search p95 latency | < 5 seconds (end-to-end) | pg_trgm indexes, debounced 300ms, limit 20, connection pool |
| **NFR-02** | Customer creation p95 | < 1 minute (end-to-end) | Optimistic UI, single INSERT, async audit |
| **NFR-03** | Detail view load p95 | < 2 seconds | Single PK lookup, eager load created_by/updated_by names |
| **NFR-04** | Update p95 | < 1 minute | Single UPDATE with version check |
| **NFR-05** | Concurrent users | 50 simultaneous | Connection pool (20), Gin worker pool (GOMAXPROCS=2) |
| **NFR-06** | Database size Year 1 | ~10K active + 2K deleted | ~50 MB data + indexes; well within 2 GB RAM |

### 11.2 Availability
| NFR ID | Requirement | Target | Implementation Approach |
|--------|-------------|--------|-------------------------|
| **NFR-07** | Uptime (business hours) | > 99% | Single VPS; health checks; auto-restart; daily backups |
| **NFR-08** | Recovery Time Objective (RTO) | < 30 minutes | Documented restore procedure; pg_dump + binary redeploy |
| **NFR-09** | Recovery Point Objective (RPO) | < 24 hours | Daily automated pg_dump at 02:00 UTC |
| **NFR-10** | Planned Maintenance | Weekend, 2-hour max | Blue-green not feasible; deploy during low usage; DB migrations backward-compatible |

### 11.3 Reliability
| NFR ID | Requirement | Target | Implementation Approach |
|--------|-------------|--------|-------------------------|
| **NFR-11** | Data Durability | Zero committed data loss | PostgreSQL WAL (fsync=on), daily backups, replication not feasible on single VPS |
| **NFR-12** | Graceful Degradation | Read-only mode if DB write fails | Health endpoint checks DB write; Nginx can serve cached static |
| **NFR-13** | Idempotency | Create/Update safe to retry | Client generates idempotency key (future); for now, duplicate detection handles |

### 11.4 Scalability
| NFR ID | Requirement | Target | Implementation Approach |
|--------|-------------|--------|-------------------------|
| **NFR-14** | Record Capacity | 10K active + 2K deleted (Year 1) | Current schema + indexes sufficient |
| **NFR-15** | Growth Rate | 200 records/month | Linear; 5 years to 22K records — no schema change needed |
| **NFR-16** | Vertical Scale Headroom | 2x current load | Connection pool, query optimization, read replica (future, separate VPS) |
| **NFR-17** | Horizontal Scale | Not required (MVP) | Stateless backend → can run multiple replicas behind Nginx if CPU allows |

### 11.5 Maintainability
| NFR ID | Requirement | Target | Implementation Approach |
|--------|-------------|--------|-------------------------|
| **NFR-18** | Deployment | Zero-downtime (rolling) | Docker Compose `deploy: restart_policy` + health checks; Nginx upstream with multiple backends (future) |
| **NFR-19** | Observability | Logs, Metrics, Health | Structured JSON logs; `/healthz` (liveness), `/readyz` (readiness: DB ping); Prometheus metrics (future) |
| **NFR-20** | Code Quality | Lint, Test, Review | `golangci-lint`, `go test`, `go vet` in CI; 80% coverage on services |

### 11.6 Security
| NFR ID | Requirement | Target | Implementation Approach |
|--------|-------------|--------|-------------------------|
| **NFR-21** | Authentication | Required for all API | JWT middleware on all `/api/*` except `/auth/login`, `/auth/refresh` |
| **NFR-22** | Authorization | Role-based | Middleware checks `role` claim per route group |
| **NFR-23** | Input Validation | All boundaries | DTO validation + custom validators + DB constraints |
| **NFR-24** | Injection Prevention | SQL, XSS | GORM parameterized queries; React auto-escapes; CSP headers via Nginx |
| **NFR-25** | Secrets Management | No secrets in code | Docker secrets / `.env` file (gitignored); `JWT_SECRET` generated at deploy |

### 11.7 Observability
| NFR ID | Requirement | Target | Implementation Approach |
|--------|-------------|--------|-------------------------|
| **NFR-26** | Health Checks | Liveness + Readiness | `GET /healthz` (process alive), `GET /readyz` (DB reachable) |
| **NFR-27** | Metrics | Key business + system | Prometheus `/metrics` (future); for now: structured logs + Grafana Loki |
| **NFR-28** | Alerting | Critical failures | Log-based alerts (Loki/Grafana): error rate, slow queries, disk space, backup failure |

---

## 12. Risks

| Risk ID | Risk | Impact | Probability | Mitigation |
|---------|------|--------|-------------|------------|
| **TECH-01** | VPS memory pressure under load (PostgreSQL + Go + Nginx) | High | High | Strict memory limits (Docker); `shared_buffers=256MB`; `GOMEMLIMIT=400MiB`; monitor `container_memory_usage_bytes` |
| **TECH-02** | Search performance degrades beyond 10K records | High | Medium | pg_trgm + GIN indexes; `pg_stat_statements` monitoring; plan for read replica or Elasticsearch if >50K |
| **TECH-03** | Single point of failure (no HA) | High | Low | Daily backups + documented 30-min restore; VPS snapshot (provider); consider multi-AZ in Phase 2 |
| **TECH-04** | JWT secret rotation breaks active sessions | Medium | Low | Dual-secret support (current + previous); rotate via env reload without restart |
| **TECH-05** | GORM performance overhead vs raw SQL | Medium | Low | Use `Debug()` in dev; benchmark critical paths; drop to raw SQL for search if needed |
| **SEC-01** | Brute force on login endpoint | High | Medium | Rate limit (10/min/IP); account lockout; bcrypt cost 12; monitor security logs |
| **SEC-02** | XSS via customer notes field | Medium | Low | React auto-escapes; CSP header; sanitize on render if rich text ever added |
| **SEC-03** | SQL Injection via search query | High | Low | GORM uses parameterized queries; no raw SQL with user input |
| **OPS-01** | Backup failure goes unnoticed | High | Medium | Cron job with exit code check → alert on failure; weekly test restore |
| **OPS-02** | Disk space exhaustion (logs + DB + backups) | High | Medium | Log rotation (daily, 30 files); backup retention (30 daily + 12 monthly); `df` monitoring alert at 80% |
| **OPS-03** | Certificate expiry (Let's Encrypt) | High | Low | Certbot auto-renewal (systemd timer); monitor cert expiry (30-day alert) |
| **SCALE-01** | Connection pool exhaustion under burst | Medium | Medium | Pool size 20; queue timeout 5s; Nginx rate limit protects; monitor `pg_stat_activity` |
| **SCALE-02** | Nginx worker saturation | Low | Low | `worker_processes auto`; `worker_connections 1024`; static file caching |

---

## 13. Assumptions

### 13.1 Business Assumptions
| ID | Assumption | Validation |
|----|------------|------------|
| **BA-01** | 5,000 initial records + 200/month growth is accurate | Confirm with Operations Manager pre-dev |
| **BA-02** | Soft delete (90-day retention) satisfies compliance | Confirm with Legal/Compliance |
| **BA-03** | Admin/Manager roles cover all current user needs | Confirm with stakeholders; RBAC scaffolded for future |
| **BA-04** | No external system integration required for MVP | Confirmed in PRD (ASM-06) |
| **BA-05** | Responsive web satisfies Manager tablet use case | Confirm with Sales Manager (ASM-09) |

### 13.2 Operational Assumptions
| ID | Assumption | Validation |
|----|------------|------------|
| **OA-01** | VPS is dedicated to this application (no noisy neighbors) | Confirm with Infrastructure Team (ASM-07) |
| **OA-02** | Daily backup window (02:00 UTC) is acceptable | Confirm with Operations Manager |
| **OA-03** | Team can operate Docker Compose on VPS | Verify team skills; document runbooks |
| **OA-04** | Let's Encrypt certificates can be obtained for domain | Verify domain ownership / DNS control |

### 13.3 Technical Assumptions
| ID | Assumption | Validation |
|----|------------|------------|
| **TA-01** | Go/Gin/GORM/PostgreSQL stack supports required features | PoC validates (DEP-INT-01) |
| **TA-02** | pg_trgm provides sufficient fuzzy search performance | Benchmark with 5K records pre-dev |
| **TA-03** | 2 GB RAM sufficient for PostgreSQL + Go + Nginx + OS | Resource limits configured; monitor in PoC |
| **TA-04** | Single-threaded Go performance adequate (GOMAXPROCS=2) | Load test during PoC |
| **TA-05** | No WebSocket/SSE needed for MVP | Confirmed in PRD/UX |

---

## 14. Dependencies

### 14.1 Internal Dependencies
| ID | Dependency | Description | Blocking |
|----|------------|-------------|----------|
| **DEP-01** | Performance PoC | Architect validates search/create on target VPS with 5K records | **Yes** — Dev cannot start |
| **DEP-02** | Data Migration Plan | Operations Manager approves cleansing + migration approach | **Yes** — Launch blocked |
| **DEP-03** | UI/UX Design Approval | Product Owner + Operations Manager sign off on designs | **Yes** — Frontend dev blocked |
| **DEP-04** | Technical Architecture Approval | This document reviewed + approved | **Yes** — Backend/Frontend dev blocked |
| **DEP-05** | Test Environment | DevOps provisions staging VPS mirroring prod | **Yes** — QA blocked |

### 14.2 External Dependencies
| ID | Dependency | Owner | Risk |
|----|------------|-------|------|
| **EXT-01** | VPS Provisioning (2 CPU / 2 GB RAM, Ubuntu 22.04+) | Infrastructure Team | High — Delay blocks all |
| **EXT-02** | Domain + DNS Configuration | Infrastructure Team | Medium — Needed for TLS |
| **EXT-03** | Stakeholder UAT Availability | Operations/Sales Managers | Medium — Launch sign-off |

---

## 15. Architecture Decision Records

### ADR-001: Monolithic Backend vs Microservices
**Decision**: Single Go monolith for Customer Management MVP.

**Context**: Small team, simple domain (5 CRUD operations), VPS constraints (2 CPU/2GB), no external integrations.

**Options Considered**:
1. **Monolith (Selected)** — Single binary, shared DB, in-process calls, simple deployment
2. **Modular Monolith** — Separate packages with strict boundaries, same deployment
3. **Microservices** — Separate services (Customer, Auth, Audit), API Gateway, message queue

**Selected Option**: Monolith (Option 1) with modular package structure (Option 2 boundaries).

**Rationale**:
- Team size (2-3 devs) cannot operate distributed system
- VPS resources insufficient for multiple runtimes + message broker
- Domain is cohesive (single aggregate: Customer)
- Deployment complexity: 1 container vs 5+
- Latency: In-process vs network hops
- Future extraction path: Clean domain boundaries allow service extraction later

**Trade-offs**:
- ❌ No independent scaling of Auth vs Customer
- ❌ Single failure domain
- ✅ Operational simplicity
- ✅ Resource efficiency
- ✅ Development velocity

---

### ADR-002: Soft Delete via `deleted_at` Column vs Separate Archive Table
**Decision**: Soft delete using `deleted_at` timestamp on Customer table with partial indexes.

**Context**: Requirement for recoverable deletion (90-day retention), MVP simplicity.

**Options Considered**:
1. **`deleted_at` Column (Selected)** — Single table, partial indexes, simple queries
2. **Archive Table** — Move rows to `customer_archive` on delete
3. **Separate `is_deleted` Boolean** — Less info than timestamp

**Selected Option**: `deleted_at` TIMESTAMPTZ column + partial unique indexes.

**Rationale**:
- Simpler queries: `WHERE deleted_at IS NULL` on all reads
- Partial unique indexes: `CREATE UNIQUE INDEX ... WHERE deleted_at IS NULL` allows email reuse after delete
- Recovery: Single `UPDATE SET deleted_at=NULL` — no cross-table move
- Audit: `deleted_at` + `deleted_by` captures who/when
- Storage: 10K records negligible; no partition needed yet

**Trade-offs**:
- ❌ All queries must filter `deleted_at IS NULL` (enforced by GORM scopes)
- ❌ Unique constraints only on active records (by design)
- ✅ Zero migration complexity for restore
- ✅ Single table for reporting/analytics

---

### ADR-003: JWT (HS256) vs RS256 vs Session/Cookie
**Decision**: JWT with HS256 (symmetric) for MVP.

**Context**: Internal app, two roles, stateless preferred, VPS constraints.

**Options Considered**:
1. **HS256 JWT (Selected)** — Simple, stateless, single secret
2. **RS256 JWT** — Asymmetric, key rotation easier, more complex
3. **Session/Cookie** — Server-side store (Redis/DB), CSRF concerns, stateful

**Selected Option**: HS256 JWT with short access (30m) + rotating refresh tokens (7d).

**Rationale**:
- No Redis/DB session store needed (saves RAM)
- Stateless horizontal scaling ready
- HS256 sufficient for internal trusted network
- Refresh token rotation provides revocation capability
- Short access token limits exposure window

**Trade-offs**:
- ❌ Secret rotation requires dual-secret or forced re-login
- ❌ Cannot revoke access tokens instantly (mitigated by short TTL)
- ✅ Zero infrastructure for sessions
- ✅ Simple implementation (golang-jwt library)

---

### ADR-004: Offset Pagination vs Cursor Pagination
**Decision**: Offset-based pagination for MVP.

**Context**: 10K records, simple UI (page numbers), PostgreSQL performance acceptable.

**Options Considered**:
1. **Offset (Selected)** — `LIMIT 20 OFFSET 40`, simple UI, total count available
2. **Cursor** — `WHERE id > last_id`, no total count, better deep-page performance

**Selected Option**: Offset pagination with `page`/`size` params.

**Rationale**:
- UI requires page numbers and total count (per UX design)
- 10K records / 20 per page = 500 pages; offset performance fine with indexes
- Simpler frontend implementation (TanStack Query `keepPreviousData`)
- Cursor pagination adds complexity (no total, no jump-to-page)

**Trade-offs**:
- ❌ Deep page latency grows linearly (mitigated: users rarely go deep; search filters first)
- ✅ Familiar UX
- ✅ Total count for "Showing X of Y"
- ✅ Simpler API contract

---

### ADR-005: pg_trgm for Fuzzy Search vs Full-Text Search vs External Engine
**Decision**: PostgreSQL `pg_trgm` (trigram) indexes for fuzzy/partial search.

**Context**: Search across name, company, email, phone; 10K records; sub-5-second target; no external deps.

**Options Considered**:
1. **pg_trgm + GIN (Selected)** — Built-in, fuzzy/prefix, good for names
2. **PostgreSQL Full-Text Search (tsvector)** — Better for documents, not short fields
3. **Elasticsearch / Meilisearch** — Powerful, but extra infrastructure (RAM/CPU)

**Selected Option**: `pg_trgm` extension with GIN indexes on `full_name`, `company_name`, `primary_email`, `primary_phone`.

**Rationale**:
- Zero additional infrastructure
- Excellent for "john" → "John Smith", "Johnson Corp" (similarity search)
- `similarity()` function + `%` operator for threshold tuning
- GIN index fast for 10K rows (< 10ms)
- Combined with exact match on ID/phone/email for precision

**Trade-offs**:
- ❌ Not as powerful as Elasticsearch for complex queries
- ❌ Index size ~2-3x column size (acceptable at 10K)
- ✅ Native, transactional, no sync lag
- ✅ Tunable similarity threshold (0.3 default)

---

### ADR-006: Optimistic Locking via `version` Column
**Decision**: Integer `version` column incremented on each UPDATE; checked in WHERE clause.

**Context**: Concurrent edit protection (BR-013); low contention expected but must handle.

**Options Considered**:
1. **Version Column (Selected)** — Simple, no locks, application-level
2. **Timestamp (`updated_at`)** — Race condition on same-second updates
3. **Pessimistic Locking (`SELECT FOR UPDATE`)** — Holds row lock, reduces concurrency

**Selected Option**: `version BIGINT DEFAULT 1`; `UPDATE ... SET version = version + 1 WHERE id = ? AND version = ?`.

**Rationale**:
- Zero database locks
- Clear conflict detection (rows affected = 0 → `CONFLICT` error)
- Frontend can implement "Reload & Reapply" (per UX design SC-07)
- Minimal storage overhead

**Trade-offs**:
- ❌ Application must handle retry logic
- ✅ High throughput under contention
- ✅ No deadlock risk

---

### ADR-007: Duplicate Detection at Application Layer vs Database Constraint
**Decision**: Application-layer duplicate detection (service) with warning, not blocking constraint.

**Context**: BR-005/006/007 — Duplicate detection is advisory; Admin can override.

**Options Considered**:
1. **Application Layer (Selected)** — Configurable rules, warning UI, Admin decision
2. **Database UNIQUE Constraints** — Hard block, inflexible, no "proceed anyway"
3. **Hybrid** — Unique on email (hard), fuzzy on name (soft)

**Selected Option**: Application-layer with configurable matching rules; UNIQUE constraint only on `customer_id` and `primary_email` (where `deleted_at IS NULL`).

**Rationale**:
- Business rules require Admin judgment (BR-006: "Proceed Anyway")
- Fuzzy matching (name similarity) cannot be expressed in DB constraint
- Rules may evolve (threshold tuning) without migration
- UNIQUE on email prevents exact duplicates at DB level (safety net)

**Trade-offs**:
- ❌ Race condition: two Admins create same email simultaneously
- ✅ Mitigated: UNIQUE index on email catches this at DB level
- ✅ Flexible, configurable, user-friendly

---

### ADR-008: Docker Compose for Production Deployment
**Decision**: Docker Compose on single VPS for production.

**Context**: VPS constraints, small team, no Kubernetes expertise, simple topology.

**Options Considered**:
1. **Docker Compose (Selected)** — Declarative, single host, health checks, restart policies
2. **Systemd + Binary** — No container overhead, but manual process management
3. **Kubernetes (k3s)** — Overkill for 2 CPU/2GB; steep learning curve

**Selected Option**: Docker Compose v2 with resource limits, health checks, log rotation.

**Rationale**:
- Matches dev environment (dev/prod parity)
- Resource limits enforce NFR-11 (memory safety)
- Health checks enable auto-recovery
- Single `docker compose up -d` deploy
- Easy backup (volume snapshots)

**Trade-offs**:
- ❌ No rolling updates (single replica); brief downtime on deploy
- ❌ No multi-host scheduling
- ✅ Operational simplicity
- ✅ Resource control
- ✅ Team can debug with `docker compose logs`

---

## 16. Validation Checklist

| Checklist Item | Status | Notes |
|----------------|--------|-------|
| [x] Business goals covered | ✅ | Centralized data, duplicate reduction, search speed |
| [x] User flows covered | ✅ | All 5 CRUD journeys + duplicate/concurrent flows |
| [x] Domain model defined | ✅ | Customer, Auth, Audit domains with boundaries |
| [x] Architecture defined | ✅ | 4-layer, monolith, deployment topology |
| [x] Database strategy defined | ✅ | Entities, relationships, retention, audit |
| [x] API strategy defined | ✅ | Resources, operations, authz, search, pagination |
| [x] Security strategy defined | ✅ | AuthN, AuthZ, validation, audit, sensitive data |
| [x] Logging strategy defined | ✅ | App, Audit, Security, Error categories |
| [x] Integration strategy defined | ✅ | Internal/external, patterns |
| [x] NFR documented | ✅ | 28 NFRs across 7 categories with implementation |
| [x] Risks documented | ✅ | 14 risks with impact/probability/mitigation |
| [x] ADR included | ✅ | 8 ADRs for key decisions |
| [x] No source code generated | ✅ | Design only |
| [x] No SQL generated | ✅ | Logical schema only |
| [x] No API endpoints generated | ✅ | Strategy only, no OpenAPI spec |
| [x] No request/response schemas generated | ✅ | DTO structure described, not coded |
| [x] No Docker configuration generated | ✅ | Topology described, not docker-compose.yml |
| [x] No Jira tasks generated | ✅ | Not in scope |
| [x] No implementation task breakdown generated | ✅ | Not in scope |

---

## 17. Handoff Package

### 17.1 Next Agents & Consumable Artifacts

| Agent | Consumes From This Document | Produces |
|-------|----------------------------|----------|
| **API Contract Agent** | Section 7 (API Strategy), Section 6 (Data Model), Section 8 (Security) | OpenAPI 3.0 Spec, DTO Definitions, Error Catalog |
| **Backend Agent** | Sections 4, 5, 6, 7, 8, 9, 11, 15 | Go Source Code, Migrations, Unit/Integration Tests |
| **Frontend Agent** | Sections 5, 7, 11, 12, 13, 15 (UX Design) | React/TypeScript App, Component Library, E2E Tests |
| **Mobile Agent** | Sections 7, 10 (API Strategy), Section 8 (Auth) | React Native App (Phase 2) |
| **QA Agent** | Sections 7, 11, 12, 14 (Acceptance Criteria, NFRs, Risks) | Test Plan, Performance Scripts, Security Test Cases |
| **DevOps Agent** | Sections 2, 3, 9, 11, 14 (Infrastructure, Logging, Deployment) | Docker Compose, Nginx Config, Backup Scripts, Monitoring |

### 17.2 Key Decisions Requiring Downstream Alignment
1. **ADR-002 (Soft Delete)** → Backend: GORM scopes; Frontend: Filter UI; API: `deleted_at` in response
2. **ADR-003 (JWT HS256)** → Backend: Token issuance/validation; Frontend: Interceptor + refresh logic
3. **ADR-005 (pg_trgm)** → Backend: Migration + search query; API Contract: Search params/response
4. **ADR-006 (Optimistic Lock)** → Backend: Version check; Frontend: Conflict modal (SC-07); API: 409 response
5. **ADR-007 (Duplicate Detection)** → Backend: Service logic; Frontend: Duplicate Modal (SC-06); API: 409 with matches

---

## 18. Appendices

### 18.1 Technology Versions (Pinned)
| Component | Version | Source |
|-----------|---------|--------|
| Go | 1.22.x | Standard Library |
| Gin | v1.9.x | github.com/gin-gonic/gin |
| GORM | v2.25.x | gorm.io/gorm |
| PostgreSQL | 16.x | Docker Hub `postgres:16-alpine` |
| React | 18.2.x | npm |
| TypeScript | 5.3.x | npm |
| Tailwind CSS | 3.4.x | npm |
| TanStack Query | v5.x | npm |
| React Hook Form | v7.x | npm |
| Zod | v3.22.x | npm |
| Nginx | 1.25.x (alpine) | Docker Hub |
| Docker Compose | v2.24.x | Docker |

### 18.2 Configuration Matrix (Environment Variables)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_ENV` | Yes | `production` | `development`, `staging`, `production` |
| `HTTP_PORT` | No | `8080` | Backend listen port |
| `DB_DSN` | Yes | — | `postgres://user:pass@postgres:5432/crm?sslmode=disable` |
| `DB_MAX_OPEN_CONNS` | No | `20` | GORM connection pool |
| `DB_MAX_IDLE_CONNS` | No | `10` | |
| `DB_CONN_MAX_LIFETIME` | No | `300` | Seconds |
| `JWT_SECRET` | Yes | — | 32+ byte base64; generate: `openssl rand -base64 32` |
| `JWT_ACCESS_TTL` | No | `30m` | Access token TTL |
| `JWT_REFRESH_TTL` | No | `168h` | Refresh token TTL (7 days) |
| `LOG_LEVEL` | No | `info` | `debug`, `info`, `warn`, `error` |
| `CORS_ALLOWED_ORIGINS` | Yes | — | Comma-separated (e.g., `https://crm.company.com`) |
| `RATE_LIMIT_RPM` | No | `100` | Requests per minute per IP |
| `BCRYPT_COST` | No | `12` | Password hash cost |

### 18.3 Database Index Strategy (Summary)
| Index | Type | Columns | Condition | Purpose |
|-------|------|---------|-----------|---------|
| `idx_customers_customer_id` | B-Tree Unique | `customer_id` | `deleted_at IS NULL` | Business key lookup |
| `idx_customers_primary_email` | B-Tree Unique | `primary_email` | `deleted_at IS NULL` | Email uniqueness (active) |
| `idx_customers_full_name_trgm` | GIN | `full_name` | — | Fuzzy name search |
| `idx_customers_company_name_trgm` | GIN | `company_name` | — | Fuzzy company search |
| `idx_customers_primary_phone` | B-Tree | `primary_phone` | `deleted_at IS NULL` | Exact phone search |
| `idx_customers_search_composite` | B-Tree | `status, created_at DESC` | `deleted_at IS NULL` | List pagination + sort |
| `idx_customers_deleted_at` | B-Tree | `deleted_at` | — | Soft delete queries, purge job |

---

*Document Version: 1.0*  
*Prepared by: Architect Agent*  
*Date: Current*  
*Status: Ready for Review*  
*Next Review: Post-PoC Validation (DEP-01)*