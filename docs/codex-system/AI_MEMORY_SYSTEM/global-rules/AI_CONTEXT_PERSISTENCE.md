# AI Context Persistence Rules

## Core Goal

Maintain long-term project continuity while minimizing unnecessary token usage.

AI agents must preserve:
- architecture consistency
- workflow continuity
- important discoveries
- project state awareness

without creating excessive context overhead.

---

# Context Loading Strategy

Use layered memory loading.

## Layer 1 — Always Read First

Read these first:

- PROJECT_STATE.md
- AI_NOTES.md

These files should remain:
- compact
- high-signal
- frequently updated

---

## Layer 2 — Read Only When Needed

Read only if relevant:

- ARCHITECTURE.md
- KNOWN_ISSUES.md
- category knowledge files

Do NOT load automatically unless needed.

---

## Layer 3 — Rarely Needed

Read only for historical debugging:

- CHANGELOG.md
- archived notes

Avoid loading large history unnecessarily.

---

# Context Compression Philosophy

Prefer:
- compact summaries
- architecture overviews
- focused notes

Avoid:
- giant session transcripts
- excessive detail
- repetitive summaries

---

# Session End Rules

Before ending major implementation sessions:

Update:
- PROJECT_STATE.md
- AI_NOTES.md

If needed:
- KNOWN_ISSUES.md
- ARCHITECTURE.md

Only document:
- meaningful changes
- reusable discoveries
- important architectural decisions
- unresolved problems

---

# Continuity Rules

When resuming work:

1. Read PROJECT_STATE.md first.
2. Read AI_NOTES.md second.
3. Load deeper files only if needed.

Avoid re-analyzing the entire codebase unnecessarily.

---

# Architecture Preservation

Always preserve:
- established folder structure
- naming consistency
- architectural patterns
- UI philosophy

Avoid introducing:
- conflicting patterns
- inconsistent workflows
- unnecessary rewrites

---

# Token Efficiency Rules

Optimize for:
- minimal unnecessary reading
- selective context loading
- high signal-to-noise ratio

Avoid:
- loading unrelated categories
- reading outdated knowledge
- loading giant memory files

---

# AI Memory Philosophy

Project memory should function as:

- persistent project continuity
- reusable architectural memory
- compact operational knowledge

NOT:
- giant historical archives
- full project duplication
- unnecessary verbose logging
