# Product Requirement Document

## Customer Management Feature — CRM System

---

## 1. Document Control

| Attribute | Value |
|-----------|-------|
| **Document ID** | PRD-CRM-CUST-001 |
| **Version** | 1.0 |
| **Status** | Draft for Review |
| **Product Owner** | [Product Owner Name] |
| **Business Analyst** | Business Enablement Agent |
| **Created Date** | [Current Date] |
| **Last Updated** | [Current Date] |
| **Approved By** | [Operations Manager, Sales Manager] |
| **Classification** | Internal — Confidential |

---

## 2. Executive Summary

### 2.1 Purpose
This Product Requirement Document defines the business requirements for the **Customer Management** feature of the CRM System. It transforms the validated Business Analysis into actionable requirements for the UI/UX Designer Agent, Architect Agent, and QA Agent to proceed without further business clarification.

### 2.2 Business Context
Customer information is currently maintained manually in Excel files across multiple departments, causing:
- **Duplicate records** (no prevention mechanism)
- **Slow search** (manual, minutes per lookup)
- **Data inconsistency** (version conflicts via email sharing)
- **Operational waste** (5–10 minutes per customer creation)

### 2.3 Solution Vision
A centralized web-based application enabling Admins to create, read, update, and delete customer records with sub-5-second search and automated duplicate detection — replacing all Excel-based workflows.

### 2.4 Scope Statement
**In Scope (MVP)**: Create, Update, Delete (soft), Search, and Detail View for Customer records — 5 core CRUD operations.

**Out of Scope**: Analytics, Campaigns, Loyalty, Bulk Import/Export, Audit Trail, RBAC, Integrations, Mobile App.

---

## 3. Business Goals & Success Metrics

### 3.1 Primary Business Goal
> **Centralize customer data management** into a single authoritative application, eliminating distributed Excel files and reducing duplicate records by 80%.

### 3.2 Secondary Business Goals
| Goal ID | Goal | Success Metric | Target | Measurement |
|---------|------|----------------|--------|-------------|
| BG-01 | Accelerate customer creation | Creation time (end-to-end) | < 1 minute | Application telemetry |
| BG-02 | Enable instant customer lookup | Search response time (p95) | < 5 seconds | Load testing / telemetry |
| BG-03 | Improve data quality | Duplicate record reduction | 80% vs. baseline | Quarterly audit |
| BG-04 | Drive user adoption | Daily active admin usage | > 90% | Login analytics |
| BG-05 | Ensure data accuracy | Record error rate | < 2% | Random sampling |
| BG-06 | Maintain operational reliability | System availability (business hours) | > 99% | Infrastructure monitoring |
| BG-07 | Validate user satisfaction | Admin satisfaction score | > 4/5 | Post-launch survey (30/60/90 days) |

> **Critical**: Baseline measurements for current duplicate rate, creation time, and search time **must be captured before launch** to validate BG-03.

---

## 4. User Personas

| Persona | Role | Primary Goals | Pain Points | Access Level |
|---------|------|---------------|-------------|--------------|
| **Admin** (Primary) | System Operator | Create/update/delete/search customers efficiently; maintain data quality | Excel version conflicts; duplicate cleanup; slow multi-file search | Full CRUD |
| **Manager** (Secondary) | Supervisor | View customer details; verify data quality; export for reporting | Inconsistent data across departments; no real-time view | Read + Search + Export (Future) |

### 4.1 User Journey Summary
| Persona | Key Journeys (MVP) |
|---------|-------------------|
| Admin | Create Customer → Search Customer → View Detail → Update Customer → Delete (Soft) Customer |
| Manager | Search Customer → View Detail → (Future: Export) |

---

## 5. Feature Scope

### 5.1 In Scope (MVP — Must Have)
| Feature ID | Feature | Business Justification |
|------------|---------|------------------------|
| FT-01 | **Create Customer** | Replaces manual Excel entry; foundation capability |
| FT-02 | **Search Customer** | Addresses primary pain point (slow search); highest value |
| FT-03 | **Customer Detail View** | Single consolidated view replaces multi-file lookup |
| FT-04 | **Update Customer** | Maintains data accuracy post-creation |
| FT-05 | **Delete Customer (Soft)** | Data lifecycle management; recoverable deletion |

