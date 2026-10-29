"""Regression tests for CareerLens. Run from this folder or discover from the project root."""
import math
import unittest

try:  # Supports both package discovery and direct unittest invocation.
    from .matching import analyze_job_match, calculate_final_score, evaluate_candidate
    from .similarity import calculate_text_similarity
    from .skill_extractor import assign_skill_weights, extract_skills, find_unrecognized_skills
except ImportError:
    from matching import analyze_job_match, calculate_final_score, evaluate_candidate
    from similarity import calculate_text_similarity
    from skill_extractor import assign_skill_weights, extract_skills, find_unrecognized_skills


class SkillExtractionTests(unittest.TestCase):
    def test_aliases_and_duplicates(self):
        skills = extract_skills("Required skills:\nPython 3, Python programming, SQL programming")
        self.assertIn("python", skills)
        self.assertIn("sql", skills)
        self.assertEqual(skills.count("python"), 1)

    def test_candidate_aliases_normalize_for_matching(self):
        result = analyze_job_match({"Python 3", "SQL Programming"},
                                   {"python": 3, "sql": 3}, verbose=False)
        self.assertEqual(result["compatibility"], 100.0)

    def test_java_and_javascript_are_distinct(self):
        skills = extract_skills("Required skills:\nJavaScript\nReact")
        self.assertIn("javascript", skills)
        self.assertIn("react", skills)
        self.assertNotIn("java", skills)

    def test_cpp_and_csharp(self):
        skills = extract_skills("Required skills:\nC++\nC#")
        self.assertIn("c++", skills)
        self.assertIn("c#", skills)

    def test_unknown_explicit_skill_is_preserved_and_flagged(self):
        skills = extract_skills("Required skills:\nPython\nTerraform")
        self.assertIn("terraform", skills)
        self.assertIn("terraform", find_unrecognized_skills(skills))

    def test_required_and_preferred_weights(self):
        description = "Required skills:\nPython\nTerraform\n\nPreferred skills:\nDocker\nGit"
        skills = extract_skills(description)
        weights = assign_skill_weights(skills, description)
        self.assertEqual(weights["python"], 3)
        self.assertEqual(weights["terraform"], 3)
        self.assertEqual(weights["docker"], 1)
        self.assertEqual(weights["git"], 1)

    def test_preferred_only_defaults_to_one(self):
        description = "Preferred skills:\nPython\nDocker"
        weights = assign_skill_weights(extract_skills(description), description)
        self.assertEqual(weights, {"python": 1, "docker": 1})

    def test_markdown_headings_and_bullets(self):
        description = "## Required skills:\n- Python\n- Terraform\n\n### Preferred skills:\n* Docker, Git"
        skills = extract_skills(description)
        weights = assign_skill_weights(skills, description)
        self.assertEqual(weights["python"], 3)
        self.assertEqual(weights["terraform"], 3)
        self.assertEqual(weights["docker"], 1)
        self.assertEqual(weights["git"], 1)

    def test_empty_description(self):
        self.assertEqual(extract_skills("   "), [])

    def test_non_string_description_returns_no_skills(self):
        self.assertEqual(extract_skills(None), [])


