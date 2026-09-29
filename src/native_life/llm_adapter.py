"""Optional LLM adapter.

The steady-state camp scenario makes ZERO LLM calls. The adapter exists only
for open-ended player dialogue, creative naming, and emotional affect. Swap
StubLLM for a real client (vLLM, OpenAI-compatible, etc.) when you need it.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    safety_passed: bool


class StubLLM:
    """Default adapter: deterministic, offline, no network."""

    name = "stub"

    def generate(self, prompt: str, *, safety_filter: bool = True) -> LLMResponse:
        # In a real deployment this would call a model. We deliberately echo a
        # safe placeholder so the rest of the system can be tested offline.
        return LLMResponse(text=f"[stub-llm] {prompt}", safety_passed=True)


# The singleton used by the agent loop. Replace in production:
#   from native_life.llm_adapter import llm; llm.adapter = RealOpenAI(...)
class _Adapter:
    def __init__(self) -> None:
        self.adapter = StubLLM()

    def generate(self, prompt: str) -> LLMResponse:
        resp = self.adapter.generate(prompt)
        if not resp.safety_passed:
            return LLMResponse(text="(I cannot talk about that.)", safety_passed=True)
        return resp


llm = _Adapter()