### 5.2 Out of Scope (Explicitly Excluded)
| Feature | Reason |
|---------|--------|
| CRM Analytics | Separate strategic initiative; requires data warehouse |
| Marketing Campaigns | Different business process; separate budget/stakeholders |
| Customer Loyalty Program | Product feature, not data management; future phase |
| Bulk Import/Export | Post-MVP; migration aid only |
| Audit Trail / Change History | Compliance not required for MVP |
| Role-Based Access Control | Only two roles (Admin/Manager) in MVP |
| Advanced Search/Filters | Basic search sufficient for MVP |
| Third-party Integrations | No external systems identified |
| Mobile Application | Responsive web acceptable |

### 5.3 Future Scope (Phase 2+)
| Feature | Trigger for Inclusion |
|---------|----------------------|
| Bulk Import/Export | Migration volume exceeds manual capacity |
| Duplicate Detection & Merge | After baseline measured; automates 80% target |
| Audit Trail | Compliance or operational need identified |
| RBAC | More user types added (support, finance) |
| Customer Segmentation/Tags | Sales requests targeting capability |
| API for Integrations | Other systems need customer data (ERP, support) |
| Advanced Search/Filters | User feedback on search limitations |

### 5.4 Items Needing Clarification (Pre-Development)
| Item | Clarification Required | Owner | Deadline |
|------|------------------------|-------|----------|
| Soft vs. Hard Delete | Business rule for data retention; compliance implications | Operations Manager | Pre-sprint |
| Customer Data Model | Required/optional fields, validation rules, formats | Product Owner + Admin | Pre-sprint |
| Data Migration Strategy | One-time vs. phased; cleansing approach; ownership | Operations Manager | Pre-sprint |
| Search Criteria | Searchable fields; fuzzy vs. exact match; result ranking | Product Owner + Admin | Pre-sprint |
| Duplicate Detection Rules | Matching logic (name+phone? email? fuzzy?); merge vs. block | Product Owner + Admin | Pre-sprint |
| Responsive Design Breakpoints | Manager field access on tablet/phone | UI/UX Agent | Design phase |

---

## 6. Functional Requirements

> **Convention**: FR-<Feature ID>-<Sequence>  
> Requirements describe **business capability**, **user behavior**, and **expected result** — not technical implementation.

### 6.1 Create Customer (FT-01)

| Requirement ID | Requirement |
|----------------|-------------|
| FR-01-01 | Admin shall be able to create a new customer record by entering required and optional customer information through a guided form. |
| FR-01-02 | The system shall validate all required fields before allowing submission. |
| FR-01-03 | The system shall check for potential duplicate customers based on configured matching rules before creating a new record. |
| FR-01-04 | If a potential duplicate is detected, the system shall present the matching record(s) to the Admin for confirmation before proceeding. |
| FR-01-05 | Upon successful creation, the system shall display the new customer's detail view and confirm the record is immediately searchable. |
| FR-01-06 | Customer creation (form load → submit → confirmation) shall complete in under 1 minute under normal conditions. |
| FR-01-07 | The system shall assign a unique customer identifier automatically upon creation. |

### 6.2 Search Customer (FT-02)

| Requirement ID | Requirement |
|----------------|-------------|
| FR-02-01 | Admin and Manager shall be able to search customers using a single search input supporting multiple criteria (name, phone, email, ID, company). |
| FR-02-02 | Search shall return results in under 5 seconds (95th percentile) for up to 10,000 records. |
| FR-02-03 | Search shall support partial/fuzzy matching (e.g., "john" finds "John Smith", "Johnson Corp"). |
| FR-02-04 | Search results shall display key identifying fields (Name, Phone, Email, Company, Customer ID) for quick recognition. |
| FR-02-05 | Selecting a result shall navigate to the Customer Detail View (FT-03). |
| FR-02-06 | If no results match, the system shall display a clear "no results" message with option to create new customer. |
| FR-02-07 | Recent searches shall be accessible for quick repeat access (Admin only). |

### 6.3 Customer Detail View (FT-03)

| Requirement ID | Requirement |
|----------------|-------------|
| FR-03-01 | The detail view shall display all customer attributes in a structured, readable layout. |
| FR-03-02 | The detail view shall be accessible from search results, create confirmation, and direct URL (for sharing). |
| FR-03-03 | Admin shall have inline or button access to Edit and Delete actions from the detail view. |
| FR-03-04 | Manager shall have read-only access to the detail view. |
| FR-03-05 | The detail view shall load in under 2 seconds. |

