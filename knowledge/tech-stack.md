# Technology Stack Standard

Version: 1.0

---

# Purpose

Dokumen ini mendefinisikan teknologi standar yang wajib digunakan oleh seluruh AI Agent dan Developer.

Tujuan:

- Konsistensi
- Maintainability
- Scalability
- Security
- Faster Development
- Reduced Technical Debt

Semua agent wajib mengikuti dokumen ini sebelum menghasilkan kode.

---

# Technology Selection Principles

Sebelum memilih teknologi, wajib mempertimbangkan:

1. Community Support
2. Long-Term Maintenance
3. Scalability
4. Security
5. Learning Curve
6. Cost
7. Enterprise Adoption

Prioritas:

```text
Stability > Trend
```

Bukan:

```text
Trend > Stability
```

---

# Approved Stack

## Frontend

Framework:

```text
React
```

Language:

```text
TypeScript
```

UI Framework:

```text
Tailwind CSS
```

State Management:

```text
Zustand
```

Data Fetching:

```text
TanStack Query
```

Form:

```text
React Hook Form
```

Validation:

```text
Zod
```

Table:

```text
TanStack Table
```

Date:

```text
Day.js
```

Charts:

```text
Recharts
```

Testing:

```text
Vitest
React Testing Library
```

---

### Frontend Folder Standard

```text
src/

├── pages/
├── components/
├── hooks/
├── services/
├── store/
├── types/
├── routes/
├── assets/
├── layouts/
├── constants/
├── utils/
└── tests/
```

---

## Backend

Runtime:

```text
Golang Stable
```

Language:

```text
Go
```

Framework:

```text
Gin
```

Alternative:

```text
Fiber
Echo
```

Validation:

```text
go-playground/validator
```

ORM:

```text
GORM
```

Query Builder Alternative:

```text
sqlx
```

Authentication:

```text
JWT
```

Authorization:

```text
RBAC
```

API Documentation:

```text
Swagger OpenAPI
```

Swagger Generator:

```text
swaggo/swag
```

Testing:

```text
testing
testify
```

Queue:

```text
Asynq
```

Alternative:

```text
Redis Queue
```

Dependency Injection:

```text
Manual Dependency Injection
```

Configuration:

```text
Viper
```

Logger:

```text
Zap
```

File Storage:

```text
Local Storage
```

Alternative:

```text
MinIO
S3
```

Migration:

```text
golang-migrate
```

Database:

```text
PostgreSQL
```

Cache:

```text
Redis
```

---

### Backend Folder Standard

```text
backend/

├── cmd/
│   └── api/
│       └── main.go
│
├── internal/
│   ├── config/
│   ├── constants/
│   ├── middleware/
│   ├── handlers/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── dto/
│   ├── validators/
│   ├── routes/
│   ├── jobs/
│   ├── utils/
│   └── database/
│
├── migrations/
│
├── docs/
│
├── tests/
│
├── scripts/
│
├── Dockerfile
├── docker-compose.yml
├── .env
├── .env.example
├── go.mod
└── go.sum
```

---

### Layer Responsibilities

### Handler Layer

Responsibilities:

- Receive HTTP Request
- Request Validation
- Call Service Layer
- Return Response

Must Not:

- Access Database Directly
- Implement Business Logic

---

### Service Layer

Responsibilities:

- Business Logic
- Transaction Management
- Domain Rules
- Process Orchestration

Must Not:

- Handle HTTP Logic
- Execute SQL Queries

---

### Repository Layer

Responsibilities:

- Database Access
- CRUD Operations
- Query Optimization

Must Not:

- Contain Business Logic

---

### Model Layer

Responsibilities:

- Database Mapping
- Entity Definition

Example:

```text
User
Role
Permission
Product
Order
```

---

### DTO Layer

Responsibilities:

- Request Structure
- Response Structure
- API Contract

Example:

```text
CreateUserRequest
UpdateUserRequest
UserResponse
```

---

### Recommended Libraries

HTTP Framework

```text
Gin
```

ORM

```text
GORM
```

Config

```text
Viper
```

Validation

```text
go-playground/validator
```

Logging

```text
Zap
```

Authentication

```text
golang-jwt/jwt
```

Testing

```text
testify
```

Documentation

```text
swaggo
```

Migration

```text
golang-migrate
```

Cache

```text
Redis
```

Queue

```text
Asynq
```

---

### Golden Rules

Backend Agent must:

- Follow Clean Architecture
- Follow Repository Pattern
- Use Dependency Injection
- Implement Unit Tests
- Implement Structured Logging
- Use Transactions for Critical Operations
- Use PostgreSQL as Primary Database
- Use GORM as Default ORM

Backend Agent must not:

- Place SQL inside Handler
- Place Business Logic inside Repository
- Hardcode Configuration
- Hardcode Secrets
- Skip Validation
- Skip Error Handling
- Skip Logging

## Mobile

Framework:

```text
React Native
```

Language:

```text
TypeScript
```

Navigation:

```text
React Navigation
```

State Management:

```text
Zustand
```

Data Fetching:

```text
TanStack Query
```

