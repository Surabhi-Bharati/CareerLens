"""TF-IDF/cosine similarity utility for CareerLens."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_text_similarity(resume_text, job_description):
    """Return text similarity as a percentage in [0, 100].

    Empty, non-string, or vocabulary-free input returns 0.0 rather than raising.
    This measures lexical similarity, not the truth or quality of a resume.
    """
    if not isinstance(resume_text, str) or not isinstance(job_description, str):
        return 0.0
    if not resume_text.strip() or not job_description.strip():
        return 0.0
    try:
        matrix = TfidfVectorizer(stop_words="english").fit_transform(
            [resume_text, job_description]
        )
    except ValueError:
        return 0.0
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100
    return float(max(0.0, min(100.0, score)))
