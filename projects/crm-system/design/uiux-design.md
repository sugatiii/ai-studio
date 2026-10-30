# UI/UX Design Specification

## Customer Management Feature — CRM System

---

## 1. Document Control

| Attribute | Value |
|-----------|-------|
| **Document ID** | UX-CRM-CUST-001 |
| **Version** | 1.0 |
| **Status** | Draft for Review |
| **UI/UX Designer** | UI/UX Designer Agent |
| **Created Date** | [Current Date] |
| **Last Updated** | [Current Date] |
| **Approved By** | [Product Owner, Operations Manager] |
| **Classification** | Internal — Confidential |

---

## 2. User Personas

### 2.1 Primary Persona: Admin (System Operator)

| Attribute | Detail |
|-----------|--------|
| **Role** | System Operator / Data Steward |
| **Primary Goals** | Create, update, search, and manage customer records efficiently; maintain data quality; eliminate Excel workflows |
| **Pain Points** | Duplicate records across Excel files; slow multi-file search (5-10 min); version conflicts via email; manual data entry errors |
| **Technical Proficiency** | Moderate — comfortable with web applications, keyboard shortcuts preferred |
| **Device Context** | Desktop (primary, 8+ hours/day); occasional tablet |
| **Access Level** | Full CRUD (Create, Read, Update, Soft Delete) |
| **Success Metrics** | < 1 min creation time; < 5 sec search; zero duplicate entries |

### 2.2 Secondary Persona: Manager (Supervisor)

| Attribute | Detail |
|-----------|--------|
| **Role** | Sales/Operations Manager |
| **Primary Goals** | View customer details for oversight; verify data quality; quick lookup during meetings |
| **Pain Points** | Inconsistent data across departments; no real-time view; cannot trust Excel exports |
| **Technical Proficiency** | Low-Moderate — prefers simple, visual interfaces; touch-friendly on tablet |
| **Device Context** | Tablet (field/meetings, 60%); Desktop (office, 40%) |
| **Access Level** | Read + Search only (no Create/Update/Delete) |
| **Success Metrics** | < 5 sec search; detail view loads < 2 sec; works on tablet in field |

---

## 3. User Goals & Success Definitions

| Goal ID | User Goal | Success Definition | Failure Definition |
|---------|-----------|-------------------|-------------------|
| UG-01 | Create new customer record | Record created in < 1 min; immediately searchable; no duplicates | Validation errors; duplicate created; > 1 min elapsed |
| UG-02 | Find existing customer | Correct customer found in < 5 sec via single search box | No results for valid query; wrong results; > 5 sec |
| UG-03 | View complete customer details | All fields visible in logical groups; loads < 2 sec | Missing fields; slow load; confusing layout |
| UG-04 | Update customer information | Changes saved in < 1 min; immediately reflected in search | Validation errors; duplicate conflict not warned; data loss |
| UG-05 | Remove customer record (soft) | Record hidden from search; recoverable within 90 days | Hard delete; not hidden from search; not recoverable |
| UG-06 | Avoid duplicate entries | System warns on potential duplicates; admin makes informed decision | Duplicate created without warning; false positives block valid entries |

---

## 4. User Pain Points (Current State)

| Pain Point | Current Impact | Design Response |
|------------|----------------|-----------------|
| **Duplicate records across Excel files** | 80% duplicate rate target reduction | Real-time duplicate detection with match preview before create/update |
| **Slow search (minutes per lookup)** | 5-10 min per search | Single search box, fuzzy matching, < 5 sec p95, recent searches |
| **Data inconsistency (version conflicts)** | Email sharing causes conflicts | Single source of truth; real-time updates; concurrent edit warning |
| **Operational waste (5-10 min per creation)** | Manual entry, cross-file validation | Guided form, auto-format phone/email, inline validation, < 1 min target |
| **No audit trail** | Cannot track changes | Future-ready audit logging (BR-015); created/updated by timestamps visible |

---

## 5. User Tasks (Frequency & Criticality)

| Task | Frequency | Criticality | Sensitivity | Primary Persona |
|------|-----------|-------------|-------------|-----------------|
| Search Customer | Very High (50+/day) | Critical | Low | Admin, Manager |
| View Customer Detail | High (30+/day) | Critical | Medium | Admin, Manager |
| Create Customer | Medium (10-20/day) | High | High (data quality) | Admin |
| Update Customer | Medium (10-15/day) | High | High (data quality) | Admin |
| Soft Delete Customer | Low (1-5/day) | Medium | High (data loss risk) | Admin |
| Recover Deleted Customer | Very Low (< 1/week) | Low | High | Admin |

---

## 6. User Journeys

### 6.1 Journey: Create New Customer (Admin)

```text
Entry Point: Dashboard → "Create Customer" button
    ↓
Action: Fill guided form (Name*, Phone*, Email*, Company, Address, Type, Notes)
    ↓
Decision: Submit form
    ↓
System Response: Validate required fields → Check duplicates
    ↓
Decision Point: Duplicate detected?
    ├─ Yes → Show match preview → Admin: Cancel / Proceed Anyway / View Existing
    └─ No → Create record → Assign CUST-ID
    ↓
Success Outcome: Redirect to Detail View → Success toast "Customer created"
    ↓
Verification: Search new customer → Appears in results < 5 sec
```

### 6.2 Journey: Search & View Customer (Admin/Manager)

```text
Entry Point: Dashboard / Global Search Bar (always visible)
    ↓
Action: Type search term (name, phone, email, ID, company)
    ↓
System Response: Debounced search → Results in < 5 sec
    ↓
Decision Point: Results found?
    ├─ Yes → Display results table/cards (Name, Phone, Email, Company, ID)
    │    ↓
    │    Action: Click result row
    │    ↓
    │    System Response: Load Detail View < 2 sec
    │    ↓
    │    Success Outcome: Full customer details displayed
    │         ├─ Admin: Edit/Delete buttons visible
    │         └─ Manager: Read-only view
    └─ No → Show "No customers found" + "Create New Customer" CTA
```

### 6.3 Journey: Update Customer (Admin)

```text
Entry Point: Customer Detail View → "Edit" button
    ↓
Action: Modify fields in pre-populated form
    ↓
Decision: Save changes
    ↓
System Response: Validate → Check duplicates on changed fields
    ↓
Decision Point: Duplicate conflict?
    ├─ Yes → Warn Admin → Cancel / Proceed Anyway
    └─ No → Save → Update timestamps
    ↓
Success Outcome: Return to Detail View → Updated values shown → Success toast
    ↓
Verification: Search with new values → Returns updated record
```

### 6.4 Journey: Soft Delete Customer (Admin)

```text
Entry Point: Customer Detail View → "Delete" button
    ↓
System Response: Confirmation modal (Name, ID, "This can be restored within 90 days")
    ↓
Decision: Confirm delete
    ↓
System Response: Mark status=Deleted, set DeletedAt/DeletedBy
    ↓
Success Outcome: Redirect to Search/List → Success toast "Customer archived"
    ↓
Verification: Search for customer → Not in standard results
    ↓
Recovery Path (Future): Admin-only "Deleted Customers" view → Restore button
```