### 6.4 Update Customer (FT-04)

| Requirement ID | Requirement |
|----------------|-------------|
| FR-04-01 | Admin shall be able to modify any editable customer field from the detail view. |
| FR-04-02 | The system shall validate all fields on update using the same rules as creation. |
| FR-04-03 | If an update creates a potential duplicate conflict, the system shall warn the Admin before saving. |
| FR-04-04 | Updated records shall be immediately reflected in search results. |
| FR-04-05 | Update operation shall complete in under 1 minute. |

### 6.5 Delete Customer (Soft) (FT-05)

| Requirement ID | Requirement |
|----------------|-------------|
| FR-05-01 | Admin shall be able to mark a customer record as deleted (soft delete) from the detail view. |
| FR-05-02 | Soft-deleted customers shall be excluded from standard search results and list views. |
| FR-05-03 | Soft-deleted customers shall be recoverable by Admin within a defined retention period (TBD). |
| FR-05-04 | The system shall require confirmation before soft delete, displaying the customer name and ID. |
| FR-05-05 | Soft delete shall not cascade to related data (no related data in MVP). |

---

## 7. User Stories & Acceptance Criteria

> **Format**: Story ID | Title | As a | I want | So that | Acceptance Criteria (Given/When/Then) | Story Points | Priority

### 7.1 Create Customer

| Story ID | US-CUST-001 |
|----------|-------------|
| **Title** | Create New Customer Record |
| **As a** | Admin |
| **I want** | to enter customer information in a structured form |
| **So that** | the customer is added to the centralized database and immediately available for search |

**Acceptance Criteria**:
- **AC-001**: Given Admin is on the Create Customer page, When Admin fills all required fields with valid data and submits, Then the customer record is created and Admin is redirected to the Customer Detail View showing the new record.
- **AC-002**: Given Admin is on the Create Customer page, When Admin leaves a required field empty and attempts to submit, Then the system displays a validation error indicating the missing field(s) and prevents submission.
- **AC-003**: Given Admin enters customer data matching an existing record (per duplicate rules), When Admin submits, Then the system displays the potential duplicate(s) and requires explicit confirmation to proceed or cancel.
- **AC-004**: Given a new customer is created, When Admin searches for the customer by any searchable field, Then the customer appears in results within 5 seconds.
- **AC-005**: Given Admin creates a customer, When the operation completes, Then total elapsed time from form load to confirmation is under 1 minute.

**Story Points**: 5 | **Priority**: Must Have (P1)

---

### 7.2 Search Customer

| Story ID | US-CUST-002 |
|----------|-------------|
| **Title** | Search Customers by Multiple Criteria |
| **As a** | Admin / Manager |
| **I want** | to find customers quickly using a single search box |
| **So that** | I can locate customer records in under 5 seconds without checking multiple files |

**Acceptance Criteria**:
- **AC-001**: Given Admin/Manager enters a search term (name, phone, email, ID, or company), When search is executed, Then results matching any searchable field are returned in under 5 seconds (p95).
- **AC-002**: Given search returns results, When Admin/Manager views the results list, Then each row displays Customer Name, Phone, Email, Company, and Customer ID.
- **AC-003**: Given search returns results, When Admin/Manager clicks a result, Then the Customer Detail View for that customer loads in under 2 seconds.
- **AC-004**: Given search returns zero results, When the results page renders, Then a "No customers found" message displays with a "Create New Customer" button.
- **AC-005**: Given Admin has performed recent searches, When Admin focuses the search input, Then the last 5 search terms are suggested for quick re-use.

**Story Points**: 8 | **Priority**: Must Have (P1)

---

### 7.3 Customer Detail View

| Story ID | US-CUST-003 |
|----------|-------------|
| **Title** | View Complete Customer Details |
| **As a** | Admin / Manager |
| **I want** | to see all customer information in one place |
| **So that** | I don't need to cross-reference multiple Excel files |

**Acceptance Criteria**:
- **AC-001**: Given Admin/Manager navigates to a Customer Detail View, When the page loads, Then all customer fields (required and optional) are displayed in a logical grouping.
- **AC-002**: Given Admin views a customer detail, When Admin clicks "Edit", Then the Update Customer form pre-populates with current values.
- **AC-003**: Given Admin views a customer detail, When Admin clicks "Delete", Then the soft delete confirmation flow initiates.
- **AC-004**: Given Manager views a customer detail, When the page loads, Then no Edit or Delete actions are visible.
- **AC-005**: Given a direct URL to a customer detail is accessed, When the user is authenticated, Then the correct customer detail loads (or 404 if not found/access denied).

