# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-29

### Added
- Core autonomous NPC kernel: world state, STRIPS/HTN goal graph, BDI loop,
  bounded multi-agent negotiation, and event-driven replanning.
- CLI camp demo (`python -m native_life` or `python -m examples.camp_demo`)
  reproducing the Monta NPC camp scenario: two agents negotiate, gather,
  build, and recover from injury / resource-blockage events.
- Optional LLM adapter (default: no-op stub) for open-ended dialogue.
- Industry adoption playbook (`docs/solution.md`, Chinese).
- Academic write-up (`docs/paper.md`, English).
- v0.1 release notes / launch blog post (`RELEASE_NOTES_v0.1.md`).
- MIT license, CITATION.cff, pytest smoke tests.

### Notes
- This release is a reference implementation. It does not include the
  closed-source Unity / Unreal binaries (which contain licensed art).
- The architecture produces life-like *behavior*; it does not claim
  consciousness. See paper §8.
