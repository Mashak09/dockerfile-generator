import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5-coder:3b"


def ask(prompt, model=DEFAULT_MODEL, timeout=300):
    """Send one prompt to the local Ollama server.

    Returns the answer text and the full response data (timings, token counts).
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data["response"], data


if __name__ == "__main__":
    text, data = ask("Write a one-line Python hello world")
    print(text)
    seconds = data["total_duration"] / 1e9
    print(f"[{data['eval_count']} tokens, {seconds:.1f}s total]")
