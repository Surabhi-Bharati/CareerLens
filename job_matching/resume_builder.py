
"""CareerLens structured resume builder.

Builds a resume from verified candidate-profile fields.
It does not generate or invent qualifications, skills, or experience.
"""

from typing import Any

from .profile import CandidateProfile


def build_resume(
    profile: CandidateProfile,
    target_role: str | None = None,
    job_description: str | None = None,
) -> dict[str, Any]:
    """Build a structured, job-tailored resume from a candidate profile."""
    if not isinstance(profile, CandidateProfile):
        raise TypeError("profile must be a CandidateProfile instance.")

    if target_role is not None and not isinstance(target_role, str):
        raise TypeError("target_role must be a string or None.")

    if job_description is not None and not isinstance(job_description, str):
        raise TypeError("job_description must be a string or None.")

    role = target_role.strip() if target_role else ""

    if not role and job_description:
        # Do not guess a job title from arbitrary job-description text.
        role = ""

    skills = sorted(set(profile.skills))

    resume = {
        "contact": {
            "full_name": profile.full_name,
            "headline": profile.headline,
            "email": profile.email,
            "phone": profile.phone,
            "location": profile.location,
        },
        "target_role": role,
        "summary": profile.summary,
        "education": profile.education,
        "skills": skills,
        "projects": profile.projects,
        "experience": profile.experience,
        "certifications": profile.certifications,
    }

    if job_description and job_description.strip():
        # Reorder existing skills to put explicitly mentioned ones first.
        # This does not add skills that are absent from the candidate profile.
        description = job_description.casefold()
        resume["skills"] = sorted(
            skills,
            key=lambda skill: (
                skill.casefold() not in description,
                skill.casefold(),
            ),
        )

    return resume


def render_resume_text(resume: dict[str, Any]) -> str:
    """Render the structured resume as readable plain text."""
    if not isinstance(resume, dict):
        raise TypeError("resume must be a dictionary.")

    contact = resume.get("contact", {})
    lines = []

    name = contact.get("full_name", "")
    if name:
        lines.append(str(name))

    headline = contact.get("headline", "")
    if headline:
        lines.append(str(headline))

    contact_details = [
        contact.get("email", ""),
        contact.get("phone", ""),
        contact.get("location", ""),
    ]
    contact_details = [str(value) for value in contact_details if value]

    if contact_details:
        lines.append(" | ".join(contact_details))

    role = resume.get("target_role", "")
    if role:
        lines.extend(["", f"Target Role: {role}"])

    summary = resume.get("summary", "")
    if summary:
        lines.extend(["", "PROFESSIONAL SUMMARY", str(summary)])

    for section_name, key in (
        ("EDUCATION", "education"),
        ("SKILLS", "skills"),
        ("PROJECTS", "projects"),
        ("EXPERIENCE", "experience"),
        ("CERTIFICATIONS", "certifications"),
    ):
        items = resume.get(key, [])
        if not items:
            continue

        lines.extend(["", section_name])

        for item in items:
            if isinstance(item, dict):
                # Display each supplied field without inventing details.
                details = [
                    f"{field}: {value}"
                    for field, value in item.items()
                    if value not in (None, "", [], {})
                ]
                lines.extend(details or ["(No details provided)"])
            else:
                lines.append(str(item))

    return "\n".join(lines)
