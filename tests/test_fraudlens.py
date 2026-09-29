import tempfile
import unittest
from pathlib import Path

from fraudlens import assess_file, assess_transaction


class FraudLensTests(unittest.TestCase):
    def test_amount_boundary_and_reason(self):
        at_limit = assess_transaction({"transaction_id": "A", "amount_sgd": "1500.00"})
        above_limit = assess_transaction({"transaction_id": "B", "amount_sgd": "1500.01"})
        self.assertEqual((at_limit["score"], at_limit["decision"]), (0, "pass"))
        self.assertEqual((above_limit["score"], above_limit["decision"]), (1, "review"))
        self.assertEqual(above_limit["reasons"], ["amount above SGD 1500"])

    def test_invalid_amount_is_rejected(self):
        for amount in ("", "NaN", "-1", "0"):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                assess_transaction({"transaction_id": "A", "amount_sgd": amount})

    def test_missing_required_csv_column_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text("transaction_id,amount\nA,2000\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "amount_sgd"):
                assess_file(path)


if __name__ == "__main__":
    unittest.main()
