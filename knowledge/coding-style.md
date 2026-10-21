# Coding Style Guide

Version: 1.0
Last Updated: 2026-10-21

---

# 1. General Principles

## 1.1 Clean Code

Code MUST:

- Easy to read
- Easy to maintain
- Easy to test
- Easy to extend

Always prioritize:

1. Readability
2. Maintainability
3. Scalability
4. Performance

Never sacrifice readability for shorter code.

## 2. Naming Convention

### Variables
Use camelCase.

### Constants
Use UPPER_SNAKE_CASE.

### Boolean
Must start with:
- is
- has
- can
- should

### Functions
Use verb + object.

### Components
PascalCase.

### Interfaces
PascalCase with I prefix.

---

# 3. File Structure

## Frontend

```text
src/
├── api/
├── assets/
├── components/
├── hooks/
├── pages/
├── routes/
├── services/
├── store/
├── types/
├── utils/
└── constants/
```

## Backend

```text
src/
├── controllers/
├── services/
├── repositories/
├── models/
├── middleware/
├── routes/
├── utils/
├── constants/
├── config/
└── validations/
```

---

# 4. Component Rules

- One component = one responsibility
- Avoid God Components
- Reuse shared components

---

# 5. Function Rules

- Maximum 50 lines per function
- Extract helpers if logic becomes complex
- Single Responsibility Principle

---

# 6. API Rules

REST conventions:

GET /users
GET /users/:id
POST /users
PUT /users/:id
DELETE /users/:id

Avoid action-style endpoints.

---

# 7. Error Handling

Always log errors.

```js
catch(error) {
  logger.error(error)
  throw error
}
```

Standard response:

```json
{
  "success": true,
  "data": {}
}
```

```json
{
  "success": false,
  "message": "User not found"
}
```

---

# 8. Logging Rules

Use logger abstraction.

- logger.info
- logger.warn
- logger.error

Never commit debug logs.

---

# 9. TypeScript Rules

- strict mode required
- avoid any
- prefer unknown
- strongly typed interfaces

---

# 10. React Rules

- Custom hooks start with use
- Define interfaces for props
- Use meaningful state names
- Avoid prop drilling when possible

---

# 11. Database Rules

Naming:

```sql
users
order_items
customer_addresses
```

Audit columns:

```sql
created_at
created_by
updated_at
updated_by
```

---

# 12. Security Rules

- Use parameterized queries
- Never hardcode secrets
- Store secrets in .env
- Validate all user input
- Sanitize external data

---

# 13. Git Rules

Branch naming:

```text
feature/TICKET-description
bugfix/TICKET-description
hotfix/TICKET-description
```

Commit format:

```text
feat:
fix:
refactor:
docs:
test:
```

---

# 14. Testing Rules

Minimum coverage: 80%

Critical modules:
- Authentication
- Payment
- Authorization
- Order Processing

Require 90%+ coverage.

---

# 15. AI Agent Rules

Before coding:

1. Read PRD
2. Read architecture.md
3. Read coding-style.md
4. Read api-contract.md

After coding:

1. Run lint
2. Run tests
3. Update documentation
4. Provide implementation summary

---

# 16. Definition of Done

A task is complete only when:

- Build successful
- Tests passed
- Lint passed
- Documentation updated
- Security checks passed
- No duplicate code
- Pull request ready