**Story Points**: 3 | **Priority**: Must Have (P1)

---

### 7.4 Update Customer

| Story ID | US-CUST-004 |
|----------|-------------|
| **Title** | Update Existing Customer Record |
| **As a** | Admin |
| **I want** | to modify customer information |
| **So that** | records remain accurate and current |

**Acceptance Criteria**:
- **AC-001**: Given Admin is on the Edit Customer form, When Admin modifies fields and saves, Then the changes are persisted and the Detail View reflects updated values.
- **AC-002**: Given Admin modifies a field to a value that matches an existing customer (per duplicate rules), When Admin saves, Then the system warns of potential duplicate and requires confirmation.
- **AC-003**: Given Admin updates a customer, When the save completes, Then the updated record is immediately findable via search with new values.
- **AC-004**: Given Admin cancels the edit, When the cancel action is confirmed, Then no changes are persisted and the Detail View shows original values.
- **AC-005**: Given Admin updates a customer, When the operation completes, Then total elapsed time is under 1 minute.

**Story Points**: 5 | **Priority**: Must Have (P1)

---

### 7.5 Delete Customer (Soft)

| Story ID | US-CUST-005 |
|----------|-------------|
| **Title** | Soft Delete Customer Record |
| **As a** | Admin |
| **I want** | to mark a customer as deleted without permanent data loss |
| **So that** | accidental deletions can be recovered and data integrity is maintained |

**Acceptance Criteria**:
- **AC-001**: Given Admin views a customer detail, When Admin clicks "Delete" and confirms, Then the customer is marked as deleted and removed from standard search results.
- **AC-002**: Given a customer is soft-deleted, When Admin searches for that customer, Then the customer does not appear in standard search results.
- **AC-003**: Given a customer is soft-deleted, When Admin accesses the deleted customer list (Future: admin-only view), Then the customer appears with a "Restore" option.
- **AC-004**: Given Admin attempts to delete, When the confirmation modal displays, Then it shows the customer name and ID for verification.
- **AC-005**: Given a soft-deleted customer is restored, When Admin confirms restore, Then the customer reappears in standard search with all data intact.

**Story Points**: 3 | **Priority**: Must Have (P1)

---

## 8. Business Rules

> **Convention**: BR-<Sequence>  
> Rules define policies, constraints, and business decisions — not technical enforcement.

| Rule ID | Business Rule | Description |
|---------|---------------|-------------|
| **BR-001** | **Unique Customer Identifier** | Every customer must have a system-generated unique ID (format: CUST-YYYY-NNNNNN) assigned at creation. |
| **BR-002** | **Required Fields for Creation** | Customer Name, Primary Phone, and Email are mandatory. All other fields are optional. |
| **BR-003** | **Phone Number Format** | Phone numbers must be stored in E.164 format (+<country><number>). Input accepts local formats; system normalizes on save. |
| **BR-004** | **Email Uniqueness (Soft)** | Email addresses should be unique across active customers. Duplicate email triggers warning but does not block creation (per BR-006). |
| **BR-005** | **Duplicate Detection Criteria** | A potential duplicate exists when: (Name similarity > 85% AND Phone match) OR (Email exact match) OR (Company exact match AND Phone match). *Exact logic TBD with stakeholders.* |
| **BR-006** | **Duplicate Handling on Create** | If duplicate detected: System presents match(es) to Admin. Admin may: (a) Cancel creation, (b) Proceed anyway (new record created), (c) Select existing record to view/edit instead. |
| **BR-007** | **Duplicate Handling on Update** | If update creates duplicate conflict: System warns Admin. Admin may: (a) Cancel update, (b) Proceed anyway. |
| **BR-008** | **Soft Delete Retention** | Soft-deleted records are retained for 90 days before permanent purge eligibility. Restore is allowed within retention period. |
| **BR-009** | **Search Scope** | Standard search returns only active (non-deleted) customers. Deleted customers require explicit "Include Deleted" filter (Admin only). |
| **BR-010** | **Data Ownership** | All customer records are owned by the organization. No department-level ownership in MVP. |
| **BR-011** | **Field Length Limits** | Name: 200 chars; Company: 200 chars; Phone: 20 chars (E.164); Email: 254 chars; Address: 500 chars; Notes: 2000 chars. |
| **BR-012** | **Case Sensitivity** | Search is case-insensitive. Email stored lowercase. Name/Company preserve input casing. |
| **BR-013** | **Concurrent Edit Protection** | If two Admins edit the same customer simultaneously, the second save shall warn of concurrent modification and offer to reload. |
| **BR-014** | **Manager Permissions** | Manager role: Read-only access to Search and Detail View. No Create, Update, Delete. |
| **BR-015** | **Audit Logging (Future-Ready)** | All Create, Update, Delete actions shall capture: Actor, Timestamp, Action, Field Changes (for Update). Storage/retention TBD. |

