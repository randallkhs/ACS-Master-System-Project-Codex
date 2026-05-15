# ACS Master System Project

Custom AI-assisted Field Service Management (FSM) platform for Apple Cleaning Systems.

## Phase 0 Goals

The purpose of Phase 0 is to establish:

- Repository structure
- Codex operating environment
- Obsidian knowledge vault integration
- System architecture foundation
- Engineering rules
- AI operational directives
- Dispatch engine planning
- Water Emergency workflow planning
- Documentation-first development workflow

---

## Critical Rules

Before generating code:

1. Read `AGENTS.md`
2. Read all architecture documents
3. Read all Phase 0 planning documents
4. Follow `CODEX_PHASE_0_BUILD_PROMPT.md`
5. Never bypass manual review safety rules
6. Never silently process uncertain jobs

---

## Main Documentation

Primary project documentation lives in:

```text
/docs/obsidian-vault/
⸻

Architecture

Main architecture directives:

* SYSTEM_ARCHITECTURE_V1.md
* PROJECT_ARCHITECTURE_VISION.md
* 04-Database-Architecture.md

⸻

Current Development Status

Current phase:

PHASE 0 — FOUNDATION & ARCHITECTURE

System status:

PLANNING / INITIALIZATION

backend/
frontend/
infrastructure/
docs/

⸻

Important Notes

This system is intended to replace multiple operational platforms currently used by ACS, including:

* FastField
* Spreadsheet-based dispatch workflows
* Manual routing systems
* Fragmented workflow tools

The system is being designed as a long-term scalable internal company platform.

⸻

AI Safety Rule

If the system is not confident:

* DO NOT auto-process
* DO NOT auto-dispatch
* Flag for manual review
* Explain uncertainty

```text
