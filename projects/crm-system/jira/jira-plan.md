# Jira Planning Structure

## Customer Management Feature — CRM System

---

## Epic Structure

### EPIC-001: Customer Management MVP

| Attribute | Value |
|-----------|-------|
| **Epic ID** | EPIC-001 |
| **Epic Title** | Customer Management MVP |
| **Business Goal** | Centralize customer data management into a single authoritative application, eliminating distributed Excel files and reducing duplicate records by 80% |
| **Business Value** | • Eliminates 5-10 hrs/week/admin in Excel management<br>• Reduces duplicate-driven errors (wrong shipments, duplicate communications)<br>• Enables sub-5-second customer lookup (vs 5-10 min currently)<br>• Foundation for all future CRM capabilities |
| **Priority** | P1 — Critical |
| **Success Metrics** | • Search p95 < 5 seconds (10K records)<br>• Customer creation < 1 minute end-to-end<br>• Duplicate record reduction 80% vs baseline<br>• Admin adoption > 90% daily usage<br>• Data accuracy < 2% error rate |
| **Description** | Deliver 5 core CRUD operations (Create, Search, Detail, Update, Soft Delete) for Customer records via a web-based SPA. Replaces manual Excel workflows across departments. Includes JWT authentication, role-based access (Admin/Manager), duplicate detection with admin override, optimistic locking for concurrent edits, and soft delete with 90-day recovery. Deployed on VPS (2 CPU/2GB RAM) with PostgreSQL, Go/Gin backend, React/TypeScript frontend. |

---

## Stories

### STORY-001: Create Customer Record

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-001 |
| **Title** | Create New Customer Record |
| **Business Goal** | Enable Admin to add new customers to centralized database replacing manual Excel entry |
| **Business Value** | Foundation capability; reduces creation time from 5-10 min to < 1 min; eliminates file-sharing overhead |
| **User** | Admin |
| **Acceptance Criteria References** | US-CUST-001 AC-001 to AC-005 |
| **Priority** | P1 — Critical |
| **Story Points** | 5 |
| **Dependencies** | None |
| **Definition of Done** | • Requirements implemented per AC-001 to AC-005<br>• API: POST /customers with validation, duplicate detection (409), audit fields<br>• UI: Create form (SC-02) with inline validation, phone/email formatting, duplicate modal (SC-06)<br>• Duplicate detection per BR-005/006 (name+phone, email, company+phone)<br>• Unit tests: service (duplicate logic, validation), handler (422, 409, 201)<br>• Integration test: full create → search verification<br>• E2E test: Admin creates customer → appears in search < 5 sec<br>• Accessibility: WCAG 2.1 AA (labels, focus, error announcements)<br>• Code reviewed, tests pass, documentation updated, QA approved |

---

### STORY-002: Search Customers

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-002 |
| **Title** | Search Customers by Multiple Criteria |
| **Business Goal** | Enable Admin and Manager to find customers in < 5 seconds via single search box |
| **Business Value** | Addresses primary pain point (slow search); highest user frequency (50+/day); direct operational impact |
| **User** | Admin, Manager |
| **Acceptance Criteria References** | US-CUST-002 AC-001 to AC-005 |
| **Priority** | P1 — Critical |
| **Story Points** | 8 |
| **Dependencies** | None (can parallel with STORY-001) |
| **Definition of Done** | • Requirements implemented per AC-001 to AC-005<br>• API: GET /customers with q, page, size, sort, order, customer_type, status<br>• pg_trgm indexes on full_name, company_name; composite index for pagination<br>• Fuzzy/partial match on name, company, phone, email, ID, city<br>• Results: Name, Phone, Email, Company, Customer ID, Status<br>• p95 < 5 sec end-to-end (DB < 500ms) with 10K records<br>• UI: Global search header (SC-01), debounced 300ms, results table (desktop) / cards (tablet/mobile)<br>• Empty state: "No customers found" + Create CTA (Admin)<br>• Recent searches (Admin only, localStorage, 5 items)<br>• Unit tests: repository (search query, pagination), handler (validation, authz)<br>• Load test: 10K records, concurrent searches, p95 verification<br>• E2E test: Admin/Manager search → click result → detail < 2 sec<br>• Accessibility: ARIA live regions, keyboard navigation, focus management<br>• Code reviewed, tests pass, documentation updated, QA approved |

