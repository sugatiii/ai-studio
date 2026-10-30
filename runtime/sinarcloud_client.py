import os
import requests
from dotenv import load_dotenv

load_dotenv()


class SinarCloudClient:
    def __init__(self):
        self.api_key = os.getenv("SINARCLOUD_API_KEY")

        if not self.api_key:
            raise ValueError(
                "SINARCLOUD_API_KEY not found in environment variables."
            )

        self.base_url = "https://ai.sinarcloud.com/v1/chat/completions"

    def chat(
        self,
        model: str,
        prompt: str,
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
            ]
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