
"""CareerLens skill-gap analysis.

Uses the existing skill extractor and weighting rules to identify
matched skills, missing requirements, and learning priorities.
"""

from typing import Any

from .profile import CandidateProfile
from .skill_extractor import (
    assign_skill_weights,
    extract_skills,
    find_unrecognized_skills,
    normalize_extracted_skill,
)


def analyze_skill_gap(
    profile: CandidateProfile,
    job_description: str,
) -> dict[str, Any]:
    """Compare a candidate profile with the skills requested by a job."""
    if not isinstance(profile, CandidateProfile):
        raise TypeError("profile must be a CandidateProfile instance.")

    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("job_description must be a non-empty string.")

    extracted_skills = extract_skills(job_description)

    if not extracted_skills:
        raise ValueError(
            "No recognizable or explicitly listed skills found "
            "in the job description."
        )

    raw_weights = assign_skill_weights(
        extracted_skills,
        job_description,
    )

    # Normalize skill names consistently with the matching engine.
    job_weights = {}

    for skill, weight in raw_weights.items():
        normalized = normalize_extracted_skill(skill)
        job_weights[normalized] = max(
            float(weight),
            job_weights.get(normalized, 0.0),
        )

    candidate_skills = {
        normalize_extracted_skill(skill)
        for skill in profile.skills
    }

    job_skill_names = set(job_weights)

    matched = sorted(candidate_skills & job_skill_names)
    missing = sorted(job_skill_names - candidate_skills)

    # Existing project convention: required skills have weight 3;
    # preferred skills have lower weights.
    required_skills = sorted(
        skill for skill, weight in job_weights.items()
        if weight >= 3
    )

    preferred_skills = sorted(
        skill for skill, weight in job_weights.items()
        if weight < 3
    )

    missing_required = sorted(set(missing) & set(required_skills))
    missing_preferred = sorted(set(missing) & set(preferred_skills))

    total_weight = sum(job_weights.values())
    matched_weight = sum(job_weights[skill] for skill in matched)

    compatibility = (
        round(matched_weight / total_weight * 100, 2)
        if total_weight > 0
        else 0.0
    )

    learning_priorities = []

    for skill in missing_required:
        learning_priorities.append({
            "skill": skill,
            "priority": "high",
            "reason": "Missing required skill",
            "weight": job_weights[skill],
        })

    for skill in missing_preferred:
        learning_priorities.append({
            "skill": skill,
            "priority": "medium",
            "reason": "Missing preferred skill",
            "weight": job_weights[skill],
        })

    learning_priorities.sort(
        key=lambda item: (-item["weight"], item["skill"])
    )

    return {
        "matched_skills": matched,
        "missing_required_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "all_missing_skills": missing,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "unrecognized_skills": sorted(
            find_unrecognized_skills(extracted_skills)
        ),
        "compatibility": compatibility,
        "total_weight": total_weight,
        "matched_weight": matched_weight,
        "learning_priorities": learning_priorities,
    }
