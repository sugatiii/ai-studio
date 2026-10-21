# Architecture Standards

Version: 1.0

---

# Purpose

Dokumen ini menjadi sumber kebenaran utama (Source of Truth) untuk seluruh AI Agent dan developer dalam membangun, memelihara, serta mengembangkan sistem.

Semua keputusan teknis wajib mengikuti dokumen ini.

---

# Architecture Goals

Tujuan utama:

- Scalability
- Maintainability
- Security
- Testability
- Observability
- Cost Efficiency
- AI Friendly Development

---

# High Level Architecture

```text
Business User
      │
      ▼
     Jira
      │
      ▼
 ┌───────────────┐
 │   PO Agent    │
 └───────┬───────┘
         ▼
        PRD
         ▼
 ┌─────────────────────┐
 │ Architect Agent     │
 └───────┬─────────────┘
         ▼
    Technical Design
         ▼
 ┌─────────────────────┐
 │ Developer Agents    │
 ├ Backend Agent       │
 ├ Frontend Agent      │
 ├ Mobile Agent        │
 └ DBA Agent           │
         ▼
       GitHub
         ▼
 ┌─────────────────────┐
 │ QA Agent            │
 └─────────┬───────────┘
           ▼
     Pull Request
           ▼
 ┌─────────────────────┐
 │ DevOps Agent        │
 └─────────┬───────────┘
           ▼
      Deployment
```

---

# Architectural Principles

## 1. Separation of Concerns

Setiap layer hanya memiliki satu tanggung jawab.

Contoh:

Controller

- menerima request

Service

- business logic

Repository

- database access

---

## 2. Dependency Rule

Dependency hanya boleh mengarah ke dalam.

```text
Controller
     ↓
Service
     ↓
Repository
     ↓
Database
```

Tidak boleh:

```text
Repository
     ↓
Controller
```

---

## 3. Single Responsibility

Satu class = satu tujuan.

Bad:

```text
UserService

- Login
- Register
- Upload File
- Send Email
```

Good:

```text
AuthService
UserService
StorageService
NotificationService
```

---

# Backend Architecture

Standar backend:

```text
src/

├── controllers/
├── services/
├── repositories/
├── models/
├── dto/
├── validations/
├── middleware/
├── routes/
├── constants/
├── config/
├── utils/
├── jobs/
└── tests/
```

---

# Layer Responsibilities

## Controller Layer

Tugas:

- menerima request
- validasi request
- memanggil service
- return response

Tidak boleh:

- query database
- business process

---

## Service Layer

Tugas:

- business logic
- orchestration
- transaction

Tidak boleh:

- express logic
- http handling

---

## Repository Layer

Tugas:

- CRUD
- database access

Tidak boleh:

- business logic

---

# Frontend Architecture

```text
src/

├── components/
├── pages/
├── routes/
├── hooks/
├── services/
├── store/
├── assets/
├── constants/
├── types/
└── utils/
```

---

# Component Rules

Satu component:

```text
One Component
One Responsibility
```

Contoh:

```text
UserCard
```

Bukan:

```text
UserCardAndPaymentAndAddress
```

---

# Mobile Architecture

React Native Standard

```text
src/

├── screens/
├── navigation/
├── components/
├── hooks/
├── services/
├── store/
└── utils/
```

---

# Clean Architecture

```text
Presentation Layer
        ↓
Application Layer
        ↓
Domain Layer
        ↓
Infrastructure Layer
```

---

# Domain Layer

Berisi:

- Entity
- Domain Service
- Business Rules

Harus bebas framework.

---

# Infrastructure Layer

Berisi:

- Database
- Redis
- External API
- Storage Provider

---

# Database Architecture

Setiap database wajib:

```sql
id
created_at
created_by
updated_at
updated_by
```

Optional:

```sql
deleted_at
deleted_by
```

---

# Microservice Guidelines

Digunakan jika:

- Team > 5 orang
- Service independen
- Scaling berbeda

Aturan:

Setiap service memiliki:

```text
Database sendiri
Repository sendiri
Deployment sendiri
```

Tidak boleh:

```text
Service A
langsung query
database Service B
```

---

# API First Design

Semua fitur wajib memiliki:

1. API Contract
2. Request Schema
3. Response Schema

Sebelum coding dimulai.

---

# Event Driven Architecture

Digunakan untuk:

- Notification
- Audit
- Integration

Contoh:

```text
Order Created

emit

order.created
```

Consumer:

```text
Notification Service
Audit Service
Reporting Service
```

---

# Security Architecture

Mandatory:

- JWT Authentication
- RBAC Authorization
- HTTPS
- Rate Limiting
- Audit Logging

---

# Logging Architecture

Level:

```text
INFO
WARN
ERROR
FATAL
```

Format:

```json
{
  "service":"user-service",
  "traceId":"123",
  "message":"User created"
}
```

---

# Monitoring Architecture

Metrics:

- CPU
- Memory
- Database Connections
- API Response Time
- Error Rate

Tools:

```text
Prometheus
Grafana
```

---

# Caching Architecture

Cache:

```text
Redis
```

Digunakan untuk:

- Session
- Frequently Used Data
- Lookup Data

---

# CI/CD Architecture

```text
GitHub
    ↓
Pull Request
    ↓
Automated Test
    ↓
Code Review
    ↓
Build
    ↓
Deploy
```

---

# Branch Strategy

```text
main
develop
feature/*
bugfix/*
hotfix/*
```

Contoh:

```text
feature/JIRA-123-create-user
```

---

# AI Agent Architecture

## PO Agent

Output:

- PRD
- User Story
- Acceptance Criteria

## Architect Agent

Output:

- Technical Design
- API Contract

## Backend Agent

Output:

- API
- Database
- Unit Test

## Frontend Agent

Output:

- UI
- State Management

## Mobile Agent

Output:

- Mobile App
- Mobile Test

## QA Agent

Output:

- Test Case
- Automation Test

## DevOps Agent

Output:

- Docker
- Deployment
- Monitoring

---

# Definition Of Ready

Task dapat dikerjakan jika:

- Jira Ticket tersedia
- Acceptance Criteria tersedia
- Technical Design tersedia

---

# Definition Of Done

Task selesai jika:

- Build Success
- Lint Success
- Unit Test Pass
- Documentation Updated
- Security Check Pass
- Pull Request Approved
- Jira Updated

---

# Architecture Decision Record

Setiap perubahan arsitektur wajib memiliki ADR:

```text
ADR-001 Use PostgreSQL

Status:
Approved

Reason:
ACID compliance
High reliability
```

---

# Golden Rules

AI Agent wajib:

- Read PRD first
- Read Architecture first
- Reuse existing code
- Avoid duplication
- Create tests
- Update documentation

AI Agent dilarang:

- Hardcode secrets
- Skip tests
- Skip documentation
- Modify unrelated modules
- Break architecture standards