Forms:

```text
React Hook Form
```

Testing:

```text
Jest
```

---

# Database

Primary:

```text
PostgreSQL
```

Reason:

- Open Source
- Stable
- ACID
- Enterprise Ready

---

# Cache

Standard:

```text
Redis
```

Use Cases:

- Session
- Temporary Data
- API Cache
- Queue Backend

---

# Search Engine

Preferred:

```text
Elasticsearch
```

Use When:

- Full Text Search
- Large Dataset

---

# Object Storage

Development:

```text
MinIO
```

Production:

```text
AWS S3
```

Alternative:

```text
Azure Blob Storage
```

---

# API Standards

Architecture:

```text
REST API
```

Versioning:

```text
/api/v1
```

Content-Type:

```text
application/json
```

---

# API Documentation

Required:

```text
OpenAPI
Swagger
```

Every endpoint must contain:

- Summary
- Request Example
- Response Example
- Error Example

---

# Authentication

Standard:

```text
JWT
```

Structure:

```text
Access Token
Refresh Token
```

---

# Authorization

Model:

```text
RBAC
```

Example:

```text
Admin
Manager
User
Guest
```

---

# Logging

Library:

```text
Winston
```

Format:

```json
{
  "service":"user-service",
  "level":"info",
  "message":"User created"
}
```

---

# Monitoring

Metrics:

```text
Prometheus
```

Dashboard:

```text
Grafana
```

APM:

```text
OpenTelemetry
```

---

# Event Streaming

Preferred:

```text
Kafka
```

Small Projects:

```text
Redis Queue
```

Use Cases:

- Notification
- Audit
- Integration

---

# AI Components

## Model Provider

Primary:

```text
OpenRouter
```

---

## Approved Free Models

Default Priority:

```text
DeepSeek Chat
Qwen 3
Gemini Flash
Kimi
GLM
```

---

## Agent Default Mapping

PO Agent:

```text
Gemini Flash
Qwen 3
```

Architect Agent:

```text
DeepSeek Chat
Qwen 3
```

Backend Agent:

```text
DeepSeek Chat
Qwen 3
```

Frontend Agent:

```text
DeepSeek Chat
Qwen 3
```

Mobile Agent:

```text
DeepSeek Chat
Qwen 3
```

QA Agent:

```text
Qwen 3
Gemini Flash
```

DevOps Agent:

```text
DeepSeek Chat
Qwen 3
```

---

## Model Selection Rules

Priority Order:

```text
1. DeepSeek Chat
2. Qwen 3
3. Gemini Flash
4. Kimi
5. GLM
```

Choose based on:

- Availability
- Cost
- Context Window
- Response Quality

---

## Forbidden Models

Do not use:

```text
Claude Paid
GPT Paid
Gemini Pro Paid
```

unless explicitly approved.

---

## Cost Optimization

Rules:

- Prefer free models first.
- Fall back only when model is unavailable.
- Avoid premium models for routine tasks.
- Use premium models only for architecture reviews, critical code reviews, or complex debugging.

---

## AI Usage Policy

Agent must:

- Reuse existing context.
- Load project knowledge before generation.
- Read architecture.md before coding.
- Read coding-style.md before coding.
- Read tech-stack.md before coding.

Agent must not:

- Generate code without understanding project context.
- Introduce new frameworks without approval.
- Change technology stack automatically.

---

## Context Sources

Before generating output, AI Agents must read:

```text
knowledge/coding-style.md
knowledge/architecture.md
knowledge/tech-stack.md
knowledge/security-rules.md
knowledge/database-rules.md
knowledge/api-standard.md
knowledge/best-practice.md
```

Priority:

```text
Project Knowledge > Prompt > Model Preference
```

# Vector Database

Preferred:

```text
Qdrant
```

Alternative:

```text
ChromaDB
```

Use Cases:

- RAG
- Knowledge Base
- Semantic Search

---

# Agent Framework

Recommended:

```text
LangGraph
```

Alternative:

```text
CrewAI
```

Avoid:

```text
Complex framework chains
```

without business justification.

---

# Source Control

Platform:

```text
GitHub
```

Branch:

```text
main
develop
feature/*
bugfix/*
hotfix/*
```

---

# CI/CD

Platform:

```text
GitHub Actions
```

Pipeline:

```text
Build
↓
Lint
↓
Test
↓
Security Scan
↓
Docker Build
↓
Deploy
```

---

# Containerization

Required:

```text
Docker
```

Base Image:

```text
Alpine
```

Preferred:

```text
Multi-stage build
```

---

# Orchestration

Small Project:

```text
Docker Compose
```

Enterprise:

```text
Kubernetes
```

---

# Infrastructure

## Infrastructure Strategy

Primary:

```text
Self Hosted VPS
```

Objective:

```text
Low Cost
Low Resource Usage
Simple Maintenance
```

---

## VPS Specification

Current Environment:

```text
CPU  : 2 Core
RAM  : 2 GB
Disk : 50+ GB SSD
```

All solutions must be optimized for low-resource deployment.

---

## Operating System

```text
Ubuntu Server 24.04 LTS
```

