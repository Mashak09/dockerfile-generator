# Dev log

## Day 1 - 2026-10-15
- Launched an EC2 instance (m7i-flex.large, Ubuntu) in us-east-1 with SSH limited to my IP
- Installed Docker, Git and Python
- Installed Ollana abd download qwen2.5-coder:3b (about1.9gb), which fits the 8gb instance
- Lesson: a loaded model is memory. Used RAM grew by about 2.2 GiB, and the free column looked alarming while the available column showed plenty left
- Hardware check: ollama ps reported a GPU split, but nvidia-smi, lspci and Ollama's own log all say CPU-only. I trust the log, so results are CPU-only on 2 vCPUs.
- Called ollama's /api/generate endpoint using curl command, then wrapped it in a small python function (llm.py)
- The first call is a bit slow because the model needs to load into the memory. A second call within about 5 minutes is faster.
