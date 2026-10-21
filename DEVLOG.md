# Dev log

## Day 1 - 2026-10-15
- Launched an EC2 instance (m7i-flex.large, Ubuntu) in us-east-1 with SSH limited to my IP
- Installed Docker, Git and Python
- Installed Ollana abd download qwen2.5-coder:3b (about1.9gb), which fits the 8gb instance
- Lesson: a loaded model is memory. Used RAM grew by about 2.2 GiB, and the free column looked alarming while the available column showed plenty left
- Hardware check: ollama ps reported a GPU split, but nvidia-smi, lspci and Ollama's own log all say CPU-only. I trust the log, so results are CPU-only on 2 vCPUs.

## Day 2 - 2026-10-17
- Called ollama's /api/generate endpoint using curl command, then wrapped it in a small python function (llm.py)
- The first call is a bit slow because the model needs to load into the memory. A second call within about 5 minutes is faster.
- Added three sample apps (python/flask, node/Express, Go) with different ports and dependency files, so that the generator detects the real facts and does not guess

## Day 3 - 2026-10-18
- Wrote hand-made reference Dockerfiles for the Python, Node and Go sample apps (non-root user, cached dependency layer, multi-stage for Go)
- Built and ran all three, and each answered on its port, so any later failure is the model's fault and not the app's
- Image sizes (from docker images): fill in the three numbers here

## Day 4 - 2026-10-19
- Set up VS Code Remote - SSH, so I edit files on the instance in a normal editor
- Wrote context.py, which scans a project and reports language, version, entry point, port and traps like a missing npm lock file
- Wrote gen_dockerfile.py (prompt v1, answer cleanup), but have not run it yet. 

## Day 5 - 2026-10-20
- First end-to-end run on the python sample app: the model's Dockerfile built on attempt 1 and mathced my reference very closely.
- Ran the generated python dockerfile through hadolint(lint) and trivy (image vulnerabilities), plus simple grep checks for USER and latest tag
- Lesson: hadolint reads the dockerfile and flags the bad practice in it and trivy insepects the docker image for vulnerablitites.

## Day 6 - 2026-10-21
- Ran the generator on the Node sample app, which has no lock file on purpose. Attempt 1 failed because the model wrote COPY package.json package-lock.json
- Finding: the prompt contained has_lockfile false, and the 3B model still ignored it