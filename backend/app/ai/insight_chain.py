"""AI insight generation chain — sends computed metrics to Groq for personalized financial insights."""

import json
import logging

from app.ai.openai_client import GroqClient

logger = logging.getLogger(__name__)

INSIGHT_SYSTEM_PROMPT = """You are a personal financial advisor AI for Indian users.
Given a summary of a user's bank statement transactions (income, spending categories, recurring payments, savings metrics), generate 3-5 personalized financial insights.

Rules:
- Each insight must have: title (short), description (1-2 sentences), severity (info/warning/critical), category (spending category if relevant), and amount_referenced (INR amount if a specific number is mentioned)
- Use Indian Rupee (₹) notation when referencing amounts
- Severity levels:
  - "info": General awareness, positive observations
  - "warning": Concerning patterns that deserve attention
  - "critical": Urgent issues that need immediate action
- Focus on actionable, specific insights — not generic advice
- If savings rate is below 20%, flag it as warning
- If a single category exceeds 30% of total spend, flag it
- If recurring payments exceed 40% of income, flag it
- Always reference specific amounts and percentages from the data

Respond in JSON format as an array:
[{"title": "...", "description": "...", "severity": "info/warning/critical", "category": "...", "amount_referenced": 1234.0}]"""

INSIGHT_USER_PROMPT_TEMPLATE = """Here is the financial summary for this user's bank statement:

Total Income: ₹{total_income}
Total Spend: ₹{total_spend}
Savings: ₹{savings}
Savings Rate: {savings_rate}%

Top Spending Categories:
{categories_text}

Biggest Transactions:
{biggest_txns_text}

Recurring Payments:
{recurring_text}

Monthly Breakdown:
{monthly_text}

Generate 3-5 personalized financial insights based on this data."""


class InsightChain:
    """Chain that sends computed metrics to Groq for insight generation."""

    def __init__(self, client: GroqClient = None):
        self.client = client or GroqClient()

    def generate_insights(
        self,
        metrics: dict,
        recurring_items: list[dict] = None,
    ) -> list[dict]:
        """Generate financial insights from computed metrics and recurring data.
        
        Returns list of insight dicts:
        [{title, description, severity, category, amount_referenced}]
        """
        # Build the user prompt with metrics data
        categories_text = "\n".join(
            f"  - {c['name']}: ₹{c['total']:.0f} ({c['percentage']}% of spend, {c['count']} transactions)"
            for c in metrics.get("top_categories", [])
        )

        biggest_txns_text = "\n".join(
            f"  - {t['description']}: ₹{abs(t['amount']):.0f} on {t['date']}"
            for t in metrics.get("biggest_transactions", [])
        )

        recurring_text = "No recurring payments detected"
        if recurring_items:
            recurring_text = "\n".join(
                f"  - {r['merchant']}: ₹{abs(r['amount']):.0f} ({r['frequency']}, next: {r['next_expected_date']}, annual: ₹{r['annual_cost']:.0f})"
                for r in recurring_items
            )

        monthly_text = "\n".join(
            f"  - {m['month']}: Income ₹{m['income']:.0f}, Spend ₹{m['spend']:.0f}"
            for m in metrics.get("monthly_breakdown", [])
        )

        savings_rate = metrics.get("savings_rate", 0) or 0
        user_prompt = INSIGHT_USER_PROMPT_TEMPLATE.format(
            total_income=metrics.get("total_income", 0),
            total_spend=metrics.get("total_spend", 0),
            savings=metrics.get("savings", 0),
            savings_rate=savings_rate,
            categories_text=categories_text,
            biggest_txns_text=biggest_txns_text,
            recurring_text=recurring_text,
            monthly_text=monthly_text,
        )

        messages = [
            {"role": "system", "content": INSIGHT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        response_text = self.client.chat_completion(messages, temperature=0.3, max_tokens=2000)

        if not response_text:
            logger.warning("AI insight generation failed — returning default insights")
            return self._fallback_insights(metrics)

        # Parse JSON response
        try:
            parsed = json.loads(response_text)
            if isinstance(parsed, list):
                insights = parsed
            elif isinstance(parsed, dict):
                # Check for wrapped array
                for key in ["insights", "results", "data"]:
                    if key in parsed and isinstance(parsed[key], list):
                        insights = parsed[key]
                        break
                else:
                    insights = [parsed]
            else:
                insights = []

            # Validate each insight
            validated = []
            for insight in insights:
                severity = insight.get("severity", "info")
                if severity not in ("info", "warning", "critical"):
                    severity = "info"
                validated.append({
                    "title": insight.get("title", "Financial Observation"),
                    "description": insight.get("description", ""),
                    "severity": severity,
                    "category": insight.get("category"),
                    "amount_referenced": insight.get("amount_referenced"),
                })

            return validated

        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI insight response: {response_text[:200]}")
            return self._fallback_insights(metrics)

    def _fallback_insights(self, metrics: dict) -> list[dict]:
        """Generate rule-based insights when AI is unavailable."""
        insights = []
        total_income = metrics.get("total_income", 0)
        total_spend = metrics.get("total_spend", 0)
        savings = metrics.get("savings", 0)
        savings_rate = metrics.get("savings_rate", 0) or 0

        # Savings rate insight
        if savings_rate < 20:
            insights.append({
                "title": "Low Savings Rate",
                "description": f"Your savings rate is {savings_rate:.1f}%, which is below the recommended 20%. Consider reducing discretionary spending.",
                "severity": "warning",
                "category": None,
                "amount_referenced": savings,
            })
        else:
            insights.append({
                "title": "Healthy Savings Rate",
                "description": f"Your savings rate is {savings_rate:.1f}%. You're saving ₹{savings:.0f} per period — good financial discipline!",
                "severity": "info",
                "category": None,
                "amount_referenced": savings,
            })

        # Top spending category insight
        top_categories = metrics.get("top_categories", [])
        if top_categories:
            top = top_categories[0]
            if top["percentage"] > 30:
                insights.append({
                    "title": f"High {top['name']} Spending",
                    "description": f"You spend {top['percentage']}% of your total on {top['name']} (₹{top['total']:.0f}). This exceeds the 30% threshold.",
                    "severity": "warning",
                    "category": top["name"],
                    "amount_referenced": top["total"],
                })

        return insights
