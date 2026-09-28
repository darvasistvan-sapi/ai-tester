# AI Tester

A simple Python client for a language model served with vLLM on RunPod. You can send it a text prompt and optionally attach an image (e.g. a screenshot).

The client uses vLLM's OpenAI-compatible Chat Completions API (`/v1/chat/completions`) and sends images as base64-encoded `image_url` content.

## Requirements

- Python 3.10 or newer
- The `openai` package
- A running vLLM server on RunPod (see [Running the model on RunPod](#running-the-model-on-runpod))

## Setup

1. Install the dependency:

   ```bash
   pip install openai
   ```

2. Copy the template and fill in your own values:

   ```bash
   cp Environment.example.py Environment.py
   ```

   ```python
   BASE_URL = "https://<POD_ID>-8000.proxy.runpod.net/v1"
   API_KEY = "<the server's --api-key value>"
   MODEL_NAME = "Qwen/Qwen3.6-35B-A3B"
   ```

   - `BASE_URL`: the pod's proxy URL, ending in `/v1`.
   - `API_KEY`: the same value you passed to the server with the `--api-key` flag.
   - `MODEL_NAME`: exactly the model name the server was started with via the `--model` flag.

> `Environment.py` contains secrets, so do not commit it. It is already listed in `.gitignore`.

## Running

```bash
python Main.py
```

`Main.py` sends a simple text prompt to the model and prints the answer.

## Usage

### Text request

```python
answer = client.send("What is 2 + 2?")
print(answer)
```

### Request with an image (screenshot analysis)

If you pass the `image_path` parameter, the image is sent along with the prompt:

```python
answer = client.send(
    prompt="""
    Examine this game screenshot.

    Find the Settings button.

    Return only JSON:
    {
        "x": <integer>,
        "y": <integer>
    }
    """,
    image_path="screenshot.png",
)

print(answer)
```

Image requests require a model that accepts image input (a vision / multimodal model).

## Running the model on RunPod

On the pod, the vLLM server is started with these arguments:

```bash
--model Qwen/Qwen3.6-35B-A3B \
--port 8000 \
--enforce-eager \
--max-model-len 36864 \
--max-num-seqs 64 \
--reasoning-parser qwen3 \
--api-key ai-test
```

| Flag | Meaning |
| --- | --- |
| `--model` | The model to load (Hugging Face ID); this goes into `MODEL_NAME` |
| `--port` | The server port; it also appears in the proxy URL (`-8000.proxy.runpod.net`) |
| `--enforce-eager` | Runs without CUDA graphs: less GPU memory, at the cost of slower generation |
| `--max-model-len` | Maximum context length in tokens (prompt + answer) |
| `--max-num-seqs` | Maximum number of requests processed at the same time |
| `--reasoning-parser qwen3` | Separates the model's "thinking" part from the answer |
| `--api-key` | The key required for requests; this goes into `API_KEY` |

Because the model has a thinking phase, the thinking also counts toward the `max_tokens` budget. If the answer is empty or cut off, increase `max_tokens`.
