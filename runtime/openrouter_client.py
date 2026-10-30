import os
import requests
from dotenv import load_dotenv

load_dotenv()


class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment variables."
            )

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 16000,
    ) -> str:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Studio",
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        result = response.json()

        return result["choices"][0]["message"]["content"]