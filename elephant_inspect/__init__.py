"""Inspect AI task wrappers for the ejentum/benchmarks suite.

Currently exposes one task:

- ``elephant_sycophancy``: a sycophancy-resistance eval built on the 40
  ELEPHANT scenarios that live alongside this package at
  ``../elephant/scenarios.json``. Each scenario is graded by a separate
  model against the three ELEPHANT dimensions (validation, indirectness,
  framing) plus an overall sycophancy-resistance score.
"""

from .task import elephant_sycophancy

__all__ = ["elephant_sycophancy"]
