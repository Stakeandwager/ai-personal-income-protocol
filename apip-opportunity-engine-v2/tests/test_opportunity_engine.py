import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.opportunity_engine import generate, readiness_score


class OpportunityEngineTests(unittest.TestCase):
    def test_generates_multiple_hypotheses(self):
        result = generate()
        self.assertGreaterEqual(len(result["opportunities"]), 3)

    def test_ideas_are_explicitly_unvalidated_and_zero_cost(self):
        for idea in generate()["opportunities"]:
            self.assertEqual(idea["status"], "UNVALIDATED_HYPOTHESIS")
            self.assertEqual(idea["estimated_cost_ngn"], 0)
            self.assertTrue(idea["validation_test"])

    def test_does_not_claim_ai_or_income(self):
        result = generate()
        self.assertFalse(result["ai_model_used"])
        self.assertFalse(result["income_generated_or_verified"])
        self.assertFalse(result["external_outreach_performed"])
        self.assertFalse(result["money_movement_performed"])

    def test_readiness_score_is_not_a_sales_probability(self):
        idea = generate()["opportunities"][0]
        self.assertEqual(idea["readiness_score"], readiness_score(idea))
        self.assertIn("not confirmed demand", generate()["notice"])


if __name__ == "__main__":
    unittest.main()
