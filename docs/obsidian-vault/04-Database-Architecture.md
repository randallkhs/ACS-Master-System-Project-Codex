# ACS FSM — Database Architecture

## Purpose

This file records the database architecture baseline for the ACS FSM platform.

Detailed entity notes are maintained in [[05-Database/CORE_DATA_MODEL]].

---

## Source Of Truth

The internal database is the operational source of truth.

External systems are integrations only:

- Google Calendar provides schedule input.
- Google Sheets is transitional output.
- FastField is transitional dispatch/work-order output.
- Verizon Connect is future vehicle/GPS input.
- AI providers are assistant/validation adapters.

No external system should own ACS workflow state.

---

## Initial Database Direction

Preferred database:

- PostgreSQL

Backend data layer:

- SQLAlchemy models
- Alembic migrations
- Pydantic schemas
- repository/service boundaries

---

## Foundational Models

Initial architecture should prepare:

- Customer
- Property
- Job
- WorkOrder
- Visit
- Technician
- RouteAssignment
- WaterEmergency
- ReviewItem
- AuditLog

The first implementation may keep models minimal, but relationships should not block future CRM, technician app, inventory, billing, or customer portal work.

---

## Phase 0 Module 2 Foundation Decisions

The domain model foundation now includes:

- flexible customer contact and tag fields without introducing full CRM contact tables yet
- many-to-many technician assignment support for work orders and visits
- technician vehicle and availability context
- route drive-time estimate storage
- generic Manual Review entity targeting for future export or integration actions
- default audit timestamps for traceability

These additions are schema foundation only. They do not implement dispatch workflows, Water Emergency workflow transitions, CRUD APIs, authentication, or external integrations.

---

## Data Safety Rules

- Use UUIDs for durable identifiers where appropriate.
- Use timestamps for important entities.
- Log important workflow transitions.
- Avoid hidden state in JSON files except debug/export snapshots.
- Never store secrets in source or plain documentation.
- Persist Manual Review reasons and operator decisions.