---

### STORY-003: Customer Detail View

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-003 |
| **Title** | View Complete Customer Details |
| **Business Goal** | Provide single consolidated view of all customer information replacing multi-file lookup |
| **Business Value** | Eliminates cross-referencing Excel files; enables informed decisions; supports Edit/Delete actions |
| **User** | Admin, Manager |
| **Acceptance Criteria References** | US-CUST-003 AC-001 to AC-005 |
| **Priority** | P1 — Critical |
| **Story Points** | 3 |
| **Dependencies** | STORY-002 (navigates from search results) |
| **Definition of Done** | • Requirements implemented per AC-001 to AC-005<br>• API: GET /customers/{id} and GET /customers/by-key/{customer_id}<br>• Returns all fields grouped: Primary Contact, Company, Additional Contact, Address, Notes, Audit (Admin only)<br>• Soft-deleted: Admin sees status=Deleted; Manager gets 404<br>• UI: Detail view (SC-03) with role-based actions (Edit/Delete for Admin only)<br>• Copy-to-clipboard for phone, email, ID<br>• Load time < 2 sec (PK lookup)<br>• Direct URL access with auth<br>• Unit tests: handler (404, 403, 200), repository (by ID, by key)<br>• E2E test: Search → click → detail loads with correct data<br>• Accessibility: Semantic headings, label-value pairs (dl/dt/dd), status badge with text+icon<br>• Code reviewed, tests pass, documentation updated, QA approved |

---

### STORY-004: Update Customer Record

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-004 |
| **Title** | Update Existing Customer Record |
| **Business Goal** | Allow Admin to maintain accurate, current customer data |
| **Business Value** | Ensures data quality post-creation; prevents stale data; supports operational accuracy |
| **User** | Admin |
| **Acceptance Criteria References** | US-CUST-004 AC-001 to AC-005 |
| **Priority** | P1 — Critical |
| **Story Points** | 5 |
| **Dependencies** | STORY-003 (Edit action from Detail View) |
| **Definition of Done** | • Requirements implemented per AC-001 to AC-005<br>• API: PATCH /customers/{id} with If-Match header (optimistic lock)<br>• Partial update supported; validation same as create<br>• Duplicate detection on changed fields only (BR-007)<br>• Version increment on success; 409 CONFLICT on version mismatch<br>• UI: Edit form (SC-04) pre-populated, dirty state warning, concurrent edit modal (SC-07)<br>• Cancel preserves original; Save → redirect to Detail with success toast<br>• Update time < 1 minute end-to-end<br>• Unit tests: service (optimistic lock, duplicate on update), handler (409 version, 409 duplicate, 403)<br>• Integration test: concurrent edit simulation → conflict modal → reload/reapply<br>• E2E test: Admin edits → search with new values returns updated record<br>• Accessibility: Form validation announcements, focus management on modal<br>• Code reviewed, tests pass, documentation updated, QA approved |

---

### STORY-005: Soft Delete Customer Record

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-005 |
| **Title** | Soft Delete Customer Record |
| **Business Goal** | Allow Admin to archive customers without permanent data loss |
| **Business Value** | Data lifecycle management; recoverable within 90 days; maintains data integrity |
| **User** | Admin |
| **Acceptance Criteria References** | US-CUST-005 AC-001 to AC-005 |
| **Priority** | P1 — Critical |
| **Story Points** | 3 |
| **Dependencies** | STORY-003 (Delete action from Detail View) |
| **Definition of Done** | • Requirements implemented per AC-001 to AC-005<br>• API: DELETE /customers/{id} with If-Match header<br>• Sets status=Deleted, deleted_at, deleted_by, version++<br>• Excluded from standard search (deleted_at IS NULL filter)<br>• UI: Delete confirmation modal (SC-05) showing name, ID, 90-day recovery notice<br>• Redirect to list with success toast "Customer archived"<br>• Soft-deleted not visible to Manager; Admin can access via future Deleted view<br>• Unit tests: handler (409 version, 404 already deleted, 403 Manager)<br>• Integration test: Create → Delete → Search (not found) → Restore (future)<br>• E2E test: Admin deletes → search excludes → detail shows Deleted status<br>• Accessibility: Destructive button styling, confirmation focus trap, screen reader announcement<br>• Code reviewed, tests pass, documentation updated, QA approved |

