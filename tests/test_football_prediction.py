import csv
import tempfile
import unittest
from pathlib import Path

from scripts.football_prediction import (
    FIELDS, calculate_probabilities, choose_outcome, create_prediction,
    outcome_for_score, poisson_distribution, resolve_prediction,
)


class FootballPredictionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.temp.name) / "predictions.csv"

    def tearDown(self):
        self.temp.cleanup()

    def test_poisson_distribution_sums_to_one(self):
        self.assertAlmostEqual(sum(poisson_distribution(1.7)), 1.0, places=10)

    def test_probabilities_sum_to_one(self):
        probs = calculate_probabilities(1.5, 0.8)
        self.assertAlmostEqual(sum(probs), 1.0, places=10)
        self.assertTrue(all(0 <= value <= 1 for value in probs))

    def test_strong_home_expectation_has_higher_home_probability(self):
        probs = calculate_probabilities(2.5, 0.5)
        self.assertGreater(probs[0], probs[2])

    def test_invalid_expected_goals_rejected(self):
        for value in (-0.1, 8.1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                poisson_distribution(value)

    def test_score_outcomes(self):
        self.assertEqual(outcome_for_score(2, 0), "HOME")
        self.assertEqual(outcome_for_score(1, 1), "DRAW")
        self.assertEqual(outcome_for_score(0, 3), "AWAY")
        with self.assertRaises(ValueError):
            outcome_for_score(-1, 0)

    def test_prediction_is_recorded_with_open_status(self):
        row = create_prediction(self.ledger, "Arsenal", "Chelsea", 1.6, 1.0)
        with self.ledger.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(reader.fieldnames, FIELDS)
            rows = list(reader)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["prediction_id"], row["prediction_id"])
        self.assertEqual(rows[0]["status"], "OPEN")
        self.assertEqual(rows[0]["actual_outcome"], "")

    def test_same_team_rejected(self):
        with self.assertRaises(ValueError):
            create_prediction(self.ledger, "Arsenal", "arsenal", 1, 1)

    def test_resolve_records_score_and_cannot_overwrite(self):
        row = create_prediction(self.ledger, "Arsenal", "Chelsea", 1.6, 1.0)
        resolved = resolve_prediction(self.ledger, row["prediction_id"], 2, 1)
        self.assertEqual(resolved["actual_outcome"], "HOME")
        self.assertEqual(resolved["status"], "RESOLVED")
        with self.assertRaises(ValueError):
            resolve_prediction(self.ledger, row["prediction_id"], 0, 2)

    def test_unknown_prediction_rejected(self):
        with self.assertRaises(ValueError):
            resolve_prediction(self.ledger, "missing", 0, 0)

    def test_choose_outcome(self):
        self.assertEqual(choose_outcome((0.6, 0.25, 0.15)), "HOME")
        self.assertEqual(choose_outcome((0.2, 0.6, 0.2)), "DRAW")


if __name__ == "__main__":
    unittest.main()
