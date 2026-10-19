"""Scan a project folder and report the facts a Dockerfile depends on."""

import json  # to read package.json and to print the result
import re  # regular expressions, for finding ports and versions in text
import sys  # gives us the command line arguments
from pathlib import Path  # easier than gluing path strings together

# folders full of other people's code. No point scanning them,
# and they could contain ports that have nothing to do with our app
SKIP_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".git", "vendor"}

# only these file types can contain the port
SOURCE_SUFFIXES = {".py", ".js", ".go"}

# ignore huge files (about 200 KB), they are never the app's main file
MAX_FILE_BYTES = 200_000

# usual names for a Python app's main file, tried in this order
PYTHON_ENTRY_CANDIDATES = ["app.py", "main.py", "server.py", "run.py"]

# three ways a port shows up in code. The brackets capture the digits
PORT_PATTERNS = [
    re.compile(r"\bport\s*=\s*(\d{2,5})", re.IGNORECASE),  # port=5000, PORT = 3000
    re.compile(r"\.listen\(\s*(\d{2,5})"),  # app.listen(3000)
    re.compile(r'ListenAndServe\(\s*"[^"]*:(\d{2,5})"'),  # Go: ListenAndServe(":8080", nil)
]


def read_text(path):
    """Read a file as text, or return None if we can't or shouldn't."""
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None  # too big, skip it
        # errors="ignore" skips bytes that aren't valid text instead of crashing
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None  # missing file or no permission


def source_files(root):
    """Hand back the source files under root, one at a time."""
    # sorted, so we get the same order on every run
    for path in sorted(root.rglob("*")):
        # skip anything inside a folder from the skip list
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file() and path.suffix in SOURCE_SUFFIXES:
            yield path


def find_port(root):
    """Return the first port number we find in the code, or None."""
    for path in source_files(root):
        text = read_text(path)
        if text is None:
            continue
        for pattern in PORT_PATTERNS:
            match = pattern.search(text)
            if match:
                return int(match.group(1))  # group(1) is the digits in brackets
    return None  # nothing found, the caller has to cope with that


def scan_python(root):
    # the version file is optional, so it might not exist
    version_file = read_text(root / ".python-version")
    # first candidate file that actually exists, otherwise None
    entry = next(
        (name for name in PYTHON_ENTRY_CANDIDATES if (root / name).exists()), None
    )
    return {
        "language": "python",
        "dependency_file": "requirements.txt",
        "version": version_file.strip() if version_file else None,  # strip the newline
        "entry_point": entry,
    }


def scan_node(root):
    try:
        package = json.loads(read_text(root / "package.json") or "{}")
    except json.JSONDecodeError:
        package = {}  # broken package.json, carry on with what we know
    scripts = package.get("scripts", {})
    return {
        "language": "node",
        "dependency_file": "package.json",
        "version": package.get("engines", {}).get("node"),
        # prefer what "npm start" runs, fall back to the main field
        "entry_point": scripts.get("start") or package.get("main"),
        # important: without a lock file "npm ci" fails, so the model must know
        "has_lockfile": (root / "package-lock.json").exists(),
    }


def scan_go(root):
    text = read_text(root / "go.mod") or ""
    # find the line that starts with "go" and grab the version after it
    match = re.search(r"^go\s+(\S+)", text, re.MULTILINE)
    return {
        "language": "go",
        "dependency_file": "go.mod",
        "version": match.group(1) if match else None,
        "entry_point": "main.go" if (root / "main.go").exists() else None,
    }


# marker file -> function that knows how to read that kind of project.
# a new language later just means one more line here
DETECTORS = [
    ("requirements.txt", scan_python),
    ("package.json", scan_node),
    ("go.mod", scan_go),
]


def scan(project_dir):
    """Return a dictionary of facts about the project in project_dir."""
    root = Path(project_dir).resolve()  # full path, no matter how it was typed
    if not root.is_dir():
        raise ValueError(f"Not a folder: {project_dir}")
    # names of the files directly in the folder, extra context for the model
    files = sorted(p.name for p in root.iterdir() if p.is_file())
    # first marker file we find decides the language
    for marker, detector in DETECTORS:
        if (root / marker).exists():
            facts = detector(root)
            facts["port"] = find_port(root)
            facts["files"] = files
            return facts
    return {"language": "unknown", "files": files}


# this part only runs when we start the file directly: python context.py <folder>
if __name__ == "__main__":
    if len(sys.argv) != 2:  # argv[0] is the script name, so we want exactly 2
        print("Usage: python context.py <project-folder>")
        sys.exit(1)
    try:
        print(json.dumps(scan(sys.argv[1]), indent=2))  # indent=2 for readable JSON
    except ValueError as error:
        print(error)
        sys.exit(2)  # non-zero exit code means "something went wrong"