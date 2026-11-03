
"""CareerLens career recommendation engine.

Recommends suitable career roles using candidate skills and interests.
This is a rule-based engine, not a trained machine-learning model.
"""

from typing import Any

from .profile import CandidateProfile


ROLE_PROFILES = {
    "Python Developer": {
        "skills": {"python", "sql", "git", "rest api", "fastapi", "django"},
        "interests": {"python development", "software development", "backend"},
        "description": "Build Python applications, APIs, and backend services.",
    },
    "Backend Developer": {
        "skills": {
            "python", "java", "node.js", "express.js", "fastapi",
            "django", "sql", "postgresql", "mongodb", "rest api",
        },
        "interests": {"backend", "api development", "software development"},
        "description": "Develop server-side logic, APIs, and database integrations.",
    },
    "Frontend Developer": {
        "skills": {
            "html", "css", "javascript", "react", "react.js",
            "next.js", "tailwind css",
        },
        "interests": {"frontend", "web development", "ui", "design"},
        "description": "Create responsive and interactive user interfaces.",
    },
    "Full Stack Developer": {
        "skills": {
            "html", "css", "javascript", "react", "react.js",
            "node.js", "express.js", "python", "fastapi",
            "sql", "postgresql", "mongodb",
        },
        "interests": {"full stack", "web development", "software development"},
        "description": "Work across frontend interfaces, backend services, and databases.",
    },
    "Data Analyst": {
        "skills": {
            "python", "sql", "excel", "pandas", "numpy",
            "matplotlib", "power bi", "tableau", "statistics",
        },
        "interests": {"data analysis", "analytics", "business intelligence"},
        "description": "Analyze data and communicate insights through reports and visualizations.",
    },
    "Machine Learning Engineer": {
        "skills": {
            "python", "pandas", "numpy", "scikit-learn",
            "tensorflow", "pytorch", "machine learning",
            "deep learning", "sql",
        },
        "interests": {"machine learning", "artificial intelligence", "ai", "deep learning"},
        "description": "Develop, evaluate, and integrate machine-learning systems.",
    },
}


SKILL_ALIASES = {
    "react.js": "react",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "artificial intelligence": "ai",
    "rest": "rest api",
}


def normalize_skill(value: str) -> str:
    """Normalize a skill or interest for consistent comparisons."""
    cleaned = " ".join(value.casefold().strip().split())
    return SKILL_ALIASES.get(cleaned, cleaned)


def recommend_careers(
    profile: CandidateProfile,
    top_n: int = 3,
) -> dict[str, Any]:
    """Return ranked career recommendations with explanations."""
    if not isinstance(profile, CandidateProfile):
        raise TypeError("profile must be a CandidateProfile instance.")

    if not isinstance(top_n, int) or isinstance(top_n, bool) or top_n < 1:
        raise ValueError("top_n must be a positive integer.")

    candidate_skills = {
        normalize_skill(skill) for skill in profile.skills if skill.strip()
    }
    interests = {
        normalize_skill(interest)
        for interest in profile.career_interests
        if interest.strip()
    }

    if not candidate_skills and not interests:
        return {
            "candidate_name": profile.full_name,
            "recommendations": [],
            "message": (
                "Add skills or career interests to your profile "
                "to receive personalized recommendations."
            ),
            "method": "rule-based",
        }

    recommendations = []

    for role, details in ROLE_PROFILES.items():
        role_skills = {
            normalize_skill(skill) for skill in details["skills"]
        }
        role_interests = {
            normalize_skill(interest) for interest in details["interests"]
        }

        matched_skills = sorted(candidate_skills & role_skills)
        missing_skills = sorted(role_skills - candidate_skills)
        matched_interests = sorted(interests & role_interests)

        skill_score = (
            len(matched_skills) / len(role_skills) * 100
            if role_skills else 0.0
        )

        # Interests contribute up to 20 additional percentage points.
        interest_bonus = min(len(matched_interests) * 10, 20)
        score = round(min(skill_score * 0.8 + interest_bonus, 100), 2)

        if score <= 0:
            continue

        reasons = []

        if matched_skills:
            reasons.append(
                "Your profile includes relevant skills: "
                + ", ".join(matched_skills)
                + "."
            )

        if matched_interests:
            reasons.append(
                "Your stated interests align with this role: "
                + ", ".join(matched_interests)
                + "."
            )

        recommendations.append({
            "role": role,
            "description": details["description"],
            "match_score": score,
            "matched_skills": matched_skills,
            "suggested_skills_to_learn": missing_skills[:5],
            "matched_interests": matched_interests,
            "reasons": reasons,
        })

    recommendations.sort(
        key=lambda item: (-item["match_score"], item["role"])
    )

    return {
        "candidate_name": profile.full_name,
        "recommendations": recommendations[:top_n],
        "message": (
            "Recommendations are based on skill and interest overlap. "
            "Scores are heuristic indicators, not predictions of hiring success."
        ),
        "method": "rule-based",
    }
