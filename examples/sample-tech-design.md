# Technical Design Document

---

# Overview

Implementasi fitur Create Customer menggunakan React Frontend, Go Backend, dan PostgreSQL.

---

# Architecture

Frontend
↓
Backend API
↓
PostgreSQL

---

# Components

Frontend

- CustomerPage
- CustomerForm

Backend

- CustomerHandler
- CustomerService
- CustomerRepository

Database

- customers

---

# Database Design

Table:

customers

Columns:

- id UUID
- name VARCHAR(255)
- email VARCHAR(255)
- phone VARCHAR(20)
- created_at
- updated_at

---

# API Design

POST /api/v1/customers

GET /api/v1/customers

GET /api/v1/customers/{id}

PUT /api/v1/customers/{id}

DELETE /api/v1/customers/{id}

---

# Security

- JWT Authentication
- RBAC
- Input Validation

---

# Risks

- Duplicate Email
- Missing Validation

---

# Task Breakdown

Backend

- Migration
- Repository
- Service
- Handler

Frontend

- Form
- List Page

QA

- Test Cases

DevOps

- Deployment Validation