---

## 7. User Flows

### 7.1 Happy Path Flows

#### Flow 1: Create Customer (No Duplicates)
```text
Dashboard → [Create Customer] → Create Form (all valid) → [Submit] 
→ Duplicate Check (none) → Create Record → Detail View → [Success Toast]
→ Search Verification → Results Show New Customer
```

#### Flow 2: Search & View (Results Found)
```text
Dashboard → Search Input → [Type "john"] → Debounced Search (300ms)
→ Results Table → [Click Row] → Detail View Loads → View Details
```

#### Flow 3: Update Customer (No Conflicts)
```text
Detail View → [Edit] → Edit Form (pre-filled) → [Modify Fields] → [Save]
→ Validation Pass → Duplicate Check (none) → Save → Detail View (updated)
→ [Success Toast]
```

#### Flow 4: Soft Delete Customer
```text
Detail View → [Delete] → Confirmation Modal → [Confirm "Archive"]
→ Soft Delete → Search/List View → [Success Toast "Customer archived"]
```

---

### 7.2 Validation Path Flows

#### Flow 5: Create Customer — Required Field Missing
```text
Create Form → [Submit with empty Name] → Inline Validation Error
→ Focus first invalid field → Error message: "Customer Name is required"
→ [Correct Field] → [Submit] → Continue Happy Path
```

#### Flow 6: Create Customer — Invalid Format
```text
Create Form → [Enter invalid email "john@"] → [Blur Field]
→ Inline Validation Error: "Enter a valid email address"
→ [Correct Format] → [Submit] → Continue Happy Path
```

#### Flow 7: Update Customer — Validation Error
```text
Edit Form → [Clear Phone field] → [Save] → Inline Error: "Primary Phone is required"
→ Focus Phone field → [Enter Valid Phone] → [Save] → Continue Happy Path
```

---

### 7.3 Error Path Flows

#### Flow 8: Create Customer — System Error
```text
Create Form → [Submit] → API Error (500/timeout)
→ Toast Error: "Unable to create customer. Please try again."
→ Form retains entered data → [Retry] or [Cancel]
```

#### Flow 9: Search — System Error
```text
Search Input → [Enter term] → API Error
→ Results Area: "Unable to load results. [Retry Button]"
→ [Retry] → Re-execute search
```

#### Flow 10: Detail View — Not Found / Access Denied
```text
Direct URL / Stale Link → 404 or 403
→ Page: "Customer not found" / "Access denied"
→ [Back to Search] button
```

---

### 7.4 Recovery Path Flows

#### Flow 11: Duplicate Detected on Create
```text
Create Form → [Submit] → Duplicate Check → Match Found
→ Duplicate Modal: "Potential duplicate found" + Match Preview Card
→ Admin Options:
    ├─ [Cancel] → Return to Form (data preserved)
    ├─ [View Existing] → Navigate to Existing Detail View
    └─ [Proceed Anyway] → Create New Record → Detail View
```

#### Flow 12: Duplicate Detected on Update
```text
Edit Form → [Save] → Duplicate Check → Conflict Found
→ Warning Modal: "This change matches existing customer"
→ Admin Options:
    ├─ [Cancel] → Return to Edit Form (changes preserved)
    └─ [Proceed Anyway] → Save → Detail View
```

#### Flow 13: Concurrent Edit Warning
```text
Admin A opens Edit Form → Admin B opens Edit Form
→ Admin A [Saves] → Admin B [Saves]
→ Admin B: Warning Modal "Another user updated this record"
→ Options: [Reload & Reapply] / [Overwrite] / [Cancel]
```

#### Flow 14: Recover Soft-Deleted Customer (Future Admin View)
```text
Deleted Customers View → [Click Restore] → Confirmation Modal
→ [Confirm Restore] → Status=Active, DeletedAt=null
→ Success Toast → Customer appears in standard search
```

---

## 8. Navigation Structure

### 8.1 Navigation Hierarchy

```text
CRM Dashboard (Home)
├── Global Search Bar (Persistent Header)
├── Navigation Sidebar
│   ├── Customers (Active)
│   │   ├── Customer List / Search Results (Default)
│   │   ├── Create Customer
│   │   └── Deleted Customers (Admin only, Future)
│   └── Settings (Future)
│
├── Customer Detail View (Modal/Page)
│   ├── Edit Customer (Admin)
│   └── Delete Confirmation (Admin)
│
└── User Menu (Header Right)
    ├── Profile
    └── Sign Out
```

### 8.2 Menu Structure

| Menu Item | Admin Access | Manager Access | State |
|-----------|--------------|----------------|-------|
| Dashboard / Customer List | ✅ | ✅ | Default landing |
| Create Customer | ✅ | ❌ Hidden | Primary CTA |
| Search (Global Header) | ✅ | ✅ | Always visible |
| Customer Detail | ✅ | ✅ | Read-only for Manager |
| Edit Customer | ✅ | ❌ | From Detail View |
| Delete Customer | ✅ | ❌ | From Detail View |
| Deleted Customers | ✅ | ❌ | Future: Admin-only tab |
| Settings | Future | Future | Future |

### 8.3 Screen Relationships

```text
[Dashboard/List] ←→ [Create Form] (Create → Detail)
[Dashboard/List] ←→ [Detail View] (Click row → Detail)
[Detail View] ←→ [Edit Form] (Edit → Detail)
[Detail View] → [Delete Modal] → [Dashboard/List]
[Global Search] → [Dashboard/List Results] → [Detail View]
```

### 8.4 Entry Points

| Entry Point | Target Screen | Context |
|-------------|---------------|---------|
| App Launch / Login | Dashboard / Customer List | Default landing |
| Global Search (Header) | Customer List (filtered) | Any screen |
| "Create Customer" Button | Create Customer Form | Dashboard, List, Empty State |
| Search Result Click | Customer Detail View | List, Search Results |
| Direct URL (Bookmark/Share) | Customer Detail View | External link |
| Edit Button (Detail) | Edit Customer Form | Detail View (Admin only) |
| Delete Button (Detail) | Delete Confirmation Modal | Detail View (Admin only) |

### 8.5 Exit Points

| Exit Point | From Screen | Destination |
|------------|-------------|-------------|
| Logo/Home Link | Any | Dashboard/List |
| "Back to List" | Detail, Create, Edit | Dashboard/List |
| Cancel (Create/Edit) | Create Form, Edit Form | Previous screen (Detail or List) |
| Sign Out | User Menu | Login Page |

---

## 9. Screen Inventory

