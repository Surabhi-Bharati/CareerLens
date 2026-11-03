
import unittest

from job_matching.profile import CandidateProfile


class TestCandidateProfile(unittest.TestCase):

    def test_profile_creation(self):
        profile = CandidateProfile(
            full_name="Alex Morgan",
            skills=["Python", "SQL"],
        )

        self.assertEqual(profile.full_name, "Alex Morgan")
        self.assertEqual(profile.skills, ["python", "sql"])

    def test_duplicate_skills_are_removed(self):
        profile = CandidateProfile(
            full_name="Alex Morgan",
            skills=["Python", "python", "SQL", "Python"],
        )

        self.assertEqual(profile.skills, ["python", "sql"])

    def test_blank_name_is_rejected(self):
        with self.assertRaises(ValueError):
            CandidateProfile(full_name=" ")

    def test_non_string_skill_is_rejected(self):
        with self.assertRaises(TypeError):
            CandidateProfile(
                full_name="Alex Morgan",
                skills=["Python", 123],
            )

    def test_json_round_trip(self):
        profile = CandidateProfile(
            full_name="Alex Morgan",
            skills=["Python", "SQL"],
            education=[{"degree": "B.Tech"}],
        )

        restored = CandidateProfile.from_dict(profile.to_dict())

        self.assertEqual(restored.to_dict(), profile.to_dict())

    def test_unknown_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            CandidateProfile.from_dict({
                "full_name": "Alex Morgan",
                "unknown_field": "unexpected",
            })

    def test_returned_dictionary_does_not_modify_profile(self):
        profile = CandidateProfile(
            full_name="Alex Morgan",
            skills=["Python"],
        )

        data = profile.to_dict()
        data["skills"].append("java")

        self.assertEqual(profile.skills, ["python"])


if __name__ == "__main__":
    unittest.main()
