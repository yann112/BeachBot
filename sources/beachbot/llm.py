import os
from dotenv import load_dotenv
import requests
import logging

load_dotenv()

class OpenRouterClient:
    def __init__(
            self,
            logger = None,
            api_key=None,
            model="mistralai/mistral-small-3.1-24b-instruct",
            max_tokens=1200
                ):
        self.logger = logger or logging.getLogger(__file__)
        self.api_key = api_key or os.environ.get("OPEN_ROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set it in the environment or pass it explicitly.")
        self.model = model
        self.max_tokens = max_tokens
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def __call__(self, prompt):
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"Error parsing response: {e}, Response text: {response.text}")
            return None