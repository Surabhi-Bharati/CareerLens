"""Standalone smoke test for the CareerLens text-similarity utility."""

try:
    from .similarity import calculate_text_similarity
except ImportError:
    from similarity import calculate_text_similarity


def main():
    resume_text = """
    B.Tech Information Technology student with skills in Python, SQL, Pandas,
    NumPy and Git. Developed machine learning projects using Python and Scikit-learn.
    """
    job_description = """
    We are looking for a Python developer with experience in Python, SQL, Git,
    machine learning, Pandas, NumPy and Scikit-learn. Backend development is preferred.
    """
    score = calculate_text_similarity(resume_text, job_description)
    print(f"Text Similarity: {score:.2f}%")
    print("Empty-input test:", calculate_text_similarity("", job_description))


if __name__ == "__main__":
    main()
