# Research Memory Rules

## Purpose

This file defines how Codex should store reusable technical knowledge learned from internet research, Context7, API docs, SDK docs, framework docs, or official documentation.

The goal is to reduce repeated research, preserve up-to-date technical findings, and keep project knowledge fresh over time.

---

## Core Rule

When Codex researches current technical information and the information may be useful again in this project or future projects, Codex must save a concise knowledge note.

---

## Before Researching

Before doing new research, Codex should check the relevant Obsidian knowledge files first.

If existing knowledge is:
- relevant
- current
- inside its recheck window

Codex should use the stored note instead of researching again.

If the knowledge is expired or incomplete, Codex should refresh it.

---

## When To Save New Knowledge

Save new knowledge when it is about:

- APIs
- SDKs
- frameworks
- libraries
- CLI tools
- cloud services
- deployment processes
- authentication flows
- breaking changes
- version migrations
- production best practices
- security-relevant technical details

Do not save:

- one-time debugging details
- obvious general programming knowledge
- temporary errors
- unrelated search results
- speculative information

---

## Required Knowledge Entry Format

Each saved research note must include:

```md
## Topic: [Short Topic Name]

- Date learned: YYYY-MM-DD
- Category: [frontend/backend/database/deployment/security/api/integration/ai/etc.]
- Recheck after: YYYY-MM-DD
- Source links:
  - [link 1]
  - [link 2]
- Summary:
  - concise useful summary
- Applicable projects:
  - ACS-FSM
  - other projects if relevant
- Confidence:
  - High / Medium / Low
- Notes:
  - implementation notes or caveats

Recheck Rule

Default recheck window:

fast-changing frameworks/APIs: 60 days
security/auth/deployment: 30 days
stable concepts: 180 days
If the current date is past the Recheck after date, Codex should refresh the research before relying on the note.

Preferred Storage Locations

General reusable knowledge:

15-Research/NEW_AI_KNOWLEDGE.md

Project-specific AI/research rules:

08-AI-Systems/AI_AUTOMATION_RULES.md

Integration-specific knowledge:

04-Integrations/
16-API-Docs/

Architecture-impacting research:

01-Architecture/
13-Decisions/

Decision Logging

If the research changes an architectural or workflow decision, Codex must also update:

13-Decisions/07-Codex-Decisions-Log.md

Final Rule

Research memory must be concise.

Do not copy full documentation.

Store only:

what was learned
why it matters
where it came from
when to recheck it

```