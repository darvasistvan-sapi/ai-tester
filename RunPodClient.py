import base64
from pathlib import Path

from openai import OpenAI
from Environment import BASE_URL, API_KEY, MODEL_NAME

class RunPodClient:
    def __init__(
        self,
        timeout: float = 120.0,
        temperature: float = 0.0,
        max_tokens: int = 500,
    ):
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
            timeout=timeout,
        )

    def send(
        self,
        prompt: str,
        image_path: str | None = None,
    ) -> str:

        if image_path is None:
            content = prompt
        else:
            image_base64 = self._encode_image(image_path)
            content = [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    },
                },
            ]

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content

    @staticmethod
    def _encode_image(image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(
                image_file.read()
            ).decode("utf-8")
