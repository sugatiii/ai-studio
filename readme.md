# AI Studio

AI Studio adalah framework pengembangan perangkat lunak berbasis AI Agent yang mengotomatisasi proses software development dari requirement hingga production deployment.

---

# Vision

Membangun AI Software House yang mampu menjalankan workflow development secara terstruktur menggunakan spesialis AI Agent.

Workflow utama:

```text
Business Request
        ↓
PO Agent
        ↓
Architect Agent
        ↓
Jira Planning
        ↓
Developer Agents
        ↓
Reviewer Agent
        ↓
QA Agent
        ↓
DevOps Agent
        ↓
Production
```

---

# Agent Architecture

## Product Owner Agent

Tanggung jawab:

```text
PRD
Business Rule
User Story
Acceptance Criteria
Jira Planning
```

---

## Architect Agent

Tanggung jawab:

```text
Technical Design
Database Design
API Contract
Security Design
```

---

## Backend Developer Agent

Tanggung jawab:

```text
Go
Gin
GORM
PostgreSQL
Swagger
Unit Test
```

---

## Frontend Developer Agent

Tanggung jawab:

```text
React
TypeScript
Tailwind
Zustand
TanStack Query
```

---

## Mobile Developer Agent

Tanggung jawab:

```text
React Native
TypeScript
Navigation
Mobile UX
```

---

## Reviewer Agent

Tanggung jawab:

```text
Code Review
Architecture Review
Security Review
```

---

## QA Agent

Tanggung jawab:

```text
Test Case
Regression
Security Testing
Release Validation
```

---

## DevOps Agent

Tanggung jawab:

```text
CI/CD
Docker
Deployment
Monitoring
Backup
```

---

# Repository Structure

```text
ai-studio/

├── knowledge/
├── agents/
├── templates/
├── prompts/
├── examples/
├── workflows/
├── projects/
└── outputs/
```

---

# Knowledge Base

Folder ini berisi source of truth seluruh agent.

```text
knowledge/

architecture.md
tech-stack.md
coding-style.md
security-rules.md
database-rules.md
api-standard.md
best-practice.md
```

Seluruh agent wajib membaca knowledge sebelum bekerja.

---

# Agents

Persona dan tanggung jawab masing-masing agent.

```text
agents/

po.md
architect.md
backend-dev.md
frontend-dev.md
mobile-dev.md
qa.md
reviewer.md
devops.md
```

---

# Templates

Format dokumen standar yang harus digunakan agent.

```text
templates/

prd-template.md
user-story-template.md
tech-design-template.md
api-template.md
test-case-template.md

api-contract-template.md
deployment-plan-template.md
release-note-template.md
bug-report-template.md
code-review-template.md
```

---

# Prompts

Prompt operasional utama untuk setiap tahapan workflow.

```text
prompts/

create-prd.md
create-architecture.md
create-jira-task.md

generate-backend.md
generate-frontend.md
generate-mobile.md

generate-reviewer.md
generate-qa.md
generate-devops.md
```

---

# Examples

Contoh output yang dianggap benar.

```text
examples/

sample-prd.md
sample-api-contract.md
sample-tech-design.md
sample-jira.md
sample-bug-report.md
sample-review-report.md
sample-release-note.md
```

---

# Workflows

Definisi alur kerja.

```text
workflows/

new-feature.md
bug-fix.md
hotfix.md
release.md
```

---

# Development Workflow

## New Feature

```text
Business Request
        ↓
Create PRD
        ↓
Create Architecture
        ↓
Create Jira Tasks
        ↓
Generate Backend
        ↓
Generate Frontend
        ↓
Generate Mobile
        ↓
Review
        ↓
QA
        ↓
Deploy
```

---

## Bug Fix

```text
Bug Report
        ↓
Impact Analysis
        ↓
Fix Task
        ↓
Review
        ↓
QA
        ↓
Deploy
```

---

## Hotfix

```text
Production Issue
        ↓
Urgent Fix
        ↓
Review
        ↓
Smoke Test
        ↓
Deploy
```

---

# Standard Technology Stack

Frontend

```text
React
TypeScript
Tailwind CSS
Zustand
TanStack Query
```

Backend

```text
Go
Gin
GORM
PostgreSQL
```

Mobile

