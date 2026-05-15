# How To Use The AI Memory System

## Purpose

This system helps Codex maintain useful long-term project memory without wasting tokens.

It separates:

- global AI rules
- project-specific memory
- category-specific technical knowledge

---

# Main Rule

Do not load everything automatically.

Use layered memory loading.

---

# Recommended Reading Order

## Always Read First

For any project task, Codex should read:

1. PROJECT_STATE.md
2. AI_NOTES.md

These files should stay compact and high-signal.

---

## Read Only When Needed

Codex should read these only when relevant:

- ARCHITECTURE.md
- KNOWN_ISSUES.md
- category knowledge files

---

## Read Rarely

Codex should read CHANGELOG.md only when historical context is needed.

---

# Category Knowledge Usage

Before doing internet research, Codex should check the relevant category folder.

Examples:

For PySide6:
category-knowledge/pyside6/

For Tailwind:
category-knowledge/tailwind/

For Next.js:
category-knowledge/nextjs/

For Python:
category-knowledge/python-development/

For UI design:
category-knowledge/ui-design/

---

# Internet Research Rules

Codex should search the internet only when:

1. No useful category knowledge exists.
2. Existing knowledge is stale.
3. The framework or API may have changed.
4. The task is complex and requires current information.

---

# Knowledge Update Rules

When Codex finds reusable, important, current technical information, it should update the proper category:

- NEW_AI_KNOWLEDGE.md
- BEST_PRACTICES.md
- KNOWN_PATTERNS.md

Do not save trivial findings.

---

# Project Memory Update Rules

Before ending major work sessions, Codex should update:

- PROJECT_STATE.md
- AI_NOTES.md

If needed, update:

- ARCHITECTURE.md
- KNOWN_ISSUES.md
- CHANGELOG.md

---

# Efficiency Rule

The system should reduce repeated research, repeated explanation, and context loss.

It should not become a giant documentation burden.
