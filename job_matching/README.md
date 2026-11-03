# 🌌 CareerLens

### Intelligent Resume Builder, Job Compatibility & Skill Gap Recommendation System

> *Bridging the gap between your skills and your next opportunity.*

CareerLens is an **independently developed full-stack project** created by **Surabhi Bharati**. It is designed to help candidates prepare structured resume content, compare their skills with a target job description, understand missing skills, and explore areas for career development.

The project brings together a React-based user interface, a FastAPI backend, and a Python NLP/ML job-matching module. It is being built as both an academic project and a portfolio project, with an emphasis on modular code, explainable results, and testable functionality.

## ✨ Key Features

- **Resume Builder:** Create structured resume content from information supplied by the user.
- **Job Compatibility Analysis:** Compare a candidate profile and resume text with a target job description.
- **Skill Extraction and Normalization:** Identify supported technical skills and normalize common aliases.
- **Weighted Skill Matching:** Give required skills greater importance than preferred or other extracted skills.
- **Resume–Job Text Similarity:** Use TF-IDF vectorization and cosine similarity to compare text.
- **Skill Gap Analysis:** Identify missing job-related skills and return learning priorities.
- **Career Development Support:** Provide a foundation for role-oriented recommendations and skills improvement.
- **API Integration:** Expose core functionality through FastAPI endpoints for the frontend.
- **Automated Tests:** Test matching logic and supporting profile, resume, skill-gap, and API-adapter behaviour.

## 🧰 Technology Stack

| Area | Technologies |
|---|---|
| Frontend | React, Vite, Tailwind CSS, JavaScript |
| Backend | Python, FastAPI |
| NLP / Matching | TF-IDF, cosine similarity, rule-based skill extraction and weighted matching |
| Testing | Python `unittest` |
| Version Control | Git and GitHub |
| Deployment | Vercel (frontend), Render (backend API) |

## 🧠 How Job Compatibility Is Calculated

CareerLens combines skill overlap with resume–job text similarity:

```text
Final Score = (0.70 × Skill Compatibility) + (0.30 × Text Similarity)
```

- **Skill Compatibility (70%)** measures how well the candidate's listed skills match the skills identified in the job description, with weighting for required and preferred skills.
- **Text Similarity (30%)** uses TF-IDF vectors and cosine similarity to estimate textual similarity between the resume and job description.

The 70/30 weighting is a project-defined heuristic. The score is **not** a hiring probability, a validated recruitment standard, or a guarantee of job suitability.

## 🏗️ High-Level Architecture

```text
┌──────────────────────────────────┐
│     React + Vite Frontend        │
│ Resume Builder • Job Analysis    │
│ Skill Gap • Career Suggestions   │
└────────────────┬─────────────────┘
                 │ HTTP / JSON
┌────────────────▼─────────────────┐
│          FastAPI Backend         │
│ API routes • Validation •        │
│ Integration and response models  │
└─────────┬───────────────┬─────────┘
          │               │
┌─────────▼────────┐ ┌────▼────────────────┐
│ Resume/Profile   │ │ Job Matching NLP/ML │
│ Processing       │ │ Skills • TF-IDF     │
│ Resume Builder   │ │ Similarity • Scores │
└──────────────────┘ └─────────────────────┘
```

## 📂 Repository Structure

```text
CareerLens/
├── frontend/                 # React + Vite + Tailwind user interface
├── job_matching/             # Job compatibility and NLP/ML logic
│   ├── matching.py
│   ├── skill_extractor.py
│   ├── similarity.py
│   ├── tfidf_test.py
│   ├── test_matching.py
│   ├── requirements.txt
│   └── README.md
├── README.md
└── .gitignore
```

> The exact files and folders may evolve as development continues. Backend and supporting modules are organized according to the current project source.

## ⚙️ Getting Started

### Prerequisites

- Python 3.10+ (or a version supported by the installed dependencies)
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Surabhi-Bharati/CareerLens.git
cd CareerLens
```

### 2. Set up the Python environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies from the requirements file for the module you want to run. For the job-matching module:

```powershell
pip install -r job_matching/requirements.txt
```

### 3. Run the job-matching module

```powershell
python job_matching/matching.py
```

### 4. Run the job-matching tests

```powershell
python -m unittest discover -s job_matching -v
```

### 5. Run the frontend

```powershell
cd frontend
npm install
npm run dev
```

Vite will print the local development URL in the terminal.

> To run the complete application locally, start the FastAPI backend using the entry point and dependencies configured in the current backend source. The frontend can use the backend URL configured through `VITE_API_URL`; if this variable is not set, the frontend code falls back to `http://127.0.0.1:8000`.

## 🧪 Testing and Validation

The project includes automated tests for the Python matching logic and supporting backend functionality. A recent source verification run completed **47 tests successfully** (`OK`). Run the test command above against your current checkout to verify its present state; results can change as code and dependencies evolve.

Sample compatibility scores depend on the resume and job-description inputs. They should be interpreted as outputs of the project's scoring heuristic, not as model accuracy or real-world hiring outcomes.

## 🚀 Project Status

CareerLens is an active independent development project. Its core work includes job-matching logic, skill extraction, text similarity, skill-gap analysis, structured resume-building support, API routes, and a React frontend. Deployment and integration should continue to be checked as features evolve; successful module tests do not by themselves guarantee that every end-to-end user flow works in every environment.

## 🔭 Planned Improvements

- Improve resume upload and parsing workflows.
- Expand the skill vocabulary and normalization rules.
- Refine role-specific career recommendations and learning priorities.
- Add broader frontend-to-backend and end-to-end tests.
- Improve accessibility, responsive design, and user feedback for API errors.
- Evaluate the scoring heuristic against carefully designed examples and relevant real-world data.

## 👩‍💻 Author

**Surabhi Bharati**  
B.Tech in Information Technology · Asansol Engineering College

CareerLens is developed independently as an academic and portfolio project.

## 📜 Disclaimer

CareerLens is an educational career-support tool. Its outputs are informational and should not be treated as definitive hiring decisions, professional assessments, or guarantees of employment. Users should verify their resume details and independently assess learning or career recommendations.

---

**Repository:** [Surabhi-Bharati/CareerLens](https://github.com/Surabhi-Bharati/CareerLens)
