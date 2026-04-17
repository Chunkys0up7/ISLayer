"""LLM client protocol + deterministic fake + Anthropic stub.

Spec reference: files/05-grounded-handoff-runner.md §LLM interface.

The ``FakeLLM`` is seed-driven and used by Phase 3 tests/CLI when no real API
key is configured — simulation proceeds deterministically. Real drivers plug
into the same ``LLMClient`` protocol.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol


class LLMNotConfigured(RuntimeError):
    """Raised when a real driver is requested but credentials/package missing."""


@dataclass
class LLMRequest:
    model: str
    prompt: str
    system: Optional[str] = None
    temperature: float = 0.0
    seed: int = 0
    max_tokens: int = 1024
    metadata: dict = field(default_factory=dict)


@dataclass
class LLMResponse:
    raw_text: str
    parsed: Optional[dict] = None  # populated by caller after parsing
    token_counts: dict = field(default_factory=lambda: {"input": 0, "output": 0})
    model: str = ""
    model_version: str = ""
    refusals: list[dict] = field(default_factory=list)
    finish_reason: str = "stop"


class LLMClient(Protocol):
    """Minimum interface every driver implements."""

    def complete(self, req: LLMRequest) -> LLMResponse: ...


# ---------------------------------------------------------------------------
# FakeLLM
# ---------------------------------------------------------------------------
def _deterministic_digest(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class FakeLLM:
    """Deterministic, offline LLM driver.

    Behavior:
    - Echoes back a JSON-shaped response that the grounded runner can parse.
    - Output depends only on ``(model, seed, prompt)`` — two identical
      requests produce identical responses.
    - Understands a handful of pseudo-commands embedded in the prompt to
      simulate specific outcomes for tests:
        * ``#FAKE_OUT:{"key":"value"}`` → exact parsed body
        * ``#FAKE_REFUSE:<reason>`` → refusal
        * ``#FAKE_STUCK`` → finish_reason="stuck"
    """

    model_version = "fake-1.0.0"

    def __init__(self, seed: int = 0, model: str = "fake"):
        self.seed = seed
        self.model = model

    def complete(self, req: LLMRequest) -> LLMResponse:
        text = req.prompt or ""
        # Command hooks for tests --------------------------------------
        if "#FAKE_REFUSE:" in text:
            reason = text.split("#FAKE_REFUSE:", 1)[1].splitlines()[0].strip()
            return LLMResponse(
                raw_text=json.dumps({"error": "refused", "reason": reason}),
                refusals=[{"reason": reason, "category": "policy"}],
                model=self.model,
                model_version=self.model_version,
                finish_reason="refused",
            )
        if "#FAKE_STUCK" in text:
            return LLMResponse(
                raw_text=json.dumps({"status": "stuck"}),
                model=self.model,
                model_version=self.model_version,
                finish_reason="stuck",
            )
        if "#FAKE_OUT:" in text:
            raw = text.split("#FAKE_OUT:", 1)[1].splitlines()[0].strip()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"value": raw}
            return LLMResponse(
                raw_text=raw,
                parsed=parsed,
                model=self.model,
                model_version=self.model_version,
                token_counts={"input": len(text), "output": len(raw)},
            )

        # Default path: deterministic echo keyed by prompt digest.
        digest = _deterministic_digest(f"{req.model}|{req.seed}|{text}")
        body = {
            "echo": f"fake-{digest}",
            "prompt_length": len(text),
            "seed": req.seed,
        }
        raw = json.dumps(body, sort_keys=True)
        return LLMResponse(
            raw_text=raw,
            parsed=body,
            model=self.model,
            model_version=self.model_version,
            token_counts={"input": len(text), "output": len(raw)},
        )


# ---------------------------------------------------------------------------
# AnthropicLLM (stub — real SDK plug-in)
# ---------------------------------------------------------------------------
class AnthropicLLM:
    """Anthropic driver stub.

    Activates only when both (a) ``ANTHROPIC_API_KEY`` is set and (b) the
    ``anthropic`` Python package is importable. Intentionally not a
    hard dependency; Phase 3 tests use ``FakeLLM``.
    """

    def __init__(self, model: str = "claude-3-5-sonnet-latest"):
        self.model = model
        try:
            import anthropic  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dep
            raise LLMNotConfigured(
                "anthropic package not installed; "
                "use FakeLLM or install `anthropic`"
            ) from exc
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMNotConfigured(
                "ANTHROPIC_API_KEY not set; "
                "use FakeLLM or export the key"
            )
        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(self, req: LLMRequest) -> LLMResponse:  # pragma: no cover
        msg = self._client.messages.create(
            model=req.model or self.model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            system=req.system or "",
            messages=[{"role": "user", "content": req.prompt}],
        )
        # ``msg.content`` is a list of content blocks; stitch text blocks.
        text_parts: list[str] = []
        for block in getattr(msg, "content", []):
            t = getattr(block, "text", None)
            if t is not None:
                text_parts.append(t)
        raw_text = "".join(text_parts)
        return LLMResponse(
            raw_text=raw_text,
            model=msg.model,
            model_version=msg.model,
            token_counts={
                "input": getattr(msg.usage, "input_tokens", 0),
                "output": getattr(msg.usage, "output_tokens", 0),
            },
            finish_reason=getattr(msg, "stop_reason", "stop") or "stop",
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
def build_default_client(
    driver: str = "auto",
    seed: int = 0,
    model: Optional[str] = None,
) -> LLMClient:
    """Pick a driver.

    driver="fake"      → always FakeLLM (tests, CI)
    driver="anthropic" → force AnthropicLLM (raises if not configured)
    driver="auto"      → AnthropicLLM if available, else FakeLLM
    """
    if driver == "fake":
        return FakeLLM(seed=seed, model=model or "fake")
    if driver == "anthropic":
        return AnthropicLLM(model=model or "claude-3-5-sonnet-latest")
    if driver == "auto":
        try:
            return AnthropicLLM(model=model or "claude-3-5-sonnet-latest")
        except LLMNotConfigured:
            return FakeLLM(seed=seed, model=model or "fake")
    raise ValueError(f"Unknown LLM driver: {driver!r}")
