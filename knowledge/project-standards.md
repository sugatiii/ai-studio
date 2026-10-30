# Project Standards

## Purpose

This document defines project-wide standards used across all AI Studio projects.

All agents must follow this document.

Applicable To:

```text
Business Enablement Agent
PO Agent
UI/UX Agent
Architect Agent
Backend Agent
Frontend Agent
Mobile Agent
Reviewer Agent
QA Agent
DevOps Agent
```

---

# Project Structure Principle

Projects must be:

```text
Organized
Predictable
Scalable
Maintainable
```

---

# Standard Project Structure

```text
project-name/

├── business/
├── architecture/
├── api/
├── backend/
├── frontend/
├── mobile/
├── qa/
├── devops/
├── docs/
└── release/
```

---

# Branch Strategy

Use Git Flow Lite.

## Main Branch

```text
main
```

Production-ready code.

---

## Development Branch

```text
develop
```

Integration branch.

---

## Feature Branch

```text
feature/<feature-name>
```

Example:

```text
feature/customer-management
feature/customer-search
```

---

## Bugfix Branch

```text
bugfix/<bug-name>
```

Example:

```text
bugfix/customer-validation
```

---

## Hotfix Branch

```text
hotfix/<issue-name>
```

Example:

```text
hotfix/login-error
```

---

# Commit Message Standard

Format:

```text
<type>: <description>
```

---

## Allowed Types

```text
feat
fix
refactor
test
docs
chore
perf
build
ci
revert
```

---

## Examples

```text
feat: create customer API

fix: resolve duplicate customer validation

refactor: simplify customer service logic

docs: update API contract
```

---

# Pull Request Standard

Every PR must contain:

```text
Summary

Business Context

Technical Changes

Testing Completed

Risks

Rollback Strategy
```

---

# Definition Of Ready

Development can start when:

```text
Business Analysis Approved

PRD Approved

UI/UX Approved

Architecture Approved

API Contract Approved
```

---

# Definition Of Done

Feature is complete when:

```text
Code Completed

Code Reviewed

Tests Passed

QA Approved

Documentation Updated

Ready For Deployment
```

---

# Naming Convention

Use:

```text
Meaningful Names

Consistent Names

Business-Friendly Names
```

Avoid:

```text
tmp

test1

abc

foo
```

---

# Review Standards

Verify:

```text
Readability

Maintainability

Security

Scalability

Testing
```

---

# Release Standards

Every release must include:

```text
Release Notes

Deployment Plan

Rollback Plan

Validation Checklist
```

---

# Golden Rule

Projects should be:

```text
Easy To Understand

Easy To Maintain

Easy To Scale
```