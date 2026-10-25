import unittest
from apip_timebank.economics import FundingEntry, Deduction, distributable_pool, allocate_rewards

class EconomicEngineTests(unittest.TestCase):
    def test_hybrid_verified_funds_and_approved_deductions(self):
        funding = [
            FundingEntry("sub-1", "NGN", 70000, "VERIFIED", 60000),
            FundingEntry("biz-1", "NGN", 50000, "VERIFIED", 40000),
            FundingEntry("pending", "NGN", 90000, "PENDING", 90000),
            FundingEntry("restricted", "NGN", 30000, "VERIFIED", 30000, restricted=True),
        ]
        deductions = [Deduction("reserve", "NGN", 10000, True), Deduction("unapproved", "NGN", 99999, False)]
        self.assertEqual(distributable_pool(funding, deductions, "NGN"), 90000)

    def test_proportional_allocation_example(self):
        result = allocate_rewards(80000, "EUR", {"a": 100, "b": 200, "c": 500})
        self.assertEqual({x.subscriber_id: x.amount_minor for x in result}, {"a": 8000, "b": 16000, "c": 56000})
        self.assertEqual(sum(x.amount_minor for x in result), 80000)

    def test_zero_pool_and_zero_points(self):
        self.assertEqual(sum(x.amount_minor for x in allocate_rewards(0, "NGN", {"a": 2})), 0)
        self.assertEqual(sum(x.amount_minor for x in allocate_rewards(100, "NGN", {"a": 0, "b": 0})), 0)

    def test_restricted_and_reversed_funding_excluded(self):
        entries = [FundingEntry("r", "NGN", 1000, "VERIFIED", 1000, restricted=True), FundingEntry("x", "NGN", 1000, "VERIFIED", 1000, reversed=True)]
        self.assertEqual(distributable_pool(entries, [], "NGN"), 0)

    def test_duplicate_funding_rejected(self):
        entries = [FundingEntry("same", "NGN", 100, "VERIFIED", 100), FundingEntry("same", "NGN", 100, "VERIFIED", 100)]
        with self.assertRaises(ValueError): distributable_pool(entries, [], "NGN")

    def test_duplicate_funding_id_rejected_across_currencies(self):
        entries = [FundingEntry("same", "NGN", 100, "VERIFIED", 100), FundingEntry("same", "EUR", 100, "VERIFIED", 100)]
        with self.assertRaises(ValueError): distributable_pool(entries, [], "NGN")

    def test_allocations_never_exceed_pool_and_round_deterministically(self):
        first = allocate_rewards(10, "NGN", {"b": 1, "a": 1, "c": 1})
        second = allocate_rewards(10, "NGN", {"c": 1, "b": 1, "a": 1})
        self.assertEqual(first, second)
        self.assertEqual(sum(x.amount_minor for x in first), 10)
        self.assertEqual({x.subscriber_id: x.amount_minor for x in first}, {"a": 4, "b": 3, "c": 3})

    def test_currency_isolated(self):
        entries = [FundingEntry("n", "NGN", 1000, "VERIFIED", 1000), FundingEntry("e", "EUR", 500, "VERIFIED", 500)]
        self.assertEqual(distributable_pool(entries, [], "NGN"), 1000)
        self.assertEqual(distributable_pool(entries, [], "EUR"), 500)

    def test_negative_inputs_rejected(self):
        with self.assertRaises(ValueError): allocate_rewards(-1, "NGN", {"a": 1})
        with self.assertRaises(ValueError): allocate_rewards(1, "NGN", {"a": -1})

if __name__ == "__main__": unittest.main()
