"""Ollama (local) LLM provider."""
import json

import requests
from typing import Optional

from .provider import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "llama3"
    ):
        self._base_url = base_url.rstrip("/")
        self._model = model

    def complete(
        self,
        prompt,
        system_prompt="",
        max_tokens=4096,
        temperature=0.2,
        stop_sequences=None,
    ):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if stop_sequences:
            payload["options"]["stop"] = stop_sequences

        resp = requests.post(
            f"{self._base_url}/api/chat", json=payload, timeout=120
        )
        resp.raise_for_status()
        data = resp.json()

        return LLMResponse(
            content=data.get("message", {}).get("content", ""),
            model=self._model,
            usage={
                "input_tokens": data.get("prompt_eval_count", 0),
                "output_tokens": data.get("eval_count", 0),
            },
            raw=data,
        )

    def complete_structured(
        self, prompt, schema, system_prompt="", max_tokens=4096
    ):
        """Use JSON mode with schema in prompt, then validate."""
        schema_instruction = (
            f"\n\nYou MUST respond with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```\n"
            f"Respond ONLY with the JSON, no other text."
        )

        full_system = (
            (system_prompt + schema_instruction)
            if system_prompt
            else schema_instruction.strip()
        )

        response = self.complete(
            prompt,
            system_prompt=full_system,
            max_tokens=max_tokens,
            temperature=0.1,
        )

        # Extract JSON from response
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(
                lines[1:-1]
                if lines[-1].strip() == "```"
                else lines[1:]
            )

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Ollama returned invalid JSON: {e}\nContent: {content[:200]}"
            )

    def name(self):
        return f"ollama:{self._model}"