---

### STORY-006: Authentication & Authorization

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-006 |
| **Title** | User Authentication and Role-Based Access Control |
| **Business Goal** | Secure the application with login, session management, and role enforcement (Admin/Manager) |
| **Business Value** | Protects customer data; enforces least privilege; audit readiness |
| **User** | Admin, Manager |
| **Acceptance Criteria References** | PRD NFR-07, NFR-08; API Contract EP-07, EP-08, EP-09 |
| **Priority** | P1 — Critical |
| **Story Points** | 5 |
| **Dependencies** | None (foundational) |
| **Definition of Done** | • API: POST /auth/login (bcrypt cost 12, rate limit 5/min), POST /auth/refresh (rotating, 7-day), GET /auth/me<br>• JWT HS256: 30-min access, 7-day refresh (hashed in DB, blocklist on revoke)<br>• Middleware: validates JWT, extracts role, enforces per route (Admin: CRUD, Manager: Read/Search)<br>• Frontend: Login page, token storage (memory + httpOnly cookie for refresh), auto-refresh at 25 min, 401 intercept → refresh → retry<br>• Role-based UI: Manager sees no Create/Edit/Delete buttons; routes guarded<br>• Security: Rate limiting (Nginx + app), brute force lockout (10 failures = 15 min), password policy<br>• Unit tests: auth service (hash, verify, token gen/validate), middleware (expired, invalid, role check)<br>• Integration test: login → access protected → token expiry → silent refresh → retry<br>• E2E test: Admin login → CRUD works; Manager login → Create/Edit/Delete blocked<br>• Security test: SQLi/XSS in login, token tampering, rate limit enforcement<br>• Code reviewed, tests pass, documentation updated, QA approved |

---

