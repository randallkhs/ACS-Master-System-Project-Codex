# ACS FSM System — Master Project Index

## Project Vision

Apple Cleaning Systems is building a long-term custom FSM (Field Service Management) platform designed to eventually replace multiple external operational systems and centralize company workflow into one integrated ecosystem.

The system will progressively include:

- Dispatch management
- Water emergency workflows
- Route optimization
- Technician management
- Customer portals
- Google Calendar integration
- Google Sheets integration
- FastField transitional integration
- Future technician mobile app
- Inventory management
- Equipment tracking
- Billing and invoicing
- Vehicle/GPS integrations
- AI-assisted workflow validation
- Internal operational dashboards

---

# Core Philosophy

The system must NOT rely heavily on AI interpreting messy human-written text.

Instead:

- structured operational workflows
- deterministic state-driven logic
- human verification systems
- AI-assisted validation only when necessary

The database becomes the operational source of truth.

Google Calendar, email, and FastField become external integrations/adapters.

---

# Current Development Phase

## Phase 1
Rebuild and replace the existing CleaningWorkflow system from scratch using proper architecture.

Focus areas:

- Dispatch pipeline
- Water emergency workflow
- Calendar normalization
- Manual review queue
- Route optimization
- Spreadsheet generation
- FastField export compatibility
- Admin operational dashboard

---

# Important Documents

## Operational Rules
- [[01-Business-Rules]]

## Water Emergency Lifecycle
- [[02-Water-Emergency-Workflow]]

## Dispatch Engine
- [[03-Dispatch-Pipeline]]

## Database Design
- [[04-Database-Architecture]]

## System Architecture
- [[05-System-Architecture]]

## External Integrations
- [[06-API-Integrations]]

## Codex Decisions
- [[07-Codex-Decisions-Log]]

## AI / Research Knowledge
- [[08-New-AI-Knowledge]]

## Current Module Scope
- [[09-First-Module-Build-Scope]]

---

# Technical Direction

## Backend
- Python
- FastAPI
- PostgreSQL
- Redis (future)
- Celery/background jobs (future)

## Frontend
- Next.js
- TypeScript
- Tailwind
- Professional dashboard architecture

## Infrastructure
- VPS hosted initially
- Future scalable architecture
- Adapter-based integrations

---

# Development Rules

1. No temporary hacks.
2. Every workflow must be state-driven.
3. All important actions must be logged.
4. Human review always overrides automation.
5. AI should assist operations, not control operations.
6. Every module must be independently extensible.
7. Water Emergency workflows are first-class workflows, not secondary job types.
8. Avoid vendor lock-in.
9. FastField is transitional, not permanent.
10. The database is the source of truth.

---

# Future System Modules

## Planned Modules
- Dispatch
- Water Emergency
- CRM
- Customer Portal
- Technician Mobile App
- Inventory
- Billing
- Reporting
- Vehicle Tracking
- Equipment Lifecycle
- AI Operational Assistant
- Internal Messaging
- Payroll Support
- Analytics

---

# Notes

This vault acts as long-term operational memory for:
- Codex
- ChatGPT
- future developers
- company operational consistency