| Screen ID | Screen Name | Purpose | Primary User | Access |
|-----------|-------------|---------|--------------|--------|
| SC-01 | **Dashboard / Customer List** | Default landing; search results; list view | Admin, Manager | Both |
| SC-02 | **Create Customer Form** | Guided form for new customer entry | Admin | Admin only |
| SC-03 | **Customer Detail View** | Complete read-only view of customer | Admin, Manager | Both (role-based actions) |
| SC-04 | **Edit Customer Form** | Pre-filled form for updating customer | Admin | Admin only |
| SC-05 | **Delete Confirmation Modal** | Soft delete verification | Admin | Admin only |
| SC-06 | **Duplicate Match Modal** | Review potential duplicates before create/update | Admin | Admin only |
| SC-07 | **Concurrent Edit Warning Modal** | Handle simultaneous edits | Admin | Admin only |
| SC-08 | **Deleted Customers View** (Future) | List/restore soft-deleted records | Admin | Admin only |
| SC-09 | **Empty State / No Results** | Guidance when no data | Admin, Manager | Both |
| SC-10 | **Error State Screen** | System error recovery | Admin, Manager | Both |

---

## 10. Screen Specifications

### 10.1 SC-01: Dashboard / Customer List

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Primary landing page; displays search results; entry point for all customer actions |
| **Users** | Admin (full), Manager (read/search) |
| **Primary Actions** | Search (global header), Create Customer (Admin), Click row → Detail |
| **Secondary Actions** | Sort columns, Pagination, Refresh |
| **Layout** | Header (Global Search + User Menu) + Sidebar + Main Content (Results Table) |
| **Components** | Global Search Input, Primary Button (Create), Data Table, Pagination, Empty State |
| **Data Displayed** | Customer Name, Primary Phone, Primary Email, Company, Customer ID, Status Badge |
| **Loading State** | Skeleton rows (5-7) in table body; search input disabled |
| **Empty State** | "No customers found" illustration + "Create your first customer" CTA (Admin) / "No matches" (Manager search) |
| **Error State** | Inline banner: "Unable to load customers. [Retry]" |
| **Success State** | Toast notification after create/update/delete from other screens |

#### Responsive Behavior
| Breakpoint | Layout Change |
|------------|---------------|
| Desktop (≥1024px) | Sidebar + Table (6+ columns) |
| Tablet (768-1023px) | Collapsible sidebar; Table → Card stack (horizontal scroll if needed) |
| Mobile (<768px) | Hidden sidebar (hamburger); Card list (vertical); Search full-width |

---

### 10.2 SC-02: Create Customer Form

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Guided entry of new customer data with real-time validation |
| **Users** | Admin only |
| **Primary Actions** | Submit (Create), Cancel |
| **Secondary Actions** | Clear Form, Auto-format Phone/Email |
| **Layout** | Single-column form (max 600px centered); Logical field groups with section headers |
| **Components** | Text Inputs, Email Input, Phone Input (with country selector), Dropdown (Customer Type), Textarea (Notes), Primary/Secondary Buttons |
| **Data Displayed** | Form fields with labels, helper text, validation messages |
| **Loading State** | Button spinner on submit; form disabled |
| **Empty State** | N/A (form starts empty) |
| **Error State** | Inline field errors + Toast on system error; data preserved |
| **Success State** | Redirect to SC-03 (Detail View) + Success Toast |

#### Field Groups & Order
```text
1. Basic Information (Required)
   - Full Name* [Text, 200 max]
   - Primary Phone* [Phone Input, E.164, auto-format]
   - Primary Email* [Email Input, lowercase]

2. Company Information (Optional)
   - Company Name [Text, 200 max]
   - Customer Type [Dropdown: Individual, Business, Government, Other]

3. Contact Details (Optional)
   - Secondary Phone [Phone Input]
   - Secondary Email [Email Input]

4. Address (Optional)
   - Address Line 1, Address Line 2, City, State/Province, Postal Code, Country [Dropdown ISO]

5. Notes (Optional)
   - Notes [Textarea, 2000 max, character counter]
```

#### Validation Rules (Inline + Submit)
| Field | Required | Format | Max Length | Error Message |
|-------|----------|--------|------------|---------------|
| Full Name | Yes | Text | 200 | "Customer Name is required" / "Name too long (max 200)" |
| Primary Phone | Yes | E.164 | 20 | "Primary Phone is required" / "Enter valid phone number" |
| Primary Email | Yes | RFC 5322 | 254 | "Primary Email is required" / "Enter valid email" |
| Company Name | No | Text | 200 | "Company name too long (max 200)" |
| Secondary Phone | No | E.164 | 20 | "Enter valid phone number" |
| Secondary Email | No | RFC 5322 | 254 | "Enter valid email" |
| Address Fields | No | Text | Per BR-011 | Per field limits |
| Notes | No | Text | 2000 | "Notes too long (max 2000)" |

---

### 10.3 SC-03: Customer Detail View

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Complete, readable display of all customer attributes; action hub for Admin |
| **Users** | Admin (CRUD actions), Manager (Read-only) |
| **Primary Actions** | Admin: Edit, Delete; Both: Back to List, Copy Field Value |
| **Secondary Actions** | Print (Future), Share URL (Future) |
| **Layout** | Header (Customer Name + ID + Status Badge) + Tabbed/Sectioned Content + Sticky Action Bar (Admin) |
| **Components** | Detail Cards/Sections, Label-Value Pairs, Status Badge, Action Buttons, Breadcrumb |
| **Data Displayed** | All fields from Data Requirements (Section 10.1 PRD) grouped logically |
| **Loading State** | Skeleton cards for each section |
| **Empty State** | N/A (always has data if accessible) |
| **Error State** | "Customer not found" (404) or "Access denied" (403) with Back button |
| **Success State** | Toast after returning from Edit/Delete |

#### Information Architecture (Field Grouping)
```text
Header: [Customer Name] [CUST-2024-000001] [Status: Active Badge]
        [Breadcrumb: Customers > John Smith]

Section 1: Primary Contact
  - Full Name, Primary Phone (click-to-call), Primary Email (mailto:)

Section 2: Company & Classification
  - Company Name, Customer Type, Customer ID, Created Date/By

Section 3: Additional Contact
  - Secondary Phone, Secondary Email

Section 4: Address
  - Full formatted address (multi-line)

Section 5: Notes
  - Notes content (read-only, expandable if long)

Section 6: Audit Info (Admin only)
  - Updated At/By, Deleted At/By (if applicable)

Sticky Footer (Admin): [Edit] [Delete] [Back to List]
Sticky Footer (Manager): [Back to List]
```

#### Role-Based UI Differences
| Element | Admin | Manager |
|---------|-------|---------|
| Edit Button | Visible | Hidden |
| Delete Button | Visible | Hidden |
| Audit Info Section | Visible | Hidden |
| Field Copy-to-Clipboard | ✅ | ✅ |

---

### 10.4 SC-04: Edit Customer Form

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Modify existing customer data with same validation as Create |
| **Users** | Admin only |
| **Primary Actions** | Save Changes, Cancel |
| **Secondary Actions** | Reset to Original, Delete (link to Detail) |
| **Layout** | Identical to Create Form (SC-02) but pre-populated; "Customer ID" displayed read-only |
| **Components** | Same as Create Form + Read-only Customer ID field |
| **Data Displayed** | Current values in all fields; original values stored for comparison |
| **Loading State** | Button spinner on save; form disabled |
| **Empty State** | N/A |
| **Error State** | Inline validation + System error toast; data preserved |
| **Success State** | Redirect to Detail View (SC-03) + Success Toast |

