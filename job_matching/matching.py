
"""CareerLens job compatibility module.

The 70/30 final-score blend is a project-defined heuristic,
not a validated hiring metric.
"""

import math

try:
    from .skill_extractor import (
        assign_skill_weights,
        extract_skills,
        find_unrecognized_skills,
        normalize_extracted_skill,
    )
    from .similarity import calculate_text_similarity
except ImportError:
    from skill_extractor import (
        assign_skill_weights,
        extract_skills,
        find_unrecognized_skills,
        normalize_extracted_skill,
    )
    from similarity import calculate_text_similarity


FINAL_SKILL_WEIGHT = 0.70
FINAL_TEXT_WEIGHT = 0.30


def analyze_job_match(candidate_skills, weighted_job_skills, verbose=True):
    """Compare candidate skills against weighted job requirements."""
    if (
        isinstance(candidate_skills, (str, bytes))
        or not hasattr(candidate_skills, "__iter__")
    ):
        raise TypeError(
            "candidate_skills must be an iterable of skill names, not a string"
        )

    if not hasattr(weighted_job_skills, "items"):
        raise TypeError(
            "weighted_job_skills must be a dictionary-like mapping"
        )

    # Normalize candidate skills and reject invalid entries.
    normalized_candidates = set()

    for skill in candidate_skills:
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError(
                "Candidate skill names must be non-empty strings"
            )

        normalized = normalize_extracted_skill(skill)
        if normalized:
            normalized_candidates.add(normalized)

    # Normalize job skills and validate their weights.
    normalized_job_skills = {}

    for skill, weight in weighted_job_skills.items():
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError("Job skill names must be non-empty strings")

        # bool is a subclass of int, so reject it explicitly.
        if isinstance(weight, bool):
            raise ValueError(
                f"Invalid weight for skill {skill!r}: {weight!r}"
            )

        try:
            numeric_weight = float(weight)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid weight for skill {skill!r}: {weight!r}"
            ) from exc

        if not math.isfinite(numeric_weight):
            raise ValueError(
                f"Weight for skill {skill!r} must be finite"
            )

        if numeric_weight < 0:
            raise ValueError(
                f"Weight for skill {skill!r} cannot be negative"
            )

        normalized = normalize_extracted_skill(skill)

        # Ignore zero-weight requirements.
        if not normalized or numeric_weight == 0:
            continue

        # Prevent aliases such as "Python" and "Python programming"
        # from being counted as separate requirements.
        normalized_job_skills[normalized] = max(
            numeric_weight,
            normalized_job_skills.get(normalized, 0.0),
        )

    matched = normalized_candidates.intersection(normalized_job_skills)
    missing = set(normalized_job_skills).difference(normalized_candidates)

    total_weight = sum(normalized_job_skills.values())
    matched_weight = sum(
        normalized_job_skills[skill] for skill in matched
    )

    compatibility = (
        matched_weight / total_weight * 100.0
        if total_weight > 0
        else 0.0
    )

    if verbose:
        print("\n===== CareerLens Job Analysis =====")

        print("\nMatched Skills:")
        for skill in sorted(matched):
            print("✓", skill)
        if not matched:
            print("None")

        print("\nMissing Skills:")
        for skill in sorted(missing):
            print("✗", skill)
        if not missing:
            print("None")

        print(f"\nJob Compatibility: {compatibility:.2f}%")

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "compatibility": compatibility,
        "total_weight": total_weight,
        "matched_weight": matched_weight,
    }


def calculate_final_score(skill_compatibility, text_similarity):
    """Blend skill and text scores using the project's 70/30 heuristic."""
    for name, score in (
        ("skill_compatibility", skill_compatibility),
        ("text_similarity", text_similarity),
    ):
        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not math.isfinite(score)
            or not 0 <= score <= 100
        ):
            raise ValueError(
                f"{name} must be a finite number between 0 and 100"
            )

    return (
        FINAL_SKILL_WEIGHT * skill_compatibility
        + FINAL_TEXT_WEIGHT * text_similarity
    )


def evaluate_candidate(
    candidate_skills,
    resume_text,
    job_description,
    verbose=True,
):
    """Evaluate candidate skills and resume text against a job description."""
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text cannot be empty")

    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Job description cannot be empty")

    extracted_skills = extract_skills(job_description)

    if not extracted_skills:
        raise ValueError(
            "No recognizable or explicitly listed skills found "
            "in the job description"
        )

    unknown_skills = find_unrecognized_skills(extracted_skills)

    weighted_skills = assign_skill_weights(
        extracted_skills,
        job_description,
    )

    match = analyze_job_match(
        candidate_skills,
        weighted_skills,
        verbose=verbose,
    )

    text_similarity = calculate_text_similarity(
        resume_text,
        job_description,
    )

    final_score = calculate_final_score(
        match["compatibility"],
        text_similarity,
    )

    if verbose:
        if unknown_skills:
            print(
                "\nWarning: These listed skills are not in "
                "CareerLens' known skill vocabulary:"
            )
            for skill in sorted(unknown_skills):
                print(" -", skill)

            print(
                "These explicitly listed skills are retained for "
                "matching but should be reviewed for vocabulary support."
            )

        print("\nExtracted skills:", sorted(extracted_skills))
        print("Skill weights:", dict(sorted(weighted_skills.items())))
        print(f"\nResume-Job Text Similarity: {text_similarity:.2f}%")
        print(f"Final Compatibility Score: {final_score:.2f}%")
        print(
            "\nNote: The final score uses a project-defined "
            "70% skill / 30% text weighting."
        )

    return {
        **match,
        "extracted_skills": extracted_skills,
        "weighted_job_skills": weighted_skills,
        "unrecognized_skills": unknown_skills,
        "text_similarity": text_similarity,
        "final_score": final_score,
    }


def main():
    """Run a sample job-matching demonstration."""
    candidate_skills = {"Python", "SQL"}

    resume_text = """
    B.Tech Information Technology student with skills in Python,
    SQL and Docker. Developed projects using Python and SQL.
    """

    job_description = """
    We are looking for a developer.

    Required skills:
    Python
    Terraform

    Preferred skills:
    Docker
    Git
    """

    try:
        evaluate_candidate(
            candidate_skills,
            resume_text,
            job_description,
        )
    except (TypeError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
