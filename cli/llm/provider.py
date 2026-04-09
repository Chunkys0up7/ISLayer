"""Abstract LLM provider interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict  # {"input_tokens": N, "output_tokens": N}
    raw: Any = None


class LLMProvider(ABC):
    @abstractmethod
    def complete(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.2,
        stop_sequences: Optional[list[str]] = None,
    ) -> LLMResponse:
        """Free-form text completion."""
        ...

    @abstractmethod
    def complete_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        max_tokens: int = 4096,
    ) -> dict:
        """Structured output completion. Returns a dict validated against the JSON Schema."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Provider name for logging/audit."""
        ...


def get_provider(config) -> LLMProvider:
    """Factory: create provider from config.
    config is a Config object with llm_provider, llm_model, llm_api_key properties.
    """
    provider_name = config.llm_provider
    if provider_name == "anthropic":
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider(api_key=config.llm_api_key, model=config.llm_model)
    elif provider_name == "openai":
        from .openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=config.llm_api_key, model=config.llm_model)
    elif provider_name == "ollama":
        from .ollama_provider import OllamaProvider
        import os

        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaProvider(base_url=base_url, model=config.llm_model)
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider_name}. Supported: anthropic, openai, ollama"
        )