#### Additional Behaviors
- **Dirty State Tracking**: Warn on navigation if unsaved changes (browser beforeunload + custom modal)
- **Concurrent Edit Check**: On save, if `updated_at` changed since load → Show SC-07 Modal
- **Duplicate Check**: Only on fields that changed (Name, Phone, Email, Company)

---

### 10.5 SC-05: Delete Confirmation Modal

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Confirm soft delete with clear consequences |
| **Users** | Admin only |
| **Primary Actions** | Confirm Archive, Cancel |
| **Secondary Actions** | None |
| **Layout** | Centered modal (480px max); Icon + Title + Warning Text + Customer Details + Buttons |
| **Components** | Modal, Warning Icon, Text, Customer Summary Card, Primary (Destructive) Button, Secondary Button |
| **Content** | 
```text
⚠️ Archive Customer?

This will remove "John Smith" (CUST-2024-000001) from search results and lists.
The record can be restored within 90 days from the Deleted Customers view.

Are you sure you want to archive this customer?
```
|
| **Loading State** | Button spinner on confirm |
| **Error State** | Toast: "Unable to archive. Please try again." Modal stays open |
| **Success State** | Modal closes → Redirect to List (SC-01) + Success Toast |

#### Button Styling
- **Confirm Archive**: Red/Destructive variant, label "Archive Customer"
- **Cancel**: Ghost variant, label "Cancel"

---

### 10.6 SC-06: Duplicate Match Modal

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Present potential duplicate(s) for Admin decision before create/update |
| **Users** | Admin only |
| **Primary Actions** | Cancel, View Existing, Proceed Anyway |
| **Secondary Actions** | None |
| **Layout** | Centered modal (600px max); Title + Match Cards (1-3) + Action Bar |
| **Components** | Modal, Match Card (Name, Phone, Email, Company, ID), Radio/Action Buttons |
| **Content** |
```text
⚠️ Potential Duplicate(s) Found

We found 1 existing customer matching your entry:

┌─────────────────────────────────────────────┐
│ John Smith                    CUST-2024-000001 │
│ 📞 +15551234567  ✉️ john@smith.com          │
│ 🏢 Acme Corp                                │
│ [View Details]                              │
└─────────────────────────────────────────────┘

What would you like to do?
[Cancel] [View Existing] [Proceed Anyway]
```
| **Loading State** | N/A (data already fetched) |
| **Error State** | Toast if fetch fails; allow proceed with warning |
| **Success State** | Action taken per button |

#### Match Card Interaction
- **View Existing**: Closes modal → Navigates to Detail View of match
- **Proceed Anyway**: Closes modal → Continues Create/Update
- **Cancel**: Closes modal → Returns to Form (data preserved)

---

### 10.7 SC-07: Concurrent Edit Warning Modal

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Handle simultaneous edits gracefully |
| **Users** | Admin only |
| **Primary Actions** | Reload & Reapply, Overwrite, Cancel |
| **Layout** | Centered modal (480px); Warning + Options |
| **Content** |
```text
⚠️ Concurrent Edit Detected

Another user updated this customer since you opened the form.
Their changes: Phone, Email updated 2 minutes ago by Jane Admin.

[Reload & Reapply]  [Overwrite Anyway]  [Cancel]
```
| **Behavior** |
| - **Reload & Reapply**: Fetch latest → Re-apply user's changes to new base → Re-validate → Save
| - **Overwrite**: Force save with user's values (last-write-wins)
| - **Cancel**: Return to Edit Form (data preserved) |

---

### 10.8 SC-08: Deleted Customers View (Future / Phase 2)

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Admin-only view to browse and restore soft-deleted customers |
| **Users** | Admin only |
| **Primary Actions** | Restore, Permanent Delete (Future), Filter by Date |
| **Layout** | Similar to SC-01 but with "Deleted" badge; Restore action per row |
| **Data Displayed** | Name, Phone, Email, Company, ID, Deleted At, Deleted By |
| **Empty State** | "No archived customers" |

---

### 10.9 SC-09: Empty State / No Results

| Context | Content |
|---------|---------|
| **Initial Dashboard (No Customers)** | Illustration + "No customers yet" + "Create your first customer" (Admin) / "Contact Admin to add customers" (Manager) |
| **Search No Results** | "No customers found for 'query'" + "Create new customer" (Admin) / "Try different search terms" (Manager) |
| **Deleted Customers Empty** | "No archived customers" |

---

### 10.10 SC-10: Error State Screen

| Context | Content |
|---------|---------|
| **Generic Error** | "Something went wrong" + [Retry] + [Go to Dashboard] |
| **404 Not Found** | "Customer not found" + [Back to Customers] |
| **403 Forbidden** | "Access denied" + [Go to Dashboard] |
| **Offline** | "You're offline. Changes will sync when reconnected." (Future PWA) |

---

## 11. ASCII Wireframes

### 11.1 SC-01: Dashboard / Customer List

#### Desktop (≥1024px)
```text
+----------------------------------------------------------------------------------+
| Header                                                                            |
| +------------------------------------------------------------------------------+ |
| | [Logo] CRM System                                    [Search Input............] [User ▼] | |
| +------------------------------------------------------------------------------+ |
+----------------------------------------------------------------------------------+
| Sidebar          | Main Content                                                 |
| +--------------+ | +----------------------------------------------------------+ |
| | ☰ Menu       | | | Toolbar                                                  | |
| |              | | | [Create Customer] [Export] [Filters] [Columns]         | |
| | 📋 Customers | | +----------------------------------------------------------+ |
| |   ├ List     | | | Data Table                                               | |
| |   ├ Create   | | | +----+----------------+----------------+------------+ | |
| |   └ Deleted  | | | | ☐  | Name             | Phone          | Email      | | |
| |              | | | +----+----------------+----------------+------------+ | |
| | ⚙️ Settings  | | | |    | John Smith       | +1 555 123 4567| john@...   | | |
| |              | | | |    | Jane Doe         | +1 555 987 6543| jane@...   | | |
| |              | | | |    | Acme Corporation | +1 555 111 2222| info@...   | | |
| |              | | | |    | ...              | ...            | ...        | | |
| |              | | | +----+----------------+----------------+------------+ | |
| |              | | | | Pagination: [< Prev] 1 2 3 4 5 [Next >]  (Showing 1-25 of 1,234) | |
| |              | | +----------------------------------------------------------+ |
| +--------------+ +----------------------------------------------------------+
```

#### Tablet (768-1023px)
```text
+--------------------------------------------------+
| Header                                           |
| [☰] CRM System              [Search......] [User]|
+--------------------------------------------------+
| Main Content                                     |
| +----------------------------------------------+ |
| | [Create Customer]                    [Filter]| |
| +----------------------------------------------+ |
| | Customer Cards (Stacked)                     | |
| | +------------------------------------------+ | |
| | | John Smith              [Active]         | | |
| | | 📞 +1 555 123 4567                       | | |
| | | ✉️ john@smith.com                        | | |
| | | 🏢 Acme Corporation                      | | |
| | | ID: CUST-2024-000001                     | | |
| | +------------------------------------------+ | |
| | +------------------------------------------+ | |
| | | Jane Doe                 [Active]         | | |
| | | 📞 +1 555 987 6543                       | | |
| | | ✉️ jane@doe.com                          | | |
| | | ID: CUST-2024-000002                     | | |
| | +------------------------------------------+ | |
| |                    [Prev] 1 2 3 [Next]     | |
| +----------------------------------------------+
```

