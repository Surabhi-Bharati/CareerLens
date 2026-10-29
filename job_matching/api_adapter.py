"""JSON-safe integration adapter for CareerLens job matching."""

import math
from collections.abc import Mapping
from typing import Any

from .matching import evaluate_candidate


def _to_json_safe(value: Any) -> Any:
    """Convert supported Python values to standard JSON-compatible values."""
    if isinstance(value, Mapping):
        return {
            str(key): _to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (set, frozenset)):
        return sorted(
            (_to_json_safe(item) for item in value),
            key=str,
        )

    if isinstance(value, (list, tuple)):
        return [_to_json_safe(item) for item in value]

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("API output cannot contain NaN or infinity")
        return value

    if value is None or isinstance(value, (str, int, bool)):
        return value

    raise TypeError(
        f"Unsupported result value for JSON conversion: "
        f"{type(value).__name__}"
    )


def evaluate_candidate_for_api(
    candidate_skills,
    resume_text: str,
    job_description: str,
) -> dict:
    """Evaluate a candidate and return a JSON-safe dictionary."""
    result = evaluate_candidate(
        candidate_skills=candidate_skills,
        resume_text=resume_text,
        job_description=job_description,
        verbose=False,
    )

    return _to_json_safe(result)