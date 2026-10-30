# Jira Story

## Story Information

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-001 |
| **Epic ID** | EPIC-001 |
| **Release** | Release 1 |
| **Priority** | P1 — Critical |
| **Story Points** | 5 |
| **Status** | Ready for Development |

---

## Business Context

| Attribute | Value |
|-----------|-------|
| **Business Goal** | Enable Admin to add new customers to centralized database replacing manual Excel entry |
| **Business Value** | Foundation capability; reduces creation time from 5-10 min to < 1 min; eliminates file-sharing overhead |
| **Users** | Admin (Primary) |
| **Expected Outcome** | Customer record created in centralized database, immediately searchable, with duplicate detection warning |

---

## User Story

**As an** Admin  
**I want** to enter customer information in a structured form  
**So that** the customer is added to the centralized database and immediately available for search

---

## Acceptance Criteria

**AC-001**: Given Admin is on the Create Customer page, When Admin fills all required fields with valid data and submits, Then the customer record is created and Admin is redirected to the Customer Detail View showing the new record.

**AC-002**: Given Admin is on the Create Customer page, When Admin leaves a required field empty and attempts to submit, Then the system displays a validation error indicating the missing field(s) and prevents submission.

**AC-003**: Given Admin enters customer data matching an existing record (per duplicate rules), When Admin submits, Then the system displays the potential duplicate(s) and requires explicit confirmation to proceed or cancel.

**AC-004**: Given a new customer is created, When Admin searches for the customer by any searchable field, Then the customer appears in results within 5 seconds.

**AC-005**: Given Admin creates a customer, When the operation completes, Then total elapsed time from form load to confirmation is under 1 minute.

---

## Business Rules

| Rule ID | Business Rule | Relevance to STORY-001 |
|---------|---------------|------------------------|
| **BR-001** | Unique Customer Identifier — Every customer must have a system-generated unique ID (format: CUST-YYYY-NNNNNN) assigned at creation. | System assigns on create |
| **BR-002** | Required Fields for Creation — Customer Name, Primary Phone, and Email are mandatory. All other fields are optional. | Form validation |
| **BR-003** | Phone Number Format — Phone numbers must be stored in E.164 format (+<country><number>). Input accepts local formats; system normalizes on save. | Input formatting + validation |
| **BR-004** | Email Uniqueness (Soft) — Email addresses should be unique across active customers. Duplicate email triggers warning but does not block creation (per BR-006). | Duplicate detection |
| **BR-005** | Duplicate Detection Criteria — A potential duplicate exists when: (Name similarity > 85% AND Phone match) OR (Email exact match) OR (Company exact match AND Phone match). *Exact logic TBD with stakeholders.* | Duplicate check on create |
| **BR-006** | Duplicate Handling on Create — If duplicate detected: System presents match(es) to Admin. Admin may: (a) Cancel creation, (b) Proceed anyway (new record created), (c) Select existing record to view/edit instead. | Duplicate modal (SC-06) |
| **BR-011** | Field Length Limits — Name: 200 chars; Company: 200 chars; Phone: 20 chars (E.164); Email: 254 chars; Address: 500 chars; Notes: 2000 chars. | Field validation |
| **BR-012** | Case Sensitivity — Search is case-insensitive. Email stored lowercase. Name/Company preserve input casing. | Email normalization |
| **BR-015** | Audit Logging (Future-Ready) — All Create, Update, Delete actions shall capture: Actor, Timestamp, Action, Field Changes (for Update). Storage/retention TBD. | created_by, created_at captured |

---

## UI/UX References

| Reference | Description | Screen ID |
|-----------|-------------|-----------|
| **Create Customer Form** | Guided form for new customer entry with inline validation, phone/email formatting, field groups | SC-02 |
| **Duplicate Match Modal** | Presents potential duplicates for Admin decision before create/update | SC-06 |
| **Global Search Header** | Persistent search input; Create Customer CTA in empty state | SC-01 |
| **Customer Detail View** | Redirect target after successful creation | SC-03 |
| **Dashboard / Customer List** | Entry point via "Create Customer" button; shows new record after creation | SC-01 |

