
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
    "natural language processing",
    "object-oriented programming",
    "machine learning",
    "deep learning",
    "computer vision",
    "data visualization",
    "data analysis",
    "tailwind css",
    "scikit-learn",
    "node.js",
    "javascript",
    "typescript",
    "postgresql",
    "mongodb",
    "kubernetes",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "xgboost",
    "lightgbm",
    "fastapi",
    "flask",
    "django",
    "express",
    "react",
    "next.js",
    "vue.js",
    "angular",
    "html",
    "css",
    "bootstrap",
    "graphql",
    "rest",
    "docker",
    "git",
    "github",
    "linux",
    "aws",
    "azure",
    "gcp",
    "mysql",
    "sqlite",
    "redis",
    "java",
    "python",
    "sql",
    "c++",
    "c#",
    "c",
    "golang",
    "go",
    "rust",
    "php",
    "ruby",
    "swift",
    "kotlin",
    "r",
    "pyspark",
    "spark",
    "hadoop",
    "airflow",
    "jenkins",
    "ci/cd",
    "llms",
    "llm",
    "rag",
    "spacy",
    "opencv",
    "scipy",
    "statistics",
    "excel",
    "power bi",
    "tableau",
    "agile",
    "scrum",
    "jira",
    "figma",
    "postman",
    "microservices",
    "api development",
    "oop",
    "ansible",
    "graphql",
]

SUPPORTED_SKILLS = sorted(
    set(SUPPORTED_SKILLS),
    key=len,
    reverse=True,
)

KNOWN_SKILLS = (
    {skill.lower() for skill in SUPPORTED_SKILLS}
    | set(SKILL_ALIASES.values())
)


REQUIRED_HEADINGS = (
    "required skills",
    "must have",
    "mandatory skills",
    "requirements",
    "required qualifications",
    "must-have skills",
    "required technical skills",
    "technical skills required",
)

PREFERRED_HEADINGS = (
    "preferred skills",
    "good to have",
    "nice to have",
    "optional skills",
    "preferred qualifications",
    "nice-to-have skills",
    "preferred technical skills",
    "optional requirements",
)

OTHER_HEADINGS = (
    "responsibilities",
    "about the role",
    "about the job",
    "what you will do",
    "qualifications",
    "benefits",
    "company overview",
    "job description",
    "key responsibilities",
    "what you bring",
    "who you are",
)

ALL_SECTION_HEADINGS = (
    REQUIRED_HEADINGS
    + PREFERRED_HEADINGS
    + OTHER_HEADINGS
)

# Match longer headings first so they aren't partially recognized.
_HEADING_ALTERNATIVES = sorted(
    ALL_SECTION_HEADINGS,
    key=len,
    reverse=True,
)

# Inline headings are recognized when followed by a colon, for example:
# Required skills: Python, Docker. Preferred skills: Git.
_INLINE_HEADING_PATTERN = re.compile(
    r"(?i)(?<!\w)("
    + "|".join(
        re.escape(heading)
        for heading in _HEADING_ALTERNATIVES
    )
    + r")\s*:"
)

_PROSE_INDICATORS = re.compile(
    r"\b(should|will|responsible|experience|years|candidate|"
    r"looking for|ability to)\b",
    re.IGNORECASE,
)


def normalize_extracted_skill(skill):
    """Normalize a skill name to a canonical lowercase form."""
    cleaned = re.sub(
        r"\s+",
        " ",
        str(skill).strip().lower(),
    )
    return SKILL_ALIASES.get(cleaned, cleaned)


def _skill_pattern(skill):
    """Build a boundary-aware pattern that avoids Java/JavaScript overlap."""
    escaped = re.escape(skill)

    if skill in {"c++", "c#", "ci/cd"}:
        return re.compile(
            r"(?<![\w])" + escaped + r"(?![\w])",
            re.IGNORECASE,
        )

    if skill in {"c", "r", "go"}:
        # Single-letter/common-word languages are only picked up from explicit
        # skill-section lists, where context makes the intent clearer.
        return None

    return re.compile(
        r"(?<![\w])" + escaped + r"(?![\w])",
        re.IGNORECASE,
    )


def _clean_heading(line):
    """Normalize a section heading for comparison."""
    line = re.sub(r"^[#*\-\s]+", "", line.strip().lower())
    return re.sub(r"[:\s]+$", "", line).strip()


def _heading_section(heading):
    """Return the section type for a recognized heading."""
    cleaned = _clean_heading(heading)

    if cleaned in REQUIRED_HEADINGS:
        return "required"

    if cleaned in PREFERRED_HEADINGS:
        return "preferred"

    if cleaned in OTHER_HEADINGS:
        return None

    return None


def _extract_skill_section_items(job_description):
    """Extract comma/list-separated items under recognized skill headings.

    Supports headings on their own lines and inline headings ending in a colon.
    For example:
        Required skills:
        Python
        Docker

    Also supports:
        Required skills: Python, Docker. Preferred skills: Git.
    """
    items = []
    current_section = None

    for raw_line in job_description.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # First handle inline headings, including multiple headings on one line.
        matches = list(_INLINE_HEADING_PATTERN.finditer(line))

        if matches:
            segments = []

            for index, match in enumerate(matches):
                start = match.end()
                end = (
                    matches[index + 1].start()
                    if index + 1 < len(matches)
                    else len(line)
                )

                heading = match.group(1)
                section = _heading_section(heading)
                segment = line[start:end].strip()

                segments.append((segment, section))

            # Only text after a recognized heading is interpreted as a section.
            current_section = segments[-1][1] if segments else None

            for segment, section in segments:
                if section is None:
                    continue

                _append_section_items(items, segment, section)

            continue

        # Then handle headings written on their own lines.
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

        _append_section_items(items, line, current_section)

    return items


def _append_section_items(items, text, section):
    """Split and append skill items from one required/preferred section."""
    cleaned = re.sub(
        r"^(?:[-*•]+|\d+[.)])\s*",
        "",
        text,
    ).strip()

    # Avoid treating descriptive sentences as comma-separated skill lists.
    if _PROSE_INDICATORS.search(cleaned):
        return

    for piece in re.split(r"[,;|]", cleaned):
        item = piece.strip().strip(". ")

        if item and len(item) <= 60:
            items.append(
                (normalize_extracted_skill(item), section)
            )


def extract_skills(job_description):
    """Return unique normalized skills found in a job description.

    Known skills are searched in free-form text. Unknown skills are retained
    when explicitly listed under recognized Required/Preferred headings.
    """
    if (
        not isinstance(job_description, str)
        or not job_description.strip()
    ):
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

    found.extend(
        item
        for item, _section in _extract_skill_section_items(
            job_description
        )
    )

    result = []
    seen = set()

    for skill in found:
        normalized = normalize_extracted_skill(skill)

        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result


def assign_skill_weights(skills, job_description):
    """Give required skills weight 3 and other extracted skills weight 1."""
    if not isinstance(job_description, str):
        job_description = ""

    section_items = _extract_skill_section_items(job_description)

    required_items = {
        item
        for item, section in section_items
        if section == "required"
    }

    weights = {}

    for skill in skills:
        normalized = normalize_extracted_skill(skill)
        weights[normalized] = (
            3 if normalized in required_items else 1
        )

    return weights


def find_unrecognized_skills(skills):
    """Return skills outside the maintained vocabulary, preserving input order."""
    unknown = []
    seen = set()

    for skill in skills:
        normalized = normalize_extracted_skill(skill)

        if normalized not in KNOWN_SKILLS and normalized not in seen:
            unknown.append(normalized)
            seen.add(normalized)

    return unknown
