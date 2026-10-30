# Code Review Standards

## Purpose

This document defines the standards, principles, and expectations for code reviews across all AI Studio projects.

The goal is to ensure:

```text
Code Quality

Maintainability

Security

Performance

Reliability

Consistency
```

Applicable To:

```text
Reviewer Agent

Backend Agent

Frontend Agent

Mobile Agent

Architect Agent

QA Agent
```

---

# Review Philosophy

Code review is not:

```text
Finding mistakes
```

Code review is:

```text
Improving software quality.
```

The objective is:

```text
Reduce Defects

Improve Maintainability

Share Knowledge

Protect Architecture

Protect Security
```

---

# Primary Review Areas

Every review must evaluate:

```text
Correctness

Readability

Maintainability

Security

Performance

Testing

Architecture Compliance
```

---

# Correctness

Verify:

```text
Business Requirements Satisfied

Acceptance Criteria Covered

Logic Works Correctly

Edge Cases Considered

Error Cases Handled
```

Questions:

```text
Does it work?

Does it solve the problem?

Will it fail under expected conditions?
```

---

# Readability

Code is read far more often than it is written.

Prefer:

```text
Self Documenting Code
```

---

## Verify

```text
Meaningful Naming

Small Functions

Clear Intent

Consistent Style
```

---

## Avoid

```text
Abbreviations

Magic Numbers

Deep Nesting

Cryptic Logic
```

---

# Naming Standards

Names should reveal intent.

---

## Good

```text
customerRepository

calculateInvoiceTotal

isCustomerActive
```

---

## Bad

```text
cr

temp

data

x
```

---

# Maintainability

Verify:

```text
Modular Design

Reusability

Separation Of Concerns

Low Coupling

High Cohesion
```

---

## Questions

```text
Can this code be modified safely?

Can another developer understand it?

Can it be extended easily?
```

---

# Architecture Compliance

Code must follow approved architecture.

Verify:

```text
Folder Structure

Design Patterns

Layer Separation

Domain Boundaries
```

---

## Violations

Examples:

```text
Business Logic In Controllers

Database Calls In UI Layer

Tight Coupling Across Modules
```

---

# Security Review

Security is mandatory.

Every review must evaluate:

```text
Authentication

Authorization

Input Validation

Sensitive Data Handling

Secrets Management
```

---

# Authentication

Verify:

```text
Protected Endpoints

Token Validation

Session Validation
```

---

# Authorization

Verify:

```text
Proper Role Checks

Permission Enforcement

Access Restrictions
```

---

## Common Mistakes

```text
UI Authorization Only

Missing Backend Validation

Hardcoded Admin Access
```

---

# Input Validation

Verify:

```text
Required Fields

Length Validation

Format Validation

Boundary Validation
```

---

## Reject

```text
Unvalidated User Input
```

---

# Sensitive Data Handling

Never expose:

```text
Passwords

Secrets

Private Keys

Access Tokens

Internal Credentials
```

---

# Performance Review

Verify:

```text
Unnecessary Queries

Repeated Computation

Large Memory Usage

Blocking Operations
```

---

# Backend Performance

Look for:

```text
N+1 Queries

Inefficient Loops

Missing Pagination

Slow Database Calls
```

---

# Frontend Performance

Look for:

```text
Unnecessary Re-Renders

Large Component Trees

Inefficient State Updates

Unoptimized Rendering
```

---

# Mobile Performance

Look for:

```text
Heavy Rendering

Memory Leaks

Excessive Network Calls
```

---

# Error Handling

Every critical operation should handle failure.

---

## Verify

```text
Error Handling Present

Meaningful Error Messages

Logging Implemented

Fallback Defined
```

---

## Avoid

```text
Silent Failure

Empty Catch Blocks

Unhandled Exceptions
```

---

# Logging Review

Verify:

```text
Useful Logs

Appropriate Log Levels

Traceability
```

---

## Log Levels

```text
DEBUG

INFO

WARN

ERROR
```

---

## Reject

```text
Sensitive Data In Logs
```

---

# Testing Review

Every implementation should be testable.

Verify:

```text
Unit Tests

Integration Tests

Edge Case Coverage

Happy Path Coverage
```

---

# Coverage Expectations

Minimum:

```text
70%
```

Recommended:

```text
80%
```

Critical Systems:

```text
90%+
```

---

# API Review Standards

Review:

```text
Request Validation

Response Structure

Error Handling

HTTP Status Usage

Authentication Rules
```

---

## Verify

```text
API Contract Compliance
```

---

# Database Review Standards

Verify:

```text
Indexes

Constraints

Normalization

Transactions
```

---

## Common Issues

```text
Missing Indexes

Duplicate Data Risk

Inefficient Queries
```

---

# Frontend Review Standards

Verify:

```text
Accessibility

State Management

Component Reusability

Error Handling

Responsive Design
```

---

# Accessibility Review

Verify:

```text
Labels Present

Keyboard Navigation

Focus States

Color Contrast
```

---

# Mobile Review Standards

Verify:

```text
Navigation Flow

Offline Scenarios

Touch Targets

Responsive Behavior
```

---

# Dependency Review

Verify:

```text
Dependency Necessity

Security Risks

Version Stability

Maintenance Status
```

---

## Avoid

```text
Unused Dependencies

Abandoned Packages

Duplicate Libraries
```

---

# Documentation Review

Verify:

```text
Documentation Updated

API Documentation Updated

README Updated

Architecture Updated
```

---

# Code Smells

Watch for:

```text
Long Functions

Large Classes

Duplicate Code

Excessive Parameters

Deep Nesting

Feature Envy

God Objects
```

---

# Review Severity Levels

## Critical

Must be fixed before merge.

Examples:

```text
Security Vulnerability

Data Corruption Risk

Broken Business Logic
```

---

## High

Should be fixed before merge.

Examples:

```text
Architecture Violation

Performance Issue

Missing Validation
```

---

## Medium

Fix if practical.

Examples:

```text
Readability Problems

Minor Refactoring
```

---

## Low

Optional improvements.

Examples:

```text
Naming Improvements

Code Style Enhancements
```

---

# Review Output Format

Reviewer must provide:

## Summary

Overall assessment.

---

## Findings

### CRITICAL

List issues.

---

### HIGH

List issues.

---

### MEDIUM

List issues.

---

### LOW

List issues.

---

## Positive Observations

Highlight good practices.

---

## Recommendation

Choose:

```text
Approve

Approve With Minor Changes

Request Changes

Reject
```

---

# Approval Criteria

Code may be approved only if:

```text
Requirements Met

Architecture Followed

Security Validated

Tests Passed

No Critical Findings

No High Findings
```

---

# Definition Of Done

Review is complete when:

```text
All Findings Addressed

Tests Passing

Documentation Updated

Approval Decision Recorded
```

---

# Review Checklist

Verify:

```text
[ ] Requirements Implemented

[ ] Acceptance Criteria Covered

[ ] Security Reviewed

[ ] Validation Present

[ ] Error Handling Present

[ ] Tests Added

[ ] Documentation Updated

[ ] Architecture Followed

[ ] Performance Acceptable

[ ] No Critical Risks
```

---

# Anti Patterns

Avoid:

```text
Rubber Stamp Reviews

Style-Only Reviews

Ignoring Security

Ignoring Business Requirements

Ignoring Testing

Approving Unreviewed Changes
```

---

# Golden Rule

A successful code review answers:

```text
Is this code safe to maintain,
safe to operate,
and safe to release?
```

Not merely:

```text
Does this code compile?
```