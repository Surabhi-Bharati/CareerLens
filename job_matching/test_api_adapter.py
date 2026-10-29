import json
import unittest

from job_matching.api_adapter import (
    _to_json_safe,
    evaluate_candidate_for_api,
)


class TestAPIAdapter(unittest.TestCase):
    def test_result_is_valid_json(self):
        result = evaluate_candidate_for_api(
            {"Python", "SQL"},
            "Python developer with SQL experience.",
            "Required skills:\nPython\nSQL",
        )

        encoded = json.dumps(result, allow_nan=False)
        decoded = json.loads(encoded)

        self.assertEqual(decoded["matched_skills"], ["python", "sql"])
        self.assertEqual(decoded["missing_skills"], [])

    def test_non_finite_output_is_rejected(self):
        for value in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _to_json_safe(value)

    def test_sets_are_converted_to_sorted_lists(self):
        result = _to_json_safe({"skills": {"sql", "python"}})
        self.assertEqual(result["skills"], ["python", "sql"])


if __name__ == "__main__":
    unittest.main()