
"""Validated request schemas for the CareerLens API."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    candidate_skills: list[str] = Field(min_length=1)
    resume_text: str = Field(min_length=1)
    job_description: str = Field(min_length=1)

    @field_validator("resume_text", "job_description")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value

    @field_validator("candidate_skills")
    @classmethod
    def validate_skills(cls, skills: list[str]) -> list[str]:
        cleaned = [skill.strip() for skill in skills]
        if any(not skill for skill in cleaned):
            raise ValueError("Skill names cannot be blank.")
        return cleaned


class CandidateProfileRequest(BaseModel):
    full_name: str = Field(min_length=1)
    headline: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    education: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    career_interests: list[str] = Field(default_factory=list)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("full_name cannot be blank.")
        return value


class SkillGapRequest(BaseModel):
    profile: CandidateProfileRequest
    job_description: str = Field(min_length=1)

    @field_validator("job_description")
    @classmethod
    def validate_job_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("job_description cannot be blank.")
        return value


class ResumeBuildRequest(BaseModel):
    profile: CandidateProfileRequest
    target_role: str | None = None
    job_description: str | None = None
