# Engineering Best Practices

Version: 1.0

---

# Purpose

Dokumen ini mendefinisikan best practice yang wajib diikuti oleh seluruh AI Agent dan Developer.

Tujuan:

- Konsistensi
- Maintainability
- Scalability
- Quality
- Security
- Faster Delivery

Dokumen ini berlaku untuk:

- PO Agent
- Architect Agent
- Backend Agent
- Frontend Agent
- Mobile Agent
- QA Agent
- DevOps Agent

---

# Core Engineering Principles

Semua solusi harus mengikuti prinsip:

```text
KISS
DRY
SOLID
YAGNI
```

---

# KISS

Keep It Simple Stupid

Pilih solusi paling sederhana yang memenuhi kebutuhan.

Good:

```text
Single API
Single Database
Single Service
```

Bad:

```text
Microservices
Kafka
Event Bus
20 Services
```

untuk CRUD sederhana.

---

# DRY

Don't Repeat Yourself

Hindari duplikasi.

Before creating:

```text
Component
Function
Repository
API
Service
```

Agent wajib mencari implementasi yang sudah ada.

---

# YAGNI

You Aren't Gonna Need It

Jangan membangun fitur yang belum dibutuhkan.

Bad:

```text
Future Feature
Future API
Future Database Schema
Future Integration
```

Good:

```text
Build What Is Needed Today
```

---

# SOLID

Backend Agent wajib mengikuti:

```text
Single Responsibility Principle
Open Closed Principle
Liskov Substitution Principle
Interface Segregation Principle
Dependency Inversion Principle
```

---

# Jira First Development

Seluruh pekerjaan harus dimulai dari:

```text
Jira Ticket
```

Tidak boleh:

```text
Coding Tanpa Ticket
```

Workflow:

```text
Jira
↓
Analysis
↓
Implementation
↓
Testing
↓
Review
↓
Done
```

---

# Documentation First

Sebelum coding:

Developer wajib membaca:

```text
architecture.md
tech-stack.md
security-rules.md
database-rules.md
api-standard.md
coding-style.md
```

---

# Clean Architecture First

Semua project wajib mengikuti:

```text
Handler
↓
Service
↓
Repository
↓
Database
```

Dilarang:

```text
Handler
↓
Database
```

secara langsung.

---

# Readability Over Cleverness

Prioritas:

```text
Readability
```

lebih penting daripada:

```text
Complex Optimization
```

Good:

```go
user, err := repo.FindByID(id)
```

Bad:

```go
u,e:=r.F(id)
```

---

# Meaningful Naming

Nama harus jelas.

Good:

```go
CreateUser
UpdateUser
DeleteUser
```

Bad:

```go
Do
Execute
Handle
Process
```

---

# Small Functions

Target:

```text
< 50 Lines
```

Jika terlalu besar:

```text
Extract Function
```

---

# Small Files

Target:

```text
< 500 Lines
```

Jika lebih besar:

```text
Refactor
```

---

# Error Handling

Semua error wajib ditangani.

Bad:

```go
result, _ := service.Create()
```

Good:

```go
result, err := service.Create()

if err != nil {
    return err
}
```

---

# Logging

Gunakan logging untuk:

```text
Errors
Important Actions
System Events
```

Jangan log:

```text
Password
Token
API Key
Credential
```

---

# Configuration Management

Configuration wajib berasal dari:

```text
Environment Variables
```

Dilarang:

```text
Hardcoded Configuration
```

---

# Secret Management

Secret wajib berada di:

```text
.env
GitHub Secret
```

Dilarang:

```text
Source Code
Repository
Documentation
```

---

# Repository Pattern

Database Access hanya boleh melalui:

```text
Repository
```

Dilarang query database dari:

```text
Handler
Controller
```

---

# API Design

API harus:

```text
Predictable
Consistent
Versioned
Documented
```

Semua API wajib:

```text
Swagger
```

---

# Database Best Practices

Selalu gunakan:

```text
Foreign Key
Index
Migration
Audit Column
```

Jangan:

```text
Manual Schema Change
```

---

# PostgreSQL Rules

Gunakan:

```text
UUID
```

untuk Primary Key.

Gunakan:

```text
Migration
```

untuk perubahan database.

---

# GORM Best Practices

Gunakan:

```text
Repository Pattern
```

Hindari:

```text
Raw SQL
```

kecuali memang diperlukan.

---

# Frontend Best Practices

State Management:

```text
Zustand
```

Data Fetching:

```text
TanStack Query
```

Validation:

```text
Zod
```

Forms:

```text
React Hook Form
```

---

# Mobile Best Practices

Gunakan:

```text
Shared API Contract
```

dengan backend.

Jangan membuat:

```text
Business Logic Berbeda
```

antara mobile dan backend.

---

# Testing Strategy

Setiap feature wajib memiliki:

```text
Unit Test
```

Critical feature wajib memiliki:

```text
Integration Test
```

---

# Pull Request Rules

Satu Pull Request:

```text
Satu Ticket
```

Jangan:

```text
Multiple Feature
Multiple Bug
```

dalam satu PR.

---

# Commit Rules

Gunakan:

```text
feat:
fix:
refactor:
docs:
test:
```

Contoh:

```text
feat(USER-101): create user API
```

---

# Code Review Rules

Reviewer wajib memeriksa:

```text
Security
Performance
Readability
Architecture
Testing
```

---

# Refactoring Rules

Refactoring boleh dilakukan jika:

```text
Improves Readability
Improves Maintainability
Improves Performance
```

Refactoring tidak boleh:

```text
Change Existing Behavior
```

tanpa persetujuan.

---

# Performance Rules

Optimasi hanya dilakukan jika:

```text
Ada Data
Ada Evidence
Ada Bottleneck
```

Jangan melakukan:

```text
Premature Optimization
```

---

# VPS Resource Rules

Karena server menggunakan:

```text
2 vCPU
2 GB RAM
```

maka wajib:

```text
Sederhana
Ringan
Hemat Resource
```

---

# Infrastructure Best Practice

Gunakan:

```text
Docker Compose
Nginx
PostgreSQL
```

Hindari:

```text
Kubernetes
Kafka
ELK
OpenShift
```

sampai memang diperlukan.

---

# AI Agent Rules

Sebelum coding AI Agent wajib:

1. Read Jira Ticket
2. Read PRD
3. Read Architecture
4. Read Tech Stack
5. Read Security Rules

---

# AI Agent Output Rules

Output harus:

```text
Production Ready
Secure
Testable
Documented
```

Tidak boleh:

```text
Pseudo Code
Half Finished Code
Hardcoded Data
```

---

# Definition of Ready

Task siap dikerjakan jika:

```text
Jira Ticket Ada
Acceptance Criteria Ada
Scope Jelas
```

---

# Definition of Done

Task selesai jika:

```text
Build Success
Lint Success
Unit Test Pass
Documentation Updated
PR Approved
Jira Updated
```

---

# Golden Rules

Jika ragu:

```text
Pilih Solusi Paling Sederhana
```

Jika ada dua solusi:

```text
Pilih Yang Lebih Mudah Dipelihara
```

Jika ada konflik:

```text
Security > Convenience

Maintainability > Cleverness

Readability > Short Code
```