### STORY-007: Infrastructure & Deployment

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-007 |
| **Title** | Infrastructure Provisioning and Deployment Pipeline |
| **Business Goal** | Deploy the application to target VPS (2 CPU/2GB RAM) with zero-downtime capability |
| **Business Value** | Enables production delivery; operational reliability; rollback capability |
| **User** | DevOps, Development Team |
| **Acceptance Criteria References** | Technical Design Sections 2.2, 3.2, 11.2, 11.4; NFR-07 to NFR-10, NFR-18 |
| **Priority** | P1 — Critical |
| **Story Points** | 5 |
| **Dependencies** | None (can start in parallel) |
| **Definition of Done** | • VPS provisioned: Ubuntu 22.04, Docker Engine, 2 CPU/2GB RAM<br>• Docker Compose: nginx (128MB), backend (512MB), postgres (1GB) with resource limits<br>• Nginx: TLS termination (Let's Encrypt), rate limiting, static serve, proxy to backend<br>• PostgreSQL: shared_buffers=256MB, work_mem=4MB, max_connections=100, pg_trgm extension<br>• Health checks: /healthz (liveness), /readyz (readiness: DB ping)<br>• Daily pg_dump backup at 02:00 UTC to /opt/crm/backups (30 daily + 12 monthly retention)<br>• Log rotation: daily, compress, max 30 files; structured JSON logs<br>• Deploy script: docker compose pull → up -d --remove-orphans (rolling with health checks)<br>• Rollback procedure documented and tested (< 30 min RTO)<br>• Monitoring: disk space alert at 80%, backup failure alert, cert expiry 30-day alert<br>• Smoke test: deploy → health checks pass → login → create customer → search works<br>• Code reviewed, tests pass, documentation updated, QA approved |

---

### STORY-008: Data Migration & Baseline Metrics

| Attribute | Value |
|-----------|-------|
| **Story ID** | STORY-008 |
| **Title** | Data Migration from Excel and Baseline Metrics Capture |
| **Business Goal** | Load clean initial customer data (5,000 records) and establish pre-launch baselines for success metrics |
| **Business Value** | Prerequisite for MVP value realization; enables 80% duplicate reduction measurement |
| **User** | Operations Manager, Admin |
| **Acceptance Criteria References** | Business Analysis: Baseline Establishment Required; PRD Section 14 Release Gate |
| **Priority** | P1 — Critical |
| **Story Points** | 5 |
| **Dependencies** | STORY-001 (Create API must work), STORY-007 (Environment ready) |
| **Definition of Done** | • Migration plan approved by Operations Manager (cleansing, deduplication, ownership)<br>• Migration scripts: Excel → CSV → validation → batch insert via API (idempotent)<br>• Duplicate detection run during migration; conflicts resolved with Admin<br>• 5,000 records loaded; verified via search and detail views<br>• Baseline metrics captured: current duplicate rate, avg creation time, avg search time<br>• Baseline documented and signed off by Operations Manager<br>• Rollback plan: truncate customers table, re-run migration<br>• Performance validation: search p95 < 5 sec with migrated data<br>• Code reviewed, tests pass, documentation updated, QA approved |

---

## Subtasks

### STORY-001: Create Customer Record
| Subtask ID | Title | Discipline | Description |
|------------|-------|------------|-------------|
| SUB-001-01 | Backend: Create Customer API | Backend | Implement POST /customers handler, service (validation, duplicate check, audit), repository (insert), DTOs, unit tests |
| SUB-001-02 | Frontend: Create Customer Form | Frontend | Build CreateCustomerPage (SC-02), CustomerForm component, Zod validation, TanStack Query mutation, duplicate modal (SC-06) |
| SUB-001-03 | QA: Create Customer Validation | QA | Execute test scenarios (positive, negative, boundary, security, business); verify AC-001 to AC-005; performance < 1 min |

### STORY-002: Search Customers
| Subtask ID | Title | Discipline | Description |
|------------|-------|------------|-------------|
| SUB-002-01 | Backend: Search Customers API | Backend | Implement GET /customers handler, service (search logic, pagination), repository (pg_trgm query, indexes), unit tests |
| SUB-002-02 | Frontend: Search & Results UI | Frontend | Build Global Search header, CustomerListPage (SC-01), CustomerTable (desktop), CustomerCard (tablet/mobile), pagination, recent searches |
| SUB-002-03 | QA: Search Validation & Load Test | QA | Execute test scenarios; load test 10K records p95 < 5 sec; verify fuzzy match, filters, empty state, accessibility |

### STORY-003: Customer Detail View
| Subtask ID | Title | Discipline | Description |
|------------|-------|------------|-------------|
| SUB-003-01 | Backend: Customer Detail API | Backend | Implement GET /customers/{id} and GET /customers/by-key/{customer_id}, repository (PK lookup, by-key lookup), unit tests |
| SUB-003-02 | Frontend: Customer Detail Page | Frontend | Build CustomerDetailPage (SC-03), DetailSection components, role-based action bar, copy-to-clipboard, breadcrumb |
| SUB-003-03 | QA: Detail View Validation | QA | Execute test scenarios; verify all fields displayed, role-based actions, direct URL access, load time < 2 sec |

### STORY-004: Update Customer Record
| Subtask ID | Title | Discipline | Description |
|------------|-------|------------|-------------|
| SUB-004-01 | Backend: Update Customer API | Backend | Implement PATCH /customers/{id} with If-Match, service (partial update, version check, duplicate on changed fields), unit tests |
| SUB-004-02 | Frontend: Edit Customer Form | Frontend | Build EditCustomerPage (SC-04), pre-populated form, dirty tracking, concurrent edit modal (SC-07), reset to original |
| SUB-004-03 | QA: Update Validation | QA | Execute test scenarios; verify optimistic lock conflict, duplicate warning, immediate search reflection, cancel behavior |

### STORY-005: Soft Delete Customer Record
| Subtask ID | Title | Discipline | Description |
|------------|-------|------------|-------------|
| SUB-005-01 | Backend: Soft Delete API | Backend | Implement DELETE /customers/{id} with If-Match, service (status=Deleted, timestamps, version++), unit tests |
| SUB-005-02 | Frontend: Delete Confirmation | Frontend | Build DeleteConfirmModal (SC-05), confirmation with name/ID, 90-day notice, destructive button styling |
| SUB-005-03 | QA: Soft Delete Validation | QA | Execute test scenarios; verify excluded from search, version increment, Manager 403, restore path (future) |

### STORY-006: Authentication & Authorization
| Subtask ID | Title | Discipline | Description |
|------------|-------|------------|-------------|
| SUB-006-01 | Backend: Auth API & Middleware | Backend | Implement login, refresh, me endpoints; JWT middleware; role enforcement; rate limiting; bcrypt; token blocklist |
| SUB-006-02 | Frontend: Auth Flow & Guards | Frontend | Build LoginPage, AuthContext (token storage, auto-refresh, 401 intercept), route guards, role-based UI hiding |
| SUB-006-03 | QA: Auth Security Validation | QA | Execute test scenarios; security tests (brute force, token tampering, rate limit, XSS); role enforcement verification |

### STORY-007: Infrastructure & Deployment
| Subtask ID | Title | Discipline | Description |
|------------|-------|------------|-------------|
| SUB-007-01 | DevOps: VPS & Docker Compose | DevOps | Provision VPS, configure Docker Compose with resource limits, health checks, Nginx config, PostgreSQL tuning |
| SUB-007-02 | DevOps: CI/CD Pipeline | DevOps | Build pipeline: lint → test → build images → deploy to staging → smoke test → promote to prod |
| SUB-007-03 | QA: Deployment Validation | QA | Smoke test deployment; verify health checks, backup/restore, rollback, monitoring alerts, TLS cert renewal |

### STORY-008: Data Migration & Baseline Metrics
| Subtask ID | Title | Discipline | Description |
|------------|-------|------------|-------------|
| SUB-008-01 | Backend: Migration Scripts | Backend | Build Excel→CSV parser, validation, batch insert via API, duplicate detection during migration, idempotency |
| SUB-008-02 | DevOps: Migration Execution | DevOps | Run migration in staging → validate → run in production; coordinate with Operations Manager |
| SUB-008-03 | QA: Baseline Capture & Verification | QA | Measure and document baseline duplicate rate, creation time, search time; verify 5K records loaded correctly |

---

## Dependencies

### Story Dependency Graph

```text
STORY-001 (Create Customer)
 └ None

STORY-002 (Search Customers)
 └ None

STORY-003 (Customer Detail View)
 └ Depends On STORY-002 (navigation from search results)

STORY-004 (Update Customer)
 └ Depends On STORY-003 (Edit action from Detail View)

STORY-005 (Soft Delete Customer)
 └ Depends On STORY-003 (Delete action from Detail View)

STORY-006 (Authentication & Authorization)
 └ None (foundational - start first)

STORY-007 (Infrastructure & Deployment)
 └ None (can start in parallel)

STORY-008 (Data Migration & Baseline Metrics)
 └ Depends On STORY-001 (Create API)
 └ Depends On STORY-007 (Environment ready)
```

### Critical Path
```
STORY-006 (Auth) → STORY-001 (Create) → STORY-002 (Search) → STORY-003 (Detail) → STORY-004/005 (Update/Delete)
                                    ↘
                                     STORY-007 (Infra) → STORY-008 (Migration)
```

### Parallelizable Groups
- **Group A (Start Immediately)**: STORY-006, STORY-007
- **Group B (After Auth Ready)**: STORY-001, STORY-002
- **Group C (After Search + Detail)**: STORY-004, STORY-005
- **Group D (After Create + Infra)**: STORY-008

---

## Story Points Summary

| Story ID | Title | Story Points | Priority |
|----------|-------|--------------|----------|
| STORY-001 | Create Customer Record | 5 | P1 |
| STORY-002 | Search Customers | 8 | P1 |
| STORY-003 | Customer Detail View | 3 | P1 |
| STORY-004 | Update Customer Record | 5 | P1 |
| STORY-005 | Soft Delete Customer Record | 3 | P1 |
| STORY-006 | Authentication & Authorization | 5 | P1 |
| STORY-007 | Infrastructure & Deployment | 5 | P1 |
| STORY-008 | Data Migration & Baseline Metrics | 5 | P1 |
| **Total** | **8 Stories** | **39 Points** | **All P1** |

> **Note**: 8 stories (within 10-story limit). All P1 as required for MVP. No story exceeds 13 points.

---

## Priority Assignment

| Priority | Stories | Rationale |
|----------|---------|-----------|
| **P1 — Critical** | STORY-001 to STORY-008 | All required for MVP delivery; no feature works without auth, infra, or core CRUD |
| **P2 — High** | — | None in MVP |
| **P3 — Medium** | — | Future scope (Bulk Import, Duplicate Merge, Audit Trail, RBAC, Tags, API) |
| **P4 — Low** | — | Deferred (Analytics, Campaigns, Loyalty, Mobile App) |

---

## Release Plan

### Release 1: MVP Launch (Single Release)

| Attribute | Value |
|-----------|-------|
| **Release Name** | CRM Customer Management v1.0 |
| **Target Date** | [Sprint 4-6, depending on team velocity] |
| **Scope** | All 8 P1 stories (39 points) |
| **Value Delivered** | Complete customer CRUD with search, auth, deployment, migrated data |
| **Deployable** | Yes — single Docker Compose deployment |
| **Testable** | Yes — all acceptance criteria covered by E2E tests |
| **Rollback Plan** | Documented: `docker compose down` → restore pg_dump → `docker compose up -d` (< 30 min) |

### Release Criteria (Definition of Ready for Release)
- [ ] All 8 stories meet Definition of Done
- [ ] Zero critical/severe defects open
- [ ] Search p95 < 5 sec with 5,000 migrated records (load test report)
- [ ] Customer creation < 1 minute (user testing + telemetry)
- [ ] Duplicate detection warns per BR-005/006/007 (functional tests pass)
- [ ] Soft delete excludes from search; restore path verified (future API)
- [ ] Role enforcement: Manager cannot Create/Update/Delete (security tests pass)
- [ ] Baseline metrics captured (duplicate rate, creation time, search time)
- [ ] Rollback plan documented and tested
- [ ] Operations Manager and Sales Manager UAT sign-off

---

## Definition of Done (Applies to All Stories)

A story is **Done** when:

1. **Requirements Implemented**
   - All acceptance criteria from referenced user story satisfied
   - Business rules (BR-001 to BR-015) enforced
   - API contract (endpoints, validation, errors) matches specification

2. **Acceptance Criteria Met**
   - QA validates each AC via manual and automated tests
   - Edge cases covered (boundary, error, security scenarios)

3. **Code Reviewed**
   - Peer review completed (minimum 1 approver)
   - No unresolved review comments
   - Follows project coding standards (knowledge/project-standards.md)

4. **Tests Passed**
   - Unit tests: ≥ 80% coverage on new service/handler code
   - Integration tests: API contracts, database operations
   - E2E tests: Critical user journeys (create→search→detail→update→delete)
   - Performance tests: Meets NFR targets (where applicable)
   - Security tests: Auth, authz, injection, XSS, rate limiting

5. **Documentation Updated**
   - API contract updated if endpoints changed
   - README/runbooks updated for deployment/operations
   - Architecture decision log updated if new ADR created

6. **QA Approved**
   - QA sign-off on story completion
   - No blocking defects
   - Defects logged and triaged (P1/P2 fixed before Done)

7. **Ready For Release**
   - Merged to main branch
   - CI/CD pipeline passes (lint, test, build, deploy to staging)
   - Staging deployment verified
   - No merge conflicts with other in-progress stories

---

## Traceability Matrix

| Story | PRD Feature | PRD User Story | UI/UX Screen | API Endpoint | Technical Design |
|-------|-------------|----------------|--------------|--------------|------------------|
| STORY-001 | FT-01 Create Customer | US-CUST-001 | SC-02, SC-06 | EP-01 POST /customers | Section 7.2, 6.1.1 |
| STORY-002 | FT-02 Search Customer | US-CUST-002 | SC-01, SC-09 | EP-02 GET /customers | Section 7.5, 6.1.1 |
| STORY-003 | FT-03 Customer Detail | US-CUST-003 | SC-03 | EP-03 GET /customers/{id}, EP-04 GET /by-key | Section 6.1.1 |
| STORY-004 | FT-04 Update Customer | US-CUST-004 | SC-04, SC-07 | EP-05 PATCH /customers/{id} | Section 6.4, 6.6 |
| STORY-005 | FT-05 Delete Customer | US-CUST-005 | SC-05 | EP-06 DELETE /customers/{id} | Section 6.2, 6.6 |
| STORY-006 | Auth (NFR-07,08) | — | Login Page, Route Guards | EP-07, EP-08, EP-09 | Section 8, 7.3 |
| STORY-007 | Infra (NFR-07-10,18) | — | — | — | Section 2.2, 3.2, 11 |
| STORY-008 | Migration (BA) | — | — | EP-01 (batch) | Section 6.5, 14 |

> **No orphan stories** — Every story maps to PRD feature, user story, UI screen, API endpoint, and technical design section.

---

## Risk-Based Planning Notes

### High Risk / High Value — Prioritized Early
1. **STORY-002 (Search, 8 pts)** — Highest technical risk (VPS performance, pg_trgm); validates architecture
2. **STORY-006 (Auth)** — Security foundation; blocks all other API work
3. **STORY-007 (Infra)** — Environment prerequisite; validates VPS constraints

### Mitigation Actions
- **STORY-002**: Performance PoC (DEP-INT-01) must complete before story starts
- **STORY-006**: Implement first; provides auth for all subsequent API development
- **STORY-007**: Start in parallel; staging environment needed for integration testing

---

## Validation Checklist

| Checklist Item | Status |
|----------------|--------|
| [x] Every requirement mapped (5 PRD features + Auth + Infra + Migration) | ✅ |
| [x] Every acceptance criteria mapped (25 ACs across 5 user stories) | ✅ |
| [x] Stories sized correctly (Fibonacci: 3,5,8; none > 13) | ✅ |
| [x] No story > 13 points | ✅ |
| [x] Dependencies minimized (only 3 true dependencies) | ✅ |
| [x] Release grouping included (Single MVP Release) | ✅ |
| [x] Vertical slices preferred (each story = Backend + Frontend + QA) | ✅ |
| [x] Definition of Done included | ✅ |
| [x] MVP scope enforced (8 stories, all P1, no future scope) | ✅ |
| [x] No architecture generated (referenced only) | ✅ |
| [x] No source code generated | ✅ |
| [x] No implementation details generated (subtasks at team level only) | ✅ |

---

## Handoff Package for Next Agents

| Agent | Input Artifacts | Expected Output |
|-------|----------------|-----------------|
| **Backend Agent** | STORY-001,002,003,004,005,006 (Backend subtasks), API Contract, Technical Design | Go source code, migrations, unit/integration tests |
| **Frontend Agent** | STORY-001,002,003,004,005,006 (Frontend subtasks), UI/UX Design, API Contract | React/TypeScript app, components, E2E tests |
| **QA Agent** | All stories (QA subtasks), Acceptance Criteria, API Contract, NFRs | Test plans, Postman collections, k6 scripts, security test cases |
| **DevOps Agent** | STORY-007,008 (DevOps subtasks), Technical Design Sections 2,3,9,11,14 | Docker Compose, Nginx config, backup scripts, CI/CD pipeline |

---

*Jira Planning Structure v1.0*  
*Prepared by: Jira Planning Agent*  
*Date: Current*  
*Status: Ready for Sprint Planning*