"""LLM client abstraction.

Spec reference: files/05-grounded-handoff-runner.md §LLM interface,
also files/07-context-isolation-harness.md §LLM interactions.

Drivers:
- ``FakeLLM``: deterministic, no network — the default for tests and CI.
- ``AnthropicLLM``: stub real driver; activates when ``ANTHROPIC_API_KEY``
  is set and the optional ``anthropic`` package is installed. Otherwise
  raises ``LLMNotConfigured``.
"""
from triple_flow_sim.components.c05_llm.client import (
    FakeLLM,
    LLMClient,
    LLMNotConfigured,
    LLMRequest,
    LLMResponse,
    build_default_client,
)

__all__ = [
    "FakeLLM",
    "LLMClient",
    "LLMNotConfigured",
    "LLMRequest",
    "LLMResponse",
    "build_default_client",
]
