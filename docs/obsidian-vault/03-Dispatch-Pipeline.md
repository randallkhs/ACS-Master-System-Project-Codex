# ACS FSM — Dispatch Pipeline

# Purpose

This document defines the official dispatch pipeline workflow for the ACS FSM platform.

The dispatch pipeline is responsible for:

- importing operational jobs
- validating operational data
- detecting problems
- routing technicians
- generating dispatch-ready output
- supporting FastField transitional workflows

This document describes BOTH:
- current operational behavior
- future architectural direction

---

# 1. High-Level Pipeline

```text
Google Calendar
    ↓
Calendar Import
    ↓
Normalization
    ↓
Classification
    ↓
Validation
    ↓
Confidence Scoring
    ↓
Manual Review Queue (if needed)
    ↓
Routing Engine
    ↓
Dispatch Generation
    ↓
Spreadsheet / FastField Export
    ↓
Audit Logging

2. Calendar Import Stage

Current Behavior

The system imports:

* NEXT DAY jobs only

Example:

* current date = 2026-05-14
* imported jobs = 2026-05-15

---

Future Behavior

Future versions may support:

* same-day dispatch
* live updates
* recurring synchronization
* customer portal requests

---

3. Import Sources

Current import sources:

* Google Calendar

Future sources:

* customer portal
* technician requests
* emergency intake forms
* CRM system
* API integrations

---

4. Normalization Stage

Imported events must be normalized into structured internal data.

Examples:

* customer name
* address
* state
* AM/PM markers
* cancellation indicators
* water emergency detection
* technician requirements

---

5. Classification Stage

Jobs must be classified into operational categories.

Examples:

* standard cleaning
* water emergency
* canceled
* manual review required

---

6. Cancellation Detection

The system must detect cancellation indicators using:

* fuzzy matching
* spelling tolerance
* confidence scoring

Examples:

* canceled
* cancelled
* canseled
* cancelld
* canneled

Low-confidence results must trigger:

* manual review

---

7. AM/PM Detection

The system must detect:

* AM jobs
* PM jobs

Examples:

* AM/DE
* DE/AM
* PM/NJ
* NJ/PM

These affect:

* routing
* technician scheduling
* dispatch grouping

---

8. State Detection

The system must detect:

* DE
* MD
* PA
* NJ

Future versions may support:

* expanded service regions

---

9. Address Validation

Addresses should be validated before dispatch.

Potential validation:

* malformed addresses
* missing street numbers
* incomplete ZIP codes
* duplicate addresses

Invalid addresses trigger:

* manual review

---

10. Water Emergency Detection

The system must identify Water Emergency workflows separately from standard jobs.

Examples:

* extraction
* flood
* water damage
* drying
* moisture
* dehumidifier

Water Emergency jobs follow different operational workflows.

---

11. Confidence Scoring

Each imported job should receive:

* operational confidence score

Examples:

High confidence

* valid address
* clear job type
* valid state marker
* no conflicting indicators

Low confidence

* malformed title
* unclear cancellation
* missing address
* conflicting states

---

12. Manual Review Queue

Jobs requiring human review must be isolated before dispatch.

Examples:

* unclear cancellation
* invalid address
* duplicate jobs
* missing data
* low confidence parsing

The system must NEVER auto-dispatch uncertain jobs.

---

13. Routing Engine

Current Routing

Current strategy:

* North group
* South group

based on:

* depot location

---

Future Routing

Future routing should support:

* AM/PM windows
* technician skills
* live traffic
* GPS integration
* Water Emergency priority
* technician availability
* equipment constraints

---

14. Technician Assignment

Dispatch generation should eventually support:

* technician specialization
* workload balancing
* regional familiarity
* emergency prioritization

---

15. Spreadsheet Generation

Current workflow generates:

* Google Sheets operational spreadsheet

Separate sections:

* standard jobs
* AM/PM jobs
* Water Emergency jobs

---

16. FastField Export

Current system exports operational data to FastField.

Different forms:

* standard jobs
* Water Emergency jobs

Future system must support:

* adapter-based export architecture

The core system should NOT depend tightly on FastField.

---

17. Audit Logging

All major pipeline stages must be logged.

Examples:

* imported jobs
* normalized records
* validation warnings
* routing results
* dispatch exports
* manual review decisions

Logs must support:

* debugging
* operational auditing
* future analytics

---

18. Future Customer Portal Integration

Future workflow:

Customer Portal
    ↓
Structured Request Form
    ↓
Internal Validation
    ↓
Dispatch Pipeline

This reduces:

* human spelling errors
* malformed requests
* ambiguous operational text

---

19. AI Usage

AI may assist:

* classification
* validation
* anomaly detection
* operational recommendations

AI must NOT:

* override human review
* auto-confirm cancellations
* auto-close Water Emergency workflows

---

20. Long-Term Goal

The dispatch pipeline should evolve into:

* deterministic
* state-driven
* scalable
* modular
* auditable
* API-first

The future platform must eventually replace:

* spreadsheet dependency
* fragmented workflows
* manual coordination
* fragile calendar parsing
```