#### Mobile (<768px)
```text
+----------------------+
| Header               |
| [☰] CRM    [Search]  |
+----------------------+
|                      |
| [+ Create Customer]  |  ← Primary FAB or Top Button
|                      |
| Customer Cards       |
| +------------------+ |
| | John Smith       | |
| | 📞 +1 555 123... | |
| | ✉️ john@...      | |
| | 🏢 Acme Corp     | |
| +------------------+ |
|                      |
| +------------------+ |
| | Jane Doe         | |
| | 📞 +1 555 987... | |
| +------------------+ |
|                      |
|      [1] [2] [3]     |  ← Pagination dots
+----------------------+
```

---

### 11.2 SC-02: Create Customer Form

#### Desktop
```text
+----------------------------------------------------------------------------------+
| Header: [← Back] Create Customer                                    [Cancel] [Save] |
+----------------------------------------------------------------------------------+
|                                                                                  |
|  ┌─ Basic Information ──────────────────────────────────────────────────────┐  |
|  │                                                                            │  |
|  │  Full Name *                    [____________________________________]   │  │
|  │  ──────────────────────────────────────────────────────────────────────   │  │
|  │  Primary Phone *                [🇺🇸 +1] [____________________________]   │  │
|  │  ──────────────────────────────────────────────────────────────────────   │  │
|  │  Primary Email *                [____________________________________]   │  │
|  │                                                                            │  │
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ┌─ Company Information ────────────────────────────────────────────────────┐  |
|  │                                                                            │  |
|  │  Company Name                   [____________________________________]   │  │
|  │  ──────────────────────────────────────────────────────────────────────   │  │
|  │  Customer Type                  [Individual ▼]                            │  │
|  │                                                                            │  │
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ┌─ Additional Contact ─────────────────────────────────────────────────────┐  |
|  │                                                                            │  |
|  │  Secondary Phone                [🇺🇸 +1] [____________________________]   │  │
|  │  ──────────────────────────────────────────────────────────────────────   │  │
|  │  Secondary Email                [____________________________________]   │  │
|  │                                                                            │  │
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ┌─ Address ─────────────────────────────────────────────────────────────────┐  |
|  │                                                                            │  |
|  │  Address Line 1                 [____________________________________]   │  │
|  │  Address Line 2                 [____________________________________]   │  │
|  │  City                             [____________________________________]   │  │
|  │  State/Province                   [____________________________________]   │  │
|  │  Postal Code                      [____________________________________]   │  │
|  │  Country                          [United States ▼]                       │  │
|  │                                                                            │  │
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ┌─ Notes ────────────────────────────────────────────────────────────────────┐  |
|  │                                                                            │  |
|  │  [____________________________________________________________________]   │  │
|  │  [____________________________________________________________________]   │  │
|  │  [____________________________________________________________________]   │  │
|  │  0/2000 characters                                                         │  │
|  │                                                                            │  │
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  [Cancel]                                              [Create Customer]         |
+----------------------------------------------------------------------------------+
```

#### Mobile
```text
+----------------------+
| ← Create Customer    |
+----------------------+
|                      |
| Basic Information    |
| ┌────────────────┐  |
| | Full Name *    |  |
| | [____________] |  |
| └────────────────┘  |
| ┌────────────────┐  |
| | Primary Phone *|  |
| | [🇺🇸+1][______]|  |
| └────────────────┘  |
| ┌────────────────┐  |
| | Primary Email *|  |
| | [____________] |  |
| └────────────────┘  |
|                      |
| Company Information  |
| ┌────────────────┐  |
| | Company Name   |  |
| | [____________] |  |
| └────────────────┘  |
| ┌────────────────┐  |
| | Customer Type  |  |
| | [Individual ▼] |  |
| └────────────────┘  |
|                      |
| [Additional Contact] ← Collapsible Section
| [Address]            ← Collapsible Section
| [Notes]              ← Collapsible Section
|                      |
| [Cancel]  [Create]   |  ← Sticky Bottom Bar
+----------------------+
```

---

### 11.3 SC-03: Customer Detail View

#### Desktop
```text
+----------------------------------------------------------------------------------+
| Header: [← Customers]  John Smith                    [CUST-2024-000001] [Active ●] |
| Breadcrumb: Customers > John Smith                                               |
+----------------------------------------------------------------------------------+
|                                                                                  |
|  ┌─ Primary Contact ────────────────────────────────────────────────────────┐  |
|  │  Full Name:        John Smith                                            │  |
|  │  Primary Phone:    +1 555 123 4567    [📞 Call] [📋 Copy]               │  |
|  │  Primary Email:    john@smith.com      [✉️ Email] [📋 Copy]             │  |
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ┌─ Company & Classification ───────────────────────────────────────────────┐  |
|  │  Company Name:     Acme Corporation                                      │  |
|  │  Customer Type:    Business                                              │  |
|  │  Customer ID:      CUST-2024-000001           [📋 Copy]                 │  |
|  │  Created:          Jan 15, 2024 10:30 AM by Admin User                  │  |
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ┌─ Additional Contact ─────────────────────────────────────────────────────┐  |
|  │  Secondary Phone:  +1 555 987 6543                                       │  |
|  │  Secondary Email:  j.smith@acme.com                                      │  |
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ┌─ Address ──────────────────────────────────────────────────────────────────┐  |
|  │  123 Business Ave, Suite 400                                               │  |
|  │  San Francisco, CA 94105                                                   │  |
|  │  United States                                                              │  |
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ┌─ Notes ────────────────────────────────────────────────────────────────────┐  |
|  │  Key decision maker for enterprise accounts. Prefers email communication.  │  |
|  │  [Show More]                                                               │  |
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ┌─ Audit Information ────────────────────────────────────────────────────────┐  |
|  │  Last Updated:     Jan 20, 2024 2:15 PM by Admin User                     │  |
|  │  Deleted:          —                                                        │  |
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ──────────────────────────────────────────────────────────────────────────────  |
|  [Edit] [Delete]                                    [Back to List]               |
+----------------------------------------------------------------------------------+
```

#### Mobile
```text
+----------------------+
| ← John Smith         |
| CUST-2024-000001 ●   |
+----------------------+
|                      |
| Primary Contact      |
| ┌────────────────┐  |
| | John Smith     |  |
| | 📞 +1 555...   |  |
| | ✉️ john@...    |  |
| └────────────────┘  |
|                      |
| Company & Type       |
| ┌────────────────┐  |
| | Acme Corp      |  |
| | Business       |  |
| | ID: CUST-...   |  |
| | Created: Jan 15|  |
| └────────────────┘  |
|                      |
| [Additional Contact] ← Expandable
| [Address]            ← Expandable
| [Notes]              ← Expandable
| [Audit Info]         ← Expandable (Admin only)
|                      |
| [Edit] [Delete]      |  ← Sticky Bottom (Admin)
| [Back to List]       |  ← Sticky Bottom (Manager)
+----------------------+
```