---

## Deployment Stack

```text
Docker
Docker Compose
Nginx
```

Avoid:

```text
Kubernetes
OpenShift
Service Mesh
```

Reason:

- High memory consumption
- Operational complexity
- Not suitable for 2GB RAM VPS

---

## Reverse Proxy

Standard:

```text
Nginx
```

Responsibilities:

- SSL
- Routing
- Compression
- Static Assets

---

## Application Stack

Backend:

```text
NestJS
```

Frontend:

```text
NextJS Static Export
or
React Build
```

Database:

```text
PostgreSQL
```

Cache:

```text
Redis (Optional)
```

---

## Resource Priority

Highest Priority:

```text
Application
Database
```

Lower Priority:

```text
Monitoring
Analytics
```

---

## Monitoring

Lightweight only:

```text
Uptime Kuma
```

Avoid:

```text
Prometheus
Grafana
ELK Stack
```

for MVP deployment.

Reason:

High RAM usage.

---

## Logging

Standard:

```text
Application Log File
Docker Logs
```

Avoid centralized logging initially.

---

## Database

Standard:

```text
PostgreSQL
```

Configuration:

```text
Shared VPS Deployment
```

Memory Limit:

```text
256MB - 512MB
```

---

## Object Storage

Default:

```text
Local Storage
```

Do not deploy:

```text
MinIO
```

until storage requirements justify it.

---

## AI Infrastructure

Provider:

```text
OpenRouter
```

Reason:

No GPU required.

No local AI inference allowed on VPS 2GB RAM.

Avoid:

```text
Ollama
OpenWebUI
vLLM
Text Generation WebUI
Local LLM Hosting
```

---

## Vector Database

Small Project:

```text
ChromaDB
```

Preferred for MVP.

Alternative:

```text
Qdrant
```

only if semantic search becomes critical.

---

## CI/CD

Platform:

```text
GitHub Actions
```

Deployment:

```text
GitHub Actions
↓
SSH
↓
Docker Compose Pull
↓
Docker Compose Up
```

---

## Security

Required:

```text
UFW Firewall
Fail2Ban
SSL
```

SSL:

```text
Let's Encrypt
```

---

## Backup

Database:

```text
Daily Backup
```

Retention:

```text
7 Days
```

Storage:

```text
Compressed Backup File
```

---

## Recommended Containers

Maximum Running Containers:

```text
Nginx
Backend
Frontend
PostgreSQL
```

Optional:

```text
Redis
```

Maximum:

```text
4-5 Containers
```

---

## Forbidden Technologies

Do Not Deploy:

```text
Kubernetes
OpenShift
ELK Stack
Kafka
Airflow
GitLab Self Hosted
Jenkins
Ollama
OpenWebUI
```

Reason:

Not suitable for 2GB RAM infrastructure.

---

## Golden Rule

Every technology introduced must:

- Fit within 2GB RAM
- Require minimal maintenance
- Support Docker Compose
- Be deployable by a single person

If not:

```text
DO NOT USE IT
```

# Security Tools

Dependency Scan:

```text
Snyk
```

Secrets Detection:

```text
GitHub Secret Scanning
```

Container Scan:

```text
Trivy
```

---

# Testing Strategy

Minimum Coverage:

```text
80%
```

Critical Modules:

```text
90%
```

Must Have:

- Unit Test
- Integration Test
- End-to-End Test

---

# Documentation

Mandatory:

- README.md
- API Documentation
- Architecture Documentation
- Deployment Documentation

---

# AI Agent Requirements

All AI Agents must:

- Use technologies defined in this document
- Avoid introducing unapproved libraries
- Reuse existing stack
- Justify exceptions
- Update documentation

---

# Technology Decision Matrix

## Default Choice

### Frontend

```text
React
TypeScript
Vite
Tailwind CSS
Zustand
TanStack Query
```

### Backend

```text
Golang
Gin
GORM
PostgreSQL
JWT
```

### Mobile

```text
React Native
TypeScript
```

### Infrastructure

```text
Docker
Docker Compose
GitHub Actions
Nginx
```

### AI

```text
OpenRouter
ChromaDB
LangGraph
```

---

## Alternative Stack

Backend Alternative

```text
NestJS
Prisma
PostgreSQL
```

Use only if:

- Existing team already knows TypeScript backend
- Need faster onboarding
- Project heavily frontend-focused

---

## Recommended For This Project

Frontend

```text
React + TypeScript
```

Backend

```text
Go + Gin + GORM
```

Database

```text
PostgreSQL
```

Authentication

```text
JWT
```

Deployment

```text
Docker Compose
```

AI

```text
OpenRouter
```

Vector Store

```text
ChromaDB
```

# Forbidden Technologies

Do not introduce technology if:

- No maintenance team
- Experimental only
- No community adoption
- Duplicate existing functionality

---

# Golden Rule

Before adding new technology:

1. Existing solution evaluated
2. Business justification available
3. Security reviewed
4. Architecture approved
5. Documentation updated

Otherwise:

```text
DO NOT ADD NEW TECHNOLOGY
```