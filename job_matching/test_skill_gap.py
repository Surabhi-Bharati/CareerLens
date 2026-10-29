
import unittest

from job_matching.profile import CandidateProfile
from job_matching.skill_gap import analyze_skill_gap


class TestSkillGap(unittest.TestCase):

    def setUp(self):
        self.profile = CandidateProfile(
            full_name="Alex Morgan",
            skills=["Python", "SQL", "Docker"],
        )

        self.job_description = """
        Required skills:
        Python
        SQL
        Terraform

        Preferred skills:
        Docker
        Git
        """

    def test_returns_expected_result_fields(self):
        result = analyze_skill_gap(
            self.profile,
            self.job_description,
        )

        expected_fields = {
            "matched_skills",
            "missing_required_skills",
            "missing_preferred_skills",
            "all_missing_skills",
            "learning_priorities",
            "compatibility",
        }

        self.assertTrue(expected_fields.issubset(result.keys()))

    def test_matched_skills_are_detected(self):
        result = analyze_skill_gap(
            self.profile,
            self.job_description,
        )

        self.assertIn("python", result["matched_skills"])
        self.assertIn("sql", result["matched_skills"])
        self.assertIn("docker", result["matched_skills"])

    def test_missing_skills_are_detected(self):
        result = analyze_skill_gap(
            self.profile,
            self.job_description,
        )

        self.assertIn(
            "terraform",
            result["missing_required_skills"],
        )
        self.assertIn(
            "git",
            result["missing_preferred_skills"],
        )

    def test_required_skills_have_high_priority(self):
        result = analyze_skill_gap(
            self.profile,
            self.job_description,
        )

        priorities = {
            item["skill"]: item["priority"]
            for item in result["learning_priorities"]
        }

        self.assertEqual(priorities["terraform"], "high")
        self.assertEqual(priorities["git"], "medium")

    def test_empty_job_description_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_skill_gap(self.profile, "")

    def test_invalid_profile_is_rejected(self):
        with self.assertRaises(TypeError):
            analyze_skill_gap({}, self.job_description)


if __name__ == "__main__":
    unittest.main()
