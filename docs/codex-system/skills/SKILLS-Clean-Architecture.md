# SKILLS - Clean Architecture Expert

## Core Philosophy

Architecture must prioritize:

- Scalability
- Maintainability
- Readability
- Separation of concerns
- Reusability
- Long-term project health

Avoid:
- tightly coupled systems
- giant files
- spaghetti architecture
- unclear responsibilities
- duplicated business logic

---

# File Organization

Prefer:

- many small focused files
- feature-based organization
- isolated responsibilities
- reusable modules

Avoid:
- giant app.py files
- giant components
- overly centralized logic

---

# Separation of Concerns

Always separate:

- UI
- business logic
- data access
- API communication
- state management
- utilities

Avoid mixing unrelated responsibilities.

---

# Component Philosophy

Components and modules should:

- have one clear purpose
- be reusable
- remain readable
- avoid unnecessary dependencies

Prefer:
- composition
over:
- massive inheritance chains

---

# Backend Structure

Prefer:

- routers
- services
- repositories
- models
- utilities
- configuration layers

Avoid:
- business logic directly in routes
- massive endpoint files
- tightly coupled database logic

---

# Frontend Structure

Prefer:

- reusable UI components
- isolated state
- feature folders
- clean hooks
- modular layouts

Avoid:
- giant pages
- duplicated state logic
- deeply nested complexity

---

# State Management

Keep state:

- localized when possible
- predictable
- easy to debug

Avoid:
- unnecessary global state
- deeply chained state mutations

---

# Reusability

Always look for:

- reusable patterns
- shared utilities
- scalable abstractions

But avoid:
- premature overengineering

---

# Refactoring Philosophy

Prefer:

- incremental improvements
- preserving stability
- clean migrations
- architecture consistency

Avoid:
- unnecessary rewrites
- destabilizing changes

---

# Professional Standards

The project should feel:

- professionally engineered
- scalable
- maintainable
- production ready

The architecture should remain understandable even as the project grows.
