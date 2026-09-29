"""Transparent transaction review rules for fictional payment data."""

import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


AMOUNT_THRESHOLD_SGD = Decimal("1500.00")


def assess_transaction(transaction):
    """Return a review decision and human-readable reasons for one transaction."""
    transaction_id = transaction["transaction_id"].strip()
    if not transaction_id:
        raise ValueError("transaction_id cannot be blank")

    try:
        amount_sgd = Decimal(transaction["amount_sgd"])
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"Invalid amount for {transaction_id}") from exc
    if not amount_sgd.is_finite() or amount_sgd <= 0:
        raise ValueError(f"Amount must be positive and finite for {transaction_id}")

    reasons = []
    if amount_sgd > AMOUNT_THRESHOLD_SGD:
        reasons.append("amount above SGD 1500")

    score = len(reasons)
    return {
        "transaction_id": transaction_id,
        "score": score,
        "reasons": reasons,
        "decision": "review" if score > 0 else "pass",
    }


def assess_file(path):
    """Read a CSV and assess its rows in order."""
    with Path(path).open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"transaction_id", "amount_sgd"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV needs transaction_id and amount_sgd columns")
        return [assess_transaction(row) for row in reader]


if __name__ == "__main__":
    sample_path = Path(__file__).parent / "data" / "sample_transactions.csv"
    for result in assess_file(sample_path):
        print(json.dumps(result))
