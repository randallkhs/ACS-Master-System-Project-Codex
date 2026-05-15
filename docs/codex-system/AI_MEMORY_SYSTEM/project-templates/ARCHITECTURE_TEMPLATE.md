# Project Architecture

## Project Purpose

Describe:
- what the application does
- primary goals
- intended users
- core workflows

Keep concise.

---

# Core Technologies

List:
- frameworks
- libraries
- APIs
- databases
- major dependencies

---

# Folder Structure

Explain:
- major folders
- responsibilities
- separation of concerns

Example:

src/
ui/
workers/
logs/
backups/

---

# Core Systems

Describe major systems such as:
- UI system
- worker/thread system
- logging system
- settings system
- API integrations
- backup system

---

# Architecture Rules

Document important architectural decisions.

Examples:
- UI logic must remain separated from processing logic
- workers handle long-running operations
- backups required before destructive operations
- settings stored through QSettings
- secrets stored through keychain/keyring

---

# Important Dependencies

Document critical dependency relationships.

Examples:
- image_processor.py depends on Pillow
- gemini_client.py requires API key manager
- workers emit Qt signals to main UI

---

# Performance Considerations

Document:
- expensive operations
- threading requirements
- caching systems
- token optimization strategies

---

# Dangerous Areas

Document:
- fragile workflows
- high-risk systems
- known architectural risks
- areas prone to regressions

---

# Future Expansion Notes

Document:
- planned systems
- future scalability ideas
- possible refactors
- upcoming integrations