---

## 9. Non-Functional Requirements (High-Level)

| NFR ID | Category | Requirement | Target / Expectation |
|--------|----------|-------------|----------------------|
| **NFR-01** | **Performance** | Search response time (p95) | < 5 seconds for 10,000 records |
| **NFR-02** | **Performance** | Customer creation time (end-to-end) | < 1 minute |
| **NFR-03** | **Performance** | Customer detail view load time | < 2 seconds |
| **NFR-04** | **Performance** | Update operation time | < 1 minute |
| **NFR-05** | **Availability** | System uptime during business hours (Mon–Fri 8am–6pm) | > 99% |
| **NFR-06** | **Availability** | Planned maintenance window | Weekend, 2-hour max, advance notice |
| **NFR-07** | **Security** | Authentication required for all access | Session-based; timeout 30 min inactivity |
| **NFR-08** | **Security** | Role-based authorization | Admin (CRUD), Manager (Read/Search) |
| **NFR-09** | **Security** | Data in transit encryption | TLS 1.2+ |
| **NFR-10** | **Security** | Data at rest encryption | VPS disk encryption |
| **NFR-11** | **Usability** | Responsive design | Desktop (primary), Tablet (Manager usable) |
| **NFR-12** | **Usability** | Browser support | Chrome, Firefox, Edge (latest 2 versions) |
| **NFR-13** | **Usability** | Accessibility | WCAG 2.1 AA compliance |
| **NFR-14** | **Scalability** | Record capacity | 10,000 active records + 2,000 deleted (Year 1) |
| **NFR-15** | **Scalability** | Growth rate | 200 records/month |
| **NFR-16** | **Reliability** | Backup frequency | Daily automated backup; point-in-time recovery |
| **NFR-17** | **Reliability** | Data loss tolerance | Zero data loss for committed transactions |
| **NFR-18** | **Maintainability** | Deployment | Zero-downtime deployment capability |
| **NFR-19** | **Localization** | Language | English only (MVP) |
| **NFR-20** | **Localization** | Date/Number formats | Locale-aware (user preference) |

> **Note**: Technical implementation of NFRs (indexing, caching, connection pooling, etc.) is the responsibility of the Architect Agent.

---

## 10. Data Requirements (Business View)

> **Logical data attributes only** — no schema, tables, or indexes.

### 10.1 Customer Entity Attributes

| Attribute | Required | Type (Business) | Validation Rules | Notes |
|-----------|----------|-----------------|------------------|-------|
| Customer ID | System-generated | Alphanumeric | Format: CUST-YYYY-NNNNNN | Unique, immutable |
| Full Name | Yes | Text (200) | Not empty; trim whitespace | Primary identifier |
| Company Name | No | Text (200) | Trim whitespace | |
| Primary Phone | Yes | Phone (E.164) | Valid E.164 format; normalized on input | Duplicate detection key |
| Secondary Phone | No | Phone (E.164) | Valid E.164 if provided | |
| Primary Email | Yes | Email (254) | Valid RFC 5322; stored lowercase | Duplicate detection key |
| Secondary Email | No | Email (254) | Valid RFC 5322 if provided | |
| Address Line 1 | No | Text (200) | | |
| Address Line 2 | No | Text (200) | | |
| City | No | Text (100) | | |
| State/Province | No | Text (100) | | |
| Postal Code | No | Text (20) | | |
| Country | No | Text (100) | ISO 3166-1 alpha-2 preferred | |
| Customer Type | No | Enum | [Individual, Business, Government, Other] | Default: Individual |
| Status | System | Enum | [Active, Deleted] | Soft delete = Deleted |
| Notes | No | Text (2000) | | Free-form |
| Created At | System | Timestamp | Auto-set on creation | |
| Created By | System | User Reference | Admin who created | |
| Updated At | System | Timestamp | Auto-set on each update | |
| Updated By | System | User Reference | Admin who last updated | |
| Deleted At | System | Timestamp | Set on soft delete | Null if active |
| Deleted By | System | User Reference | Admin who deleted | Null if active |

