#build the generated dockerfile; if the build fails send the error back

import json # turns the facts dictiopnary into json text  to make it more readable
import subprocess # lets python runs other orogrtams eg: docker
import sys # gives us the typed command line words and sys.exit()
from pathlib import Path # a clean way to work with forlder and file paths

from context import scan # reads the projects and returns facts
from gen_dockerfile import PROMPT_TEMPLATE, extract_dockerfile, save # reuse code we already wrote
from llm import ask # our helper from llm.py that sends prompt to ollama

# the user must type exactly one thing after the script name: the project folder
if len(sys.argv) != 2:  # sys.argv is the list of typed words: [script name, folder]
    sys.exit("Usage: python gen_and_build.py <project-folder>")  # explain the usage and stop
project = Path(sys.argv[1]).resolve()  # turn the typed folder into a full path

facts = scan(project)  # run the scanner: language, version, port and so on
if facts["language"] == "unknown":  # the scanner did not recognise this project
    sys.exit("Could not detect the language of this project")  # stop instead of guessing

task = PROMPT_TEMPLATE.format(facts=json.dumps(facts, indent=2))  # fill the prompt with the facts
prompt = task  # the first attempt uses the plain task
worked = False  # nothing has built successfully yet

for attempt in range(1, 4):  # attempt is 1, then 2, then 3: at most three tries
    answer, _ = ask(prompt)  # send the prompt to the model, and ignore the extra data with _
    dockerfile = extract_dockerfile(answer)  # remove code fences and chatter from the answer
    path = save(dockerfile, project)  # write it to generated/<project>/Dockerfile

    # the docker build command as a list: use this Dockerfile, name the image gen-<project>, build in the project folder
    command = ["docker", "build", "-f", str(path), "-t", "gen-" + project.name, str(project)]
    result = subprocess.run(command, capture_output=True, text=True)  # run it, collect the output as text
    worked = result.returncode == 0  # return code 0 means the build worked

    print(f"Attempt {attempt}: {'build OK' if worked else 'build FAILED'}")  # report how this try went
    if worked:  # the build succeeded
        break  # stop retrying and leave the loop

    # join the normal output and the errors, keep only the last 25 lines (the error is at the end)
    log = "\n".join((result.stdout + result.stderr).splitlines()[-25:])
    print(log + "\n")  # show the error so you can read it too
    # new prompt: the original task plus the failed Dockerfile and its error, because the model has no memory
    prompt = task + f"\nYour previous Dockerfile failed to build. Fix it.\n\nDockerfile:\n{dockerfile}\n\nBuild output:\n{log}\n"

if not worked:  # the loop ended and no attempt built
    sys.exit(f"No working Dockerfile after 3 attempts. See {path}")  # stop, say where the last file is
print(f"Done. Final Dockerfile: {path}")  # success message with the file locatio>n