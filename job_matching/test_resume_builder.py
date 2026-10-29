
import unittest

from job_matching.profile import CandidateProfile
from job_matching.resume_builder import build_resume, render_resume_text


class TestResumeBuilder(unittest.TestCase):
    def setUp(self):
        self.profile = CandidateProfile(
            full_name="Test Candidate",
            headline="Python Developer",
            email="test@example.com",
            skills=["Python", "SQL", "Docker"],
            education=[{"degree": "B.Tech"}],
            projects=[{"name": "CareerLens"}],
            certifications=["Programming with Java"],
        )

    def test_build_resume_preserves_profile_information(self):
        resume = build_resume(self.profile)

        self.assertEqual(
            resume["contact"]["full_name"],
            "Test Candidate",
        )
        self.assertEqual(
            set(resume["skills"]),
            {"python", "sql", "docker"},
        )
        self.assertEqual(resume["education"], [{"degree": "B.Tech"}])
        self.assertEqual(resume["projects"], [{"name": "CareerLens"}])

    def test_job_description_only_reorders_existing_skills(self):
        resume = build_resume(
            self.profile,
            target_role="Backend Developer",
            job_description="Python and Docker experience required.",
        )

        self.assertEqual(resume["target_role"], "Backend Developer")
        self.assertEqual(resume["skills"][0], "docker")
        self.assertEqual(set(resume["skills"]), {"python", "sql", "docker"})

    def test_render_resume_text_includes_sections(self):
        resume = build_resume(self.profile)
        text = render_resume_text(resume)

        self.assertIn("Test Candidate", text)
        self.assertIn("PROFESSIONAL SUMMARY", text) if self.profile.summary else None
        self.assertIn("EDUCATION", text)
        self.assertIn("SKILLS", text)
        self.assertIn("PROJECTS", text)
        self.assertIn("CERTIFICATIONS", text)

    def test_invalid_profile_is_rejected(self):
        with self.assertRaises(TypeError):
            build_resume({"full_name": "Test Candidate"})

    def test_invalid_resume_input_is_rejected(self):
        with self.assertRaises(TypeError):
            render_resume_text("not a resume dictionary")


if __name__ == "__main__":
    unittest.main()