> **Reference Only**: Full screen specifications, wireframes, component inventory, validation rules, and accessibility requirements are documented in `uiux-design.md` (Sections 10.2, 10.6, 11.2, 12, 13, 14).

---

## API References

| Resource | Endpoint ID | Method | Path | Purpose |
|----------|-------------|--------|------|---------|
| **Customer** | EP-01 | POST | `/api/v1/customers` | Create new customer record |
| **Customer** | EP-02 | GET | `/api/v1/customers` | Search customers (verify creation) |
| **Customer** | EP-03 | GET | `/api/v1/customers/{id}` | Get customer detail (redirect target) |
| **Auth** | EP-07 | POST | `/api/v1/auth/login` | Authentication (prerequisite) |
| **Auth** | EP-09 | GET | `/api/v1/auth/me` | Current user profile (role verification) |

### Authentication Requirements
- **Mechanism**: JWT Bearer Token (HS256)
- **Access Token TTL**: 30 minutes
- **Required Header**: `Authorization: Bearer <access_token>`
- **Public Endpoints**: `/auth/login`, `/auth/refresh` only

### Authorization Requirements
| Role | EP-01 (Create) | EP-02 (Search) | EP-03 (Detail) |
|------|----------------|----------------|----------------|
| **Admin** | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Manager** | ❌ Forbidden (403) | ✅ Allowed | ✅ Allowed |

> **Reference Only**: Full API contracts, request/response schemas, validation rules, error envelopes, and field classifications are documented in `api-contract.md` (EP-01, EP-02, EP-03, EP-07, EP-09).

---

## Technical Constraints

| Constraint Category | Details |
|---------------------|---------|
| **Performance** | Creation end-to-end < 1 minute (NFR-02); API latency p95 < 500ms; DB INSERT ~50ms |
| **Security** | Input validation at DTO + service + DB layers; bcrypt cost 12 for passwords; TLS 1.2+; log masking for PII |
| **Infrastructure** | VPS: 2 CPU / 2 GB RAM; Docker Compose: nginx (128MB), backend (512MB), postgres (1GB); Connection pool: 20 |
| **Database** | PostgreSQL 16; pg_trgm extension for search; partial unique indexes on active records; optimistic locking via `version` column |
| **Concurrency** | Optimistic locking not applicable for create; duplicate detection race condition mitigated by UNIQUE index on email |

> **Reference Only**: Full technical design, architecture, database strategy, NFRs, and ADRs are documented in `technical-design.md` (Sections 6, 7, 11, 15).

---

## Dependencies

### Blocking Dependencies
| Dependency | Description | Status |
|------------|-------------|--------|
| **STORY-006 (Auth)** | JWT authentication and role enforcement must be functional before Create API can be secured | Must complete first |
| **STORY-007 (Infra)** | Staging environment with PostgreSQL, Docker Compose, Nginx must be provisioned | Can start in parallel |
| **UI/UX Design Approval** | SC-02 and SC-06 designs must be approved by Product Owner + Operations Manager | Must complete before Frontend dev |

### Related Stories
| Story | Relationship |
|-------|--------------|
| **STORY-002 (Search)** | Creates customer must be immediately searchable (AC-004) |
| **STORY-003 (Detail)** | Create redirects to Detail View (AC-001) |
| **STORY-004 (Update)** | Uses same validation, duplicate detection, and form components |
| **STORY-008 (Migration)** | Depends on Create API working for batch insert |

---

## Team Scope

### Backend Scope
- Implement `POST /api/v1/customers` handler (EP-01)
- Customer Service: validation, duplicate detection (BR-005), audit fields (`created_by`, `created_at`), customer_id generation (CUST-YYYY-NNNNNN)
- Customer Repository: INSERT with GORM, return created entity with all fields
- Duplicate detection service: name similarity (Levenshtein >85%), phone exact match, email exact match, company+phone exact match
- Unit tests: service (duplicate logic, validation, customer_id generation), handler (422, 409, 403, 201)
- Integration test: full create → search verification (EP-01 → EP-02)
- Database migration: `customers` table with all columns, indexes, constraints per `technical-design.md` Section 6.1.1

