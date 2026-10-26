"""CareerLens job compatibility module.

The 70/30 final-score blend is a project-defined heuristic, not a validated
hiring metric. Functions are reusable; the sample CLI runs only when this file
is executed directly.
"""

try:  # Supports both package imports and running matching.py directly.
    from .skill_extractor import (
        assign_skill_weights,
        extract_skills,
        find_unrecognized_skills,
        normalize_extracted_skill,
    )
    from .similarity import calculate_text_similarity
except ImportError:  # Direct script execution from this directory.
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
    """Compare candidate skills with a {skill: weight} mapping.

    Returns matched/missing sets, weighted skill compatibility, and weight totals.
    Candidate skill names are normalized before comparison.
    """
    if not hasattr(candidate_skills, "__iter__") or isinstance(candidate_skills, (str, bytes)):
        raise TypeError("candidate_skills must be an iterable of skill names, not a string")
    if not hasattr(weighted_job_skills, "items"):
        raise TypeError("weighted_job_skills must be a dictionary-like mapping")

    normalized_candidates = {
        normalize_extracted_skill(skill)
        for skill in candidate_skills
        if str(skill).strip()
    }
    normalized_job_skills = {}
    for skill, weight in weighted_job_skills.items():
        normalized = normalize_extracted_skill(skill)
        try:
            numeric_weight = float(weight)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid weight for skill {skill!r}: {weight!r}") from exc
        if numeric_weight < 0:
            raise ValueError(f"Weight for skill {skill!r} cannot be negative")
        if numeric_weight > 0:
            normalized_job_skills[normalized] = max(
                numeric_weight, normalized_job_skills.get(normalized, 0.0)
            )

    matched = normalized_candidates.intersection(normalized_job_skills)
    missing = set(normalized_job_skills).difference(normalized_candidates)
    total_weight = sum(normalized_job_skills.values())
    matched_weight = sum(normalized_job_skills[skill] for skill in matched)
    compatibility = matched_weight / total_weight * 100 if total_weight else 0.0

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
    """Blend skill and text scores with the documented project heuristic."""
    for name, score in (("skill_compatibility", skill_compatibility),
                        ("text_similarity", text_similarity)):
        if not isinstance(score, (int, float)) or not 0 <= score <= 100:
            raise ValueError(f"{name} must be a number between 0 and 100")
    return FINAL_SKILL_WEIGHT * skill_compatibility + FINAL_TEXT_WEIGHT * text_similarity


def evaluate_candidate(candidate_skills, resume_text, job_description, verbose=True):
    """Run extraction, weighting, skill matching, text similarity, and final score.

    Returns a structured dictionary suitable for later API/UI integration.
    """
    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Job description cannot be empty")
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text cannot be empty")

    extracted_skills = extract_skills(job_description)
    if not extracted_skills:
        raise ValueError("No recognizable or explicitly listed skills found in the job description")

    unknown_skills = find_unrecognized_skills(extracted_skills)
    weighted_skills = assign_skill_weights(extracted_skills, job_description)
    match = analyze_job_match(candidate_skills, weighted_skills, verbose=verbose)
    text_similarity = calculate_text_similarity(resume_text, job_description)
    final_score = calculate_final_score(match["compatibility"], text_similarity)

    if verbose:
        if unknown_skills:
            print("\nWarning: These listed skills are not in CareerLens' known skill vocabulary:")
            for skill in sorted(unknown_skills):
                print(" -", skill)
            print("They are included in matching because they were explicitly listed in a recognized skills section.")
        print("\nExtracted skills:", sorted(extracted_skills))
        print("Skill weights:", dict(sorted(weighted_skills.items())))
        print(f"\nResume-Job Text Similarity: {text_similarity:.2f}%")
        print(f"Final Compatibility Score: {final_score:.2f}%")
        print("\nNote: The final score uses a project-defined 70% skill / 30% text weighting.")

    return {
        **match,
        "extracted_skills": extracted_skills,
        "weighted_job_skills": weighted_skills,
        "unrecognized_skills": unknown_skills,
        "text_similarity": text_similarity,
        "final_score": final_score,
    }


def main():
    """Runnable demonstration; replace sample data with extracted resume data."""
    candidate_skills = {"Python"}
    resume_text = """
    B.Tech Information Technology student with skills in Python, SQL and Docker.
    Developed projects using Python and SQL.
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
        evaluate_candidate(candidate_skills, resume_text, job_description)
    except (TypeError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
