from pathlib import Path
import shutil

VAULT = Path.cwd()

# 1. Replace strange separators with normal Markdown separators
for file in VAULT.rglob("*.md"):
    text = file.read_text(encoding="utf-8", errors="ignore")
    original = text

    text = text.replace("⸻", "---")

    # 2. Fix unclosed markdown code fences
    if text.count("```") % 2 != 0:
        text = text.rstrip() + "\n```\n"

    if text != original:
        backup = file.with_suffix(file.suffix + ".bak")
        shutil.copy2(file, backup)
        file.write_text(text, encoding="utf-8")
        print(f"Fixed: {file.relative_to(VAULT)}")

# 3. Move weird Obsidian test files to Inbox
inbox = VAULT / "00-Inbox"
inbox.mkdir(exist_ok=True)

for pattern in ["Untitled*.base", "Untitled*.canvas"]:
    for file in VAULT.glob(pattern):
        target = inbox / file.name
        shutil.move(str(file), str(target))
        print(f"Moved to Inbox: {file.name}")

print("\nDone. Backup .bak files were created before changes.")
