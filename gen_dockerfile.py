"""Ask the local model to write a Dockerfile for a project folder."""

import json
import re
import sys
from pathlib import Path

import requests  # only needed to catch the "Ollama is not running" error

from context import scan  # our scanner from the last step
from llm import ask  # our Ollama helper from day 2

# generated Dockerfiles go here, one folder per project (it's in .gitignore)
OUTPUT_DIR = Path("generated")

# three backticks, built this way so the file is easy to paste anywhere
FENCE = "`" * 3

# prompt v1. Every rule is something we learned from the reference files,
# and we can change them later and measure whether the results improve
PROMPT_TEMPLATE = """You are a DevOps engineer. Write a production-quality Dockerfile for the project described below.

Project facts (detected automatically):
{facts}

Rules:
- Use a small, official base image with an exact version tag. Never use the latest tag.
- Copy the dependency file first and install dependencies before copying the rest of the code, so Docker can cache that layer.
- Run the application as a non-root user.
- Use EXPOSE with the port from the facts.
- Use the exec form for CMD.
- Use a multi-stage build only if the language needs a compile step.
- Output ONLY the contents of the Dockerfile. No explanations and no markdown fences.
"""


def extract_dockerfile(answer):
    """Models don't always obey 'only the Dockerfile', so clean up the answer."""
    # if the answer is wrapped in a fenced block, take what's inside the first one
    pattern = re.escape(FENCE) + r"[a-zA-Z]*\s*\n(.*?)" + re.escape(FENCE)
    match = re.search(pattern, answer, re.DOTALL)
    text = match.group(1) if match else answer

    # drop chatter like "Here is your Dockerfile:" before the first FROM or ARG line
    lines = text.strip().splitlines()
    for index, line in enumerate(lines):
        if line.upper().startswith(("FROM ", "ARG ")):
            lines = lines[index:]
            break
    return "\n".join(lines).strip() + "\n"


def generate(project_dir):
    """Scan the project, ask the model, return the cleaned Dockerfile."""
    facts = scan(project_dir)
    if facts["language"] == "unknown":
        raise ValueError(f"Could not detect the language of {project_dir}")
    # the facts go into the prompt as readable JSON
    prompt = PROMPT_TEMPLATE.format(facts=json.dumps(facts, indent=2))
    answer, data = ask(prompt)
    return extract_dockerfile(answer), facts, data


def save(dockerfile, project_dir):
    """Write the Dockerfile to generated/<project name>/Dockerfile."""
    folder = OUTPUT_DIR / Path(project_dir).resolve().name
    folder.mkdir(parents=True, exist_ok=True)  # create it, no error if it exists
    path = folder / "Dockerfile"
    path.write_text(dockerfile)
    return path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python gen_dockerfile.py <project-folder>")
        sys.exit(1)
    project = sys.argv[1]
    try:
        dockerfile, facts, data = generate(project)
    except ValueError as error:  # bad folder or unknown language
        print(error)
        sys.exit(2)
    except requests.exceptions.RequestException:  # Ollama didn't answer
        print("Could not reach Ollama. Check: systemctl is-active ollama")
        sys.exit(4)
    path = save(dockerfile, project)
    seconds = data["total_duration"] / 1e9  # Ollama reports nanoseconds
    print(f"Detected: {facts['language']}, port {facts.get('port')}")
    print(f"Model answered in {seconds:.0f}s, saved to {path}\n")
    print(dockerfile)