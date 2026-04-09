"""OpenAI LLM provider."""
import json
from typing import Optional

from .provider import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package required. Install: pip install openai"
            )

        self._client = openai.OpenAI(api_key=api_key)
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

        kwargs = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if stop_sequences:
            kwargs["stop"] = stop_sequences

        response = self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            },
            raw=response,
        )

    def complete_structured(
        self, prompt, schema, system_prompt="", max_tokens=4096
    ):
        """Use json_schema response format for structured output."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=0.1,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "structured_output",
                    "schema": schema,
                    "strict": True,
                },
            },
        )
        return json.loads(response.choices[0].message.content)

    def name(self):
        return f"openai:{self._model}"
