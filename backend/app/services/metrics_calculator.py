"""Financial metrics calculator — computes income, spend, savings, top categories, biggest transactions, monthly breakdown."""

import logging
from collections import defaultdict
from typing import Optional

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Compute comprehensive financial metrics from categorized transactions."""

    def compute(self, transactions: list[dict]) -> dict:
        """Compute all financial metrics from a list of categorized transactions.
        
        Returns a metrics dict matching the MetricsResponse schema:
        {
            total_income, total_spend, savings, savings_rate,
            top_categories, biggest_transactions, monthly_breakdown
        }
        """
        if not transactions:
            return self._empty_metrics()

        # Total income (sum of positive amounts)
        total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)

        # Total spend (sum of negative amounts, as positive number)
        total_spend = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)

        # Savings and savings rate
        savings = total_income - total_spend
        savings_rate = (savings / total_income * 100) if total_income > 0 else None

        # Top categories (spending breakdown)
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        for t in transactions:
            if t["amount"] < 0:  # Only spending
                category_totals[t["category"]] += abs(t["amount"])
                category_counts[t["category"]] += 1

        top_categories = []
        for cat, total in category_totals.items():
            percentage = (total / total_spend * 100) if total_spend > 0 else 0
            top_categories.append({
                "name": cat,
                "total": total,
                "count": category_counts[cat],
                "percentage": round(percentage, 1),
            })
        top_categories.sort(key=lambda c: c["total"], reverse=True)

        # Biggest transactions (top 5 largest debits by absolute amount)
        debits = [t for t in transactions if t["amount"] < 0]
        debits_sorted = sorted(debits, key=lambda t: abs(t["amount"]), reverse=True)
        biggest_transactions = [
            {
                "description": t["description"],
                "amount": t["amount"],
                "date": t["date"].strftime("%Y-%m-%d") if hasattr(t["date"], "strftime") else str(t["date"]),
            }
            for t in debits_sorted[:5]
        ]

        # Monthly breakdown
        monthly_data = defaultdict(lambda: {"income": 0.0, "spend": 0.0})
        for t in transactions:
            if hasattr(t["date"], "strftime"):
                month_key = t["date"].strftime("%Y-%m")
            else:
                month_key = str(t["date"])[:7]  # Fallback
            if t["amount"] > 0:
                monthly_data[month_key]["income"] += t["amount"]
            else:
                monthly_data[month_key]["spend"] += abs(t["amount"])

        monthly_breakdown = []
        for month in sorted(monthly_data.keys()):
            monthly_breakdown.append({
                "month": month,
                "income": monthly_data[month]["income"],
                "spend": monthly_data[month]["spend"],
            })

        return {
            "total_income": round(total_income, 2),
            "total_spend": round(total_spend, 2),
            "savings": round(savings, 2),
            "savings_rate": round(savings_rate, 2) if savings_rate is not None else None,
            "top_categories": top_categories,
            "biggest_transactions": biggest_transactions,
            "monthly_breakdown": monthly_breakdown,
        }

    def _empty_metrics(self) -> dict:
        """Return an empty metrics response for no-data scenarios."""
        return {
            "total_income": 0.0,
            "total_spend": 0.0,
            "savings": 0.0,
            "savings_rate": None,
            "top_categories": [],
            "biggest_transactions": [],
            "monthly_breakdown": [],
        }