---

### 11.4 SC-04: Edit Customer Form

#### Desktop
```text
+----------------------------------------------------------------------------------+
| Header: [← Detail] Edit Customer: John Smith                    [Cancel] [Save]  |
+----------------------------------------------------------------------------------+
|                                                                                  |
|  Customer ID: CUST-2024-000001 (read-only)                                       |
|                                                                                  |
|  ┌─ Basic Information ──────────────────────────────────────────────────────┐  |
|  │                                                                            │  |
|  │  Full Name *                    [John Smith___________________________]  │  │
|  │  ──────────────────────────────────────────────────────────────────────   │  │
|  │  Primary Phone *                [🇺🇸 +1] [5551234567__________________]  │  │
|  │  ──────────────────────────────────────────────────────────────────────   │  │
|  │  Primary Email *                [john@smith.com______________________]   │  │
|  │                                                                            │  │
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
|  ... (Same sections as Create Form, pre-filled) ...                             |
|                                                                                  |
|  [Cancel]  [Reset]                                    [Save Changes]             |
+----------------------------------------------------------------------------------+
```

#### Mobile
```text
+----------------------+
| ← Edit: John Smith   |
| ID: CUST-2024-000001 |
+----------------------+
|                      |
| (Same as Create Form |
|  but pre-filled)     |
|                      |
| [Cancel] [Save]      |  ← Sticky Bottom
+----------------------+
```

---

### 11.5 SC-05: Delete Confirmation Modal

#### Desktop & Mobile (Responsive Modal)
```text
+--------------------------------------------------+
|  ⚠️  Archive Customer?                    [×]    |
+--------------------------------------------------+
|                                                  |
|  This will remove "John Smith"                   |
|  (CUST-2024-000001) from search results          |
|  and lists.                                      |
|                                                  |
|  The record can be restored within 90 days       |
|  from the Deleted Customers view.                |
|                                                  |
|  ┌────────────────────────────────────────────┐  |
|  │  John Smith                    [Active]    │  |
|  │  📞 +1 555 123 4567                        │  |
|  │  ✉️ john@smith.com                         │  |
|  │  🏢 Acme Corporation                       │  |
|  │  ID: CUST-2024-000001                      │  |
|  └────────────────────────────────────────────┘  |
|                                                  |
|  Are you sure you want to archive this customer? |
|                                                  |
|  [Cancel]                    [Archive Customer]  |  ← Red button
+--------------------------------------------------+
```

---

### 11.6 SC-06: Duplicate Match Modal

#### Desktop
```text
+------------------------------------------------------------------+
|  ⚠️  Potential Duplicate(s) Found                        [×]     |
+------------------------------------------------------------------+
|                                                                  |
|  We found 1 existing customer matching your entry:               |
|                                                                  |
|  ┌────────────────────────────────────────────────────────────┐  |
|  │  John Smith                          CUST-2024-000001      │  |
|  │  📞 +1 555 123 4567    ✉️ john@smith.com                   │  |
|  │  🏢 Acme Corporation                                         │  |
|  │  [View Details]                                              │  |
|  └────────────────────────────────────────────────────────────┘  |
|                                                                  |
|  What would you like to do?                                      |
|                                                                  |
|  [Cancel]        [View Existing]        [Proceed Anyway]         |
+------------------------------------------------------------------+
```

#### Mobile
```text
+----------------------+
| ⚠️ Duplicate Found  ×|
+----------------------+
|                      |
| Match found:         |
|                      |
| ┌────────────────┐  |
| | John Smith     |  |
| | 📞 +1 555...   |  |
| | ✉️ john@...    |  |
| | 🏢 Acme Corp   |  |
| | [View Details] |  |
| └────────────────┘  |
|                      |
| [Cancel]             |
| [View Existing]      |
| [Proceed Anyway]     |
+----------------------+
```

---

## 12. Component Inventory

### 12.1 Core Components

| Component | Variants | States | Usage |
|-----------|----------|--------|-------|
| **Button** | Primary, Secondary, Ghost, Destructive, Link | Default, Hover, Focus, Active, Disabled, Loading | All actions |
| **Input** | Text, Email, Phone, Number, Password | Default, Focus, Error, Disabled, Read-only | Forms |
| **Textarea** | Auto-resize, Fixed | Default, Focus, Error, Disabled | Notes field |
| **Dropdown/Select** | Single, Searchable | Default, Open, Focus, Error, Disabled | Customer Type, Country |
| **Date Picker** | Single, Range | Default, Open, Focus, Error | Future: Date filters |
| **Table** | Sortable, Selectable, Striped | Loading, Empty, Error, Hover Row | Customer List (Desktop) |
| **Card** | Interactive, Static, Expandable | Default, Hover, Focus, Selected | Customer List (Tablet/Mobile), Detail Sections |
| **Modal** | Small (480px), Medium (600px), Large (800px) | Open, Closing, Closed | Confirmations, Duplicate Match, Concurrent Edit |
| **Toast/Notification** | Success, Error, Warning, Info | Enter, Visible, Exit | All feedback |
| **Badge/Status** | Active, Deleted, Pending, Warning | Default | Customer Status, Type |
| **Breadcrumb** | Standard, Collapsed | Default | Detail View, Edit Form |
| **Search Input** | With History, With Suggestions | Default, Focus, Loading, With Results | Global Header |
| **Pagination** | Numbers, Prev/Next, Page Size | Default, Disabled | Customer List |
| **Skeleton Loader** | Table Row, Card, Form Field | Animating | All loading states |
| **Empty State** | Illustration, Title, Description, Action | Default | List, Search, Deleted View |
| **Tooltip** | Top, Bottom, Left, Right | Hover, Focus | Icon buttons, Truncated text |
| **Avatar/Icon** | User, Company, Phone, Email, Map | Default | Detail View, Cards |

### 12.2 Composite Components

| Component | Composition | Purpose |
|-----------|-------------|---------|
| **Customer Row (Table)** | Checkbox + Name Link + Phone + Email + Company + ID + Status Badge | List view row |
| **Customer Card** | Name + Status + Phone + Email + Company + ID + Actions | Tablet/Mobile list |
| **Detail Section** | Section Title + Label-Value Pairs + Copy Actions | Detail View grouping |
| **Form Section** | Section Title + Field Group + Divider | Create/Edit Forms |
| **Phone Input** | Country Selector + Formatted Input + Validation | Phone fields |
| **Action Bar** | Primary + Secondary Buttons + Breadcrumbs | Form footers, Detail sticky footer |

---

## 13. Validation Rules

### 13.1 Field-Level Validation