```text
React Native
TypeScript
```

Infrastructure

```text
Ubuntu
Docker Compose
Nginx
PostgreSQL
GitHub Actions
```

---

# Infrastructure Constraints

Default target infrastructure:

```text
CPU  : 2 Core
RAM  : 2 GB
DISK : SSD
```

Semua solusi harus:

```text
Simple
Maintainable
Cost Efficient
Resource Efficient
```

---

# Design Principles

Semua agent wajib mengikuti:

```text
KISS
DRY
SOLID
YAGNI
```

Prioritas:

```text
Maintainability
Security
Reliability
Readability
```

---

# Security Principles

Wajib:

```text
JWT Authentication
RBAC Authorization
Input Validation
Audit Logging
HTTPS
```

Dilarang:

```text
Hardcoded Secrets
Plain Text Password
Direct OpenRouter Access From Client
```

---

# Quality Gates

Sebelum masuk production:

```text
PRD Approved
Architecture Approved
Code Reviewed
QA Approved
Deployment Validated
```

---

# Success Criteria

AI Studio dianggap berhasil apabila:

```text
Requirement jelas
Development terstandarisasi
Testing konsisten
Deployment aman
Knowledge dapat digunakan ulang
```

---

# Golden Rule

```text
Business Defines What.

Architecture Defines How.

Developers Implement.

Reviewers Protect Quality.

QA Validates.

DevOps Delivers.
```

# Installation Guide

## Requirements

### Operating System

Supported:

```text
Windows 11
Ubuntu 22.04+
Ubuntu 24.04+
macOS
WSL2
```

---

### Required Software

Git

```text
>= 2.40
```

Node.js

```text
>= 20 LTS
```

Recommended:

```text
22 LTS
```

Docker

```text
>= 27
```

Docker Compose

```text
Latest Version
```

---

### Optional Tools

VS Code

```text
Recommended
```

GitHub Desktop

```text
Optional
```

Postman

```text
Optional
```

---

## Clone Repository

```bash
git clone https://github.com/<your-org>/ai-studio.git

cd ai-studio
```

---

## Initial Setup

Create required folders:

```bash
mkdir -p projects
mkdir -p outputs
```

Expected structure:

```text
projects/
outputs/
```

---

## Environment Configuration

Create:

```text
.env
```

Example:

```env
OPENROUTER_API_KEY=

GITHUB_TOKEN=

JIRA_API_TOKEN=
JIRA_BASE_URL=

PROJECT_NAME=

DEFAULT_MODEL=
```

---

## Recommended Models

### Product Owner Agent

```text
GPT-5
Claude Sonnet
Gemini Pro
```

### Architect Agent

```text
GPT-5
Claude Sonnet
Gemini Pro
```

### Backend Agent

```text
GPT-5
Claude Sonnet
DeepSeek
```

### Frontend Agent

```text
GPT-5
Claude Sonnet
Gemini Flash
```

### Reviewer Agent

```text
GPT-5
Claude Sonnet
```

---

# Quick Start

## Create New Project

Create a project directory:

```text
projects/customer-management/
```

Example structure:

```text
customer-management/

├── business/
├── architecture/
├── jira/
├── implementation/
├── qa/
└── release/
```

---

# Development Workflow

## Step 1 - Create Business Request

Create file:

```text
projects/customer-management/business/request.md
```

Example:

```md
# Business Request

Need capability for Admin to create and manage customers.

Users:
- Admin
- Manager

Priority:
High
```

---

## Step 2 - Generate PRD

Use:

```text
prompts/create-prd.md
```

Input:

```text
business/request.md
```

Output:

```text
business/prd/prd-create-customer.md
```

---

## Step 3 - Generate Technical Design

Use:

```text
prompts/create-architecture.md
```

Input:

```text
PRD
```

Output:

```text
architecture/technical-design/td-create-customer.md
```

---

## Step 4 - Generate Jira Structure

Use:

```text
prompts/create-jira-task.md
```

Input:

```text
PRD
Technical Design
```

Output:

```text
jira/

├── epic/
├── story/
└── subtask/
```

---

## Step 5 - Generate Backend

Use:

```text
prompts/generate-backend.md
```

Input:

```text
Jira Story
Technical Design
API Contract
```

Output:

```text
Backend Source Code
Migration
Swagger
Unit Tests
```

---

## Step 6 - Generate Frontend

Use:

```text
prompts/generate-frontend.md
```

Output:

```text
Pages
Components
Hooks
Services
Store
Tests
```

---

## Step 7 - Generate Mobile

Use:

```text
prompts/generate-mobile.md
```

Output:

```text
Screens
Navigation
Store
Tests
```

---

## Step 8 - Code Review

Use:

```text
prompts/generate-reviewer.md
```

Output:

```text
Code Review Report
Quality Score
Approval Decision
```

---

## Step 9 - QA Validation

Use:

```text
prompts/generate-qa.md
```

Output:

```text
Test Cases
Regression Suite
QA Recommendation
```

---

## Step 10 - Deployment Planning

Use:

```text
prompts/generate-devops.md
```

Output:

```text
Deployment Plan
Rollback Plan
Infrastructure Review
Release Recommendation
```

---

# Workflow Overview

## New Feature Workflow

```text
Business Request
        ↓
Create PRD
        ↓
Create Architecture
        ↓
Create Jira Tasks
        ↓
Backend Development
        ↓
Frontend Development
        ↓
Mobile Development
        ↓
Code Review
        ↓
QA Validation
        ↓
Deployment
        ↓
Production
```

---

## Bug Fix Workflow

```text
Bug Report
        ↓
Root Cause Analysis
        ↓
Fix Development
        ↓
Review
        ↓
QA
        ↓
Deploy
```

---

## Hotfix Workflow

```text
Production Issue
        ↓
Impact Analysis
        ↓
Fix
        ↓
Review
        ↓
Smoke Test
        ↓
Deploy
```

---

# Git Strategy

## Main Branch

```text
main
```

## Development Branch

```text
develop
```

## Feature Branch

```text
feature/CRM-101-create-customer
```

## Bug Fix Branch

```text
bugfix/CRM-201-fix-login
```

## Hotfix Branch

```text
hotfix/PROD-001-payment-error
```

---

# Naming Conventions

## PRD

```text
prd-create-customer.md
```

## Technical Design

```text
td-create-customer.md
```

## API Contract

```text
api-create-customer.md
```

## Jira Task

```text
CRM-101-create-customer.md
```

## Test Case

```text
tc-create-customer.md
```

---

# Quality Gates

Every feature must pass:

```text
✓ PRD Review

✓ Technical Design Review

✓ Code Review

✓ Security Validation

✓ QA Validation

✓ Deployment Validation
```

before production deployment.

---

# Troubleshooting

## Agent Produces Inconsistent Results

Verify:

```text
knowledge/*
templates/*
examples/*
```

are aligned and updated.

---

## Agent Ignores Standards

Verify prompt includes references to:

```text
knowledge/*
agents/*
templates/*
```

---

## Output Quality Is Low

Provide:

```text
Prompt
+
Template
+
Example
+
Relevant Context
```

at the same time.

---

# Recommended Project Structure

```text
projects/

└── customer-management/
    ├── business/
    │   ├── request.md
    │   ├── prd/
    │   └── stories/
    │
    ├── architecture/
    │   ├── technical-design/
    │   └── api-contract/
    │
    ├── jira/
    │   ├── epic/
    │   ├── story/
    │   └── subtask/
    │
    ├── implementation/
    │   ├── backend/
    │   ├── frontend/
    │   └── mobile/
    │
    ├── qa/
    │   ├── test-cases/
    │   ├── bug-reports/
    │   └── reports/
    │
    └── release/
        ├── deployment/
        ├── release-notes/
        └── rollback-plans/
```

---

# Future Roadmap

Planned:

```text
Agent Orchestration Engine

GitHub Integration

Jira Integration

Automatic Story Creation

Automatic PR Creation

Automatic Code Review

Automatic Deployment

Knowledge RAG

Agent Memory

Project Dashboard

Metrics Dashboard
```

---

# Philosophy

AI Studio follows:

```text
Business First

Architecture Before Code

Quality Before Release

Security By Default

Automation Where Possible

Simplicity Over Complexity
```

---

# Golden Rule

```text
Requirements Define The What.

Architecture Defines The How.

Developers Implement.

Reviewers Protect Quality.

QA Validates.

DevOps Delivers.
```