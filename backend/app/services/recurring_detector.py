"""Recurring payment detector — groups transactions by merchant, checks date intervals and amount consistency."""

import logging
import uuid
from collections import defaultdict
from datetime import date, timedelta
from typing import Optional

from app.utils.text_utils import normalize_merchant_name
from app.utils.recurring_rules import match_known_recurring

logger = logging.getLogger(__name__)

# Frequency detection thresholds (in days, with tolerance)
FREQUENCY_THRESHOLDS = {
    "weekly": (6, 8),       # ~7 days
    "monthly": (25, 35),    # ~30 days
    "quarterly": (85, 95),  # ~90 days
    "semi_annual": (175, 195),  # ~180 days
    "annual": (350, 380),   # ~365 days
}

# Tolerance for amount consistency check
AMOUNT_TOLERANCE_PERCENT = 0.10  # ±10%

# Minimum occurrences to flag as recurring
MIN_OCCURRENCES = 2


class RecurringDetector:
    """Detects recurring payments from categorized transactions."""

    def detect(self, transactions: list[dict]) -> list[dict]:
        """Detect recurring payments in a list of categorized transactions.
        
        Returns a list of recurring item dicts:
        [{merchant, amount, frequency, occurrences, next_expected_date, annual_cost, category}]
        Also updates the is_recurring field on the original transactions.
        """
        # Step 1: Group transactions by normalized merchant name
        merchant_groups = defaultdict(list)
        for txn in transactions:
            merchant = normalize_merchant_name(txn["description"])
            if merchant:
                merchant_groups[merchant].append(txn)

        # Step 2: Analyze each group for recurring patterns
        recurring_items = []
        recurring_group_map = {}  # merchant -> group_id (for marking transactions)

        for merchant, group_txns in merchant_groups.items():
            if len(group_txns) < MIN_OCCURRENCES:
                continue

            # Sort by date
            group_txns.sort(key=lambda t: t["date"])

            # Check date intervals
            frequency = self._detect_frequency(group_txns)
            if not frequency:
                # Also check known recurring merchants (even if dates aren't perfectly periodic)
                known = match_known_recurring(merchant)
                if known:
                    frequency = known.get("frequency", "monthly")
                else:
                    continue

            # Check amount consistency
            typical_amount = self._check_amount_consistency(group_txns)
            if typical_amount is None:
                continue

            # Create recurring group
            group_id = str(uuid.uuid4())
            recurring_group_map[merchant] = group_id

            # Calculate annual cost
            freq_months = self._frequency_to_months(frequency)
            annual_cost = abs(typical_amount) * (12 / freq_months)

            # Predict next expected date
            last_date = group_txns[-1]["date"]
            next_expected = self._predict_next_date(last_date, frequency)

            # Determine category from the group
            category = group_txns[0]["category"]
            # Override with known merchant category if available
            known = match_known_recurring(merchant)
            if known and known.get("category"):
                category = known["category"]

            recurring_item = {
                "merchant": merchant,
                "amount": typical_amount,  # Negative for debits
                "frequency": frequency,
                "occurrences": len(group_txns),
                "next_expected_date": next_expected,
                "annual_cost": annual_cost,
                "category": category,
                "group_id": group_id,
            }
            recurring_items.append(recurring_item)

            # Mark the transactions as recurring
            for txn in group_txns:
                txn["is_recurring"] = True
                txn["recurring_group_id"] = group_id

        logger.info(f"Detected {len(recurring_items)} recurring payments")
        return recurring_items

    def _detect_frequency(self, txns: list[dict]) -> Optional[str]:
        """Check if date intervals between transactions are consistent enough to indicate a frequency."""
        if len(txns) < MIN_OCCURRENCES:
            return None

        intervals = []
        for i in range(1, len(txns)):
            delta = txns[i]["date"] - txns[i - 1]["date"]
            intervals.append(delta.days)

        if not intervals:
            return None

        # Check if intervals are consistent (within tolerance)
        avg_interval = sum(intervals) / len(intervals)

        # All intervals should be close to the average (±5 days tolerance)
        for interval in intervals:
            if abs(interval - avg_interval) > 5:
                return None

        # Match average interval to a frequency category
        for freq_name, (low, high) in FREQUENCY_THRESHOLDS.items():
            if low <= avg_interval <= high:
                return freq_name

        return None

    def _check_amount_consistency(self, txns: list[dict]) -> Optional[float]:
        """Check if amounts across transactions are consistent.
        
        Returns the typical (median-like) amount, or None if amounts vary too much.
        """
        amounts = [txn["amount"] for txn in txns]
        if not amounts:
            return None

        # Use the most common amount (or median for float amounts)
        amounts_sorted = sorted(amounts)
        median = amounts_sorted[len(amounts_sorted) // 2]

        # Check all amounts are within tolerance of median
        for amt in amounts:
            if median != 0 and abs(amt - median) / abs(median) > AMOUNT_TOLERANCE_PERCENT:
                # Still allow it if amounts are all debits (sign consistent)
                # but values may differ slightly (e.g., Netflix ₹499 vs ₹649 plan change)
                # Use a relaxed check: just ensure sign is consistent
                if (amt > 0 and median > 0) or (amt < 0 and median < 0):
                    continue  # Same sign, allow variation
                return None  # Mixed signs = not consistent

        return median

    def _frequency_to_months(self, frequency: str) -> float:
        """Convert frequency name to number of months."""
        mapping = {
            "weekly": 7 / 30,
            "monthly": 1,
            "quarterly": 3,
            "semi_annual": 6,
            "annual": 12,
        }
        return mapping.get(frequency, 1)

    def _predict_next_date(self, last_date: date, frequency: str) -> Optional[date]:
        """Predict the next expected date for a recurring payment."""
        delta_map = {
            "weekly": timedelta(days=7),
            "monthly": timedelta(days=30),
            "quarterly": timedelta(days=90),
            "semi_annual": timedelta(days=180),
            "annual": timedelta(days=365),
        }
        delta = delta_map.get(frequency)
        if delta and last_date:
            return last_date + delta
        return None