| Field | Rule | Trigger | Message |
|-------|------|---------|---------|
| Full Name | Required | Blur / Submit | "Customer Name is required" |
| Full Name | Max 200 chars | Input / Blur | "Name must be 200 characters or fewer" |
| Primary Phone | Required | Blur / Submit | "Primary Phone is required" |
| Primary Phone | Valid E.164 | Blur / Submit | "Enter a valid phone number (e.g., +15551234567)" |
| Primary Email | Required | Blur / Submit | "Primary Email is required" |
| Primary Email | Valid RFC 5322 | Blur / Submit | "Enter a valid email address" |
| Primary Email | Unique (Soft) | Submit | "A customer with this email already exists" (Warning, not block) |
| Secondary Phone | Valid E.164 if provided | Blur | "Enter a valid phone number" |
| Secondary Email | Valid RFC 5322 if provided | Blur | "Enter a valid email address" |
| Company Name | Max 200 chars | Input / Blur | "Company name must be 200 characters or fewer" |
| Address Fields | Max per BR-011 | Input / Blur | "Field too long (max X characters)" |
| Notes | Max 2000 chars | Input | Character counter; "Notes must be 2000 characters or fewer" |
| Customer Type | Valid Enum | Change | N/A (dropdown prevents invalid) |
| Country | Valid ISO 3166-1 | Change | N/A (dropdown prevents invalid) |

### 13.2 Form-Level Validation (Submit)

| Rule | Trigger | Message | Action |
|------|---------|---------|--------|
| All required fields complete | Submit | Inline errors on each field + Focus first | Block submit |
| Duplicate Check (Create) | Submit | SC-06 Modal | Block until decision |
| Duplicate Check (Update) | Submit | SC-06 Modal | Block until decision |
| Concurrent Edit (Update) | Submit | SC-07 Modal | Block until decision |
| System Error | Submit | Toast Error | Retry enabled |

### 13.3 Business Validation (BR-005 Duplicate Criteria)

| Match Type | Criteria | Threshold |
|------------|----------|-----------|
| **Name + Phone** | Name similarity > 85% (Levenshtein) AND Phone exact match (normalized) | High Confidence |
| **Email Exact** | Primary or Secondary Email exact match (case-insensitive) | High Confidence |
| **Company + Phone** | Company exact match AND Phone exact match | Medium Confidence |
| **Name + Email** | Name similarity > 85% AND Email exact match | High Confidence |

> **Note**: Exact algorithm TBD with stakeholders (Section 5.4 PRD). UI must support configurable thresholds.

---

## 14. Accessibility Requirements (WCAG 2.1 AA)

### 14.1 Semantic HTML & Structure

| Requirement | Implementation |
|-------------|----------------|
| **Page Structure** | `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>` landmarks |
| **Headings** | Hierarchical: h1 (page title), h2 (sections), h3 (subsections) |
| **Lists** | `<ul>`/`<ol>` for navigation, actions; `<dl>` for detail view label-value pairs |
| **Tables** | `<table>` with `<thead>`, `<tbody>`, `<th scope="col">`, `<caption>` |
| **Forms** | `<form>`, `<fieldset>`/`<legend>` for groups, `<label for="id">` for every input |

### 14.2 Keyboard Navigation

| Requirement | Implementation |
|-------------|----------------|
| **Focus Order** | Logical tab order matching visual layout |
| **Focus Indicators** | Visible 2px outline (3:1 contrast) on all interactive elements |
| **Skip Links** | "Skip to main content" at top of page |
| **Modal Trap** | Focus trapped in modal; Esc closes; focus returns to trigger |
| **Table Navigation** | Arrow keys for row navigation (optional enhancement) |
| **Search Input** | Accessible via `/` key shortcut (power user) |

### 14.3 Screen Reader Support

| Requirement | Implementation |
|-------------|----------------|
| **Labels** | All inputs have associated `<label>` (visible or `aria-label`) |
| **Error Announcements** | `aria-live="polite"` for inline errors; `aria-live="assertive"` for toasts |
| **Required Fields** | `aria-required="true"` + visual `*` indicator |
| **Invalid State** | `aria-invalid="true"` + `aria-describedby="error-id"` |
| **Status Updates** | `aria-live` region for search results count, save confirmation |
| **Modal Labels** | `aria-labelledby` (title) + `aria-describedby` (body) |
| **Expandable Sections** | `aria-expanded`, `aria-controls` on triggers |
| **Sortable Columns** | `aria-sort="ascending/descending/none"` on `<th>` |

### 14.4 Color & Contrast

| Requirement | Standard |
|-------------|----------|
| **Text Contrast** | 4.5:1 (normal), 3:1 (large text ≥18pt/14pt bold) |
| **UI Component Contrast** | 3:1 for borders, focus indicators, icons |
| **Color Independence** | No information conveyed by color alone (use icons, text, patterns) |
| **Status Badges** | Text + Icon + Color (e.g., "● Active" not just green dot) |
| **Error States** | Red border + Error icon + Text message |
| **Focus Indicator** | 2px solid outline, offset 2px, contrast 3:1 against background |

### 14.5 Responsive & Touch

| Requirement | Implementation |
|-------------|----------------|
| **Touch Targets** | Minimum 44×44px (48×48px preferred) for all interactive elements |
| **Viewport** | No horizontal scroll at 320px width |
| **Zoom** | Content reflows at 200% zoom; no loss of function |
| **Orientation** | Works in portrait and landscape |

### 14.6 Forms & Validation

| Requirement | Implementation |
|-------------|----------------|
| **Error Identification** | Errors announced, focused, described in text |
| **Error Suggestion** | Provide correction guidance (format examples) |
| **Error Prevention** | Confirm for destructive actions (Delete); Review before submit (Create/Update) |
| **Auto-complete** | `autocomplete` attributes on all fields (name, tel, email, address-line1, etc.) |

---

## 15. Responsive Design Guidelines

### 15.1 Breakpoints

| Breakpoint | Name | Target Devices | Layout Strategy |
|------------|------|----------------|-----------------|
| **≥1200px** | Desktop Large | Large monitors | Full sidebar + 6+ column table |
| **1024-1199px** | Desktop | Standard laptops | Full sidebar + 5-6 column table |
| **768-1023px** | Tablet | iPad, tablets | Collapsible sidebar; Card list or horizontal-scroll table |
| **480-767px** | Mobile Large | Phablets, large phones | Hidden sidebar; Stacked cards; Sticky actions |
| **<480px** | Mobile Small | Small phones | Compact cards; Full-width inputs; Bottom sheets for modals |

### 15.2 Layout Patterns by Screen

| Screen | Desktop | Tablet | Mobile |
|--------|---------|--------|--------|
| **List (SC-01)** | Sidebar + Data Table | Collapsible Sidebar + Card Stack | Card Stack + FAB |
| **Create/Edit (SC-02/04)** | Centered 600px Form | Full-width Form (with margins) | Full-width Form, Collapsible Sections |
| **Detail (SC-03)** | Multi-section Layout + Sticky Actions | Stacked Sections + Sticky Actions | Accordion Sections + Sticky Bottom Bar |
| **Modals (SC-05/06/07)** | Centered 480-600px | Centered 90% width | Bottom Sheet (slide up) |

### 15.3 Component Adaptations

