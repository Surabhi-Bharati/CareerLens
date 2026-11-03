
import unittest

from job_matching.profile import CandidateProfile
from job_matching.career_recommendation import recommend_careers


class TestCareerRecommendation(unittest.TestCase):

    def test_recommends_relevant_careers(self):
        profile = CandidateProfile(
            full_name="Test User",
            skills=["Python", "SQL", "FastAPI", "Git"],
            career_interests=["backend", "software development"],
        )

        result = recommend_careers(profile)

        self.assertEqual(result["method"], "rule-based")
        self.assertGreater(len(result["recommendations"]), 0)

        roles = [item["role"] for item in result["recommendations"]]
        self.assertIn("Python Developer", roles)

    def test_empty_profile_returns_helpful_message(self):
        profile = CandidateProfile(full_name="Test User")

        result = recommend_careers(profile)

        self.assertEqual(result["recommendations"], [])
        self.assertIn("Add skills", result["message"])

    def test_top_n_limits_results(self):
        profile = CandidateProfile(
            full_name="Test User",
            skills=["Python", "SQL", "JavaScript", "React"],
        )

        result = recommend_careers(profile, top_n=2)

        self.assertLessEqual(len(result["recommendations"]), 2)

    def test_invalid_top_n_raises_error(self):
        profile = CandidateProfile(
            full_name="Test User",
            skills=["Python"],
        )

        with self.assertRaises(ValueError):
            recommend_careers(profile, top_n=0)


if __name__ == "__main__":
    unittest.main()
