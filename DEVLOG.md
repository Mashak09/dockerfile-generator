# Dev log

## Day 1 - 2026-10-15
- Launched an EC2 instance (m7i-flex.large, Ubuntu) in us-east-1 with SSH limited to my IP
- Installed Docker, Git and Python
- Installed Ollana abd download qwen2.5-coder:3b (about1.9gb), which fits the 8gb instance
- Lesson: a loaded model is memory. Used RAM grew by about 2.2 GiB, and the free column looked alarming while the available column showed plenty left
- Hardware check: ollama ps reported a GPU split, but nvidia-smi, lspci and Ollama's own log all say CPU-only. I trust the log, so results are CPU-only on 2 vCPUs.
- Called ollama's /api/generate endpoint using curl command, then wrapped it in a small python function (llm.py)
- The first call is a bit slow because the model needs to load into the memory. A second call within about 5 minutes is faster.
- Added three sample apps (python/flask, node/Express, Go) with different ports and dependency files, so that the generator detects the real facts and does not guess
- Wrote hand-made reference Dockerfiles for the Python, Node and Go sample apps (non-root user, cached dependency layer, multi-stage for Go)
- Built and ran all three, and each answered on its port, so any later failure is the model's fault and not the app's
- Image sizes (from docker images): fill in the three numbers here
- Set up VS Code Remote - SSH, so I edit files on the instance in a normal editor
- Wrote context.py, which scans a project and reports language, version, entry point, port and traps like a missing npm lock file
- Wrote gen_dockerfile.py (prompt v1, answer cleanup), but have not run it yet. That is the first job tomorrow
