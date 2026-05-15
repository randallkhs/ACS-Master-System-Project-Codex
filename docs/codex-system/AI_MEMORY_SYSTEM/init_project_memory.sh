#!/bin/bash

PROJECT_DIR="$1"

if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: ./init_project_memory.sh /path/to/project"
  exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Project folder does not exist: $PROJECT_DIR"
  exit 1
fi

cp project-templates/ARCHITECTURE_TEMPLATE.md "$PROJECT_DIR/ARCHITECTURE.md"
cp project-templates/PROJECT_STATE_TEMPLATE.md "$PROJECT_DIR/PROJECT_STATE.md"
cp project-templates/AI_NOTES_TEMPLATE.md "$PROJECT_DIR/AI_NOTES.md"
cp project-templates/KNOWN_ISSUES_TEMPLATE.md "$PROJECT_DIR/KNOWN_ISSUES.md"
cp project-templates/CHANGELOG_TEMPLATE.md "$PROJECT_DIR/CHANGELOG.md"

echo "Project memory files created in: $PROJECT_DIR"
