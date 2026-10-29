
"""CareerLens analysis and resume API routes."""

from fastapi import APIRouter, HTTPException

from job_matching.api_adapter import evaluate_candidate_for_api
from job_matching.profile import CandidateProfile
from job_matching.resume_builder import build_resume
from job_matching.skill_gap import analyze_skill_gap

from backend.schemas.requests import (
    AnalyzeRequest,
    ResumeBuildRequest,
    SkillGapRequest,
)

router = APIRouter(prefix="/api", tags=["CareerLens"])


def create_profile(profile_data) -> CandidateProfile:
    """Convert validated API input into the existing profile model."""
    return CandidateProfile(**profile_data.model_dump())


@router.post("/analyze")
def analyze_candidate(request: AnalyzeRequest) -> dict:
    """Evaluate compatibility between a candidate and a job."""
    try:
        return evaluate_candidate_for_api(
            candidate_skills=request.candidate_skills,
            resume_text=request.resume_text,
            job_description=request.job_description,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/skill-gap")
def get_skill_gap(request: SkillGapRequest) -> dict:
    """Return matched skills, missing skills, and learning priorities."""
    try:
        profile = create_profile(request.profile)
        return analyze_skill_gap(profile, request.job_description)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/resume/build")
def create_resume(request: ResumeBuildRequest) -> dict:
    """Build a structured resume from verified profile information."""
    try:
        profile = create_profile(request.profile)
        return build_resume(
            profile=profile,
            target_role=request.target_role,
            job_description=request.job_description,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
