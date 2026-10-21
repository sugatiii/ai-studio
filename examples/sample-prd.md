# Product Requirement Document

---

# Document Information

Project Name:

Customer Management System

Feature Name:

Create Customer

Version:

1.0

Created Date:

2026-10-21

---

# Executive Summary

Fitur Create Customer memungkinkan Admin membuat data customer baru ke dalam sistem agar proses pengelolaan pelanggan dapat dilakukan secara terpusat.

---

# Background

Saat ini data customer dicatat secara manual menggunakan spreadsheet sehingga sering terjadi data duplikat dan kesalahan input.

---

# Problem Statement

Admin kesulitan mengelola data customer karena data tersebar di banyak file.

---

# Objectives

- Memusatkan data customer
- Mengurangi duplikasi data
- Mempercepat proses pencarian customer

---

# Success Metrics

- 100% customer tersimpan dalam sistem
- Waktu input customer < 1 menit
- Duplicate customer < 2%

---

# Target Users

Primary:

- Admin

Secondary:

- Manager

---

# In Scope

- Create Customer
- Field Validation
- Customer List Refresh

---

# Out Of Scope

- Import Excel
- Export Excel
- Customer Analytics

---

# User Flow

Admin Login
↓
Customer Menu
↓
Create Customer
↓
Submit
↓
Customer Created

---

# Functional Requirements

FR-001

Admin dapat menambahkan customer baru.

Priority:

High

---

FR-002

Email customer harus unik.

Priority:

High

---

# Non Functional Requirements

Performance

Response < 2 Seconds

Security

JWT Authentication

Availability

99%

---

# Business Rules

BR-001

Email customer harus unik.

BR-002

Nama customer wajib diisi.

BR-003

No Telp wajib diisi.

---

# Acceptance Criteria

AC-001

Given Admin Login

When Mengisi Data Valid

Then Customer Berhasil Dibuat

---

AC-002

Given Email Sudah Ada

When Submit Form

Then Tampil Error Duplicate Email

---

# Risks

- Duplikasi data lama
- Input tidak valid

---

# Dependencies

- User Authentication

---

# Definition Of Done

- Backend selesai
- Frontend selesai
- QA Approved
- Documentation Updated