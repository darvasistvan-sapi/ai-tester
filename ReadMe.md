# AI Tester

A simple Python client for a language model served with vLLM on RunPod. You can send it a text prompt and optionally attach an image (e.g. a screenshot).

The `MCP/` folder contains helpers for controlling a single target window: taking screenshots of it and clicking, scrolling, moving and dragging the mouse inside it.

The client uses vLLM's OpenAI-compatible Chat Completions API (`/v1/chat/completions`) and sends images as base64-encoded `image_url` content.

## Requirements

- Python 3.10 or newer
- The `openai` package
- The `pyautogui` package (for the window and mouse control in `MCP/`; it also installs `pygetwindow` and `Pillow`)
- Windows (the window handling in `MCP/` uses the Windows API)
- A running vLLM server on RunPod (see [Running the model on RunPod](#running-the-model-on-runpod))

## Setup

1. Install the dependencies:

   ```bash
   pip install openai pyautogui
   ```

2. Copy the template and fill in your own values:

   ```bash
   cp Environment.example.py Environment.py
   ```

   ```python
   BASE_URL = "https://<POD_ID>-8000.proxy.runpod.net/v1"
   API_KEY = "<the server's --api-key value>"
   MODEL_NAME = "Qwen/Qwen3.6-35B-A3B"
   WINDOW_TITLE = "<title of the window to control>"
   ```

   - `BASE_URL`: the pod's proxy URL, ending in `/v1`.
   - `API_KEY`: the same value you passed to the server with the `--api-key` flag.
   - `MODEL_NAME`: exactly the model name the server was started with via the `--model` flag.
   - `WINDOW_TITLE`: the title of the window to control. A part of the title is enough (e.g. `"File Explorer"`); if several windows match, the first one is used.

> `Environment.py` contains secrets, so do not commit it. It is already listed in `.gitignore`.

## Running

```bash
python Main.py
```

`Main.py` contains short examples of the client and the window and mouse helpers; comment in the ones you want to try.

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

## Window and mouse control

The classes in `MCP/` are static, so you call their methods directly on the class without creating an instance.

The target window is the one whose title contains `WINDOW_TITLE` from `Environment.py`. It is looked up on first use, and you can switch to another window at any time:

```python
from MCP.WindowController import WindowController

WindowController.selectWindow("Notepad")
```

Before every action the window is brought to the front (and restored if it is minimized), so the action always lands in the target window, even if another window was covering it.

### Coordinates

All coordinates are relative values between 0 and 1 inside the window's **client area**, which is the content of the window without the title bar and borders:

- `(0, 0)` is the client area's top-left corner,
- `(1, 1)` is its bottom-right corner,
- `(0.5, 0.5)` is its center.

`CoordinateConverter.convert(x, y)` turns them into absolute screen pixels, based on the client area's current position and size, so moving or resizing the window does not break anything. Values outside 0..1 raise a `ValueError`.

> Applications that draw their own title bar (e.g. VS Code, Chrome, File Explorer, many games) have the title bar inside the client area.

### Screenshots

```python
from MCP.WindowController import WindowController

image = WindowController.getScreenshot()            # returns a PIL image
WindowController.saveScreenshot("screenshot.png")   # saves it to a file
```

The screenshot covers exactly the client area, so a position the model finds on the image (as a fraction of the image width and height) can be passed straight to `MouseController`. Anything shown on top of the window at that moment (e.g. a notification) is captured too.

### Mouse actions

```python
from MCP.MouseController import MouseController

MouseController.click(0.5, 0.5)                          # left click
MouseController.click(0.5, 0.5, button="right")          # right click
MouseController.click(0.5, 0.5, clicks=2)                # double click
MouseController.scroll(0.5, 0.5, -5)                     # scroll at (x, y); positive = up, negative = down
MouseController.mouseMove(0.1, 0.9, duration=0.3)        # move the cursor
MouseController.dragAndDrop(0.2, 0.3, 0.7, 0.8)          # drag from (0.2, 0.3) and drop at (0.7, 0.8)
```

`dragAndDrop` presses the button at the start point, moves to the end point over `duration` seconds (default 0.5) and releases it there. The gradual move is needed because many applications ignore a drag where the cursor jumps instantly. The button is always released, even if an error happens during the move.

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
