from pathlib import Path

IGNORE = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".idea",
    ".vscode",
}

def tree(path: Path, prefix=""):
    items = sorted(
        [p for p in path.iterdir() if p.name not in IGNORE],
        key=lambda x: (x.is_file(), x.name.lower())
    )

    for i, item in enumerate(items):
        last = i == len(items) - 1
        print(prefix + ("└── " if last else "├── ") + item.name)
        if item.is_dir():
            tree(item, prefix + ("    " if last else "│   "))

tree(Path("."))