| Component | Desktop | Tablet | Mobile |
|-----------|---------|--------|--------|
| **Global Search** | 400px width in header | Full-width in header | Full-width, dedicated row |
| **Create Button** | Top-right toolbar | Top-right toolbar | Floating Action Button (FAB) |
| **Table** | Full columns | Horizontal scroll or Card | Card list only |
| **Pagination** | Full controls | Prev/Next + Page # | Prev/Next + Dots |
| **Modals** | Centered overlay | Centered overlay | Bottom sheet |
| **Tooltips** | Hover + Focus | Focus only | Long-press or Focus |
| **Date Picker** | Calendar popup | Calendar popup | Native `<input type="date">` |

### 15.4 Manager-Specific Responsive Needs

- **Tablet Primary**: Manager uses tablet in field → Card layout optimized for touch
- **Large Tap Targets**: 48×48px minimum on all actions
- **Readable Text**: 16px base font size minimum (no zoom needed)
- **Simplified Density**: Fewer fields visible by default; progressive disclosure

---

## 16. Analytics & Telemetry Recommendations

### 16.1 Key Events to Track

| Event Name | Trigger | Properties | Purpose |
|------------|---------|------------|---------|
| `customer_created` | Create Form Submit Success | `customer_id`, `duration_ms`, `has_company`, `field_count` | Measure creation time (BG-01), adoption |
| `customer_updated` | Edit Form Submit Success | `customer_id`, `duration_ms`, `changed_fields`, `had_duplicate_warning` | Measure update efficiency |
| `customer_deleted` | Delete Confirm | `customer_id`, `duration_ms` | Track deletion frequency |
| `customer_restored` | Restore Action (Future) | `customer_id` | Track recovery needs |
| `search_executed` | Search Debounce Fire | `query_length`, `result_count`, `duration_ms`, `user_role` | Measure search performance (BG-02), patterns |
| `search_result_clicked` | Result Row Click | `customer_id`, `position`, `query` | Result relevance |
| `duplicate_detected` | Duplicate Modal Shown | `match_type`, `match_count`, `action_taken` | Tune duplicate rules (BG-03) |
| `duplicate_action` | Modal Button Click | `action` (cancel/view/proceed), `match_type` | Understand admin behavior |
| `validation_error` | Inline Error Shown | `field`, `error_type`, `screen` | Identify UX friction |
| `form_abandoned` | Navigate Away with Dirty Form | `screen`, `time_spent_ms`, `fields_filled` | Identify drop-off points |
| `concurrent_edit_warning` | SC-07 Shown | `action_taken` | Measure conflict frequency |
| `page_view` | Screen Load | `screen`, `user_role`, `load_time_ms` | Usage patterns |
| `error_occurred` | System Error | `screen`, `error_code`, `user_action` | Reliability monitoring |

### 16.2 Dashboard Metrics (Product/UX)

| Metric | Target | Source |
|--------|--------|--------|
| **Avg Creation Time** | < 60 sec | `customer_created.duration_ms` |
| **Search p95 Latency** | < 5 sec | `search_executed.duration_ms` |
| **Duplicate Warning Rate** | < 10% of creates | `duplicate_detected` / `customer_created` |
| **Duplicate Override Rate** | Track | `duplicate_action=proceed` / `duplicate_detected` |
| **Validation Error Rate** | < 5% of submits | `validation_error` / submits |
| **Form Abandonment Rate** | < 15% | `form_abandoned` / form opens |
| **Mobile vs Desktop Usage** | Track | `page_view` by viewport |
| **Manager Search Success** | > 90% clicks result | `search_result_clicked` / `search_executed` (Manager) |

---

## 17. Design System Tokens (Reference)

### 17.1 Color Palette

| Token | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `color-primary` | #1E40AF | #3B82F6 | Primary actions, links, focus |
| `color-primary-hover` | #1E3A8A | #60A5FA | Button hover |
| `color-destructive` | #DC2626 | #EF4444 | Delete, errors |
| `color-destructive-hover` | #B91C1C | #F87171 | Destructive hover |
| `color-success` | #16A34A | #4ADE80 | Success toasts, saved state |
| `color-warning` | #D97706 | #FBBF24 | Warnings, duplicate alerts |
| `color-bg-primary` | #FFFFFF | #111827 | Page background |
| `color-bg-secondary` | #F9FAFB | #1F2937 | Cards, sidebar |
| `color-bg-tertiary` | #F3F4F6 | #374151 | Hover states, inputs |
| `color-text-primary` | #111827 | #F9FAFB | Primary text |
| `color-text-secondary` | #6B7280 | #9CA3AF | Helper text, labels |
| `color-border` | #E5E7EB | #374151 | Input borders, dividers |
| `color-border-focus` | #1E40AF | #3B82F6 | Focus rings |

### 17.2 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Icon gaps, inline spacing |
| `space-2` | 8px | Form field gaps, card padding |
| `space-3` | 12px | Section gaps |
| `space-4` | 16px | Component padding, modal padding |
| `space-5` | 24px | Section margins, page padding |
| `space-6` | 32px | Large section gaps |
| `space-8` | 48px | Page-level margins |

### 17.3 Typography

| Token | Font Size | Line Height | Weight | Usage |
|-------|-----------|-------------|--------|-------|
| `text-xs` | 12px | 1.5 | 400 | Timestamps, captions |
| `text-sm` | 14px | 1.5 | 400 | Labels, helper text, table cells |
| `text-base` | 16px | 1.5 | 400 | Body text, inputs |
| `text-lg` | 18px | 1.4 | 400 | Card titles, emphasized text |
| `text-xl` | 20px | 1.3 | 600 | Section headers |
| `text-2xl` | 24px | 1.2 | 600 | Page titles |
| `text-3xl` | 30px | 1.1 | 700 | Modal titles |

### 17.4 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-sm` | 4px | Inputs, buttons |
| `radius-md` | 8px | Cards, modals, dropdowns |
| `radius-lg` | 12px | Large containers |
| `radius-full` | 9999px | Badges, pills, FAB |

### 17.5 Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-sm` | 0 1px 2px rgba(0,0,0,0.05) | Cards, inputs focus |
| `shadow-md` | 0 4px 6px rgba(0,0,0,0.07) | Modals, dropdowns |
| `shadow-lg` | 0 10px 15px rgba(0,0,0,0.1) | Large modals, sidebars |

---

## 18. Handoff Checklist for Next Agents

### 18.1 For Architect Agent
- [ ] API Contracts for: Create, Read, Update, Delete, Search, Duplicate Check
- [ ] Data Model (Physical) matching Section 10.1 PRD
- [ ] Auth/Authorization: Session-based, Roles (Admin/Manager), 30-min timeout
- [ ] Performance: Indexing strategy for fuzzy search on 10K records
- [ ] Soft Delete Implementation: `deleted_at` filter on all queries
- [ ] Concurrent Edit: Optimistic locking with `updated_at` version check
- [ ] Audit Logging: Capture actor, timestamp, action, field changes (BR-015)

### 18.2 For Frontend Agent
- [ ] Component Library: All components in Section 12 implemented
- [ ] State Management: React Query / TanStack Query for server state
- [ ] Form Library: React Hook Form + Zod validation (matching Section 13)
- [ ] Routing: `/customers