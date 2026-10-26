# CareerLens — Job Compatibility & NLP/ML Module

This folder contains the reusable job-matching module and a runnable demonstration.

## Files

- `skill_extractor.py` — skill extraction, alias normalization, skill weighting, and vocabulary warnings.
- `similarity.py` — TF-IDF/cosine text similarity.
- `matching.py` — weighted skill matching, missing-skill analysis, final score, reusable `evaluate_candidate()` API, and sample CLI.
- `tfidf_test.py` — standalone text-similarity smoke test.
- `test_matching.py` — regression tests for key behavior.

## Setup (Windows / VS Code)

Activate your existing virtual environment, then run:

```powershell
python -m pip install -r requirements.txt
```

Run the sample:

```powershell
python matching.py
```

Run the tests from inside `job_matching`:

```powershell
python -m unittest -v test_matching
```

You can also run discovery from the CareerLens project root:

```powershell
python -m unittest discover -s job_matching -v
```

Run the similarity test separately:

```powershell
python tfidf_test.py
```

## Connecting to the rest of CareerLens

The main reusable entry point is `evaluate_candidate(candidate_skills, resume_text, job_description)` in `matching.py`.

Example:

```python
from matching import evaluate_candidate

result = evaluate_candidate(
    candidate_skills={"Python", "SQL", "Docker"},
    resume_text="Candidate resume text goes here...",
    job_description="Required skills:\nPython\nSQL\n\nPreferred skills:\nDocker",
    verbose=False,
)

print(result["final_score"])
print(result["missing_skills"])
```

The result dictionary includes `matched_skills`, `missing_skills`, `compatibility`, `text_similarity`, `final_score`, `extracted_skills`, `weighted_job_skills`, and `unrecognized_skills`.

## How skill weighting works

- Skills explicitly listed under a recognized `Required skills`, `Must have`, `Mandatory skills`, `Requirements`, or `Required qualifications` heading receive weight 3.
- Other extracted skills receive weight 1.
- When there is no recognized required heading, extracted skills default to weight 1.
- Unfamiliar skill names explicitly listed under recognized skills headings are included in matching and flagged if they are not in the maintained vocabulary.

## Score interpretation and limitations

The final score is a project-defined heuristic:

`final_score = 0.70 * skill_compatibility + 0.30 * text_similarity`

This weighting is not validated as a hiring metric. TF-IDF measures lexical overlap; it does not understand the full semantic meaning of a resume or job description. The skill extractor uses a curated vocabulary and recognized section headings; it cannot reliably discover every technical skill in arbitrary prose. Review outputs before using them in any real hiring decision.

## Job-description format recommended for best extraction

Use standalone headings and list skills on separate lines or separate them with commas:

```text
Required skills:
Python
SQL
Terraform

Preferred skills:
Docker, Git, AWS
```
