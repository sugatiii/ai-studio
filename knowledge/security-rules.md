# Security Rules

Version: 1.0

---

# Purpose

Dokumen ini mendefinisikan standar keamanan minimum yang wajib diterapkan oleh seluruh AI Agent dan Developer.

Security adalah tanggung jawab seluruh tim.

Semua fitur wajib mengikuti aturan pada dokumen ini.

---

# Security Principles

Priority Order:

```text
1. Authentication
2. Authorization
3. Data Protection
4. Auditability
5. Availability
```

Every feature must be:

```text
Secure By Default
```

Not:

```text
Secure Later
```

---

# Security Responsibility

PO Agent

Responsible For:

- Security Requirement Definition

---

Backend Agent

Responsible For:

- Authentication
- Authorization
- Input Validation
- API Security

---

Frontend Agent

Responsible For:

- Secure Session Handling
- Secure Token Usage

---

DevOps Agent

Responsible For:

- Server Security
- SSL
- Backup
- Firewall

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

Access Token:

```text
15 Minutes
```

Refresh Token:

```text
7 Days
```

---

# Password Rules

Minimum Length:

```text
8 Characters
```

Recommended:

```text
12 Characters
```

Required:

```text
Uppercase
Lowercase
Number
Special Character
```

---

# Password Storage

Allowed:

```text
bcrypt
```

Never:

```text
Plain Text Password
MD5
SHA1
```

---

# Authorization

Standard:

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

Every protected endpoint must verify:

```text
Authentication
Authorization
```

---

# Token Rules

Never store:

```text
Password
Sensitive Data
```

inside JWT.

Only store:

```text
User ID
Role
Session Information
```

---

# API Security

Every API must:

- Validate Request
- Validate Authentication
- Validate Authorization
- Return Standard Response

---

# Rate Limiting

Required for:

```text
Login
Register
OTP
Password Reset
```

Example:

```text
5 Requests Per Minute
```

---

# Input Validation

All request bodies must be validated.

All query parameters must be validated.

All path parameters must be validated.

Never trust client input.

---

# SQL Injection Protection

Allowed:

```text
GORM
Parameterized Query
```

Example:

```go
db.Where("email = ?", email)
```

Never:

```go
fmt.Sprintf(
  "SELECT * FROM users WHERE email='%s'",
  email,
)
```

---

# XSS Protection

Frontend must:

- Escape user content
- Sanitize HTML input

Never render raw HTML unless required.

---

# CSRF Protection

Required if:

```text
Cookie Authentication
```

Not required when:

```text
JWT Authorization Header
```

is properly implemented.

---

# Sensitive Data

Sensitive Data:

```text
Password
API Key
Access Token
Refresh Token
Private Key
Database Credential
```

Never expose sensitive data in:

```text
API Response
Log File
Frontend Source Code
Git Repository
```

---

# Environment Variables

Store secrets in:

```text
.env
```

Example:

```env
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

JWT_SECRET=

OPENROUTER_API_KEY=
```

Never commit:

```text
.env
```

to repository.

---

# Git Security

Required:

```text
.gitignore
```

Must Ignore:

```text
.env
.env.local
.env.production
```

---

# OpenRouter Security

API Key must be stored in:

```text
Environment Variable
```

Never:

```text
Hardcoded in Source Code
Hardcoded in React Frontend
```

Allowed:

```text
Backend Environment Variable
```

---

# Frontend Security

Frontend Must Not:

```text
Store Secrets
Store Database Credentials
Store API Keys
```

Frontend Should:

```text
Call Backend API
```

Backend handles:

```text
OpenRouter
Database
Business Logic
```

---

# Database Security

Database must:

```text
Require Password
```

Use:

```text
Dedicated User
```

Do Not Use:

```text
postgres superuser
```

for application access.

---

# Database Backup

Required:

```text
Daily Backup
```

Retention:

```text
7 Days
```

Backup File:

```text
Compressed
Timestamped
```

---

# VPS Security

Operating System:

```text
Ubuntu Server LTS
```

Required:

```text
SSH Key Authentication
```

Disable:

```text
Password Login
```

whenever possible.

---

# Firewall

Required:

```text
UFW
```

Open Ports:

```text
22
80
443
```

Close:

```text
Everything Else
```

---

# Fail2Ban

Required:

```text
Enabled
```

Protect:

```text
SSH
```

against brute force attack.

---

# HTTPS

Required:

```text
Yes
```

Provider:

```text
Let's Encrypt
```

Reverse Proxy:

```text
Nginx
```

No production traffic should use:

```text
HTTP Only
```

---

# File Upload Security

Validate:

```text
Extension
Content Type
Maximum Size
```

Never trust file extension only.

---

# Logging Rules

Allowed:

```text
User ID
Request ID
Error Message
```

Do Not Log:

```text
Password
Token
Credit Card Data
API Key
```

---

# Audit Log

Must Record:

```text
Login
Logout
Password Change
Role Change
Delete Operation
```

Audit Log should include:

```text
User ID
Timestamp
Action
```

---

# Dependency Security

Before deployment:

```text
Audit Dependencies
```

Required:

```text
go mod tidy
go list -m all
```

Remove:

```text
Unused Packages
```

---

# CI/CD Security

GitHub Actions must:

- Use Secrets
- Never hardcode credentials
- Never log secrets

Store credentials in:

```text
GitHub Secrets
```

---

# AI Agent Security Rules

All AI Agents must:

- Read security-rules.md before coding
- Never generate hardcoded credentials
- Never expose secret keys
- Follow authentication standard
- Follow authorization standard

---

# Security Checklist

Before Pull Request Approval:

Authentication

```text
[ ] Verified
```

Authorization

```text
[ ] Verified
```

Validation

```text
[ ] Verified
```

Logging

```text
[ ] Verified
```

Secrets

```text
[ ] Verified
```

HTTPS

```text
[ ] Verified
```

Database Access

```text
[ ] Verified
```

Audit Trail

```text
[ ] Verified
```

---

# Golden Rule

If a feature reduces security for convenience:

```text
Security Wins
```

Not:

```text
Convenience Wins
```