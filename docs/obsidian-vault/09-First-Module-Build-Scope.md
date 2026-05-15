# ACS FSM — First Module Build Scope

# Purpose

This document defines the EXACT scope of the first ACS FSM rebuild module.

The goal is to:
- replace the fragile existing CleaningWorkflow system
- stabilize operations
- build professional architecture
- prepare long-term scalability

WITHOUT attempting to build the entire future FSM platform immediately.

---

# 1. Primary Goal

Replace the current:
- Google Calendar → Sheets → FastField workflow

with a properly architected operational dispatch platform.

---

# 2. What This First Module WILL Include

## Core Operational Features

### Calendar Import
- Google Calendar integration
- next-day schedule import
- event normalization

---

### Dispatch Pipeline
- classification
- validation
- confidence scoring
- cancellation detection
- AM/PM detection
- Water Emergency detection

---

### Manual Review Queue
- low-confidence jobs
- malformed jobs
- uncertain cancellations
- invalid addresses
- duplicate detection

---

### Routing System
- North/South grouping
- route optimization
- technician grouping preparation

---

### Spreadsheet Generation
- operational dispatch sheets
- separate Water Emergency grouping
- AM/PM grouping

---

### FastField Transitional Export
- standard jobs export
- Water Emergency export
- adapter-based architecture

---

### Water Emergency Workflow Foundation
- Water Emergency job entities
- visit structure
- status lifecycle
- preparation for future expansion

---

### Admin Dashboard
Initial dashboard functionality:
- operational overview
- dispatch review
- manual review queue
- routing visibility
- export actions
- logs/errors

---

### Audit Logging
- imports
- validation warnings
- dispatch actions
- manual overrides
- exports

---

# 3. What This First Module WILL NOT Include Yet

## NOT INCLUDED YET

### Billing
- invoices
- payments
- accounting

---

### Inventory Management
- product tracking
- chemical inventory
- warehouse management

---

### Technician Mobile App
- field app
- live updates
- photo uploads
- signatures

---

### Vehicle Tracking
- Verizon Connect integration
- GPS live tracking

---

### Payroll
- payroll calculation
- labor tracking

---

### CRM
- customer communication system
- marketing tools

---

### Full Customer Portal
- customer dashboards
- customer requests
- self-service workflows

Only architecture preparation will exist.

---

# 4. Architecture Requirements

The first module MUST be designed so future modules can attach cleanly.

Examples:
- billing
- inventory
- CRM
- technician apps
- customer portals

The architecture must avoid:
- tight coupling
- monolithic logic
- spreadsheet dependency
- FastField dependency

---

# 5. Technical Direction

## Backend
- Python
- FastAPI
- PostgreSQL

---

## Frontend
- Next.js
- TypeScript
- Tailwind

---

## Deployment
- VPS initially
- scalable architecture later

---

# 6. Operational Philosophy

The first module must prioritize:

1. Reliability
2. Deterministic workflows
3. Human review safety
4. Auditability
5. Extensibility

NOT:
- maximum automation
- AI over-control
- risky auto-dispatch

---

# 7. AI Usage

AI may assist:
- classification
- anomaly detection
- validation suggestions

AI must NOT:
- override human operators
- auto-confirm dangerous actions
- auto-dispatch uncertain jobs

---

# 8. FastField Strategy

FastField is temporary compatibility infrastructure.

The system architecture must assume:
- FastField will eventually be replaced

Future versions will include:
- native ACS technician workflows
- ACS technician mobile apps

---

# 9. Current Operational Priority

The MOST IMPORTANT operational goals are:

1. prevent bad dispatches
2. prevent canceled jobs from dispatching
3. stabilize Water Emergency workflow handling
4. reduce human operational workload
5. improve routing consistency
6. improve operational visibility

---

# 10. Long-Term Vision

This module is the FIRST FOUNDATION PIECE of a complete company operational ecosystem.

Future expansion must remain possible without:
- rewriting core architecture
- rebuilding database structure
- replacing workflow foundations