### Frontend Scope
- Build `CreateCustomerPage` (SC-02) with `CustomerForm` component
- Zod validation schema mirroring backend rules (required fields, E.164 phone, RFC 5322 email, max lengths)
- TanStack Query mutation for create with optimistic UI
- Phone input with country selector and auto-formatting to E.164
- Email input with lowercase normalization
- Inline validation on blur + submit; error announcements via `aria-live`
- Duplicate Match Modal (SC-06) integration: display matches, handle Cancel/View Existing/Proceed Anyway
- Success: redirect to `CustomerDetailPage` (SC-03) with success toast
- Accessibility: WCAG 2.1 AA (labels, focus management, error announcements, autocomplete attributes)
- Responsive: Desktop (centered 600px form), Tablet/Mobile (full-width, collapsible sections)

### Mobile Scope
- Same as Frontend Scope (responsive web covers tablet; mobile app is Phase 2)
- Ensure touch targets ≥ 48×48px on form fields and buttons
- Native `<input type="tel">` and `<input type="email">` on mobile for keyboard optimization

### QA Scope
- Execute test scenarios from `api-contract.md` EP-01 Test Scenarios (Positive, Negative, Boundary, Security, Business)
- Verify AC-001 to AC-005 via manual and automated tests
- Performance test: creation time < 1 minute end-to-end (form load → submit → detail view)
- Accessibility audit: WCAG 2.1 AA compliance on Create form and Duplicate modal
- Cross-browser: Chrome, Firefox, Edge (latest 2 versions)
- Role enforcement: Verify Manager receives 403 on Create attempt

### Reviewer Scope
- Code review: Backend handler, service, repository, DTOs, validation, tests
- Code review: Frontend page, form component, validation schema, mutation hook, modal integration
- Verify API contract compliance (request/response schemas, error envelopes, field classifications)
- Verify business rule implementation (BR-001, BR-002, BR-003, BR-004, BR-005, BR-006, BR-011, BR-012, BR-015)
- Verify traceability: All ACs covered, all BRs enforced, all UI/UX refs implemented

### DevOps Scope
- Ensure staging environment has PostgreSQL with `pg_trgm` extension enabled
- Verify Docker Compose resource limits allow backend (512MB) and postgres (1GB) to run create operations
- Configure Nginx rate limiting: 100 req/min/IP general, 10 req/min/IP for auth
- Ensure TLS termination works for Create endpoint
- Log rotation configured for application logs (daily, compress, max 30 files)
- Health checks: `/healthz` (liveness), `/readyz` (readiness: DB ping) pass during create operations

---

## Definition Of Done

- [ ] **Acceptance Criteria Passed** — All AC-001 to AC-005 validated by QA
- [ ] **Code Reviewed** — Peer review completed (minimum 1 approver); no unresolved comments
- [ ] **Tests Passed** — Unit tests ≥ 80% coverage on new service/handler code; integration test (create → search) passes; E2E test (Admin creates → appears in search < 5 sec) passes
- [ ] **Documentation Updated** — API contract updated if endpoints changed; README/runbooks updated
- [ ] **QA Approved** — QA sign-off on story completion; no blocking defects
- [ ] **Ready For Release** — Merged to main branch; CI/CD pipeline passes (lint, test, build, deploy to staging); staging deployment verified

---

## Test Scenarios

### Positive Scenarios
| Scenario | Description | Expected Result |
|----------|-------------|-----------------|
| **TC-001** | Valid request with all required fields (Name, Phone, Email) | 201 Created, customer returned, immediately searchable via EP-02 |
| **TC-002** | Valid request with all optional fields populated | 201 Created, optional fields persisted |
| **TC-003** | Valid request with only required fields | 201 Created, optional fields null/empty |
| **TC-004** | Duplicate detected, Admin chooses "Proceed Anyway" | 201 Created (new record), duplicate warning dismissed |
| **TC-005** | Duplicate detected, Admin chooses "View Existing" | 409 returned, frontend navigates to existing Detail View |
| **TC-006** | Phone number entered in local format, auto-formatted to E.164 | Stored as E.164 (+15551234567) |
| **TC-007** | Email entered with uppercase, stored lowercase | Stored as lowercase (john@smith.com) |

