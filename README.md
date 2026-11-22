# 🌌 CareerLens
### Intelligent Resume Analysis, Job Compatibility & Skill Gap Recommendation System

> *Bridging the gap between your skills and your next opportunity.*

CareerLens is a student-developed project designed to help candidates understand how their resumes align with job descriptions. It aims to analyze candidate skills, estimate job compatibility, identify missing skills, and provide actionable recommendations to support career preparation.

The project is being developed as a modular application, with separate components for job compatibility analysis, skill-gap recommendations, resume processing, backend integration, and user-interface development.

## ✨ Project Objectives

- **Resume Analysis:** Process candidate resume information for further analysis.
- **Job Compatibility:** Compare candidate skills and resume content against a job description.
- **Skill Gap Identification:** Highlight relevant skills that are missing from the candidate's current profile.
- **Skill Recommendations:** Help candidates identify areas to improve for a target role.
- **Modular Architecture:** Keep components separate so they can be tested and integrated independently.

## 🧠 Job Compatibility & NLP/ML Module

The `job_matching/` directory contains the job compatibility analysis module.

### Current Features

- Skill extraction from job descriptions using a curated vocabulary and recognized skill-section headings.
- Skill normalization and alias handling to reduce duplicate representations.
- Weighted skill matching that gives greater importance to required skills than preferred skills.
- TF-IDF vectorization and cosine similarity to compare resume text with job-description text.
- A combined compatibility score using a configurable, project-defined weighting formula.
- Warnings for explicitly listed skills that are outside the known vocabulary.
- Automated unit tests for core module behavior.

### Compatibility Scoring

The current implementation combines skill compatibility and resume–job text similarity:

`Final Score = (0.70 × Skill Compatibility) + (0.30 × Text Similarity)`

The weights are a project-defined heuristic, not a validated hiring or recruitment standard.

## 🏗️ Planned Application Architecture

```text
                 ┌────────────────────────┐
                 │     User Interface     │
                 └────────────┬───────────┘
                              │
                 ┌────────────▼───────────┐
                 │    Backend / API       │
                 └────────────┬───────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
    ┌────────▼────────┐ ┌─────▼─────────┐ ┌────▼────────────┐
    │ Resume          │ │ Job Matching  │ │ Skill Gap &     │
    │ Processing      │ │ NLP/ML        │ │ Recommendations │
    └─────────────────┘ └───────────────┘ └─────────────────┘
```

*The diagram represents the intended modular architecture; the complete application and integration are still under development.*

## 📂 Repository Structure

```text
CareerLens/
├── job_matching/
│   ├── matching.py
│   ├── skill_extractor.py
│   ├── similarity.py
│   ├── tfidf_test.py
│   ├── test_matching.py
│   ├── requirements.txt
│   └── README.md
├── .gitignore
└── README.md
```

Additional modules will be added as they are implemented and integrated.

## ⚙️ Getting Started

### Prerequisites

- Python 3.10 or another version supported by the project's dependencies.
- Git.
- Visual Studio Code or another Python-compatible editor.

### 1. Clone the repository

```bash
git clone https://github.com/Surabhi-Bharati/CareerLens.git
cd CareerLens
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r job_matching/requirements.txt
```

### 4. Run the job matching module

```powershell
python job_matching/matching.py
```

### 5. Run automated tests

```powershell
python -m unittest discover -s job_matching -v
```

## 🧪 Testing

The job-matching module has been tested independently. 
Test results may vary if the code or dependencies change. Full-application integration testing remains a separate step.

## ⚠️ Current Limitations

- The compatibility score is an estimate, not a guarantee of job suitability or hiring success.
- Skill extraction depends on the vocabulary, aliases, and section headings supported by the implementation.
- TF-IDF measures textual similarity, not a complete understanding of professional competence.
- Skill recommendations depend on the rules and role mappings implemented in the recommendation component.
- The complete end-to-end application is still under development.

## 🚀 Future Enhancements

- Integrate resume upload and text extraction.
- Connect job matching to the backend API.
- Add skill-gap prioritization and role-specific recommendations.
- Develop an interactive, responsive user interface.
- Expand skill vocabularies and test coverage.
- Evaluate scoring behavior against carefully designed examples and relevant real-world data.
- Add end-to-end tests for the integrated application.

## 📜 Disclaimer

CareerLens is an educational project intended to support resume analysis and career preparation. Its outputs should not be treated as definitive hiring decisions, professional assessments, or guarantees of employment.

---

**Repository:** [Surabhi-Bharati/CareerLens](https://github.com/Surabhi-Bharati/CareerLens)
