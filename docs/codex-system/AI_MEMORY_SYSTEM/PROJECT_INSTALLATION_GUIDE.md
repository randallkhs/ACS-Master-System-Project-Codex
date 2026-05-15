# Project Memory Installation Guide

## Purpose

This guide explains how to install AI project memory files into any project.

---

# Install Command

From:

/Users/randyr/Library/Mobile Documents/com~apple~CloudDocs/Codex-MCP/AI_MEMORY_SYSTEM

Run:

./init_project_memory.sh /path/to/project

---

# Example

./init_project_memory.sh /Users/randyr/Library/Mobile\ Documents/com\~apple\~CloudDocs/ACS-Projects/ACS-Workflow-Master-System

---

# Files Created

The script creates:

- ARCHITECTURE.md
- PROJECT_STATE.md
- AI_NOTES.md
- KNOWN_ISSUES.md
- CHANGELOG.md

---

# How Codex Should Use Them

For every project session, Codex should first read:

1. PROJECT_STATE.md
2. AI_NOTES.md

Codex should only read deeper files when needed:

- ARCHITECTURE.md
- KNOWN_ISSUES.md
- CHANGELOG.md

---

# When To Update Files

Before ending major work sessions, Codex should update:

- PROJECT_STATE.md
- AI_NOTES.md

If needed, update:

- ARCHITECTURE.md
- KNOWN_ISSUES.md
- CHANGELOG.md

---

# Efficiency Rule

Do not over-document.

Only record:

- meaningful project changes
- important decisions
- known problems
- architecture changes
- reusable discoveries

Avoid recording trivial UI tweaks or temporary experiments.