### Negative Scenarios
| Scenario | Description | Expected Result |
|----------|-------------|-----------------|
| **TC-008** | Missing `full_name` | 422 Validation Error, `REQUIRED_FIELD` on `full_name` |
| **TC-009** | Missing `primary_phone` | 422 Validation Error, `REQUIRED_FIELD` on `primary_phone` |
| **TC-010** | Missing `primary_email` | 422 Validation Error, `REQUIRED_FIELD` on `primary_email` |
| **TC-011** | Invalid `primary_email` format (e.g., "john@") | 422 Validation Error, `INVALID_EMAIL_FORMAT` |
| **TC-012** | Invalid `primary_phone` format (not E.164) | 422 Validation Error, `INVALID_PHONE_FORMAT` |
| **TC-013** | `full_name` exceeds 200 chars | 422 Validation Error, `MAX_LENGTH_EXCEEDED` |
| **TC-014** | `notes` exceeds 2000 chars | 422 Validation Error, `MAX_LENGTH_EXCEEDED` |
| **TC-015** | Invalid `customer_type` enum value | 422 Validation Error, `INVALID_ENUM_VALUE` |
| **TC-016** | Invalid `country` code (not ISO 3166-1 alpha-2) | 422 Validation Error, `INVALID_COUNTRY_CODE` |
| **TC-017** | Manager role attempts create | 403 Forbidden |
| **TC-018** | Expired/missing JWT | 401 Unauthenticated |
| **TC-019** | Duplicate detected, Admin chooses "Cancel" | 409 returned, frontend returns to form with data preserved |

### Security Scenarios
| Scenario | Description | Expected Result |
|----------|-------------|-----------------|
| **TC-020** | SQL injection attempt in `full_name` (e.g., `' OR 1=1--`) | 422 or sanitized, no execution, no data leak |
| **TC-021** | XSS payload in `notes` (e.g., `<script>alert(1)</script>`) | Stored as-is, escaped on render (React auto-escapes) |
| **TC-022** | Password field in request body (should not exist) | 422 Validation Error (unexpected field) |
| **TC-023** | Rate limit exceeded (101 requests/min) | 429 Rate Limited (Nginx) |

### Regression Scenarios
| Scenario | Description | Expected Result |
|----------|-------------|-----------------|
| **TC-024** | Create customer → Search by name → Verify appears | Customer found in < 5 sec |
| **TC-025** | Create customer → Search by phone → Verify appears | Customer found in < 5 sec |
| **TC-026** | Create customer → Search by email → Verify appears | Customer found in < 5 sec |
| **TC-027** | Create customer → Search by customer_id → Verify appears | Customer found in < 5 sec |
| **TC-028** | Create customer → Direct URL to Detail View (EP-03) | 200 OK, full data displayed |
| **TC-029** | Create customer with duplicate email → Verify UNIQUE constraint catches race condition | Second create returns 409 or 422 (DB constraint) |
| **TC-030** | Create customer → Update same customer (STORY-004) → Verify version increment | Version = 2 after update |

---

## Traceability