### 10.2 Searchable Fields (MVP)
- Full Name (fuzzy/partial)
- Company Name (fuzzy/partial)
- Primary Phone (exact/partial)
- Secondary Phone (exact/partial)
- Primary Email (exact/partial)
- Secondary Email (exact/partial)
- Customer ID (exact)
- City (exact)
- Customer Type (exact filter)

---

## 11. Dependencies

### 11.1 Internal Dependencies
| Dependency ID | Description | Dependent On | Impact if Delayed |
|---------------|-------------|--------------|-------------------|
| DEP-INT-01 | **Performance Proof-of-Concept** | Architect Agent | Development cannot start until VPS performance validated with 5,000 records |
| DEP-INT-02 | **Data Migration Plan** | Operations Manager + Product Owner | MVP launch blocked if dirty data loaded; parallel run required |
| DEP-INT-03 | **UI/UX Design Completion** | UI/UX Designer Agent | Frontend development blocked without approved designs |
| DEP-INT-04 | **Technical Architecture Approval** | Architect Agent | Backend/Frontend agents need approved architecture |
| DEP-INT-05 | **Test Environment Provisioning** | DevOps Agent | QA cannot validate without environment |

### 11.2 External Dependencies
| Dependency ID | Description | Owner | Risk Level |
|---------------|-------------|-------|------------|
| DEP-EXT-01 | **VPS Infrastructure Stability** | Infrastructure Team | High — 2 CPU / 2 GB RAM constraint |
| DEP-EXT-02 | **Existing Tech Stack Compatibility** | Architect Agent | Medium — Assumption A1 validation needed |
| DEP-EXT-03 | **Stakeholder Availability for UAT** | Operations/Sales Managers | Medium — Sign-off required for launch |

---

## 12. Risks & Mitigations

| Risk ID | Risk | Probability | Impact | Mitigation Strategy | Owner |
|---------|------|-------------|--------|---------------------|-------|
| **RSK-01** | VPS performance insufficient for 5,000+ records | High | High | PoC before dev; pagination; query optimization; caching (Architect) | Architect |
| **RSK-02** | Data migration errors from Excel | High | High | Cleansing scripts; parallel run; rollback plan; validation reports | Product Owner + Ops Mgr |
| **RSK-03** | Low user adoption (Excel habit) | Medium | High | Phased rollout; admin champions; training; quick wins demo | Product Owner + Ops Mgr |
| **RSK-04** | Change resistance from established workflows | High | Medium | Stakeholder involvement in design; clear communication | Product Owner |
| **RSK-05** | Single point of failure (no HA) | Low | High | Backup/restore documented; manual fallback procedure | DevOps + Architect |
| **RSK-06** | Search degrades with data growth | Medium | High | Indexing strategy; archive policy; per-release benchmarks | Architect |
| **RSK-07** | Small team capacity limits quality | High | Medium | Scope discipline (MoSCoW); reusable components; automated tests | Product Owner + Tech Lead |
| **RSK-08** | Scope creep during development | Medium | High | Frozen MVP scope; change control board for additions | Product Owner |
| **RSK-09** | Key person risk (small team) | Medium | High | Documentation; pair programming; knowledge sharing | Tech Lead |
| **RSK-10** | Duplicate detection rules too strict/loose | Medium | Medium | Configurable thresholds; Admin override; post-launch tuning | Product Owner + Admin |

---

## 13. Assumptions

