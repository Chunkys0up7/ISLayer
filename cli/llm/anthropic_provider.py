"""Anthropic Claude LLM provider."""
import json
from typing import Optional

from .provider import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"
    ):
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install: pip install anthropic"
            )

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def complete(
        self,
        prompt,
        system_prompt="",
        max_tokens=4096,
        temperature=0.2,
        stop_sequences=None,
    ):
        messages = [{"role": "user", "content": prompt}]
        kwargs = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if stop_sequences:
            kwargs["stop_sequences"] = stop_sequences

        response = self._client.messages.create(**kwargs)
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            raw=response,
        )

    def complete_structured(
        self, prompt, schema, system_prompt="", max_tokens=4096
    ):
        """Use tool-use to get structured output."""
        tool = {
            "name": "structured_output",
            "description": "Return structured data matching the schema",
            "input_schema": schema,
        }
        messages = [
            {
                "role": "user",
                "content": prompt
                + "\n\nUse the structured_output tool to return your response.",
            }
        ]
        kwargs = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": 0.1,  # Lower temp for structured output
            "messages": messages,
            "tools": [tool],
            "tool_choice": {"type": "tool", "name": "structured_output"},
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)

        # Extract tool use input
        for block in response.content:
            if block.type == "tool_use":
                return block.input

        raise ValueError("No structured output returned from Anthropic API")

    def name(self):
        return f"anthropic:{self._model}"