| Artifact | Reference | Section |
|----------|-----------|---------|
| **Business Analysis** | `business-analysis.md` | Problem Analysis, User Impact, Scope Recommendation (Create Customer) |
| **PRD** | `prd.md` | FT-01, FR-01-01 to FR-01-07, US-CUST-001, BR-001 to BR-007, BR-011, BR-012, BR-015 |
| **UI/UX Design** | `uiux-design.md` | SC-02 (Create Form), SC-06 (Duplicate Modal), SC-01 (Dashboard/List), Section 11.2 (Wireframes), Section 13 (Validation), Section 14 (Accessibility) |
| **Technical Design** | `technical-design.md` | Section 6.1.1 (Customer Entity), Section 7.2 (EP-01), Section 8 (Security), Section 11.1 (NFR-02), ADR-002, ADR-007 |
| **API Contract** | `api-contract.md` | EP-01 (Create Customer), EP-02 (Search), EP-03 (Detail), EP-07 (Login), EP-09 (Me) |
| **Jira Plan** | `jira-plan.md` | STORY-001 Definition of Done, Subtasks SUB-001-01/02/03, Dependency Graph |

---

## Risks

| Risk ID | Risk | Probability | Impact | Mitigation |
|---------|------|-------------|--------|------------|
| **RSK-001** | Duplicate detection rules (BR-005) not finalized before development | Medium | High | Implement configurable thresholds; Admin override (BR-006) allows proceed anyway; tune post-launch |
| **RSK-002** | Race condition: two Admins create same email simultaneously | Low | Medium | UNIQUE index on `primary_email` WHERE `deleted_at IS NULL` catches at DB level; service handles 409 |
| **RSK-003** | Phone number parsing/normalization edge cases (international formats) | Medium | Medium | Use libphonenumber-go for E.164 normalization; comprehensive test cases |
| **RSK-004** | VPS performance: create latency exceeds 1 minute under load | Low | High | Connection pooling (20), async audit logging, monitor p95; load test in staging |
| **RSK-005** | Frontend validation diverges from backend (Zod vs Go validator) | Medium | Medium | Shared validation constants; contract tests; Zod schema mirrors DTO tags |

---

## Implementation Notes

> **Guidance Only — No Code**

1. **Customer ID Generation**: Use `CUST-` + `YYYY` + 6-digit sequence (per year). Sequence can be DB-side (serial) or application-side with atomic counter.

2. **Duplicate Detection Algorithm**: 
   - Exact match on normalized `primary_email` (lowercase) → `match_type: "EMAIL_EXACT"`
   - Exact match on normalized `primary_phone` (E.164) + name similarity > 0.85 (Levenshtein) → `match_type: "NAME_PHONE"`
   - Exact match on `company_name` + exact match on `primary_phone` → `match_type: "COMPANY_PHONE"`
   - Return all matches with similarity scores; frontend displays in SC-06 modal

3. **Phone Normalization**: Use `github.com/nyaruka/phonenumbers` (Go port of libphonenumber). Accept input with country selector; store E.164.

4. **Email Normalization**: `strings.ToLower(strings.TrimSpace(email))` before validation and storage.

5. **Audit Fields**: Set `created_by` from JWT `sub` claim; `created_at` = `time.Now().UTC()`; `version` = 1.

6. **Response Envelope**: Follow standardized format per `api-contract.md` (success, message, data, meta.request_id).

7. **Error Handling**: Map validation errors to `VALIDATION_ERROR` (422) with field-level details; duplicate → `DUPLICATE_DETECTED` (409) with matches array; authz → `FORBIDDEN` (403).

8. **Frontend State**: TanStack Query mutation with `onSuccess` redirect to `/customers/{id}`; `onError` handles 409 (show modal), 422 (inline errors), 401/403 (toast + redirect).

9. **Accessibility**: 
   - Form: `<fieldset>`/`<legend>` for sections; `<label for="id">` for all inputs; `aria-required="true"` on required fields
   - Errors: `aria-invalid="true"` + `aria-describedby="error-id"`; error container with `aria-live="polite"`
   - Modal: `role="dialog"`, `aria-modal="true"`, `aria-labelledby="modal-title"`, focus trap, Esc closes

10. **Responsive**: 
    - Desktop: Centered form max-width 600px, sticky header with Cancel/Save
    - Tablet/Mobile: Full-width, collapsible sections (Company, Contact, Address, Notes), sticky bottom bar with Cancel/Save

---

*Story Artifact Generated: STORY-001.md*  
*Status: Implementation-Ready*  
*Generated by: Story Detail Generator Agent*