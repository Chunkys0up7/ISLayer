"""Tests for the LLM client abstractions."""
from __future__ import annotations

import pytest

from triple_flow_sim.components.c05_llm import (
    FakeLLM,
    LLMNotConfigured,
    LLMRequest,
    build_default_client,
)


def test_fake_llm_deterministic():
    llm = FakeLLM(seed=42)
    req = LLMRequest(model="fake", prompt="hello", seed=42)
    a = llm.complete(req)
    b = llm.complete(req)
    assert a.raw_text == b.raw_text
    assert a.parsed == b.parsed


def test_fake_llm_out_command():
    llm = FakeLLM()
    req = LLMRequest(
        model="fake", prompt='some text\n#FAKE_OUT:{"status": "approved"}'
    )
    resp = llm.complete(req)
    assert resp.parsed == {"status": "approved"}


def test_fake_llm_refuse_command():
    llm = FakeLLM()
    req = LLMRequest(model="fake", prompt="#FAKE_REFUSE:policy")
    resp = llm.complete(req)
    assert resp.finish_reason == "refused"
    assert resp.refusals and resp.refusals[0]["reason"] == "policy"


def test_fake_llm_stuck_command():
    llm = FakeLLM()
    req = LLMRequest(model="fake", prompt="#FAKE_STUCK")
    resp = llm.complete(req)
    assert resp.finish_reason == "stuck"


def test_build_default_client_fallback_to_fake(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    llm = build_default_client(driver="auto")
    assert isinstance(llm, FakeLLM)


def test_build_default_client_force_anthropic_without_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMNotConfigured):
        build_default_client(driver="anthropic")