class MatchingTests(unittest.TestCase):
    def test_weighted_compatibility(self):
        result = analyze_job_match({"Python", "Docker"},
                                   {"python": 3, "terraform": 3, "docker": 1, "git": 1},
                                   verbose=False)
        self.assertAlmostEqual(result["compatibility"], 50.0)
        self.assertEqual(result["matched_skills"], {"python", "docker"})
        self.assertEqual(result["missing_skills"], {"terraform", "git"})

    def test_strong_match_is_100_percent(self):
        description = "Required skills:\nPython\nSQL\n\nPreferred skills:\nDocker\nGit"
        result = evaluate_candidate(
            {"Python", "SQL", "Docker", "Git"}, description, description, verbose=False
        )
        self.assertEqual(result["compatibility"], 100.0)
        self.assertAlmostEqual(result["text_similarity"], 100.0)
        self.assertAlmostEqual(result["final_score"], 100.0)
        self.assertEqual(result["missing_skills"], set())

    def test_partial_match_required_skills_count_more(self):
        description = "Required skills:\nPython\nSQL\n\nPreferred skills:\nDocker\nGit"
        result = evaluate_candidate({"Python", "Docker"},
                                    "Python developer who uses Docker.", description, verbose=False)
        # Python (3) + Docker (1) matched out of total weight 8.
        self.assertAlmostEqual(result["compatibility"], 50.0)
        self.assertEqual(result["matched_skills"], {"python", "docker"})
        self.assertEqual(result["missing_skills"], {"sql", "git"})

    def test_no_matched_skills(self):
        result = analyze_job_match({"Ruby"}, {"python": 3, "sql": 1}, verbose=False)
        self.assertEqual(result["compatibility"], 0.0)
        self.assertEqual(result["matched_skills"], set())
        self.assertEqual(result["missing_skills"], {"python", "sql"})

    def test_unknown_required_skill_counts_as_missing(self):
        result = evaluate_candidate({"Python"}, "Python developer", 
                                    "Required skills:\nPython\nTerraform", verbose=False)
        self.assertEqual(result["missing_skills"], {"terraform"})
        self.assertAlmostEqual(result["compatibility"], 50.0)
        self.assertEqual(result["unrecognized_skills"], ["terraform"])

    def test_empty_inputs_raise_useful_error(self):
        with self.assertRaisesRegex(ValueError, "Job description cannot be empty"):
            evaluate_candidate({"Python"}, "resume text", " ", verbose=False)
        with self.assertRaisesRegex(ValueError, "Resume text cannot be empty"):
            evaluate_candidate({"Python"}, "", "Required skills:\nPython", verbose=False)

    def test_no_recognizable_skills_raises_useful_error(self):
        with self.assertRaisesRegex(ValueError, "No recognizable or explicitly listed skills"):
            evaluate_candidate({"Python"}, "resume text", "A motivated team player.", verbose=False)

    def test_final_score_blend(self):
        self.assertAlmostEqual(calculate_final_score(50, 20), 41.0)

    def test_final_score_rejects_out_of_range_values(self):
        for values in [(-1, 20), (101, 20), (50, -1), (50, 101)]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                calculate_final_score(*values)

    def test_negative_skill_weight_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            analyze_job_match({"Python"}, {"python": -1}, verbose=False)

    def test_text_similarity_empty_or_unusable_text(self):
        self.assertEqual(calculate_text_similarity("", "Python developer"), 0.0)
        self.assertEqual(calculate_text_similarity("!!!", "???"), 0.0)
        self.assertEqual(calculate_text_similarity(None, "Python developer"), 0.0)

    def test_text_similarity_is_bounded(self):
        score = calculate_text_similarity("Python SQL Docker", "Python SQL Git")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
    def test_final_score_rejects_non_finite_values(self):
        for values in [
            (math.nan, 20),
            (math.inf, 20),
            (50, -math.inf),
            (True, 20),
        ]:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    calculate_final_score(*values)

    def test_non_finite_skill_weights_are_rejected(self):
        for weight in [math.nan, math.inf, -math.inf, True]:
            with self.subTest(weight=weight):
                with self.assertRaises(ValueError):
                    analyze_job_match(
                        {"Python"},
                        {"python": weight},
                        verbose=False,
                    )

    def test_duplicate_normalized_job_skills_are_not_double_counted(self):
        result = analyze_job_match(
            {"Python"},
            {"Python": 3, "python programming": 3},
            verbose=False,
        )
        self.assertEqual(result["total_weight"], 3.0)
        self.assertEqual(result["matched_weight"], 3.0)
        self.assertEqual(result["compatibility"], 100.0)

    def test_invalid_candidate_skill_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_job_match(
                {"Python", ""},
                {"python": 3},
                verbose=False,
            )


if __name__ == "__main__":
    unittest.main()
