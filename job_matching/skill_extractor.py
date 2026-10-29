"""Skill extraction and weighting utilities for CareerLens.

The extractor combines a curated vocabulary with skills explicitly listed under
recognized job-description skill headings. It is dictionary-based, not a general
purpose NLP entity recognizer.
"""

import re

SKILL_ALIASES = {
    "python programming": "python",
    "python 3": "python",
    "python3": "python",
    "sql programming": "sql",
    "rest api": "rest",
    "rest apis": "rest",
    "restful api": "rest",
    "restful apis": "rest",
    "node": "node.js",
    "nodejs": "node.js",
    "react.js": "react",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "postgres": "postgresql",
    "mongo db": "mongodb",
    "amazon web services": "aws",
    "c plus plus": "c++",
    "c sharp": "c#",
    "natural language processing (nlp)": "natural language processing",
}

SUPPORTED_SKILLS = [
    "natural language processing", "object-oriented programming",
    "machine learning", "deep learning", "computer vision",
    "data visualization", "data analysis", "tailwind css", "scikit-learn",
    "node.js", "javascript", "typescript", "postgresql", "mongodb",
    "kubernetes", "tensorflow", "pytorch", "pandas", "numpy",
    "matplotlib", "seaborn", "xgboost", "lightgbm", "fastapi", "flask",
    "django", "express", "react", "next.js", "vue.js", "angular", "html",
    "css", "bootstrap", "graphql", "rest", "docker", "git", "github",
    "linux", "aws", "azure", "gcp", "mysql", "sqlite", "redis", "java",
    "python", "sql", "c++", "c#", "c", "golang", "go", "rust", "php",
    "ruby", "swift", "kotlin", "r", "pyspark", "spark", "hadoop",
    "airflow", "jenkins", "ci/cd", "llms", "llm", "rag", "spacy",
    "opencv", "scipy", "statistics", "excel", "power bi", "tableau",
    "agile", "scrum", "jira", "figma", "postman", "microservices",
    "api development", "oop", "ansible", "graphql",
]
SUPPORTED_SKILLS = sorted(set(SUPPORTED_SKILLS), key=len, reverse=True)
KNOWN_SKILLS = {s.lower() for s in SUPPORTED_SKILLS} | set(SKILL_ALIASES.values())

REQUIRED_HEADINGS = (
    "required skills", "must have", "mandatory skills", "requirements",
    "required qualifications","must-have skills",
    "required technical skills",
    "technical skills required",
)
PREFERRED_HEADINGS = (
    "preferred skills", "good to have", "nice to have", "optional skills",
    "preferred qualifications","nice-to-have skills",
    "preferred technical skills",
    "optional requirements",
)
OTHER_HEADINGS = (
    "responsibilities", "about the role", "about the job", "what you will do",
    "qualifications", "benefits", "company overview", "job description",
    "key responsibilities", "what you bring", "who you are",
)
ALL_SECTION_HEADINGS = REQUIRED_HEADINGS + PREFERRED_HEADINGS + OTHER_HEADINGS


def normalize_extracted_skill(skill):
    """Normalize a skill name to a canonical lowercase form."""
    cleaned = re.sub(r"\s+", " ", str(skill).strip().lower())
    return SKILL_ALIASES.get(cleaned, cleaned)


def _skill_pattern(skill):
    """Build a boundary-aware pattern that avoids Java/JavaScript overlap."""
    escaped = re.escape(skill)
    if skill in {"c++", "c#", "ci/cd"}:
        return re.compile(r"(?<![\w])" + escaped + r"(?![\w])", re.IGNORECASE)
    if skill in {"c", "r", "go"}:
        # Single-letter/common-word languages are only picked up from explicit
        # skill-section lists, where context makes the intent clearer.
        return None
    return re.compile(r"(?<![\w])" + escaped + r"(?![\w])", re.IGNORECASE)


def _clean_heading(line):
    line = re.sub(r"^[#*\-\s]+", "", line.strip().lower())
    return re.sub(r"[:\s]+$", "", line).strip()


def _extract_skill_section_items(job_description):
    """Extract comma/list-separated items under recognized skills headings."""
    items = []
    current_section = None
    for raw_line in job_description.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        heading = _clean_heading(line)
        if heading in REQUIRED_HEADINGS:
            current_section = "required"
            continue
        if heading in PREFERRED_HEADINGS:
            current_section = "preferred"
            continue
        if heading in OTHER_HEADINGS:
            current_section = None
            continue
        if current_section is None:
            continue

        cleaned = re.sub(r"^(?:[-*•]+|\d+[.)])\s*", "", line).strip()
        # Ignore descriptive prose rather than misclassifying whole sentences as skills.
        if re.search(r"\b(should|will|responsible|experience|years|candidate|looking for|ability to)\b", cleaned, re.I):
            continue
        for piece in re.split(r"[,;|]", cleaned):
            item = piece.strip().strip(". ")
            if item and len(item) <= 60:
                items.append((normalize_extracted_skill(item), current_section))
    return items


def extract_skills(job_description):
    """Return unique normalized skills found in a job description.

    Known skills are searched in free-form text. Unknown skills are retained when
    explicitly listed under recognized Required/Preferred skills headings.
    """
    if not isinstance(job_description, str) or not job_description.strip():
        return []

    found = []
    for skill in SUPPORTED_SKILLS:
        pattern = _skill_pattern(skill)
        if pattern is not None and pattern.search(job_description):
            found.append(normalize_extracted_skill(skill))
        # Detect aliases in free text as well as in explicit skill lists.
    for alias, canonical in SKILL_ALIASES.items():
        pattern = _skill_pattern(alias)
        if pattern is not None and pattern.search(job_description):
            found.append(normalize_extracted_skill(canonical))

    found.extend(item for item, _section in _extract_skill_section_items(job_description))

    result, seen = [], set()
    for skill in found:
        normalized = normalize_extracted_skill(skill)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def assign_skill_weights(skills, job_description):
    """Give required skills weight 3 and other extracted skills weight 1.

    If no recognized required-skills heading exists, every extracted skill gets
    the default weight 1. Preferred skills always get weight 1.
    """
    if not isinstance(job_description, str):
        job_description = ""

    section_items = _extract_skill_section_items(job_description)
    required_items = {item for item, section in section_items if section == "required"}
    has_required_section = any(_clean_heading(line) in REQUIRED_HEADINGS
                               for line in job_description.splitlines())

    weights = {}
    for skill in skills:
        normalized = normalize_extracted_skill(skill)
        weights[normalized] = 3 if has_required_section and normalized in required_items else 1
    return weights


def find_unrecognized_skills(skills):
    """Return skills outside the maintained vocabulary, preserving input order."""
    unknown, seen = [], set()
    for skill in skills:
        normalized = normalize_extracted_skill(skill)
        if normalized not in KNOWN_SKILLS and normalized not in seen:
            unknown.append(normalized)
            seen.add(normalized)
    return unknown
