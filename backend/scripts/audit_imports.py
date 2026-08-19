import os
import ast
import importlib.util
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # backend/scripts/ -> backend
CODE_ROOT = PROJECT_ROOT.parent / "backend"

def get_top_level_imports(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return []
    imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])
    return imports

all_imports = set()
for py_file in CODE_ROOT.rglob("*.py"):
    all_imports.update(get_top_level_imports(py_file))

# Filter out standard library modules (rough heuristic: try import, if succeeds and module file is in stdlib path, consider stdlib)
missing = []
for mod in sorted(all_imports):
    try:
        spec = importlib.util.find_spec(mod)
        if spec is None:
            raise ImportError
        # If spec.origin is None, treat as missing
        if spec.origin is None:
            raise ImportError
    except ImportError:
        missing.append(mod)

result = {
    "project_root": str(PROJECT_ROOT),
    "code_root": str(CODE_ROOT),
    "all_imports": sorted(all_imports),
    "missing_imports": missing,
}
print(json.dumps(result, indent=2))