| Assumption ID | Assumption | Validation Status | Impact if Invalid |
|---------------|------------|-------------------|-------------------|
| **ASM-01** | Existing tech stack supports web-based CRUD application | Pending (Architect) | Architecture redesign; delay |
| **ASM-02** | 5,000 initial records + 200/month growth is accurate | Pending (Ops Mgr) | Capacity planning wrong; performance issues |
| **ASM-03** | "Internal application only" — no external access | Confirmed (Stakeholders) | Security model insufficient if exposed later |
| **ASM-04** | Admin and Manager roles cover all user needs | Pending (Stakeholders) | Missing roles require RBAC redesign |
| **ASM-05** | Soft delete is acceptable for "Delete Customer" | Pending (Legal/Compliance) | Compliance/legal issues if hard delete required |
| **ASM-06** | No integration requirements with other systems | Confirmed (Stakeholders) | Future integration cost higher |
| **ASM-07** | VPS is dedicated to this application | Pending (Infra Team) | Resource contention degrades performance |
| **ASM-08** | Data migration from Excel is a separate activity | Pending (Ops Mgr) | MVP launch blocked by dirty data |
| **ASM-09** | Responsive web (not mobile app) satisfies Manager field access | Pending (Sales Mgr) | Mobile app needed if not |
| **ASM-10** | No regulatory compliance requirements (GDPR, etc.) | Pending (Legal) | Compliance features needed if wrong |

---

## 14. Acceptance Criteria Summary (Release Gate)

The MVP release is **accepted** when all criteria are met:

| Criterion | Validation Method |
|-----------|-------------------|
| All 5 Must-Have features (FT-01 to FT-05) implemented and demoed | UAT with Admin/Manager |
| Search p95 < 5 seconds with 5,000 test records | Load test report (Architect) |
| Customer creation < 1 minute (end-to-end) | User testing + telemetry |
| Duplicate detection warns per BR-005/006/007 | Functional test cases |
| Soft delete excludes from search; restore works | Functional test cases |
| Role enforcement: Manager cannot Create/Update/Delete | Security test cases |
| Zero critical/severe defects open | QA sign-off |
| Baseline metrics captured (current duplicate rate, creation time, search time) | Pre-launch audit |
| Rollback plan documented and tested | DevOps validation |
| Operations Manager and Sales Manager sign-off | Formal UAT acceptance |

---

## 15. Handoff Package for Next Agents

### 15.1 For UI/UX Designer Agent
- **Required**: User flows for 5 stories (US-CUST-001 to 005)
- **Required**: Wireframes for Create, Search Results, Detail, Edit, Delete Confirmation
- **Required**: Responsive breakpoints (desktop primary, tablet for Manager)
- **Required**: Accessibility annotations (WCAG 2.1 AA)
- **Input**: This PRD (Sections 4, 6, 7, 9, 10)

### 15.2 For Architect Agent
- **Required**: Technical architecture for 5 CRUD features
- **Required**: Performance PoC on target VPS (2 CPU/2GB) with 5,000 records
- **Required**: Data model design (logical → physical)
- **Required**: API contract (internal) for CRUD operations
- **Required**: Security model (auth, authz, encryption)
- **Required**: Deployment architecture (zero-downtime, backup)
- **Input**: This PRD (Sections 6, 9, 10, 11, 12)

### 15.3 For QA Agent
- **Required**: Test plan covering all acceptance criteria (Section 7)
- **Required**: Performance test scripts (search, create, update)
- **Required**: Security test cases (auth, authz, injection)
- **Required**: Accessibility test checklist
- **Required**: UAT coordination with Admin/Manager
- **Input**: This PRD (Sections 7, 9, 14)

---

## 16. Appendices

### 16.1 Glossary
| Term | Definition |
|------|------------|
| **Admin** | Primary system operator responsible for customer data management |
| **Manager** | Secondary user with read/search access for oversight |
| **Soft Delete** | Logical deletion marking record as inactive without physical removal |
| **E.164** | International phone number format: +[country code][subscriber number] |
| **p95** | 95th percentile — 95% of requests faster than this value |
| **MVP** | Minimum Viable Product — Must Have features only |
| **PoC** | Proof of Concept — Technical validation before commitment |

### 16.2 Reference Documents
- Business Analysis Document (../business/business-analysis.md)
- Project Standards (knowledge/project-standards.md)
- Non-Functional Requirements (knowledge/non-functional-requirements.md)
- Documentation Standard (knowledge/documentation-standard.md)

### 16.3 Change Log
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Current Date] | Product Owner Agent | Initial PRD from Business Analysis |

---

## 17. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Operations Manager | | | |
| Sales Manager | | | |
| Architect (Technical Feasibility) | | | |
| UI/UX Lead (Design Feasibility) | | | |

---

*End of Document*