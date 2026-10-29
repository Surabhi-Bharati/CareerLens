
"""Shared candidate profile for CareerLens.

This module stores candidate information in one reusable structure.
It does not calculate compatibility scores or invent candidate details.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field, fields
import json
from typing import Any, Mapping


def _clean_string_list(
    values: list[str],
    *,
    lowercase: bool = False,
) -> list[str]:
    """Remove blank entries and duplicate strings while preserving order."""
    if not isinstance(values, list):
        raise TypeError("Expected a list of strings.")

    cleaned = []
    seen = set()

    for value in values:
        if not isinstance(value, str):
            raise TypeError("Every list item must be a string.")

        value = value.strip()
        if not value:
            continue

        normalized = value.casefold()
        if normalized in seen:
            continue

        seen.add(normalized)
        cleaned.append(value.lower() if lowercase else value)

    return cleaned


def _clean_records(
    records: list[dict[str, Any]],
    field_name: str,
) -> list[dict[str, Any]]:
    """Validate and copy lists of education, project, or experience records."""
    if not isinstance(records, list):
        raise TypeError(f"{field_name} must be a list.")

    cleaned = []

    for record in records:
        if not isinstance(record, Mapping):
            raise TypeError(
                f"Every item in {field_name} must be a dictionary."
            )

        if not all(isinstance(key, str) for key in record):
            raise TypeError(
                f"All keys in {field_name} records must be strings."
            )

        cleaned.append(deepcopy(dict(record)))

    return cleaned


@dataclass
class CandidateProfile:
    """Reusable candidate information for CareerLens features."""

    full_name: str
    headline: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""

    education: list[dict[str, Any]] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    projects: list[dict[str, Any]] = field(default_factory=list)
    experience: list[dict[str, Any]] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    career_interests: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate and normalize the profile after creation."""
        if not isinstance(self.full_name, str) or not self.full_name.strip():
            raise ValueError("full_name must be a non-empty string.")

        self.full_name = self.full_name.strip()

        for name in (
            "headline",
            "email",
            "phone",
            "location",
            "summary",
        ):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            setattr(self, name, value.strip())

        self.skills = _clean_string_list(
            self.skills,
            lowercase=True,
        )
        self.certifications = _clean_string_list(self.certifications)
        self.career_interests = _clean_string_list(
            self.career_interests
        )

        self.education = _clean_records(self.education, "education")
        self.projects = _clean_records(self.projects, "projects")
        self.experience = _clean_records(self.experience, "experience")

        # Fail early if the profile cannot be serialized for an API.
        try:
            json.dumps(asdict(self), allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Profile data must contain JSON-compatible values."
            ) from exc

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible dictionary without exposing internal lists."""
        return deepcopy(asdict(self))

    def to_json(self, *, indent: int = 2) -> str:
        """Convert the profile into a JSON string."""
        return json.dumps(
            self.to_dict(),
            indent=indent,
            allow_nan=False,
        )

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "CandidateProfile":
        """Create a profile from a dictionary, such as an API request."""
        if not isinstance(data, Mapping):
            raise TypeError("Profile input must be a dictionary.")

        allowed_fields = {item.name for item in fields(cls)}
        unknown_fields = set(data.keys()) - allowed_fields

        if unknown_fields:
            names = ", ".join(sorted(str(name) for name in unknown_fields))
            raise ValueError(f"Unknown profile fields: {names}")

        return cls(**dict(data))
